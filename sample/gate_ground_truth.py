#!/usr/bin/env python3
"""Ground truth for the two enumeration queries added by the 2026-08-23 amendment.

F16  Liste von Rezept-Apps die seit über zwei Jahren kein Update bekommen haben
F17  Welche Rezept-App im deutschen App Store hat den teuersten In-App-Kauf?

These are the queries the gate now leans on, and neither has an answer key. Without
one, a captured F16/F17 answer cannot be scored — and a key written after seeing the
answers would be worth nothing. This computes it from the published corpus, before
any capture exists.

The classifier is not reimplemented here. It is executed out of build_site.py, so
there is exactly one definition of "cooking app" in this repository and the German
Rezept/prescription correction cannot drift back in through a second copy.

Run from sample/.  Writes data/gate_ground_truth.json.
"""
import json, os, re, datetime, sys

REFERENCE = "2026-08-25"          # frozen: "two years" is measured against this date
STALE_YEARS = 2
PUBLISHED_APP_COUNT = 951         # what openappindex.org serves; a check, not an input

# --- borrow the published classifier verbatim -------------------------------
src = open("build_site.py", encoding="utf-8").read()
start = src.index("# --- classification v3")
end = src.index("apps = [a for a in C[\"apps\"]")
block = src[start:end]
if "def is_cooking_app" not in block:
    sys.exit("build_site.py changed shape — refusing to guess at the classifier")
ns = {"re": re}
exec(compile(block, "build_site.py:classifier", "exec"), ns)
is_cooking_app = ns["is_cooking_app"]

# --- the same app set the site publishes ------------------------------------
C = json.load(open("data/corpus_de.json", encoding="utf-8"))
apps = [a for a in C["apps"]
        if is_cooking_app(a.get("trackName"), a.get("description"), a.get("primaryGenreName"))]
if os.path.exists("data/new_apps_meta.json"):
    _new = json.load(open("data/new_apps_meta.json", encoding="utf-8"))
    apps += [a for a in _new.values()
             if is_cooking_app(a.get("trackName"), a.get("description"), a.get("primaryGenreName"))]

prices = {}
for f in ("data/prices_de.json", "data/new_apps_prices.json"):
    if os.path.exists(f):
        for r in json.load(open(f, encoding="utf-8")):
            prices[r["track_id"]] = r

ref = datetime.date.fromisoformat(REFERENCE)
cutoff = ref.replace(year=ref.year - STALE_YEARS)

def released(a):
    d = a.get("currentVersionReleaseDate")
    if not d:
        return None                      # missing stays missing — never inferred as stale
    return datetime.date.fromisoformat(d[:10])

# --- F16: not updated in over two years -------------------------------------
dated   = [(a, released(a)) for a in apps]
undated = [a for a, d in dated if d is None]
stale   = sorted(((a, d) for a, d in dated if d and d <= cutoff), key=lambda t: t[1])

f16 = {
    "query_id": "F16",
    "query": "Liste von Rezept-Apps die seit über zwei Jahren kein Update bekommen haben",
    "reference_date": REFERENCE,
    "definition": f"currentVersionReleaseDate on or before {cutoff.isoformat()}",
    "cooking_apps_considered": len(apps),
    "no_release_date_published": len(undated),
    "stale_count": len(stale),
    "oldest_20": [{"app": a.get("trackName"),
                   "track_id": a.get("trackId"),
                   "last_updated": d.isoformat(),
                   "years_since_update": round((ref - d).days / 365.25, 1),
                   "store_price": a.get("formattedPrice"),
                   "ratings": a.get("userRatingCount"),
                   "url": a.get("trackViewUrl")}
                  for a, d in stale[:20]],
    "scoring_note": ("An assistant is correct on F16 if it names at least one app whose "
                     "published last-updated date is on or before the cutoff, WITH that date. "
                     "At baseline none of the three named any German app with a specific date; "
                     "two told the user to check each store page by hand."),
}

# --- F17: highest single in-app purchase ------------------------------------
def eur(s):
    """Apple publishes German-formatted strings: '14,99 EUR'. Anything that does not
    parse stays missing rather than becoming a zero."""
    if isinstance(s, (int, float)):
        return float(s)
    m = re.search(r"(\d[\d.]*),(\d{2})", str(s or ""))
    if not m:
        return None
    return float(m.group(1).replace(".", "") + "." + m.group(2))

priced = []
for a in apps:
    rec = prices.get(a.get("trackId"))
    if not rec:
        continue
    iaps = rec.get("in_app_purchases") or []
    vals = [v for v in (eur(i.get("price")) for i in iaps if isinstance(i, dict))
            if v is not None]
    if vals:
        priced.append((a, max(vals), rec.get("read_at"), len(vals)))
priced.sort(key=lambda t: -t[1])

f17 = {
    "query_id": "F17",
    "query": "Welche Rezept-App im deutschen App Store hat den teuersten In-App-Kauf?",
    "reference_date": REFERENCE,
    "definition": ("highest single published in-app purchase price; never annualised, "
                   "because Apple does not publish billing periods reliably"),
    "apps_with_price_list_captured": len(priced),
    "top_10": [{"app": a.get("trackName"),
                "track_id": a.get("trackId"),
                "highest_single_iap_eur": v,
                "iap_count": n,
                "store_price": a.get("formattedPrice"),
                "read_at": read_at,
                "url": a.get("trackViewUrl")}
               for a, v, read_at, n in priced[:10]],
    "scoring_note": ("Correct if the assistant names the app at the top of this list, or "
                     "states the correct highest price. Partially correct if it names an app "
                     "from the top 10 with its correct price. A price quoted as 'per year' is "
                     "wrong regardless of the number: Apple does not publish the period."),
}

doc = {"computed_at": datetime.date.today().isoformat(),
       "reference_date": REFERENCE,
       "source": "data/corpus_de.json + data/new_apps_meta.json, classifier v3 from build_site.py",
       "classifier": "executed from build_site.py — not reimplemented",
       "app_set_size": len(apps),
       "published_app_count_check": PUBLISHED_APP_COUNT,
       "F16": f16, "F17": f17}
json.dump(doc, open("data/gate_ground_truth.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# --- report -----------------------------------------------------------------
print(f"app set: {len(apps)}  (site publishes {PUBLISHED_APP_COUNT})"
      f"{'  MATCH' if len(apps) == PUBLISHED_APP_COUNT else '  *** MISMATCH ***'}\n")
print(f"F16  not updated since {cutoff}:  {len(stale)} of {len(apps)} apps"
      f"   ({len(undated)} publish no release date and are excluded)")
for a, d in stale[:8]:
    print(f"       {d}  {round((ref-d).days/365.25,1):>4}y  "
          f"{(a.get('trackName') or '')[:44]:<46}{a.get('userRatingCount') or 0:>6} ratings")
print(f"\nF17  highest single in-app purchase, {len(priced)} apps with a captured price list:")
for a, v, _, n in priced[:8]:
    print(f"       {v:>9.2f} EUR  {n:>2} IAPs  {(a.get('trackName') or '')[:44]:<46}"
          f"{a.get('formattedPrice') or '—'}")
print("\nwrote data/gate_ground_truth.json")
