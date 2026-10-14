#!/usr/bin/env python3
"""
Dated snapshot of the served index — the unit the weekly changelog diffs.

    python3 snapshot.py --from-local [--date YYYY-MM-DD]
        Build a snapshot from the local working data (corpus + closure metadata
        + product-page price reads), classified with the same v4 rule the site
        serves. The date defaults to the corpus file's read date. Use this to
        reconstruct the snapshot the site was built from.

    python3 snapshot.py --fetch [--ids-from data/public/snapshots/<date>.json]
        Re-read every app of the previous snapshot through the public Lookup API
        (100 ids per call) and write today's snapshot. An id the API no longer
        returns is recorded as ok=false — "not found on read", nothing more.
        In-app purchase lists come from product pages, which are rate-limited;
        this mode does NOT read them and marks them as not collected, so a price
        diff between two --fetch snapshots is never invented from a missing read.

Output: data/public/snapshots/<date>.json — public fields only (no descriptions,
no release-note text; lengths and presence only, as in export_public.py).
The set of apps is fixed by the pipeline that admits apps to the index
(build_corpus.py, the closure crawl, precision_check.py). A --fetch snapshot
never adds apps: "new in the index" is a pipeline decision, not a lookup result.
"""
import json, os, sys, time, datetime, argparse, urllib.request
from classify import is_cooking_app, CLASSIFIER_VERSION
from site_common import parse_eur

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
SNAP_DIR = "data/public/snapshots"

def compact(a, read, price=None):
    """Public-safe record for one app. None means not collected, never zero. `read` is the
    date the Lookup fields were read — it travels with the record, not with the file."""
    notes = (a.get("releaseNotes") or "").strip()
    r = {"read": read, "n": a.get("trackName"), "dev": a.get("sellerName"), "genre": a.get("primaryGenreName"),
         "v": a.get("version"), "upd": (a.get("currentVersionReleaseDate") or "")[:10] or None,
         "rel": (a.get("releaseDate") or "")[:10] or None, "price": a.get("formattedPrice"),
         "notes": bool(notes), "notes_len": len(notes), "ok": True,
         "iap_n": None, "iap_min": None, "iap_max": None, "iap_read": None}
    if price and price.get("read_ok"):
        iaps = price.get("in_app_purchases") or []
        vals = sorted(v for v in (parse_eur(i.get("price")) for i in iaps) if v is not None)
        r["iap_n"] = len(iaps)
        r["iap_min"], r["iap_max"] = (vals[0], vals[-1]) if vals else (None, None)
        r["iap_read"] = (price.get("read_at") or "")[:10] or None
    return r

def from_local(date):
    C = json.load(open("data/corpus_de.json", encoding="utf-8"))
    corpus_read = datetime.date.fromtimestamp(os.path.getmtime("data/corpus_de.json")).isoformat()
    apps = [(a, corpus_read) for a in C["apps"]
            if is_cooking_app(a.get("trackName"), a.get("description"), a.get("primaryGenreName"))]
    if os.path.exists("data/new_apps_meta.json"):
        closure_read = datetime.date.fromtimestamp(os.path.getmtime("data/new_apps_meta.json")).isoformat()
        new = json.load(open("data/new_apps_meta.json", encoding="utf-8"))
        apps += [(a, closure_read) for a in new.values()
                 if is_cooking_app(a.get("trackName"), a.get("description"), a.get("primaryGenreName"))]
    prices = {}
    for f in ("data/prices_de.json", "data/new_apps_prices.json"):
        if os.path.exists(f):
            for r in json.load(open(f, encoding="utf-8")):
                prices[r["track_id"]] = r
    recs = {str(a["trackId"]): compact(a, rd, prices.get(a["trackId"])) for a, rd in apps}
    if not date:
        date = max(rd for _, rd in apps)
    return {"read_at": date, "storefront": "de", "classifier": CLASSIFIER_VERSION,
            "source": ("local working data: iTunes Search API sweep + closure crawl (per-app `read` dates) "
                       "+ product-page price reads (per-app `iap_read` dates)"),
            "collected": {"lookup": True, "in_app_purchases": True}, "apps": recs}

def fetch(ids_from):
    prev = json.load(open(ids_from, encoding="utf-8"))
    ids = list(prev["apps"].keys())
    got = {}
    for i in range(0, len(ids), 100):
        chunk = ids[i:i+100]
        url = "https://itunes.apple.com/lookup?id=" + ",".join(chunk) + "&country=de"
        for attempt in range(3):
            try:
                r = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40).read())
                for a in r.get("results", []):
                    got[str(a["trackId"])] = a
                break
            except Exception as e:
                print(f"  ! lookup {i}: {e}", file=sys.stderr, flush=True)
                time.sleep(5 * (attempt + 1))
        time.sleep(1.0)
    today = datetime.date.today().isoformat()
    recs = {}
    for tid in ids:
        if tid in got:
            recs[tid] = compact(got[tid], today)
        else:
            # keep the previous name so the changelog can say which app it was
            p = prev["apps"][tid]
            recs[tid] = {"read": today, "n": p.get("n"), "dev": p.get("dev"), "genre": p.get("genre"), "v": None,
                         "upd": None, "rel": p.get("rel"), "price": None, "notes": None, "notes_len": None,
                         "ok": False, "iap_n": None, "iap_min": None, "iap_max": None, "iap_read": None}
    print(f"lookup: {len(got)} of {len(ids)} ids returned; {len(ids)-len(got)} not found on read", flush=True)
    return {"read_at": today, "storefront": "de", "classifier": prev.get("classifier"),
            "source": "public Lookup API re-read of the previous snapshot's ids",
            "collected": {"lookup": True, "in_app_purchases": False}, "apps": recs}

def latest_snapshot():
    if not os.path.isdir(SNAP_DIR): return None
    fs = sorted(f for f in os.listdir(SNAP_DIR) if f.endswith(".json"))
    return os.path.join(SNAP_DIR, fs[-1]) if fs else None

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-local", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--ids-from")
    args = ap.parse_args()
    if args.from_local == args.fetch:
        sys.exit("choose exactly one of --from-local / --fetch")
    snap = from_local(args.date) if args.from_local else fetch(args.ids_from or latest_snapshot())
    os.makedirs(SNAP_DIR, exist_ok=True)
    out = f"{SNAP_DIR}/{snap['read_at']}.json"
    if os.path.exists(out) and not args.date:
        sys.exit(f"{out} exists — a dated read is not overwritten; delete it deliberately if you must")
    json.dump(snap, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    n = len(snap["apps"]); ok = sum(1 for r in snap["apps"].values() if r["ok"])
    iap = sum(1 for r in snap["apps"].values() if r["iap_read"])
    print(f"{out}: {n} apps · {ok} found on read · {iap} with in-app purchase lists read")
