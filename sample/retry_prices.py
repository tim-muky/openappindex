#!/usr/bin/env python3
"""Retry only the rate-limited fetches, slower, with backoff. Merges into prices_de.json."""
import json,re,time,urllib.request,datetime
UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
C={a["trackId"]:a for a in json.load(open("data/corpus_de.json",encoding="utf-8"))["apps"]}
recs=json.load(open("data/prices_de.json",encoding="utf-8"))
todo=[r for r in recs if not r["read_ok"]]
print(f"retrying {len(todo)}",flush=True)
def walk(n,out):
    if isinstance(n,dict):
        if isinstance(n.get("textPairs"),list):
            g=[(p[0],p[1]) for p in n["textPairs"] if isinstance(p,list) and len(p)==2]
            if g: out.append(g)
        for v in n.values(): walk(v,out)
    elif isinstance(n,list):
        for v in n: walk(v,out)
    return out
fixed=0
for i,r in enumerate(todo,1):
    a=C.get(r["track_id"])
    if not a: continue
    for attempt in range(3):
        try:
            h=urllib.request.urlopen(urllib.request.Request(a["trackViewUrl"],
                headers={"User-Agent":UA,"Accept-Language":"de-DE,de;q=0.9"}),timeout=40).read().decode("utf-8","replace")
            m=re.search(r'<p class="subtitle[^"]*">([^<]{0,140})</p>',h)
            if m: r["subtitle"]=m.group(1).strip()
            m=re.search(r'class="attributes[^"]*"[^>]*>([^<]{0,160})<',h)
            if m: r["attributes_line"]=m.group(1).strip()
            m=re.search(r'<script type="application/json" id="serialized-server-data">(.*?)</script>',h,re.S)
            if m:
                g=walk(json.loads(m.group(1)),[])
                if g: r["in_app_purchases"]=[{"name":n,"price":p} for n,p in g[0]]
            r["read_ok"]=True; r.pop("error",None)
            r["read_at"]=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
            fixed+=1; break
        except Exception as e:
            r["error"]=str(e)[:120]
            time.sleep(6*(attempt+1))
    if i%25==0:
        json.dump(recs,open("data/prices_de.json","w",encoding="utf-8"),ensure_ascii=False)
        print(f"  {i}/{len(todo)} fixed={fixed}",flush=True)
    time.sleep(2.6)
json.dump(recs,open("data/prices_de.json","w",encoding="utf-8"),ensure_ascii=False)
ok=sum(1 for r in recs if r["read_ok"]); iap=sum(1 for r in recs if r.get("in_app_purchases"))
print(f"DONE recovered {fixed} · total {ok}/{len(recs)} read · {iap} with prices",flush=True)
