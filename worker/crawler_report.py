#!/usr/bin/env python3
"""
Weekly crawler report from the Worker's anonymous request log (Workers Analytics Engine).

    python3 worker/crawler_report.py [days]     # default 7

Prints, per crawler, how many requests it made to each page type, and writes the same
counts to sample/data/crawler_report_<date>.json. Counts only: the log holds no IP
address and no full user agent (see /datenschutz.html).

Needs a Cloudflare API token with "Account Analytics: Read" at
~/.config/cloudflare_analytics_token (never printed).
"""
import json, os, sys, urllib.request, urllib.error, collections, datetime

ACCOUNT = "346420fbb345201f091a6daf86735346"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def kind(path):
    if path.startswith("/de/frage/"): return "question page"
    if path.startswith("/de/app/") and path != "/de/app/": return "app page"
    if path.startswith("/de/aenderungen"): return "changelog"
    if path in ("/", "/de/", "/de/app/"): return "home / lists"
    if path.startswith("/data"): return "data"
    if path.endswith((".txt", ".xml")): return "robots, sitemap, llms.txt"
    if path.endswith(".html"): return "documents"
    return "other"

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    p = os.path.expanduser("~/.config/cloudflare_analytics_token")
    if not os.path.exists(p):
        sys.exit("No token at ~/.config/cloudflare_analytics_token (Account Analytics: Read).")
    sql = (f"SELECT blob1 AS path, blob2 AS class, blob3 AS crawler, SUM(_sample_interval) AS hits "
           f"FROM openappindex_requests WHERE timestamp > NOW() - INTERVAL '{days}' DAY "
           f"AND blob2 IN ('search','ai','other-bot') GROUP BY path, class, crawler FORMAT JSON")
    req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/analytics_engine/sql",
                                 data=sql.encode(), method="POST",
                                 headers={"Authorization": f"Bearer {open(p).read().strip()}"})
    try:
        rows = json.loads(urllib.request.urlopen(req, timeout=60).read())["data"]
    except urllib.error.HTTPError as e:
        sys.exit(f"Analytics Engine query failed: HTTP {e.code} {e.read()[:300]!r}")
    table = collections.defaultdict(collections.Counter)
    for r in rows:
        who = r["crawler"] or r["class"]
        table[who][kind(r["path"])] += int(float(r["hits"]))
    kinds = sorted({k for c in table.values() for k in c})
    print(f"Crawler requests, last {days} days\n{'crawler':22}" + "".join(f"{k[:14]:>16}" for k in kinds))
    for who, c in sorted(table.items(), key=lambda x: -sum(x[1].values())):
        print(f"{who:22}" + "".join(f"{c.get(k, 0):>16}" for k in kinds))
    out = os.path.join(ROOT, "sample", "data", f"crawler_report_{datetime.date.today().isoformat()}.json")
    json.dump({"days": days, "counts": {w: dict(c) for w, c in table.items()}}, open(out, "w"), indent=1)
    print(f"-> {out}")

if __name__ == "__main__":
    main()
