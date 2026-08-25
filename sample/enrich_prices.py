#!/usr/bin/env python3
"""
Fetch real in-app purchase prices for the recipe slice.

Store facts only: this reads the price list Apple publishes on each product
page. No reviews, no third-party content, no personal data. Where a price
cannot be read the record says so - never guessed.
"""
import json, re, sys, time, urllib.request, datetime

UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
RECIPE=re.compile(r"rezept|kochbuch|kochen|backen", re.I)

C=json.load(open("data/corpus_de.json",encoding="utf-8"))
apps=[a for a in C["apps"] if RECIPE.search(a.get("description") or "")]
print(f"recipe slice: {len(apps)} apps", flush=True)

def walk(node,out):
    if isinstance(node,dict):
        if isinstance(node.get("textPairs"),list):
            g=[(p[0],p[1]) for p in node["textPairs"] if isinstance(p,list) and len(p)==2]
            if g: out.append(g)
        for v in node.values(): walk(v,out)
    elif isinstance(node,list):
        for v in node: walk(v,out)
    return out

done=[]
for i,a in enumerate(apps,1):
    rec={"track_id":a["trackId"],"subtitle":None,"attributes_line":None,
         "in_app_purchases":None,"read_at":datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
         "read_ok":False}
    try:
        h=urllib.request.urlopen(urllib.request.Request(a["trackViewUrl"],
            headers={"User-Agent":UA,"Accept-Language":"de-DE,de;q=0.9"}),timeout=30).read().decode("utf-8","replace")
        m=re.search(r'<p class="subtitle[^"]*">([^<]{0,140})</p>',h)
        if m: rec["subtitle"]=m.group(1).strip()
        m=re.search(r'class="attributes[^"]*"[^>]*>([^<]{0,160})<',h)
        if m: rec["attributes_line"]=m.group(1).strip()
        m=re.search(r'<script type="application/json" id="serialized-server-data">(.*?)</script>',h,re.S)
        if m:
            groups=walk(json.loads(m.group(1)),[])
            if groups: rec["in_app_purchases"]=[{"name":n,"price":p} for n,p in groups[0]]
        rec["read_ok"]=True
    except Exception as e:
        rec["error"]=str(e)[:120]
    done.append(rec)
    if i%25==0:
        json.dump(done,open("data/prices_de.json","w",encoding="utf-8"),ensure_ascii=False)
        print(f"  {i}/{len(apps)}",flush=True)
    time.sleep(0.8)

json.dump(done,open("data/prices_de.json","w",encoding="utf-8"),ensure_ascii=False)
ok=sum(1 for r in done if r["read_ok"]); iap=sum(1 for r in done if r["in_app_purchases"])
print(f"DONE {ok}/{len(done)} pages read, {iap} with in-app purchase lists",flush=True)
