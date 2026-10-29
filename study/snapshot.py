#!/usr/bin/env python3
"""
A one-page snapshot of how an app shows up in openAPPindex's measurements, offered to everyone
who takes part in the developer study (protocol, amendment 2). It uses public App Store data
only. No survey answer is read here, and the results form is never joined to the survey.

    python3 study/snapshot.py --example
        The example linked from the invitations: a fictional app with illustrative numbers.
        Writes study/snapshot-example.html, published at /study/snapshot-example.html (and, per
        invitation text, as counted copies; see sample/build_site.py), and
        study/snapshot-example.jpg, a picture of it for community posts.

    python3 study/snapshot.py --opens [DAYS]
        How often the example was opened, per link (a, b = invitation texts, r = reminder,
        c = community posts, t = test copies), from the site's anonymous request log: page
        fetches, and stylesheet loads, which a browser showing the page makes and a mail scanner
        that only checks the link usually does not. Counts only; the log holds no address.

    python3 study/snapshot.py APP_STORE_LINK_OR_ID [...]
        A participant's snapshot. Re-reads the 25 searches of the app's category today (one
        request per search, cached for the day), looks the app up, and writes HTML and PDF to
        study/records/snapshots/, which is never published.
"""
import base64, html, json, os, re, subprocess, sys, time, urllib.parse, urllib.request
from datetime import date

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "study", "records", "snapshots")
CACHE = os.path.join(ROOT, "study", "records", "search-cache")
FONTS = os.path.join(ROOT, "sample", "site", "fonts")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
UA = "openAPPindex-study/1.0 (+https://openappindex.org/study/)"
DEPTH = 200                                  # Apple's search interface returns at most 200 results
CATS = {
    "sleep": {"label": "sleep and meditation", "obvious": "schlaf"},
    "cooking": {"label": "cooking and recipe", "obvious": "rezepte"},
}

# The example (fictional app, illustrative numbers). The category counts are the index's own.
EXAMPLE = {
    "example": True, "read": "2026-10-30", "app": "Your App", "dev": "Your Studio", "cat": "sleep",
    "released": "2025-03-14", "updated": "2026-09-02", "ratings": 23, "stars": 4.6, "price": "Free",
    "languages": ["DE", "EN"], "route": ("search", 0), "measured": "1–2 September 2026",
    "searches": [("schlaf", 112), ("schlafen", None), ("besser schlafen", None), ("einschlafen", None),
                 ("einschlafhilfe", 64), ("schlaf app", None), ("schlaftracker", None),
                 ("schlafanalyse", None), ("schlafzyklus wecker", None), ("schlafgeschichten", None),
                 ("einschlafgeräusche", 37), ("weisses rauschen", None), ("naturgeräusche schlafen", 21),
                 ("entspannungsmusik", None), ("meditation", None), ("meditieren lernen", None),
                 ("meditation deutsch", None), ("meditation gegen stress", None),
                 ("geführte meditation", None), ("achtsamkeit", None), ("entspannung", None),
                 ("atemübungen", None), ("stress abbauen", None), ("innere ruhe", None),
                 ("hypnose schlafen", None)],
    "year": 2025, "n_year": 755, "rank_year": 141, "n_cat": 3578, "rank_cat": 1206,
}

def esc(s):
    return html.escape(str(s), quote=True)

def day(iso):
    d = date.fromisoformat(iso[:10])
    return f"{d.day} {d.strftime('%b')} {d.year}"

def fonts_css(embed):
    """On the site the fonts come from /fonts/; for an image or a PDF they are embedded."""
    if not embed:
        return '<link rel="stylesheet" href="/fonts/fonts.css">'
    faces = [("Fraunces", "normal", "400 700", "fraunces-normal-400_700-latin.woff2"),
             ("Schibsted Grotesk", "normal", "400 700", "schibsted-grotesk-normal-400-latin.woff2"),
             ("Geist Mono", "normal", "400 500", "geist-mono-normal-400-latin.woff2")]
    css = "".join(
        f"@font-face{{font-family:'{f}';font-style:{s};font-weight:{w};"
        f"src:url(data:font/woff2;base64,{base64.b64encode(open(os.path.join(FONTS, n), 'rb').read()).decode()}) format('woff2')}}"
        for f, s, w, n in faces)
    return f"<style>{css}</style>"

