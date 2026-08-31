#!/usr/bin/env python3
"""
Finish hop 2 (GAL-511): retry what the rate limit blocked, classify whatever
that yields, then read the product-page prices for every precision-passed find.

Safe to run repeatedly - every stage skips work already done:

  1. closure_hop2.py     retries only unfetched shelf pages (4 known 404s are
                         delisted apps and will simply fail again)
  2. merge + classify    any shelf find not yet in closure_hop2_cook_meta.json:
                         bulk iTunes lookup -> v3 on full metadata -> v4
                         precision rules -> merged into cook_meta + precise
  3. price pass          product pages for every id in closure_hop2_precise.json
                         not yet in closure_hop2_prices.json, same record shape
                         as enrich_prices.py so build_site.py can read it

Run from sample/. Rate: 2.6s per product page - yesterday 0.8s survived one
hop and 2.6s survived one but not two; this is the whole reason the pass runs
a day later.
"""
import json, re, sys, time, subprocess, urllib.request, datetime

sys.path.insert(0, ".")
from precision_check import v3, v4_excluded

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# ---- 1. retry the unfetched shelf pages ------------------------------------
print("=== stage 1: retry unfetched shelf pages ===", flush=True)
subprocess.run([sys.executable, "closure_hop2.py"], check=True)

# ---- 2. merge + classify anything new --------------------------------------
print("\n=== stage 2: classify and merge new finds ===", flush=True)
new = json.load(open("data/closure_hop2_new.json", encoding="utf-8"))
meta = json.load(open("data/closure_hop2_cook_meta.json", encoding="utf-8"))
precise = json.load(open("data/closure_hop2_precise.json", encoding="utf-8"))
todo = [k for k in new if k not in meta]
looked, added = 0, 0
for i in range(0, len(todo), 50):
    u = f"https://itunes.apple.com/lookup?id={','.join(todo[i:i+50])}&country=de"
    d = json.loads(urllib.request.urlopen(u, timeout=30).read())
    for r in d.get("results", []):
        if r.get("wrapperType") != "software":
            continue
        looked += 1
        if not v3(r.get("trackName"), r.get("description"), r.get("primaryGenreName")):
            continue
        meta[str(r["trackId"])] = r
        if not v4_excluded(r):
            precise[str(r["trackId"])] = r
            added += 1
    time.sleep(1)
json.dump(meta, open("data/closure_hop2_cook_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(precise, open("data/closure_hop2_precise.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"new shelf finds {len(todo)} · looked up {looked} · precision-passed additions {added}", flush=True)
print(f"cook_meta {len(meta)} · precise {len(precise)} · lower bound 941 served + {len(precise)} pending", flush=True)

# ---- 3. price pass over the precise survivors ------------------------------
print("\n=== stage 3: product-page price pass ===", flush=True)
PRICES = "data/closure_hop2_prices.json"
try:
    done = json.load(open(PRICES, encoding="utf-8"))
except FileNotFoundError:
    done = []
have = {r["track_id"] for r in done}
queue = [r for k, r in precise.items() if r["trackId"] not in have]
print(f"{len(precise)} survivors · already priced {len(have)} · to fetch {len(queue)}", flush=True)

def walk(node, out):
    if isinstance(node, dict):
        if isinstance(node.get("textPairs"), list):
            g = [(p[0], p[1]) for p in node["textPairs"] if isinstance(p, list) and len(p) == 2]
            if g: out.append(g)
        for v in node.values(): walk(v, out)
    elif isinstance(node, list):
        for v in node: walk(v, out)
    return out

fails = 0
for i, a in enumerate(queue, 1):
    rec = {"track_id": a["trackId"], "subtitle": None, "attributes_line": None,
           "in_app_purchases": None,
           "read_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "read_ok": False}
    try:
        h = urllib.request.urlopen(urllib.request.Request(a["trackViewUrl"],
            headers={"User-Agent": UA, "Accept-Language": "de-DE,de;q=0.9"}), timeout=40).read().decode("utf-8", "replace")
        m = re.search(r'<p class="subtitle[^"]*">([^<]{0,140})</p>', h)
        if m: rec["subtitle"] = m.group(1).strip()
        m = re.search(r'class="attributes[^"]*"[^>]*>([^<]{0,160})<', h)
        if m: rec["attributes_line"] = m.group(1).strip()
        m = re.search(r'<script type="application/json" id="serialized-server-data">(.*?)</script>', h, re.S)
        if m:
            groups = walk(json.loads(m.group(1)), [])
            if groups: rec["in_app_purchases"] = [{"name": n, "price": p} for n, p in groups[0]]
        rec["read_ok"] = True
        done.append(rec)
    except Exception as e:
        fails += 1
        print(f"  ! {a['trackId']} {str(e)[:60]}", flush=True)
        time.sleep(8)
    if i % 10 == 0:
        json.dump(done, open(PRICES, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"  {i}/{len(queue)}", flush=True)
    time.sleep(2.6)

json.dump(done, open(PRICES, "w", encoding="utf-8"), ensure_ascii=False)
ok = sum(1 for r in done if r["read_ok"]); iap = sum(1 for r in done if r["in_app_purchases"])
print(f"\nDONE prices: {ok}/{len(precise)} read · {iap} with in-app purchase lists · {fails} failed this run", flush=True)
print("Failed fetches rerun on the next invocation; nothing is guessed.", flush=True)
