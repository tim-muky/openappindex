#!/usr/bin/env python3
"""
Recompute every published sleep-category headline from data/public/ only —
the files anyone can download — and report match/mismatch against the
published figures (README, docs/second-category-findings.md, working paper §6).

Definitions (stated so they can be argued with):
  free-listed      formattedPrice == "Gratis"
  page read        read_ok is true
  charges in-app   at least one in-app purchase item priced above €0,00
  highest IAP      the largest single item price on the page, as shown; never annualised
Run from anywhere:  python3 sleep/verify_public.py
"""
import json, os, re, statistics

os.chdir(os.path.dirname(os.path.abspath(__file__)))
cat = json.load(open("data/public/category_sleep_de.json", encoding="utf-8"))
pr  = {r["track_id"]: r for r in json.load(open("data/public/prices_sleep_de.json", encoding="utf-8"))["records"]}
apps = cat["apps"]

def eur(s):
    return float(s.replace("\xa0", " ").replace("€", "").strip().replace(".", "").replace(",", "."))

free = [a for a in apps if a["formattedPrice"] == "Gratis"]
read = [a for a in free if pr[a["trackId"]]["read_ok"] is True]
listed = [a for a in read if pr[a["trackId"]]["in_app_purchases"]]
hi = {a["trackId"]: max(eur(i["price"]) for i in pr[a["trackId"]]["in_app_purchases"]) for a in listed}
charging = [t for t, v in hi.items() if v > 0]
sweep = [a for a in apps if a["found_via"]["route"] == "query_sweep"]
not_schlaf = [a for a in sweep if not any(s["query"] == "schlaf" for s in a["found_via"]["seen_in"])]
graph_only = [a for a in apps if a["found_via"]["route"] == "similar_apps_graph"]

rows = [("category apps",                       "3,578",     f"{len(apps):,}"),
        ("listed Gratis",                       "3,417",     f"{len(free):,}"),
        ("free-listed, page read",              "3,351",     f"{len(read):,}"),
        ("…of those, charge in-app",            "2,581",     f"{len(charging):,}"),
        ("median highest single IAP",           "€39.99",    f"€{statistics.median(hi[t] for t in charging):,.2f}"),
        ("max highest single IAP",              "€1,199.99", f"€{max(hi.values()):,.2f}"),
        ("sweep-classified apps",               "1,155",     f"{len(sweep):,}"),
        ("…absent from 'schlaf'",               "1,013",     f"{len(not_schlaf):,}"),
        ("reachable only via similar-apps graph","2,423",    f"{len(graph_only):,}")]

print(f"{'figure':<40} {'published':>11} {'recomputed':>11}  result")
bad = 0
for name, pub, got in rows:
    ok = pub == got; bad += not ok
    print(f"{name:<40} {pub:>11} {got:>11}  {'match' if ok else 'MISMATCH'}")

# context lines — not headlines, printed so the definitions are visible
zero_only = len(listed) - len(charging)
print(f"\ncontext: {len(listed):,} free-listed read pages carry an IAP list; {zero_only} of them list only €0,00 items "
      f"(not counted as charging). Not collected: {len(free) - len(read)} free-listed pages.")

# copyright guard: no description / release-note text anywhere in the public files
leak = [k for a in apps for k in ("description", "releaseNotes") if k in a]
long_str = [(a["trackId"], k) for a in apps for k, v in a.items()
            if isinstance(v, str) and len(v) > 300 and k != "trackViewUrl"]
print(f"copyright guard: description/releaseNotes keys present: {len(leak)} · strings >300 chars: {len(long_str)}")
raise SystemExit(1 if bad or leak or long_str else 0)