CSS = """
:root{--bg:#ffffff;--ink:#141a16;--muted:#4f4955;--faint:#665f6d;--rule:#e2d2dc;--surface:#f3e9ee;
--surface-2:#e8d8e1;--blue:#0652a9;--pink:#ff7ad9;--pink-hi:#b3238d;color-scheme:light;
--sans:"Schibsted Grotesk",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
--serif:"Fraunces",Georgia,serif;--mono:"Geist Mono",ui-monospace,SFMono-Regular,Menlo,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 var(--sans)}
.page{max-width:780px;margin:0 auto;padding:28px 28px 32px}
.top{display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap;
padding-bottom:14px;border-bottom:1px solid var(--rule)}
.brand{font-weight:800;letter-spacing:-.03em;font-size:19px;color:var(--ink);text-decoration:none}
.brand b{color:var(--blue)}
.stamp,.eyebrow,.q,.pos,.k{font-family:var(--mono);font-variant-numeric:tabular-nums}
.stamp{font-size:11.5px;color:var(--faint)}
.example{margin:16px 0 0;padding:9px 12px;background:var(--surface);border-left:3px solid var(--pink);
font-size:13px;color:var(--muted)}
.example b{color:var(--pink-hi)}
h1{font-family:var(--serif);font-weight:560;font-variation-settings:"opsz" 90;letter-spacing:-.015em;
line-height:1.08;font-size:34px;margin:22px 0 6px}
h1 span{color:var(--blue);font-style:italic}
.sub{color:var(--muted);margin:0 0 22px;font-size:14px}
h2{font-family:var(--serif);font-weight:560;font-size:20px;letter-spacing:-.01em;margin:26px 0 10px}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--rule);border:1px solid var(--rule)}
.tile{background:var(--bg);padding:16px 16px 14px}
.tile p{margin:0;font-size:13px;color:var(--muted)}
.tile .eyebrow{font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--blue);margin:0 0 10px}
.tile .big{font-family:var(--serif);font-weight:560;font-size:30px;line-height:1.05;color:var(--ink);margin:0 0 6px}
.tile .big.none{color:var(--faint)}
.sweep{display:grid;grid-template-columns:1fr 1fr;column-gap:28px;margin:0;padding:0;list-style:none}
.sweep li{display:flex;justify-content:space-between;gap:12px;padding:5px 0;border-bottom:1px solid var(--rule);font-size:13px}
.q{color:var(--ink)}
.q em{font-style:normal;color:var(--faint);font-size:11px;margin-left:6px}
.pos{color:var(--faint);white-space:nowrap}
.found .pos{color:var(--pink-hi);font-weight:500}
.found .pos:before{content:"";display:inline-block;width:8px;height:8px;border-radius:2px;background:var(--pink);
margin-right:7px;vertical-align:0}
.key{margin:8px 0 0;font-size:12px;color:var(--faint)}
.facts{width:100%;border-collapse:collapse;font-size:14px}
.facts th,.facts td{text-align:left;padding:7px 0;border-bottom:1px solid var(--rule);vertical-align:top}
.facts th{font-weight:400;color:var(--muted);width:42%}
.k{font-weight:500}
.read{margin-top:22px;padding:14px 16px;background:var(--surface);font-size:12.5px;color:var(--muted)}
.read p{margin:0 0 6px}
.read p:last-child{margin:0}
.read a,.foot a{color:var(--blue)}
.foot{margin-top:16px;font-size:11.5px;color:var(--faint);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
@media(max-width:640px){.tiles{grid-template-columns:1fr}.sweep{grid-template-columns:1fr}h1{font-size:28px}}
@media print{@page{size:A4;margin:10mm}body{font-size:13px}.page{padding:0}h1{font-size:26px;margin:14px 0 4px}h2{font-size:16px;margin:14px 0 6px}.sub{margin-bottom:14px}.tile{padding:10px 12px}.tile .big{font-size:24px}.sweep li{padding:2px 0;font-size:11.5px}.facts th,.facts td{padding:3px 0;font-size:12.5px}.read{margin-top:12px;padding:9px 12px;font-size:10.5px}.read p{margin:0 0 4px}.foot{margin-top:10px}}
"""

