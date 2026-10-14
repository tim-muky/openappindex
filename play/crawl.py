#!/usr/bin/env python3
"""
Google Play, German store: the cooking and sleep & meditation categories (docs/play-protocol.md).

    python3 play/crawl.py --seed            # category pages -> hop-0 queue
    python3 play/crawl.py --run [--pilot N] # read app and developer pages, hop by hop, until the stop rule
    python3 play/crawl.py --report          # counts per hop and category

Rules (protocol, 2026-10-14): robots.txt-allowed pages only, one request at a time, >= 3 s
apart, >= 30 min pause on 429/503, crawler names itself. Same classifiers as iOS: cooking v4,
sleep v1 + precision v3. Developer email addresses are not collected. State is resumable in
play/data/state.json (gitignored: it holds descriptions, which are the developers' copyright).
"""
import json, os, re, sys, time, html, urllib.request, urllib.error, urllib.parse, importlib.util
from datetime import datetime, timezone

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "play", "data")
STATE = os.path.join(DATA, "state.json")
UA = "Mozilla/5.0 (compatible; openAPPindex-bot/1.0; +https://openappindex.org/methode.html)"
PACE, BACKOFF = 3.0, 1800
SEED_CATEGORIES = ["FOOD_AND_DRINK", "HEALTH_AND_FITNESS", "LIFESTYLE", "MEDICAL"]
MAX_HOP, MIN_GROWTH = 6, 0.02

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.join(ROOT, path)))
    spec.loader.exec_module(mod)
    return mod

cook = _load("cook_classify", "sample/classify.py")
sleep_v1 = _load("sleep_classify", "sleep/classify.py")
sleep_v3 = _load("sleep_precision_v3", "sleep/precision_v3.py")

GENRE = {"ENTERTAINMENT": "Entertainment", "TOOLS": "Utilities", "PHOTOGRAPHY": "Photo & Video",
         "VIDEO_PLAYERS": "Photo & Video", "TRAVEL_AND_LOCAL": "Travel", "MAPS_AND_NAVIGATION": "Travel",
         "FINANCE": "Finance", "BUSINESS": "Business", "NEWS_AND_MAGAZINES": "Magazines & Newspapers",
         "BOOKS_AND_REFERENCE": "Book", "SHOPPING": "Shopping", "EDUCATION": "Education",
         "FOOD_AND_DRINK": "Food & Drink", "HEALTH_AND_FITNESS": "Health & Fitness",
         "LIFESTYLE": "Lifestyle", "MEDICAL": "Medical", "MUSIC_AND_AUDIO": "Music"}

def apple_genre(play_cat):
    if not play_cat: return None
    if play_cat.startswith("GAME"): return "Games"
    return GENRE.get(play_cat, play_cat)

def classify(rec):
    g = apple_genre(rec.get("category"))
    cooking = bool(cook.is_cooking_app(rec.get("name"), rec.get("description"), g))
    r = {"trackName": rec.get("name"), "description": rec.get("description"), "primaryGenreName": g}
    ok, _ = sleep_v1.v1(r)
    sleep = bool(ok and not sleep_v3.v3_excluded(r))
    return {"cooking": cooking, "sleep": sleep}

# ---------------------------------------------------------------- fetching
_last = [0.0]
def get(url):
    for attempt in range(6):
        wait = PACE - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "de-DE,de;q=0.9"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                print(f"  {datetime.now():%H:%M} HTTP {e.code}, pausing {BACKOFF // 60} min", flush=True)
                time.sleep(BACKOFF); continue
            return e.code, ""
        except Exception as e:
            print(f"  network error {type(e).__name__}, retry", flush=True); time.sleep(30)
    return 0, ""

DETAILS = re.compile(r'/store/apps/details\?id=([\w.]+)')
DEVLINK = re.compile(r'href="(/store/apps/(?:dev|developer)\?id=[^"&]+)')

def visible_text(h):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))

