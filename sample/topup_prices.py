#!/usr/bin/env python3
"""Fetch the recipe-slice apps that have no price record yet."""
import json,re,time,urllib.request,datetime
UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
RECIPE=re.compile(r"rezept|kochbuch|kochen|backen",re.I)
C={a["trackId"]:a for a in json.load(open("data/corpus_de.json",encoding="utf-8"))["apps"]}
recs=json.load(open("data/prices_de.json",encoding="utf-8"))
have={r["track_id"] for r in recs}
todo=[a for tid,a in C.items() if tid not in have and RECIPE.search(a.get("description") or "")]
print(f"top-up: {len(todo)}",flush=True)
def walk(n,out):
    if isinstance(n,dict):
        if isinstance(n.get("textPairs"),list):
            g=[(p[0],p[1]) for p in n["textPairs"] if isinstance(p,list) and len(p)==2]
            if g: out.append(g)
        for v in n.values(): walk(v,out)
    elif isinstance(n,list):
        for v in n: walk(v,out)
    return out
for i,a in enumerate(todo,1):
    r={"track_id":a["trackId"],"subtitle":None,"attributes_line":None,"in_app_purchases":None,
       "read_at":datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),"read_ok":False}
    for att in range(3):
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
            r["read_ok"]=True; break
        except Exception as e:
            r["error"]=str(e)[:120]; time.sleep(6*(att+1))
    recs.append(r)
    if i%20==0:
        json.dump(recs,open("data/prices_de.json","w",encoding="utf-8"),ensure_ascii=False)
        print(f"  {i}/{len(todo)}",flush=True)
    time.sleep(2.6)
json.dump(recs,open("data/prices_de.json","w",encoding="utf-8"),ensure_ascii=False)
ok=sum(1 for r in recs if r["read_ok"])
print(f"DONE total {len(recs)} records · {ok} read ok",flush=True)