def render(s, embed=False):
    cat = CATS[s["cat"]]
    found = [(q, p) for q, p in s["searches"] if p]
    obvious = dict(s["searches"]).get(cat["obvious"])
    rows = sorted(found, key=lambda x: x[1]) + [(q, None) for q, p in s["searches"] if not p]
    li = "".join(
        f'<li class="{"found" if p else ""}"><span class="q">{esc(q)}'
        f'{"<em>obvious</em>" if q == cat["obvious"] else ""}</span>'
        f'<span class="pos">{f"#{p}" if p else "—"}</span></li>' for q, p in rows)
    route, hop = s["route"] or (None, None)
    if route == "search":
        reach = ("Search", "one of the 25 searches found it directly")
    elif route == "graph":
        steps = f", {hop} step{'s' if hop != 1 else ''} away from the search results" if hop else ""
        reach = ("Similar apps", f"only Apple's “similar apps” lists led to it{steps}")
    else:
        reach = ("Not yet", "the app was not in the index when it was measured")
    tiles = [
        ("The obvious search", f"#{obvious}" if obvious else "—",
         f"for „{cat['obvious']}“, the word most people type" if obvious
         else f"not in the first {DEPTH} results for „{cat['obvious']}“"),
        ("25 common searches", f"{len(found)} of {len(s['searches'])}",
         f"find it in their first {DEPTH} results"),
        ("How our index reached it", reach[0], reach[1]),
    ]
    tiles_html = "".join(
        f'<div class="tile"><p class="eyebrow">{esc(e)}</p><p class="big{" none" if v == "—" else ""}">{esc(v)}</p>'
        f"<p>{esc(c)}</p></div>" for e, v, c in tiles)
    ranks = []
    if s.get("rank_year"):
        ranks.append(f'<span class="k">{s["rank_year"]:,}</span> of {s["n_year"]:,} {cat["label"]} apps released in {s["year"]}')
    if s.get("rank_cat"):
        ranks.append(f'<span class="k">{s["rank_cat"]:,}</span> of {s["n_cat"]:,} {cat["label"]} apps in the index')
    stars = f" · average {s['stars']:.1f} ★" if s.get("ratings") and s.get("stars") else ""
    facts = [("Ratings in the German App Store", f'<span class="k">{s["ratings"]:,}</span>{stars}'),
             ("Rank by number of ratings", "<br>".join(ranks) or "—"),
             ("Released", day(s["released"])), ("Last update", day(s["updated"])),
             ("Price", esc(s["price"])), ("Languages", esc(", ".join(s["languages"]) or "—"))]
    facts_html = "".join(f"<tr><th>{esc(k)}</th><td>{v}</td></tr>" for k, v in facts)
    example = ('<p class="example"><b>Example</b> · a fictional app with illustrative numbers. Your '
               "snapshot uses your app's own public App Store data, read on the day it is made.</p>"
               if s.get("example") else "")
    title = "Example snapshot: how an app shows up" if s.get("example") else f"Snapshot: how {s['app']} shows up"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — openAPPindex</title>
