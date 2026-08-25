#!/usr/bin/env python3
"""
Bring the closure-crawl discoveries up to servable quality.

The similarItems graph gave us name/developer/subtitle/description/ratings for the
351 newly found cooking apps, but not the fields the index needs: last-updated date,
version, release notes, store price. Those come from the Lookup API (100 ids per
call, no rate limit observed). Then product pages for the in-app price lists.

Resumable: checkpoints every 20, skips anything already done.
"""
import json, re, os, time, urllib.request, datetime

UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
RECIPE=re.compile(r"rezept|kochbuch|kochen|backen",re.I)
PHARMA=re.compile(r"apothek|e-?rezept|erezept|medikament|arznei|verschreib|krankenkasse|versichert|arzt|ärzt|praxis|gesundheitskarte|krankschreib|telemedizin|einl[oö]sen",re.I)
COOK=re.compile(r"koch|back|zutat|essen|mahlzeit|gericht|k[üu]che|ern[äa]hrung|lebensmittel|einkaufsliste|men[üu]|speise|food|recipe",re.I)
def is_cook(name,desc):
    t=(name or '')+' '+(desc or '')
    if not RECIPE.search(t): return False
    ph=len(PHARMA.findall(t)); ck=len(COOK.findall(t))
    if ph>=3 and ph>ck: return False
    return ck>=2

new=json.load(open("data/closure_new_apps.json",encoding="utf-8"))
ids=[k for k,v in new.items() if is_cook(v.get("name"),v.get("desc"))]
print(f"cooking apps to enrich: {len(ids)}",flush=True)

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
json.dump(meta,open("data/new_apps_meta.json","w",encoding="utf-8"),ensure_ascii=False)

def walk(n,out):
    if isinstance(n,dict):
        if isinstance(n.get("textPairs"),list):
            g=[(p[0],p[1]) for p in n["textPairs"] if isinstance(p,list) and len(p)==2]
            if g: out.append(g)
        for v in n.values(): walk(v,out)
    elif isinstance(n,list):
        for v in n: walk(v,out)
    return out

path="data/new_apps_prices.json"
recs=json.load(open(path,encoding="utf-8")) if os.path.exists(path) else []
done={r["track_id"] for r in recs}
todo=[(k,v) for k,v in meta.items() if int(k) not in done and v.get("trackViewUrl")]
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
        json.dump(recs,open(path,"w",encoding="utf-8"),ensure_ascii=False)
        print(f"  {i}/{len(todo)}",flush=True)
    time.sleep(2.6)
json.dump(recs,open(path,"w",encoding="utf-8"),ensure_ascii=False)
ok=sum(1 for r in recs if r["read_ok"]); iap=sum(1 for r in recs if r.get("in_app_purchases"))
print(f"DONE {ok}/{len(recs)} pages read · {iap} with in-app price lists",flush=True)
