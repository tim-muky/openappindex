#!/usr/bin/env python3
"""
Closure crawl, hop 2 — sleep/meditation category (mirrors sample/closure_hop2.py).

Hop 1 walked the similar-apps shelf from the 1,167-app v2 seed set and found
1,197 new category apps (v1+v2 classification on full descriptions). This walks
the same shelf from those 1,197, plus retries the seeds hop 1 failed on. Same
state file, so anything already fetched is skipped and the neighbour set
accumulates.

Reports the hop-2 delta separately: closure is only measured if we can say what
each hop added. The delta here is shelf-keyword pre-selected only — the
countable number comes from the finishing pass (enrich_new_apps mechanics) over
these stubs.
"""
import json, re, os, time, urllib.request

UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
CORE=re.compile(r"schlaf|einschlaf|meditat|entspann|achtsam|beruhig|sleep|meditat|calm|relax",re.I)
STATE="data/closure_state.json"

C=json.load(open("data/corpus_sleep_de.json",encoding="utf-8"))["apps"]
sweep_ids={a["trackId"] for a in C}
finds=json.load(open("data/new_apps_sleep.json",encoding="utf-8"))
seed=json.load(open("data/sleep_slice_v2.json",encoding="utf-8"))

state=json.load(open(STATE,encoding="utf-8"))
done=set(state["done"]); neigh=state["neighbours"]
known_before={int(k) for k in neigh} | sweep_ids   # everything any earlier pass saw

# frontier: hop-1 finds, plus the hop-1 seeds that failed (never marked done)
frontier=[{"trackId":a["trackId"],"trackViewUrl":a["trackViewUrl"]}
          for a in finds.values()
          if a.get("trackViewUrl") and str(a["trackId"]) not in done]
retry=[{"trackId":a["trackId"],"trackViewUrl":a["trackViewUrl"]}
       for a in seed if str(a["trackId"]) not in done]
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

hop2_new={int(k):v for k,v in neigh.items() if int(k) not in known_before}
hop2_core={k:v for k,v in hop2_new.items()
           if CORE.search((v.get("desc") or "")+" "+(v.get("name") or ""))}
zero=[v for v in hop2_core.values() if (v.get("rating_count") or 0)==0]

print(f"\nDONE fetched {len(done)} total")
print(f"hop-2: distinct NEW apps discovered (never seen by sweep or hop 1): {len(hop2_new)}")
print(f"  of those, sleep/meditation by shelf keyword: {len(hop2_core)}")
print(f"  with zero ratings (shelf stubs may omit the field): {len(zero)}")
json.dump({str(k):v for k,v in hop2_core.items()},
          open("data/closure_hop2_new.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("wrote data/closure_hop2_new.json")