<meta name="description" content="What participants of the study “The cost of being found” receive: a one-page snapshot of how their app shows up in openAPPindex's App Store measurements.">
{fonts_css(embed)}<style>{CSS}</style></head>
<body><div class="page">
<div class="top"><a class="brand" href="https://openappindex.org/">open<b>APP</b>index</a>
<span class="stamp">Snapshot · read {day(s["read"])} · App Store Germany</span></div>
{example}
<h1>How <span>{esc(s["app"])}</span> shows up</h1>
<p class="sub">{esc(cat["label"].capitalize())} · {esc(s["dev"])} · released {date.fromisoformat(s["released"]).strftime("%B %Y")}</p>
<div class="tiles">{tiles_html}</div>
<h2>The 25 searches, read {day(s["read"])}</h2>
<ul class="sweep">{li}</ul>
<p class="key">#&nbsp;position in the results · —&nbsp;not in the first {DEPTH} results</p>
<h2>Among similar apps</h2>
<table class="facts">{facts_html}</table>
<div class="read">
<p><b>How to read this.</b> Search positions come from Apple's public search interface for the German
App Store (first {DEPTH} results per search), read on {day(s["read"])}. A phone can show a slightly
different order, and positions change from day to day.</p>
<p>The 25 searches are the ones the index uses for this category. “How our index reached it” is from the
measurement of {esc(s["measured"])}: one of the searches found the app, or only Apple's “similar apps”
lists on other apps' pages led to it. Ranks count ratings only; they say nothing about quality.</p>
<p>This is not a rating of the app, and nothing here is for sale. Taking part in the study changes nothing
about how an app appears in the index. Method and data: <a href="https://openappindex.org/">openappindex.org</a></p>
</div>
<div class="foot"><span>openAPPindex · an independent, open index of the App Store</span>
<span>For participants of <a href="https://openappindex.org/study/">The cost of being found</a></span></div>
</div></body></html>
"""

def chrome(src_html, out, kind, size=(860, 1400), scale=1.5):
    """Render with headless Chrome: an image of the page (cut below the content), or an A4 PDF."""
    path = out + ".tmp.html"
    open(path, "w", encoding="utf-8").write(src_html)
    args = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-pdf-header-footer",
            f"--window-size={size[0]},{size[1]}", f"--force-device-scale-factor={scale}"]
    args += [f"--screenshot={out}"] if kind == "png" else [f"--print-to-pdf={out}"]
    subprocess.run(args + ["file://" + os.path.abspath(path)], check=True, capture_output=True, timeout=120)
    os.remove(path)
    if kind == "png":
        from PIL import Image, ImageChops
        im = Image.open(out).convert("RGB")
        box = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
        im.crop((0, 0, im.width, min(im.height, box[3] + int(28 * scale)))).save(out)

def example():
    page = render(EXAMPLE)
    open(os.path.join(ROOT, "study", "snapshot-example.html"), "w", encoding="utf-8").write(page)
    png = os.path.join(ROOT, "study", "snapshot-example.png")
    chrome(render(EXAMPLE, embed=True), png, "png", size=(800, 2000), scale=1.25)
    from PIL import Image
    jpg = os.path.join(ROOT, "study", "snapshot-example.jpg")
    Image.open(png).save(jpg, quality=72, optimize=True, progressive=True)
    os.remove(png)
    print("wrote study/snapshot-example.html and study/snapshot-example.jpg",
          f"({os.path.getsize(jpg) // 1024} KB)")

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=30))

def universe():
    """Every app of the two measured categories, with how the index reached it and the ratings
    count and release date it had when measured. An app measured in both categories is in both."""
    apps = []
    sl = json.load(open(os.path.join(ROOT, "sleep", "data", "public", "category_sleep_de.json")))
    for a in sl["apps"]:
        fv = a.get("found_via") or {}
        apps.append({"id": a["trackId"], "cat": "sleep", "ratings": a.get("userRatingCount") or 0, "rel": a["releaseDate"][:10],
                              "route": ("search", 0) if fv.get("route") == "query_sweep" else ("graph", fv.get("hop")),
                     "measured": "1–2 September 2026", "queries": sl["queries"]})
    pub = os.path.join(ROOT, "sample", "data", "public")
    corpus = json.load(open(os.path.join(pub, "corpus_de.json")))
    closure = json.load(open(os.path.join(pub, "closure_apps.json")))
    snaps = sorted(f for f in os.listdir(os.path.join(pub, "snapshots")) if f.endswith(".json"))
    cooking = json.load(open(os.path.join(pub, "snapshots", snaps[-1])))["apps"]
    found = {a["trackId"]: a for a in corpus["apps"]}
    via_graph = {a["trackId"]: a for a in closure}
    for tid, a in cooking.items():
        tid = int(tid)
        rec = found.get(tid) or via_graph.get(tid) or {}
        apps.append({"id": tid, "cat": "cooking", "ratings": rec.get("userRatingCount") or 0, "rel": a["rel"],
                     "route": ("search", 0) if tid in found else ("graph", None),
                     "measured": "August–September 2026", "queries": corpus["queries"]})
    return apps

def sweep(cat, queries):
    """Today's results for the category's 25 searches, one request each, cached for the day."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{cat}-{date.today().isoformat()}.json")
    cached = json.load(open(path)) if os.path.exists(path) else {}
    for q in queries:
        if q in cached:
            continue
        url = ("https://itunes.apple.com/search?" +
               urllib.parse.urlencode({"term": q, "country": "de", "entity": "software", "limit": DEPTH}))
        cached[q] = [r["trackId"] for r in get_json(url)["results"]]
        json.dump(cached, open(path, "w"))
        time.sleep(3)
    return cached

