#!/usr/bin/env python3
"""
Closure crawl, hop N (N >= 3):  python3 closure_hopn.py 3

Generalizes closure_hop2.py: walks the similarItems shelf from the previous
hop's classified finds (data/hop{N-1}_sleep.json; hop 1's finds live in
data/new_apps_sleep.json), accumulating into the same state file. The hop-N
delta is written to data/closure_hop{N}_new.json, shelf-keyword pre-selected;
the countable number comes from enrich_hopn.py over these stubs.
"""
import json, re, sys, time, urllib.request

N=int(sys.argv[1])
assert N>=3, "hops 1 and 2 have their own scripts, run as they were run"
FRONTIER_FILE="data/new_apps_sleep.json" if N==2 else f"data/hop{N-1}_sleep.json"
OUT=f"data/closure_hop{N}_new.json"

UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
CORE=re.compile(r"schlaf|einschlaf|meditat|entspann|achtsam|beruhig|sleep|meditat|calm|relax",re.I)
STATE="data/closure_state.json"

C=json.load(open("data/corpus_sleep_de.json",encoding="utf-8"))["apps"]
sweep_ids={a["trackId"] for a in C}
frontier_meta=json.load(open(FRONTIER_FILE,encoding="utf-8"))

state=json.load(open(STATE,encoding="utf-8"))
done=set(state["done"]); neigh=state["neighbours"]
known_before={int(k) for k in neigh} | sweep_ids

todo=[{"trackId":a["trackId"],"trackViewUrl":a["trackViewUrl"]}
      for a in frontier_meta.values()
      if a.get("trackViewUrl") and str(a["trackId"]) not in done]
print(f"hop-{N} frontier {len(todo)} to fetch",flush=True)

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
                        "via":a["trackId"],"hop":N}
        done.add(str(a["trackId"]))
    except Exception as e:
        print(f"  ! {a['trackId']} {str(e)[:60]}",flush=True)
        time.sleep(8)
    if i%20==0:
        json.dump({"done":sorted(done),"neighbours":neigh},open(STATE,"w",encoding="utf-8"),ensure_ascii=False)
        print(f"  {i}/{len(todo)} · neighbours total {len(neigh)}",flush=True)
    time.sleep(2.6)

json.dump({"done":sorted(done),"neighbours":neigh},open(STATE,"w",encoding="utf-8"),ensure_ascii=False)

hopn_new={int(k):v for k,v in neigh.items() if int(k) not in known_before}
hopn_core={k:v for k,v in hopn_new.items()
           if CORE.search((v.get("desc") or "")+" "+(v.get("name") or ""))}
print(f"\nDONE fetched {len(done)} total")
print(f"hop-{N}: distinct NEW apps discovered: {len(hopn_new)}")
print(f"  of those, sleep/meditation by shelf keyword: {len(hopn_core)}")
json.dump({str(k):v for k,v in hopn_core.items()},
          open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(f"wrote {OUT}")
