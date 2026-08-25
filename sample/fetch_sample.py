#!/usr/bin/env python3
"""
openAPPindex proof-of-concept sample.

Pulls a real App Store search result set and enriches each app with the two
dimensions the store does not let you search on:
  1. maintenance  - when was this actually last updated?
  2. real cost    - what does it cost after "Gratis"?

Every field is read from a public Apple source and stamped with the date it
was read. No estimates, no invented values. If a field cannot be read, it is
recorded as null and excluded from scoring - never guessed.

Sources:
  - iTunes Search API   https://itunes.apple.com/search   (ranking + metadata)
  - App Store product page  https://apps.apple.com/...    (in-app purchase list)
"""
import json, re, sys, time, urllib.request, urllib.parse, datetime

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
FETCHED_AT = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Language": "de-DE,de;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def search(term, country="de", limit=15):
    url = (f"https://itunes.apple.com/search?term={urllib.parse.quote(term)}"
           f"&country={country}&entity=software&limit={limit}")
    return json.loads(get(url))["results"]


def walk_textpairs(node, out):
    """Collect every AnnotationItem textPairs group (in-app purchase lists)."""
    if isinstance(node, dict):
        if "textPairs" in node and isinstance(node["textPairs"], list):
            group = [(p[0], p[1]) for p in node["textPairs"]
                     if isinstance(p, list) and len(p) == 2]
            if group:
                out.append(group)
        for v in node.values():
            walk_textpairs(v, out)
    elif isinstance(node, list):
        for v in node:
            walk_textpairs(v, out)


def product_page(track_view_url):
    html = get(track_view_url)
    out = {"attributes_line": None, "in_app_purchases": None, "page_read": True}

    m = re.search(r'class="attributes[^"]*"[^>]*>([^<]{0,160})<', html)
    if m:
        out["attributes_line"] = m.group(1).strip()

    m = re.search(r'<script type="application/json" id="serialized-server-data">(.*?)</script>',
                  html, re.S)
    if m:
        groups = []
        walk_textpairs(json.loads(m.group(1)), groups)
        if groups:
            # first group belongs to this app's own information section
            out["in_app_purchases"] = [{"name": n, "price": p} for n, p in groups[0]]
    return out


def parse_eur(s):
    m = re.search(r"(\d+(?:[.,]\d+)?)", (s or "").replace(".", ""))
    return float(m.group(1).replace(",", ".")) if m else None


def annualised_max(iaps):
    """Highest plausible yearly spend visible on the product page. Monthly
    prices are x12 only when the name says monthly - otherwise taken as-is."""
    best = None
    for p in iaps or []:
        v = parse_eur(p["price"])
        if v is None:
            continue
        name = p["name"].lower()
        if any(k in name for k in ("monat", "month", "/mo", "wochen", "week")):
            v = v * 12 if "monat" in name or "month" in name else v * 52
        if best is None or v > best:
            best = round(v, 2)
    return best


def main(term, country="de", limit=15):
    rows = []
    for rank, r in enumerate(search(term, country, limit), start=1):
        page = {}
        try:
            page = product_page(r["trackViewUrl"])
            time.sleep(1.2)
        except Exception as e:
            page = {"attributes_line": None, "in_app_purchases": None,
                    "page_read": False, "error": str(e)}
        last = r.get("currentVersionReleaseDate")
        days = None
        if last:
            days = (datetime.datetime.now(datetime.timezone.utc)
                    - datetime.datetime.fromisoformat(last.replace("Z", "+00:00"))).days
        rows.append({
            "store_rank": rank,
            "name": r.get("trackName"),
            "seller": r.get("sellerName"),
            "track_id": r.get("trackId"),
            "url": r.get("trackViewUrl"),
            "icon": r.get("artworkUrl100"),
            "formatted_price": r.get("formattedPrice"),
            "rating": r.get("averageUserRating"),
            "rating_count": r.get("userRatingCount"),
            "version": r.get("version"),
            "first_released": r.get("releaseDate"),
            "last_updated": last,
            "days_since_update": days,
            "release_notes": (r.get("releaseNotes") or "").strip(),
            "min_ios": r.get("minimumOsVersion"),
            "genre": r.get("primaryGenreName"),
            "attributes_line": page.get("attributes_line"),
            "in_app_purchases": page.get("in_app_purchases"),
            "max_annual_eur": annualised_max(page.get("in_app_purchases")),
            "page_read": page.get("page_read"),
        })
    doc = {"query": term, "storefront": country, "fetched_at": FETCHED_AT,
           "sources": {
               "ranking": "https://itunes.apple.com/search (public iTunes Search API)",
               "in_app_purchases": "App Store product page, serialized-server-data JSON"},
           "caveat": ("iTunes Search API ordering is the closest public proxy for App Store "
                      "search ranking. It excludes paid placements and personalisation, so the "
                      "live in-app ranking may differ."),
           "results": rows}
    path = f"/Users/timmeyerdierks/Claude/BAS/sample/data/{term.replace(' ','_')}_{country}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"wrote {path}  ({len(rows)} apps)")


if __name__ == "__main__":
    import urllib.parse
    main(sys.argv[1] if len(sys.argv) > 1 else "rezepte",
         sys.argv[2] if len(sys.argv) > 2 else "de",
         int(sys.argv[3]) if len(sys.argv) > 3 else 15)
