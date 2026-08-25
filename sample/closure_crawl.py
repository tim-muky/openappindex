#!/usr/bin/env python3
"""
Closure crawl (GAL-511 / GAL-532).

One hop over Apple's similar-apps graph from the 914-app recipe seed set.
Each product page carries a `similarItems` shelf of ~10 apps WITH their metadata
attached (adamId, title, developer, subtitle, description, rating count) - so one
fetch yields ten neighbour records without fetching any of them.

Question this answers: how many recipe apps exist that a 25-query sweep never found?

Resumable: checkpoints every 20 fetches, skips anything already done.
"""
import json, re, os, time, urllib.request, collections

UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
RECIPE=re.compile(r"rezept|kochbuch|kochen|backen",re.I)
STATE="data/closure_state.json"

C=json.load(open("data/corpus_de.json",encoding="utf-8"))["apps"]
seed=[a for a in C if RECIPE.search(a.get("description") or "")]
seed_ids={a["trackId"] for a in C}                      # everything the sweep saw
state=json.load(open(STATE,encoding="utf-8")) if os.path.exists(STATE) else {"done":[],"neighbours":{}}
done=set(state["done"]); neigh=state["neighbours"]

def grab(o,key,acc):
    if isinstance(o,dict):
        for k,v in o.items():
            if k==key: acc.append(v)
            grab(v,key,acc)
    elif isinstance(o,list):
        for v in o: grab(v,key,acc)
    return acc

todo=[a for a in seed if str(a["trackId"]) not in done]
print(f"seed {len(seed)} · already done {len(done)} · to fetch {len(todo)}",flush=True)

for i,a in enumerate(todo,1):
    try:
        h=urllib.request.urlopen(urllib.request.Request(a["trackViewUrl"],
            headers={"User-Agent":UA,"Accept-Language":"de-DE,de;q=0.9"}),timeout=40).read().decode("utf-8","replace")
        m=re.search(r'<script type="application/json" id="serialized-server-data">(.*?)</script>',h,re.S)
        if m:
            for shelf in grab(json.loads(m.group(1)),"similarItems",[]):
                for it in (shelf.get("items") or []):
                    aid=it.get("adamId")
                    if not aid: continue
                    neigh[str(aid)]={"name":it.get("title"),"developer":it.get("developerName"),
                        "subtitle":it.get("subtitle"),"desc":(it.get("productDescription") or "")[:600],
                        "rating":it.get("rating"),"rating_count":it.get("ratingCount"),
                        "has_iap":(it.get("offerDisplayProperties") or {}).get("hasInAppPurchases"),
                        "via":a["trackId"]}
        done.add(str(a["trackId"]))
    except Exception as e:
        print(f"  ! {a['trackId']} {str(e)[:60]}",flush=True)
        time.sleep(8)
    if i%20==0:
        json.dump({"done":sorted(done),"neighbours":neigh},open(STATE,"w",encoding="utf-8"),ensure_ascii=False)
        print(f"  {i}/{len(todo)} · neighbours so far {len(neigh)}",flush=True)
    time.sleep(2.6)

json.dump({"done":sorted(done),"neighbours":neigh},open(STATE,"w",encoding="utf-8"),ensure_ascii=False)

new={k:v for k,v in neigh.items() if int(k) not in seed_ids}
new_recipe={k:v for k,v in new.items() if RECIPE.search((v.get("desc") or "")+" "+(v.get("name") or ""))}
print(f"\nDONE fetched {len(done)}/{len(seed)}")
print(f"distinct neighbours discovered: {len(neigh)}")
print(f"  not in the 1,312-app sweep at all: {len(new)}")
print(f"  of those, recipe/cooking apps: {len(new_recipe)}")
zero=[v for v in new_recipe.values() if (v.get('rating_count') or 0)==0]
print(f"  with zero ratings: {len(zero)}")
json.dump(new_recipe,open("data/closure_new_apps.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
