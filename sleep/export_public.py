#!/usr/bin/env python3
"""
Build the publishable dataset for the second category (sleep & meditation,
German iOS storefront) into data/public/. Mirrors sample/export_public.py.

The working files hold each app's full store description and release notes —
third-party copyrighted text. It is not published. Only derived measurements
of that text are (its length, whether release notes exist), as in cooking.

The app set is exactly the final v3 category produced by apply_v3.py: the
sweep-visible slice plus hops 1-4 of the similar-apps graph, every hop filtered
under identical rules (v1 classifier + precision v2 + rule MH). 3,578 apps.

What IS published:
  category_sleep_de.json  one record per category app: Lookup API facts, how
                          the app was found (query sweep with query+position,
                          or graph hop N with the app it was reached from),
                          classification version
  prices_sleep_de.json    one product-page read per category app: when it was
                          read, whether the read succeeded, and Apple's
                          published in-app purchase list (names + prices, as
                          shown, never converted or annualised)
  README.md               licence, field meanings, what is deliberately omitted

Missing values stay null. Nothing is estimated, inferred or zero-filled.
Run from sleep/:  python3 export_public.py
"""
import json, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
OUT = "data/public"
os.makedirs(OUT, exist_ok=True)

CLASSIFICATION = "v3"   # v1 classifier + precision v2 + rule MH (precision_v3.py), via apply_v3.py

# (label, hop, final v3 category file, product-page file, closure provenance file)
SETS = [("sweep", 0, "data/sleep_slice_v3.json", "data/prices_sleep_de.json",  None),
        ("hop-1", 1, "data/hop1_sleep_v3.json",  "data/new_apps_prices.json",  "data/closure_new_apps.json"),
        ("hop-2", 2, "data/hop2_sleep_v3.json",  "data/hop2_prices.json",      "data/closure_hop2_new.json"),
        ("hop-3", 3, "data/hop3_sleep_v3.json",  "data/hop3_prices.json",      "data/closure_hop3_new.json"),
        ("hop-4", 4, "data/hop4_sleep_v3.json",  "data/hop4_prices.json",      "data/closure_hop4_new.json")]

# Factual Lookup-API fields. Same choice as cooking, minus fields this pipeline
# never collected (price, currency, minimumOsVersion) — those are absent, not null.
KEEP = ("trackId","trackName","sellerName","artistId","primaryGenreName","genres",
        "version","releaseDate","currentVersionReleaseDate","formattedPrice",
        "averageUserRating","userRatingCount","languageCodesISO2A","trackViewUrl")

def strip(a):
    r = {k: a.get(k) for k in KEEP}          # missing stays null — never dropped, never filled
    n = a.get("releaseNotes")
    r["release_notes_present"] = None if n is None else bool(n.strip())
    r["release_notes_length"]  = None if n is None else len(n.strip())
    d = a.get("description")
    r["description_length"]    = None if d is None else len(d)
    return r

corpus = json.load(open("data/corpus_sleep_de.json", encoding="utf-8"))

apps, prices, seen = [], [], set()
for label, hop, f, pf, cf in SETS:
    d = json.load(open(f, encoding="utf-8"))
    rows = d if isinstance(d, list) else list(d.values())
    prov = json.load(open(cf, encoding="utf-8")) if cf else {}
    pr = {r["track_id"]: r for r in json.load(open(pf, encoding="utf-8"))}
    for a in rows:
        tid = a["trackId"]
        assert tid not in seen, f"duplicate app {tid} across hops"
        seen.add(tid)
        r = strip(a)
        if hop == 0:
            r["found_via"] = {"route": "query_sweep", "hop": 0,
                              "seen_in": [{"query": s["query"], "position": s["position"]}
                                          for s in (a.get("seen_in") or [])],
                              "reached_from_track_id": None}
        else:
            r["found_via"] = {"route": "similar_apps_graph", "hop": hop, "seen_in": None,
                              "reached_from_track_id": (prov.get(str(tid)) or {}).get("via")}
        r["classification"] = CLASSIFICATION
        apps.append(r)

        p = pr.get(tid)
        if p is None:   # no product-page record at all: say so, guess nothing
            prices.append({"track_id": tid, "read_at": None, "read_ok": None, "in_app_purchases": None})
        else:
            prices.append({"track_id": tid, "read_at": p.get("read_at"), "read_ok": p.get("read_ok"),
                           "in_app_purchases": p.get("in_app_purchases")})

