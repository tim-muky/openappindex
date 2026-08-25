#!/usr/bin/env python3
"""
openAPPindex ranking v0 - applied to the fetched sample.

Rules, in full, so anyone can check or disagree:

  MAINTENANCE (0-50)   days since the last version was published
  COST VISIBILITY (0-30)  how much money sits behind the word the search
                          result shows. Penalty is on the GAP, not the price:
                          an app that costs money and says so is not penalised
                          for costing money - the store is penalised for hiding it.
  RELEASE NOTES (0-20)    does the changelog say what changed, or "bug fixes"?

  Rating count / downloads: WEIGHT 0. That is the entire point.

Prices are reported exactly as the App Store prints them. Billing periods are
NOT inferred from in-app purchase names - Apple does not publish them reliably,
so nothing here is annualised or extrapolated.
"""
import json, re, sys

GENERIC = re.compile(r"(fehlerbehebung|bug ?fix|kleinere (verbesserung|fehler)|"
                     r"performance improvement|stabilit|allgemeine verbesserung|"
                     r"we fixed|minor (fix|improvement))", re.I)


def parse_eur(s):
    m = re.search(r"(\d+(?:[.,]\d+)?)", (s or "").replace("\xa0", " "))
    return float(m.group(1).replace(",", ".")) if m else None


def cost_profile(r):
    iaps = r.get("in_app_purchases") or []
    prices = sorted(p for p in (parse_eur(i["price"]) for i in iaps) if p is not None)
    yearly = sorted(p for i, p in zip(iaps, (parse_eur(i["price"]) for i in iaps))
                    if p is not None and re.search(r"jahr|annual|year", i["name"], re.I))
    return {
        "shown_in_search": r.get("formatted_price"),
        "iap_count": len(iaps),
        "iap_min": prices[0] if prices else None,
        "iap_max": prices[-1] if prices else None,
        # only where the app itself labels the plan as yearly
        "cheapest_labelled_yearly": yearly[0] if yearly else None,
        "dearest_labelled_yearly": yearly[-1] if yearly else None,
    }


def score(r):
    d = r.get("days_since_update")
    if d is None:            m = 0
    elif d <= 30:            m = 50
    elif d <= 90:            m = 45
    elif d <= 180:           m = 35
    elif d <= 365:           m = 20
    elif d <= 730:           m = 8
    else:                    m = 0

    c = cost_profile(r)
    hi = c["iap_max"]
    free = (r.get("formatted_price") or "").lower() in ("gratis", "free", "kostenlos")
    if not free and not c["iap_count"]:      cost = 30   # price on the tin, nothing hidden
    elif hi is None:                          cost = 30   # free, no in-app purchases found
    elif hi < 10:                             cost = 22
    elif hi < 30:                             cost = 14
    elif hi < 60:                             cost = 7
    else:                                     cost = 3

    n = r.get("release_notes") or ""
    if not n:                                 notes = 0
    elif GENERIC.search(n) and len(n) < 160:  notes = 5
    elif len(n) >= 200:                       notes = 20
    elif len(n) >= 60:                        notes = 12
    else:                                     notes = 5

    return {"maintenance": m, "cost_visibility": cost, "release_notes": notes,
            "total": m + cost + notes, "cost_profile": c}


def main(path):
    doc = json.load(open(path, encoding="utf-8"))
    for r in doc["results"]:
        r.pop("max_annual_eur", None)
        r["openstore"] = score(r)
    ranked = sorted(doc["results"], key=lambda r: (-r["openstore"]["total"], r["store_rank"]))
    for i, r in enumerate(ranked, 1):
        r["openstore_rank"] = i
    doc["method"] = {
        "version": "v0",
        "weights": {"maintenance": 50, "cost_visibility": 30, "release_notes": 20,
                    "downloads_or_rating_count": 0},
        "note": ("Billing periods are not inferred from in-app purchase names; no price "
                 "is annualised. Yearly figures appear only where the app labels the plan "
                 "as a yearly plan itself.")
    }
    json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"{'store':>5} {'OS':>3}  {'name':<34}{'upd':>7}  {'shown':<8}{'real in-app':<22}{'score':>6}")
    for r in ranked:
        c = r["openstore"]["cost_profile"]
        rng = "-" if not c["iap_count"] else (
            f"{c['iap_min']:.2f}-{c['iap_max']:.2f} EUR ({c['iap_count']})")
        print(f"{r['store_rank']:>5} {r['openstore_rank']:>3}  {r['name'][:32]:<34}"
              f"{r['days_since_update']:>6}d  {(r['formatted_price'] or '')[:7]:<8}{rng:<22}"
              f"{r['openstore']['total']:>6}")


main(sys.argv[1] if len(sys.argv) > 1 else
     "data/rezepte_de.json")
