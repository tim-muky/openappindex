#!/usr/bin/env python3
"""
Closure crawl, hop 2 (GAL-511).

Hop 1 walked the similar-apps shelf from the 914-app seed and found 247 new
cooking apps (v3 classification). This walks the same shelf from those 247,
plus retries the 48 seeds hop 1 failed on. Same state file, so anything
already fetched is skipped and the neighbour set accumulates.

Reports the hop-2 delta separately: closure is only measured if we can say
what each hop added.
"""
import json, re, os, time, urllib.request

UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
RECIPE=re.compile(r"rezept|kochbuch|kochen|backen",re.I)
# v3 classification, identical to build_site.py — pharmacy and games stay out
PHARMA=re.compile(r"apothek|e-?rezept|medikament|arzt|ärzt|verschreib|krankenkasse",re.I)
COOK=re.compile(r"koch|back|zutat|essen|mahlzeit|gericht|k[üu]che|ern[äa]hrung|"
                r"lebensmittel|einkaufsliste|men[üu]|speise|food|recipe",re.I)
STATE="data/closure_state.json"

C=json.load(open("data/corpus_de.json",encoding="utf-8"))["apps"]
seed_ids={a["trackId"] for a in C}
meta=json.load(open("data/new_apps_meta.json",encoding="utf-8"))
new_cook=set(json.load(open("data/new_cook_ids.json",encoding="utf-8")))

state=json.load(open(STATE,encoding="utf-8"))
done=set(state["done"]); neigh=state["neighbours"]
known_before={int(k) for k in neigh} | seed_ids   # everything any earlier pass saw

# frontier: hop-1 cooking finds not yet fetched, plus the failed hop-1 seeds
frontier=[{"trackId":a["trackId"],"trackViewUrl":a["trackViewUrl"]}
          for a in meta.values()
          if a["trackId"] in new_cook and a.get("trackViewUrl")
          and str(a["trackId"]) not in done]
retry=[{"trackId":a["trackId"],"trackViewUrl":a["trackViewUrl"]}
       for a in C
       if RECIPE.search(a.get("description") or "") and str(a["trackId"]) not in done]
todo=frontier+retry
print(f"hop-2 frontier {len(frontier)} · seed retries {len(retry)} · to fetch {len(todo)}",flush=True)

def grab(o,key,acc):
    if isinstance(o,dict):
        for k,v in o.items():
            if k==key: acc.append(v)
            grab(v,key,acc)
    elif isinstance(o,list):
        for v in o: grab(v,key,acc)
    return acc

for i,a in enumerate(todo,1):
    try:
        h=urllib.request.urlopen(urllib.request.Request(a["trackViewUrl"],
            headers={"User-Agent":UA,"Accept-Language":"de-DE,de;q=0.9"}),timeout=40).read().decode("utf-8","replace")
        m=re.search(r'<script type="application/json" id="serialized-server-data">(.*?)</script>',h,re.S)
        if m:
            for shelf in grab(json.loads(m.group(1)),"similarItems",[]):
                for it in (shelf.get("items") or []):
                    aid=it.get("adamId")
                    if not aid or str(aid) in neigh: continue
                    neigh[str(aid)]={"name":it.get("title"),"developer":it.get("developerName"),
                        "subtitle":it.get("subtitle"),"desc":(it.get("productDescription") or "")[:600],
                        "rating":it.get("rating"),"rating_count":it.get("ratingCount"),
                        "has_iap":(it.get("offerDisplayProperties") or {}).get("hasInAppPurchases"),
                        "via":a["trackId"],"hop":2}
        done.add(str(a["trackId"]))
    except Exception as e:
        print(f"  ! {a['trackId']} {str(e)[:60]}",flush=True)
        time.sleep(8)
    if i%20==0:
        json.dump({"done":sorted(done),"neighbours":neigh},open(STATE,"w",encoding="utf-8"),ensure_ascii=False)
        print(f"  {i}/{len(todo)} · neighbours total {len(neigh)}",flush=True)
    time.sleep(2.6)

json.dump({"done":sorted(done),"neighbours":neigh},open(STATE,"w",encoding="utf-8"),ensure_ascii=False)

# --- hop-2 delta, v3-classified ---------------------------------------------
hop2_new={int(k):v for k,v in neigh.items() if int(k) not in known_before}
def looks_cooking(v):
    t=(v.get("desc") or "")+" "+(v.get("name") or "")
    if not RECIPE.search(t): return False
    ph,ck=len(PHARMA.findall(t)),len(COOK.findall(t))
    if ph>=3 and ph>ck: return False
    return ck>=2
hop2_cook={k:v for k,v in hop2_new.items() if looks_cooking(v)}
zero=[v for v in hop2_cook.values() if (v.get("rating_count") or 0)==0]

print(f"\nDONE fetched {len(done)} total")
print(f"hop-2: distinct NEW apps discovered (never seen by sweep or hop 1): {len(hop2_new)}")
print(f"  of those, cooking apps (v3 shelf-classification): {len(hop2_cook)}")
print(f"  with zero ratings: {len(zero)}")
json.dump({str(k):v for k,v in hop2_cook.items()},
          open("data/closure_hop2_new.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("wrote data/closure_hop2_new.json")
