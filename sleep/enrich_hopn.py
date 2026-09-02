#!/usr/bin/env python3
"""
Finishing pass for hop N (N >= 3):  python3 enrich_hopn.py 3

Generalizes enrich_hop2.py:  data/closure_hop{N}_new.json  →
data/hop{N}_meta.json · data/hop{N}_sleep.json · data/hop{N}_prices.json

Lookup API for full metadata, v1+v2 classification on full descriptions before
anything is counted, then product pages for the survivors' price lists.
Resumable on the price stage.
"""
import json, re, os, sys, time, urllib.request, datetime
from classify import v1
from precision_v2 import v2_excluded

N=int(sys.argv[1]); assert N>=3
IN=f"data/closure_hop{N}_new.json"
META,SLEEP,PRICES=(f"data/hop{N}_meta.json",f"data/hop{N}_sleep.json",f"data/hop{N}_prices.json")

UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

ids=list(json.load(open(IN,encoding="utf-8")).keys())
print(f"hop-{N} keyword candidates to look up: {len(ids)}",flush=True)

KEEP=("trackId","trackName","sellerName","artistId","description","releaseNotes","releaseDate",
      "currentVersionReleaseDate","version","averageUserRating","userRatingCount","formattedPrice",
      "primaryGenreName","genres","trackViewUrl","artworkUrl100","languageCodesISO2A")
meta={}
for i in range(0,len(ids),100):
    chunk=ids[i:i+100]
    url="https://itunes.apple.com/lookup?id="+",".join(chunk)+"&country=de"
    try:
        r=json.loads(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=40).read())
        for a in r.get("results",[]):
            meta[str(a["trackId"])]={k:a.get(k) for k in KEEP}
    except Exception as e:
        print("  ! lookup",e,flush=True)
    time.sleep(1.0)
print(f"metadata retrieved for {len(meta)}/{len(ids)}",flush=True)
json.dump(meta,open(META,"w",encoding="utf-8"),ensure_ascii=False)

kept={}; v1_out=v2_out=0
for k,a in meta.items():
    ok,_=v1(a)
    if not ok: v1_out+=1; continue
    if v2_excluded(a): v2_out+=1; continue
    kept[k]=a
print(f"classified on full descriptions: v1 excludes {v1_out} · v2 excludes {v2_out} "
      f"· HOP-{N} NEW SLEEP/MEDITATION APPS: {len(kept)}",flush=True)
json.dump(kept,open(SLEEP,"w",encoding="utf-8"),ensure_ascii=False,indent=1)

def walk(n,out):
    if isinstance(n,dict):
        if isinstance(n.get("textPairs"),list):
            g=[(p[0],p[1]) for p in n["textPairs"] if isinstance(p,list) and len(p)==2]
            if g: out.append(g)
        for v in n.values(): walk(v,out)
    elif isinstance(n,list):
        for v in n: walk(v,out)
    return out

recs=json.load(open(PRICES,encoding="utf-8")) if os.path.exists(PRICES) else []
done={r["track_id"] for r in recs}
todo=[(k,v) for k,v in kept.items() if int(k) not in done and v.get("trackViewUrl")]
print(f"product pages to fetch: {len(todo)}",flush=True)
for i,(k,v) in enumerate(todo,1):
    r={"track_id":int(k),"subtitle":None,"in_app_purchases":None,"read_ok":False,
       "read_at":datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    for att in range(3):
        try:
            h=urllib.request.urlopen(urllib.request.Request(v["trackViewUrl"],
                headers={"User-Agent":UA,"Accept-Language":"de-DE,de;q=0.9"}),timeout=40).read().decode("utf-8","replace")
            m=re.search(r'<p class="subtitle[^"]*">([^<]{0,140})</p>',h)
            if m: r["subtitle"]=m.group(1).strip()
            m=re.search(r'<script type="application/json" id="serialized-server-data">(.*?)</script>',h,re.S)
            if m:
                g=walk(json.loads(m.group(1)),[])
                if g: r["in_app_purchases"]=[{"name":n,"price":p} for n,p in g[0]]
            r["read_ok"]=True; break
        except Exception as e:
            r["error"]=str(e)[:100]; time.sleep(6*(att+1))
    recs.append(r)
    if i%20==0:
        json.dump(recs,open(PRICES,"w",encoding="utf-8"),ensure_ascii=False)
        print(f"  {i}/{len(todo)}",flush=True)
    time.sleep(2.6)
json.dump(recs,open(PRICES,"w",encoding="utf-8"),ensure_ascii=False)
ok=sum(1 for r in recs if r["read_ok"]); iap=sum(1 for r in recs if r.get("in_app_purchases"))
print(f"DONE {ok}/{len(recs)} pages read · {iap} with in-app price lists",flush=True)
