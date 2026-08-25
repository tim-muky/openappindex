#!/usr/bin/env python3
"""
How much does the App Store's search miss?

Apple indexes an app's name, subtitle and a 100-character keyword field.
It does not index the description. This measures what that costs:
how many apps that describe themselves as recipe apps, in German, never
appear when someone searches for recipes.

One request per query. Descriptions come back in the same response.
"""
import json, re, time, urllib.request, urllib.parse, collections

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

QUERIES = ["rezepte", "rezept", "kochen", "kochbuch", "rezepte speichern",
           "rezepte sammeln", "rezepte verwalten", "eigene rezepte", "kochrezepte",
           "backen", "essensplaner", "wochenplan essen", "meal planner deutsch",
           "einkaufsliste rezepte", "rezepte app", "digitales kochbuch",
           "rezepte scannen", "rezeptsammlung", "kochbuch digital", "was koche ich heute",
           "vegetarische rezepte", "schnelle rezepte", "rezepte organisieren",
           "lieblingsrezepte", "rezepte importieren"]

RECIPE_WORDS = re.compile(r"rezept|kochbuch|kochen|backen", re.I)


def search(term, limit=200):
    url = ("https://itunes.apple.com/search?term=" + urllib.parse.quote(term) +
           f"&country=de&entity=software&limit={limit}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["results"]


apps, seen_in = {}, collections.defaultdict(set)
for q in QUERIES:
    try:
        res = search(q)
    except Exception as e:
        print("  ! failed", q, e); continue
    for r in res:
        apps[r["trackId"]] = r
        seen_in[r["trackId"]].add(q)
    print(f"  {q:<26} {len(res):>3} results")
    time.sleep(0.4)

# the universe this sweep discovered
total = len(apps)
# apps whose OWN description says they are recipe apps
selfdesc = {i: a for i, a in apps.items()
            if RECIPE_WORDS.search(a.get("description") or "")}
# of those, which never show up for the single most obvious query
rezepte_set = {i for i, qs in seen_in.items() if "rezepte" in qs}
missed = {i: a for i, a in selfdesc.items() if i not in rezepte_set}
# how thin is any single query?
per_query = {q: sum(1 for i, qs in seen_in.items() if q in qs) for q in QUERIES}
only_one = sum(1 for i, qs in seen_in.items() if len(qs) == 1)

out = {
    "queries_run": len(QUERIES),
    "unique_apps_found": total,
    "apps_describing_themselves_as_recipe_apps": len(selfdesc),
    "of_those_missing_from_query_rezepte": len(missed),
    "miss_rate_pct": round(100 * len(missed) / max(1, len(selfdesc)), 1),
    "biggest_single_query": max(per_query.items(), key=lambda kv: kv[1]),
    "single_query_coverage_pct": round(100 * max(per_query.values()) / total, 1),
    "found_by_only_one_query": only_one,
    "found_by_only_one_query_pct": round(100 * only_one / total, 1),
    "examples_missed": [
        {"name": a["trackName"], "seller": a["sellerName"],
         "recipe_words_in_description": len(RECIPE_WORDS.findall(a["description"])),
         "found_only_via": sorted(seen_in[i])[:3],
         "ratings": a.get("userRatingCount", 0)}
        for i, a in sorted(missed.items(),
                           key=lambda kv: -len(RECIPE_WORDS.findall(kv[1]["description"])))[:12]],
}
json.dump(out, open("data/recall_experiment.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print("\n" + "=" * 68)
print(f"queries run                                  {out['queries_run']}")
print(f"unique apps the sweep found                  {out['unique_apps_found']}")
print(f"…that call themselves recipe apps in their own description   {out['apps_describing_themselves_as_recipe_apps']}")
print(f"…of those, NOT returned for 'rezepte'        {out['of_those_missing_from_query_rezepte']}  ({out['miss_rate_pct']}%)")
print(f"best single query covers                     {out['single_query_coverage_pct']}% of what the sweep found")
print(f"apps reachable by exactly one of 25 queries  {out['found_by_only_one_query']}  ({out['found_by_only_one_query_pct']}%)")