def parse_app(pkg, h):
    rec = {"pkg": pkg, "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    for m in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S):
        try: d = json.loads(m)
        except Exception: continue
        if d.get("@type") == "SoftwareApplication":
            rec["name"] = d.get("name"); rec["category"] = d.get("applicationCategory")
            a = d.get("author") or {}
            rec["developer"], rec["developer_site"] = a.get("name"), a.get("url")
            rec["rating_count"] = int((d.get("aggregateRating") or {}).get("ratingCount") or 0) or None
            offers = d.get("offers") or []
            rec["price"] = float(offers[0]["price"]) if offers and offers[0].get("price") not in (None, "") else None
    m = re.search(r'data-g-id="description"[^>]*>(.*?)</div>', h, re.S)
    rec["description"] = html.unescape(re.sub(r"<br\s*/?>", "\n", re.sub(r"<(?!br)[^>]+>", "", m.group(1)))) if m else None
    t = visible_text(h)
    m = re.search(r"([\d.,]+\s*(?:Mrd\.|Mio\.|Tsd\.)?\+)\s*Downloads", t)
    rec["downloads"] = m.group(1).replace("\xa0", " ") if m else None
    m = re.search(r"Aktualisiert am\s*(\d{2}\.\d{2}\.\d{4})", t)
    rec["updated"] = datetime.strptime(m.group(1), "%d.%m.%Y").date().isoformat() if m else None
    rec["ads"] = "Enthält Werbung" in t
    rec["iap"] = "In-App-Käufe" in t
    m = re.search(r"(\d{1,4}(?:\.\d{3})*,\d{2})\s?€\s?[–-]\s?(\d{1,4}(?:\.\d{3})*,\d{2})\s?€", h.replace("\xa0", " "))
    eur = lambda s: float(s.replace(".", "").replace(",", "."))
    rec["iap_min"], rec["iap_max"] = (eur(m.group(1)), eur(m.group(2))) if (m and rec["iap"]) else (None, None)
    rec["similar"] = [p for p in dict.fromkeys(DETAILS.findall(h)) if p != pkg]
    dl = DEVLINK.findall(h)
    rec["dev_page"] = html.unescape(dl[0]) if dl else None
    rec.update(classify(rec))
    return rec

# ---------------------------------------------------------------- state
def load():
    if os.path.exists(STATE): return json.load(open(STATE, encoding="utf-8"))
    return {"apps": {}, "hop_of": {}, "dev_pages_done": [], "hop": 0, "stopped": None, "log": []}

def save(s):
    tmp = STATE + ".tmp"; json.dump(s, open(tmp, "w", encoding="utf-8"), ensure_ascii=False); os.replace(tmp, STATE)

def seed():
    s = load()
    for c in SEED_CATEGORIES:
        st, h = get(f"https://play.google.com/store/apps/category/{c}?hl=de&gl=DE")
        ids = list(dict.fromkeys(DETAILS.findall(h)))
        for p in ids: s["hop_of"].setdefault(p, 0)
        print(f"seed {c}: HTTP {st}, {len(ids)} apps")
    s["log"].append({"at": datetime.now().isoformat(timespec="seconds"), "event": "seeded", "n": len(s["hop_of"])})
    save(s)

def in_cat(r): return r.get("cooking") or r.get("sleep")

def run(pilot=None):
    s = load(); n = 0
    while s["hop"] <= MAX_HOP and not s["stopped"]:
        hop = s["hop"]
        todo = [p for p, h in s["hop_of"].items() if h == hop and p not in s["apps"]]
        print(f"hop {hop}: {len(todo)} app pages to read", flush=True)
        for p in todo:
            st, h = get(f"https://play.google.com/store/apps/details?id={p}&hl=de&gl=DE")
            s["apps"][p] = parse_app(p, h) if st == 200 and h else {"pkg": p, "http": st, "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            n += 1
            if n % 20 == 0:
                save(s); print(f"  read {n} pages", flush=True)
            if pilot and n >= pilot:
                save(s); print(f"pilot limit {pilot} reached"); return
        # expand from in-category apps of this hop: similar apps and developer pages
        hop_apps = [s["apps"][p] for p, h in s["hop_of"].items() if h == hop and p in s["apps"]]
        cat = [r for r in hop_apps if in_cat(r)]
        before = sum(1 for r in s["apps"].values() if in_cat(r))
        for r in cat:
            for q in r.get("similar", []):
                s["hop_of"].setdefault(q, hop + 1)
            dp = r.get("dev_page")
            if dp and dp not in s["dev_pages_done"]:
                st, h = get("https://play.google.com" + dp + "&hl=de&gl=DE")
                for q in dict.fromkeys(DETAILS.findall(h)):
                    s["hop_of"].setdefault(q, hop + 1)
                s["dev_pages_done"].append(dp); n += 1
        new_in_cat = len(cat) if hop == 0 else sum(1 for r in cat)
        prev_total = before - len(cat) if hop else 0
        growth = (new_in_cat / prev_total) if prev_total else 1.0
        s["log"].append({"at": datetime.now().isoformat(timespec="seconds"), "hop": hop, "read": len(hop_apps),
                         "in_category_new": new_in_cat, "growth": round(growth, 4)})
        print(f"hop {hop} done: {len(hop_apps)} read, {new_in_cat} new in category, growth {growth:.1%}", flush=True)
        if hop >= 1 and growth < MIN_GROWTH:
            s["stopped"] = f"growth {growth:.1%} < {MIN_GROWTH:.0%} after hop {hop}"
        s["hop"] = hop + 1
        save(s)
    if not s["stopped"]: s["stopped"] = f"hop limit {MAX_HOP}"
    save(s); print("stopped:", s["stopped"])

def report():
    s = load(); A = list(s["apps"].values())
    ok = [r for r in A if r.get("name")]
    print(f"pages read: {len(A)} (parsed {len(ok)}) · queue known: {len(s['hop_of'])} · stopped: {s['stopped']}")
    for k in ("cooking", "sleep"):
        c = [r for r in ok if r.get(k)]
        free = [r for r in c if r.get("price") == 0]
        iap = [r for r in free if r.get("iap")]
        print(f"{k:8} in category: {len(c):4} · listed free {len(free)} · free with in-app purchases {len(iap)}")
    for e in s["log"][-8:]: print("  ", e)

if __name__ == "__main__":
    os.makedirs(DATA, exist_ok=True)
    a = sys.argv[1:]
    if a[:1] == ["--seed"]: seed()
    elif a[:1] == ["--run"]: run(int(a[2]) if a[1:2] == ["--pilot"] else None)
    elif a[:1] == ["--report"]: report()
    else: sys.exit(__doc__)