def participant(arg):
    m = re.search(r"id(\d+)", arg) or re.fullmatch(r"\s*(\d+)\s*", arg)
    if not m:
        sys.exit(f"not an App Store link or id: {arg}")
    tid = int(m.group(1))
    apps = universe()
    me = next((x for x in apps if x["id"] == tid), None)     # sleep first if measured in both
    if not me:
        print(f"{tid}: not in the two measured categories; no snapshot (say so in the reply)")
        return
    look = get_json(f"https://itunes.apple.com/lookup?id={tid}&country=de")["results"]
    if not look:
        print(f"{tid}: not found in the German App Store today; no snapshot")
        return
    a = look[0]
    results = sweep(me["cat"], me["queries"])
    year = int(me["rel"][:4])
    peers = [x for x in apps if x["cat"] == me["cat"]]
    same = [x for x in peers if int(x["rel"][:4]) == year]
    s = {"example": False, "read": date.today().isoformat(), "app": a["trackName"], "dev": a["sellerName"],
         "cat": me["cat"], "released": a["releaseDate"][:10], "updated": a["currentVersionReleaseDate"][:10],
         "ratings": a.get("userRatingCount") or 0, "stars": a.get("averageUserRating"),
         "price": "Free" if not a.get("price") else a.get("formattedPrice", ""),
         "languages": a.get("languageCodesISO2A") or [], "route": me["route"], "measured": me["measured"],
         "searches": [(q, results[q].index(tid) + 1 if tid in results[q] else None) for q in me["queries"]],
         "year": year, "n_year": len(same), "rank_year": 1 + sum(x["ratings"] > me["ratings"] for x in same),
         "n_cat": len(peers), "rank_cat": 1 + sum(x["ratings"] > me["ratings"] for x in peers)}
    os.makedirs(OUT, exist_ok=True)
    base = os.path.join(OUT, f"{tid}-{s['read']}")
    page = render(s, embed=True)
    open(base + ".html", "w", encoding="utf-8").write(page)
    chrome(page, base + ".pdf", "pdf")
    print(f"{tid}: {s['app']} → {base}.pdf")

def opens(days=30):
    links = {"a": "text A", "b": "text B", "r": "reminder", "c": "community", "t": "test copies", "": "study page"}
    paths = [f"/study/snapshot-example{'-' + v if v else ''}.html" for v in links] + \
            [f"/study/snapshot-open-{v}.css" for v in links if v]
    sql = (f"SELECT blob1 AS path, blob2 AS class, SUM(_sample_interval) AS hits FROM openappindex_requests "
           f"WHERE timestamp > NOW() - INTERVAL '{int(days)}' DAY AND blob1 IN ({', '.join(repr(x) for x in paths)}) "
           f"GROUP BY path, class FORMAT JSON")
    token = open(os.path.expanduser("~/.config/cloudflare_analytics_token")).read().strip()
    req = urllib.request.Request("https://api.cloudflare.com/client/v4/accounts/346420fbb345201f091a6daf86735346"
                                 "/analytics_engine/sql", data=sql.encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token}"})
    rows = json.loads(urllib.request.urlopen(req, timeout=60).read())["data"]
    tokens = json.load(open(os.path.join(ROOT, "study", "frame", "tokens.json")))
    sent = {v.lower(): sum(1 for t in tokens if t.get("version") == v and "address" in t)    # from amendment 2 on
            for v in ("A", "B")}
    sent["r"] = sum(1 for t in tokens if t.get("channel") == "email-reminder")
    print(f"Example snapshot, last {days} days: page fetches (people / bots) and stylesheet loads")
    for v, label in links.items():
        page = f"/study/snapshot-example{'-' + v if v else ''}.html"
        hits = {r["class"]: int(float(r["hits"])) for r in rows if r["path"] == page}
        css = sum(int(float(r["hits"])) for r in rows if r["path"] == f"/study/snapshot-open-{v}.css" and r["class"] == "human")
        people, bots = hits.get("human", 0), sum(n for c, n in hits.items() if c != "human")
        base = f"  of {sent[v]:,} sent" if v in sent else ""
        print(f"  {label:12} page {people:>5} / {bots:<4} stylesheet {css if v else '-':>5}{base}")

if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--example"]:
        example()
    elif a[:1] == ["--opens"]:
        opens(*(int(x) for x in a[1:2]))
    elif a:
        for x in a:
            participant(x)
    else:
        sys.exit(__doc__)