hops = {}
for r in apps: hops[r["found_via"]["hop"]] = hops.get(r["found_via"]["hop"], 0) + 1

out = {"title": "openAPPindex — sleep & meditation apps, German iOS App Store",
       "licence": "CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/",
       "attribution": "openAPPindex — https://openappindex.org",
       "storefront": corpus["storefront"],
       "measured": "2026-09-01 to 2026-09-02 (product-page read time is recorded per app in prices_sleep_de.json; "
                   "per-app Lookup API time was not recorded)",
       "classification": "v3 = v1 classifier + precision v2 + rule MH, applied uniformly to every hop by apply_v3.py; "
                         "rules and dated amendments in openappindex-sleep-category-protocol.md",
       "queries": corpus["queries"],
       "counts": {"apps": len(apps), "by_hop": {str(k): v for k, v in sorted(hops.items())}},
       "note": "Descriptions and release-note text are deliberately omitted — see sleep/export_public.py",
       "apps": apps}
json.dump(out, open(f"{OUT}/category_sleep_de.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pout = {"licence": out["licence"], "attribution": out["attribution"], "storefront": out["storefront"],
        "note": "Apple's published in-app purchase list per product page, as shown (name + price label). "
                "read_ok=false: page not collected. read_ok=true with in_app_purchases=null: page read, "
                "no in-app purchase list found on it. Prices are single items, never annualised.",
        "records": prices}
json.dump(pout, open(f"{OUT}/prices_sleep_de.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

README = f"""# openAPPindex dataset — sleep & meditation, German iOS App Store

{len(apps):,} apps, measured 1–2 September 2026. Licence: **CC BY 4.0**
(https://creativecommons.org/licenses/by/4.0/). Attribution: openAPPindex — https://openappindex.org

Factual records about publicly listed apps, read from public Apple endpoints and dated.
Built by `sleep/export_public.py`; every headline figure is recomputed from these files by
`sleep/verify_public.py`.

## Files

- `category_sleep_de.json` — one record per app in the final v3 category. Lookup API fields
  (`trackId`, `trackName`, `sellerName`, `artistId`, `primaryGenreName`, `genres`, `version`,
  `releaseDate`, `currentVersionReleaseDate`, `formattedPrice` = the store's own price label,
  `averageUserRating`, `userRatingCount`, `languageCodesISO2A`, `trackViewUrl`);
  `description_length`, `release_notes_present`, `release_notes_length` (measurements only);
  `found_via` — `query_sweep` (hop 0, with every query and result position the app appeared at)
  or `similar_apps_graph` (hop 1–4, with the app it was first reached from);
  `classification` (`v3`).
- `prices_sleep_de.json` — one product-page read per app: `read_at`, `read_ok`, and
  `in_app_purchases` (name + price exactly as Apple shows them).

## Rules

- **Missing stays null.** `read_ok: false` means the page was not collected. `read_ok: true`
  with `in_app_purchases: null` means the page was read and showed no in-app purchase list.
  Nothing is estimated, inferred, or zero-filled.
- **No annualising.** An in-app purchase price is the price of one item. Apple does not publish
  billing periods reliably, so none is converted.
- **Deliberately omitted:** app descriptions and release-note text (the developers' copyright),
  product-page subtitles, icons. Regenerate full records locally with the scripts in `sleep/`.
- Fields this pipeline never collected (`price`, `currency`, `minimumOsVersion`) are absent.

Corrections: korrektur@openappindex.org
"""
open(f"{OUT}/README.md", "w", encoding="utf-8").write(README)

tot = sum(os.path.getsize(f"{OUT}/{f}") for f in os.listdir(OUT))
print(f"public dataset: {len(apps)} apps · {len(prices)} price records · {tot/1024/1024:.1f} MB")
print("by hop:", ", ".join(f"{k}={v}" for k, v in sorted(hops.items())))
print("omitted: full descriptions, release-note text, subtitles")
