#!/usr/bin/env python3
"""
Build the publishable dataset.

The working corpus holds each app's full store description and release notes —
several thousand words of third-party copyrighted text per file. Republishing
that wholesale would contradict the rule this project applies to its own pages
(short cited quotes only), so it is not published.

What IS published: the facts. Names, developers, categories, versions, dates,
prices, and Apple's published in-app purchase lists. All of it is factual data
about apps, none of it is anyone's creative text, and every row can be
re-derived from the public endpoints with the scripts in this repo.

Anyone who wants the descriptions can regenerate them: build_corpus.py.
"""
import json, os, re

os.makedirs("data/public", exist_ok=True)
KEEP = ("trackId","trackName","sellerName","artistId","primaryGenreName","genres",
        "version","releaseDate","currentVersionReleaseDate","formattedPrice","price",
        "currency","averageUserRating","userRatingCount","minimumOsVersion",
        "languageCodesISO2A","trackViewUrl")

def strip(a):
    r = {k: a.get(k) for k in KEEP if a.get(k) is not None}
    # keep only whether a changelog exists and how substantial it is — not its text
    n = (a.get("releaseNotes") or "").strip()
    r["release_notes_present"] = bool(n)
    r["release_notes_length"] = len(n)
    # keep the recipe-relevance signal without the description itself
    d = a.get("description") or ""
    r["description_length"] = len(d)
    return r

corpus = json.load(open("data/corpus_de.json", encoding="utf-8"))
out = {"storefront": corpus["storefront"], "queries": corpus["queries"],
       "note": "Descriptions and release-note text are deliberately omitted — see export_public.py",
       "apps": [strip(a) for a in corpus["apps"]]}
json.dump(out, open("data/public/corpus_de.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

prices = []
for f in ("data/prices_de.json","data/new_apps_prices.json"):
    if os.path.exists(f):
        for r in json.load(open(f, encoding="utf-8")):
            prices.append({"track_id": r["track_id"], "read_at": r.get("read_at"),
                           "read_ok": r.get("read_ok"), "subtitle": r.get("subtitle"),
                           "in_app_purchases": r.get("in_app_purchases")})
json.dump(prices, open("data/public/prices_de.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

if os.path.exists("data/new_apps_meta.json"):
    meta = json.load(open("data/new_apps_meta.json", encoding="utf-8"))
    json.dump([strip(a) for a in meta.values()],
              open("data/public/closure_apps.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

for f in ("gate_baseline_perplexity.json","gate_baseline_chatgpt.json"):
    if os.path.exists(f"data/{f}"):
        json.dump(json.load(open(f"data/{f}",encoding="utf-8")),
                  open(f"data/public/{f}","w",encoding="utf-8"), ensure_ascii=False, indent=1)

tot = sum(os.path.getsize(f"data/public/{f}") for f in os.listdir("data/public"))
print(f"public dataset: {len(out['apps'])} apps · {len(prices)} price records · {tot/1024/1024:.1f} MB")
print("omitted: full descriptions, release-note text")
