#!/usr/bin/env python3
"""
"The cost of being found" — the invitation frame and its contact addresses.

Every developer in the two measured categories is invited once (protocol §4–5). This
script builds that list in three resumable stages; each writes to study/frame/, which
is NEVER published (it holds personal data and is deleted when the survey closes,
31 January 2027 — privacy notice §3.1).

    python3 study/contacts.py --frame     # apps -> developers, group per developer (iTunes Lookup)
    python3 study/contacts.py --links     # each developer's Website / Support / Privacy links (App Store page)
    python3 study/contacts.py --emails    # an address the developer publishes there, with its source page
    python3 study/contacts.py --report    # coverage figures, no addresses printed

Rules (privacy notice §3.1):
- Only addresses the developer publishes as a contact on their own website, support or
  privacy page. The page is recorded, because the invitation names it.
- One address per developer, and one email per address across both categories.
- Nothing else about the person is collected. No guessing of addresses (no info@ by pattern).
"""
import hashlib, json, os, re, sys, time, html, urllib.request, urllib.parse, urllib.robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "study", "frame")
FRAME, LINKS, EMAILS = (os.path.join(OUT, f) for f in ("frame.json", "links.json", "emails.json"))

UA_BROWSER = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
              "(KHTML, like Gecko) Version/18.0 Safari/605.1.15")
UA_STUDY = "openAPPindex-study/1.0 (+https://openappindex.org/study/; tim@study.openappindex.org)"

COOKING_SNAPSHOT_DIR = os.path.join(ROOT, "sample", "data", "public", "snapshots")
SLEEP_CATEGORY = os.path.join(ROOT, "sleep", "data", "public", "category_sleep_de.json")
OWN_APPS = {6764606059}          # galleybook, the maintainer's own app: excluded (protocol §4)
CUTOFF = "2023-10-01"            # target group: released on/after this date ...
SMALL_RATINGS = 1000             # ... with fewer ratings than this ...
SMALL_DEV_APPS = 3               # ... by a developer with at most this many apps in the category

def get(url, ua=UA_BROWSER, timeout=20, limit=3_000_000):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Language": "de-DE,de;q=0.9,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        ctype = r.headers.get("Content-Type", "")
        body = r.read(limit)
        return r.geturl(), ctype, body.decode(r.headers.get_content_charset() or "utf-8", "replace")

def load(p, default):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default

def save(p, obj):
    tmp = p + ".tmp"
    json.dump(obj, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, p)

# ---------------------------------------------------------------- stage 1: frame
def category_ids():
    snap = sorted(f for f in os.listdir(COOKING_SNAPSHOT_DIR) if f.endswith(".json"))[-1]
    cook = json.load(open(os.path.join(COOKING_SNAPSHOT_DIR, snap), encoding="utf-8"))["apps"]
    sleep = json.load(open(SLEEP_CATEGORY, encoding="utf-8"))["apps"]
    return ({"cooking": [int(i) for i in cook], "sleep": [a["trackId"] for a in sleep]},
            {"cooking": snap, "sleep": os.path.basename(SLEEP_CATEGORY)},
            {a["trackId"]: a for a in sleep})

def lookup(ids):
    out = {}
    for i in range(0, len(ids), 150):
        chunk = ids[i:i + 150]
        url = "https://itunes.apple.com/lookup?country=de&id=" + ",".join(map(str, chunk))
        for attempt in range(4):
            try:
                for r in json.loads(get(url)[2])["results"]:
                    if r.get("trackId"):
                        out[r["trackId"]] = r
                break
            except Exception as e:
                time.sleep(5 * (attempt + 1))
        time.sleep(1.5)
    return out

def stage_frame():
    ids, sources, sleep_stored = category_ids()
    allids = sorted({i for v in ids.values() for i in v} - OWN_APPS)
    live = lookup(allids)
    # Removed apps stay in the frame (protocol §11); their developer is known from the stored record.
    stored = {}
    for p in (os.path.join(ROOT, "sample", "data", "public", "closure_apps.json"),
              os.path.join(ROOT, "sample", "data", "public", "corpus_de.json")):
        d = json.load(open(p, encoding="utf-8"))
        for a in (d["apps"] if isinstance(d, dict) else d):
            stored.setdefault(a["trackId"], a)
    stored.update(sleep_stored)
    apps = []
    for cat, lst in ids.items():
        for tid in lst:
            if tid in OWN_APPS:
                continue
            a = live.get(tid) or stored.get(tid)
            if not a:
                continue
            apps.append({"cat": cat, "trackId": tid, "live": tid in live, "name": a.get("trackName"),
                         "artistId": a.get("artistId"), "dev": a.get("sellerName") or a.get("artistName"),
                         "rel": (a.get("releaseDate") or "")[:10], "ratings": a.get("userRatingCount") or 0,
                         "sellerUrl": a.get("sellerUrl")})
    n_dev_apps = {}
    for a in apps:
        n_dev_apps[(a["cat"], a["artistId"])] = n_dev_apps.get((a["cat"], a["artistId"]), 0) + 1
    def size_group(a):
        if a["rel"] >= CUTOFF and a["ratings"] < SMALL_RATINGS and n_dev_apps[(a["cat"], a["artistId"])] <= SMALL_DEV_APPS:
            return "new-small"
        if a["rel"] < CUTOFF and a["ratings"] >= SMALL_RATINGS:
            return "established"
        return "in-between"
    for a in apps:
        a["size"] = size_group(a)
    # One record per developer and category. The app named in the invitation (and whose size group
    # the link carries) is the developer's most recently released live app in that category.
    devs = {}
    for a in apps:
        devs.setdefault(f'{a["cat"]}:{a["artistId"]}', []).append(a)
    frame = []
    for key, lst in devs.items():
        lst.sort(key=lambda a: (a["live"], a["rel"]), reverse=True)
        named = lst[0]
        frame.append({"key": key, "cat": named["cat"], "artistId": named["artistId"], "dev": named["dev"],
                      "app": named["name"], "trackId": named["trackId"], "live": named["live"],
                      "group": f'{named["cat"]}/{named["size"]}', "n_apps": len(lst),
                      "other_ids": [a["trackId"] for a in lst[1:] if a["live"]][:3],
                      "sellerUrl": named["sellerUrl"]})
    save(FRAME, {"built": date.today().isoformat(), "sources": sources,
                 "rule": f"new-small = released >= {CUTOFF}, < {SMALL_RATINGS} ratings, developer <= {SMALL_DEV_APPS} apps in category; "
                         f"established = released < {CUTOFF} and >= {SMALL_RATINGS} ratings; else in-between",
                 "n_apps": {c: sum(1 for a in apps if a["cat"] == c) for c in ids},
                 "n_live": {c: sum(1 for a in apps if a["cat"] == c and a["live"]) for c in ids},
                 "developers": frame})
    print(f"frame: {len(apps)} apps, {len(frame)} developer×category records -> {FRAME}")

# ---------------------------------------------------------------- stage 2: links
PACE = 300                       # seconds between App Store pages (at 90 s Apple blocked after 1-7 pages, 2026-10-15)
EXT = re.compile(r'"\$kind":"ExternalUrlAction"[^{}]*?"url":"([^"]+)"')

LABEL = re.compile(r'"(?:text|title|name)":"([^"]{1,80})"')

def app_links(tid):
    """The app's own external links, labelled by the text the App Store shows next to each
    (Website / Entwicklerwebsite, Support, Datenschutz…)."""
    _, _, h = get(f"https://apps.apple.com/de/app/id{tid}")
    labelled = {}
    for m in EXT.finditer(h):
        u = m.group(1)
        if "\\u" in u:
            u = u.encode().decode("unicode_escape")
        if "apple.com" in urllib.parse.urlparse(u).netloc:
            continue
        labels = LABEL.findall(h[max(0, m.start() - 1500):m.start()])
        last = labels[-1].lower() if labels else ""
        kind = ("privacy" if "datenschutz" in last or "privacy" in last else
                "support" if last == "support" else
                "website" if "website" in last or "webseite" in last else "other")
        labelled.setdefault(kind, u)
    return labelled

def stage_links():
    frame = load(FRAME, None)["developers"]
    done = load(LINKS, {})
    found = load(EMAILS, {})
    # Apple throttles store pages after ~30 quick requests, so pages are fetched only for
    # developers whose Lookup website gave no address, at one page every ~20 s.
    todo = [d for d in frame if d["key"] not in done and not found.get(d["key"], {}).get("email")]
    print(f"links: {len(done)} done, {len(todo)} to fetch")
    def work(d):
        transient = False
        for tid in [d["trackId"]] + d["other_ids"]:
            for attempt in range(8):
                try:
                    time.sleep(PACE)
                    return d["key"], {"from": tid, **app_links(tid)}
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        break
                    transient = True
                    print(f"  {time.strftime('%H:%M')} HTTP {e.code} on {tid}, pausing", flush=True)
                    time.sleep(7200 if e.code == 429 else 10)   # retrying sooner seems to extend the block
                except Exception as e:
                    transient = True
                    print(f"  {time.strftime('%H:%M')} {type(e).__name__} on {tid}: {str(e)[:80]}", flush=True)
                    time.sleep(5)
        # Only a page Apple says is gone (404) closes the record; anything else is retried next run.
        return d["key"], None if transient else {"from": None}
    with ThreadPoolExecutor(1) as ex:
        futs = [ex.submit(work, d) for d in todo]
        for n, f in enumerate(as_completed(futs), 1):
            k, v = f.result()
            if v is None:
                continue
            done[k] = v
            save(LINKS, done)                   # every page: at this pace a page is hours of waiting
            if n % 25 == 0:
                print(f"  {n}/{len(todo)}", flush=True)
    save(LINKS, done)
    print(f"links: {len(done)} records -> {LINKS}")

# ---------------------------------------------------------------- stage 3: addresses
EMAIL = re.compile(r"(?<![\w.+-])([A-Za-z0-9][A-Za-z0-9._%+-]{0,63}@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,24})(?![\w-])")
OBFUSCATED = re.compile(r"([A-Za-z0-9._%+-]{1,64})\s*[\[\(\{]\s*(?:at|AT|@)\s*[\]\)\}]\s*([A-Za-z0-9-]+(?:\s*[\[\(\{]\s*(?:dot|DOT|\.)\s*[\]\)\}]\s*[A-Za-z0-9-]+|\.[A-Za-z0-9-]+)+)")
CFEMAIL = re.compile(r'data-cfemail="([0-9a-fA-F]+)"')
# Addresses that belong to a platform or a template, never to the developer.
BAD_DOMAINS = ("example.", "sentry.", "wixpress.com", "domain.com", "email.com", "yourdomain", "yoursite",
               "termsfeed.com", "privacypolicies.com", "freeprivacypolicy.com", "iubenda.com", "flycricket",
               "app-privacy-policy-generator", "privacypolicygenerator", "termly.io", "godaddy.com",
               "squarespace.com", "wordpress.com", "w3.org", "schema.org", "apple.com", "google.com",
               "cloudflare.com", "notion.so", "github.com", "jsdelivr", "mailchimp", "sentry.io", "gravatar",
               "zendesk.com", "freshdesk.com", "intercom.io", "hubspot", "datenschutz-generator.de",
               "e-recht24.de", "activemind.de", "lfd.niedersachsen", "datenschutz-berlin.de", "bfdi.bund.de",
               "ldi.nrw.de", "edpb.europa.eu", "ico.org.uk", "cnil.fr", "aepd.es", "gpdp.it",
               "openappindex.org", "beispiel.", "musterfirma", "mustermann", "fb.com", "facebook.com",
               "above.com", "sedo.com", "dan.com", "incsub.com", "wpengine", "hostinger", "ionos.", "strato.",
               "jimdo.com", "webflow.com", "framer.com", "carrd.co", "shopify.com", "stripe.com", "paypal.com",
               # platforms whose own help or profile pages some developers give as their support page
               # (review of 2026-10-20): their addresses belong to the platform, not the developer
               "passion.io", "webador.", "vk-portal.net", "linktr.ee",
               # vendors, templates, authorities and typos found in the same review
               "automattic.com", "defiant.com", "de-mail.de", "latofonts.com", "klicktipp.com",
               "rss-parrot.net", "telegram.org", "company.com", "doe.com", "gamil.com", "icoud.com",
               # processors named in privacy policies, and data protection authorities
               "consentmanager.net", "brevo.com", "sendinblue.com", "vimeo.com", "paddle.com", "usercentrics.",
               "cookiebot.com", "onetrust.com", "mailerlite.com", "revenuecat.com", "datenschutz.hessen.de",
               "datenschutz.rlp.de", "datenschutz.ekd.de", "baden-wuerttemberg.datenschutz.de", "lda.bayern.de",
               "datenschutzzentrum.de", "datenschutz.sachsen.de", "datenschutz-hamburg.de",
               "adjust.com", "wordpress.org", "amazon.", "t-systems.com", "appsflyer.com", "branch.io",
               "mixpanel.com", "amplitude.com", "segment.com", "onesignal.com", "facebookmail.com",
               # one-off decisions of the 2026-10-20 review, kept so a later search cannot re-find them
               "cdsfulfillment.com", "aquashield-ips.eu", "response-nordic.", "userwerk.com", "ws-datenschutz.de",
               "penguinrandomhouse.de", "psychol.uni-giessen.de", "cybersoft.com", "philipsprojection.com",
               "ohqqunobb.qr")
# Personal addresses of third parties, as SHA-256 so the public code does not repeat them:
# the Lato font designer, quoted in font licence notices.
BAD_ADDRESS_HASHES = {"63b022b054c70e4a14ba88cb059af9845144965af37d8dd2a0c4b33f35ab7b24"}
# Platform pages are not the developer's own site; an address seen there may be anyone's.
SKIP_SOURCES = ("youtube.com", "youtu.be", "facebook.com", "instagram.com", "twitter.com", "x.com",
                "tiktok.com", "linkedin.com", "pinterest.", "reddit.com", "apps.apple.com", "play.google.com")
BAD_LOCAL = re.compile(r"^(no-?reply|donotreply|mailer-daemon|postmaster|abuse|webmaster|user|name|email|"
                       r"your|you|test|someone|john|jane|max\.?mustermann|mustermann|deine|ihre|dein\.?name|"
                       r"ihr\.?name|your\.?name|yourname|vorname\.?nachname|firstname\.?lastname|name\.?surname|"
                       r"beispiel|example|mail|e-?mail|ihre\.?email|deine\.?email|your\.?email|navn|notifications?)$", re.I)
FREEMAIL = {"gmail.com", "googlemail.com", "icloud.com", "me.com", "mac.com", "outlook.com", "hotmail.com",
            "live.com", "yahoo.com", "gmx.de", "gmx.net", "gmx.at", "web.de", "t-online.de", "proton.me",
            "protonmail.com", "pm.me", "mail.ru", "yandex.ru", "qq.com", "163.com", "naver.com", "aol.com",
            "posteo.de", "mailbox.org", "freenet.de", "email.de", "hey.com", "zoho.com", "fastmail.com"}
GOOD_LOCAL = re.compile(r"^(support|help|hello|hallo|hi|contact|kontakt|info|team|app|apps|feedback|office|mail|studio|dev|developer)", re.I)
PRIV_LOCAL = re.compile(r"(privacy|datenschutz|dpo|gdpr|dsgvo|legal)", re.I)
FOLLOW = re.compile(r"(contact|kontakt|impressum|imprint|legal|about|support|privacy|datenschutz)", re.I)
HREF = re.compile(r'href="([^"#]+)"', re.I)

_robots = {}
def allowed(url):
    p = urllib.parse.urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            _, _, txt = get(base + "/robots.txt", ua=UA_STUDY, timeout=8, limit=200_000)
            rp.parse(txt.splitlines())
        except Exception:
            rp = None                      # no readable robots.txt: allowed
        _robots[base] = rp
    rp = _robots[base]
    return rp is None or rp.can_fetch(UA_STUDY, url)

def cf_decode(hexs):
    k = int(hexs[:2], 16)
    return "".join(chr(int(hexs[i:i + 2], 16) ^ k) for i in range(2, len(hexs), 2))

def emails_in(h):
    h2 = html.unescape(urllib.parse.unquote(h))
    found = [m.group(1) for m in EMAIL.finditer(h2)]
    found += [cf_decode(x) for x in CFEMAIL.findall(h)]
    for m in OBFUSCATED.finditer(h2):
        dom = re.sub(r"\s*[\[\(\{]\s*(?:dot|DOT|\.)\s*[\]\)\}]\s*", ".", m.group(2))
        found.append(f"{m.group(1)}@{dom}")
    out = []
    for e in found:
        e = e.strip(".").lower()
        local, _, dom = e.partition("@")
        if any(b in dom for b in BAD_DOMAINS) or BAD_LOCAL.match(local) or hashlib.sha256(e.encode()).hexdigest() in BAD_ADDRESS_HASHES:
            continue
        if re.search(r"\.(png|jpe?g|gif|svg|webp|css|js)$", dom) or re.match(r"^\d+x$", dom.split(".")[0]):
            continue
        if e not in out:
            out.append(e)
    return out

def regdomain(host):
    parts = host.lower().split(".")
    return ".".join(parts[-3:]) if len(parts) > 2 and parts[-2] in ("co", "com", "org", "net") and len(parts[-1]) == 2 else ".".join(parts[-2:])

def score(e, kind, dev_domains):
    local, _, dom = e.partition("@")
    s = {"support": 30, "website": 20, "contact": 25, "privacy": 15}.get(kind, 10)
    if regdomain(dom) in dev_domains:
        s += 20
    if GOOD_LOCAL.match(local):
        s += 10
    if PRIV_LOCAL.search(local):
        s -= 5
    return s

def find_address(rec):
    pages = [(k, rec[k]) for k in ("support", "privacy", "website") if rec.get(k)]
    dev_domains = {regdomain(urllib.parse.urlparse(u).netloc) for _, u in pages}
    cands, fetched, tried = [], set(), []
    def visit(kind, url):
        if url in fetched or len(fetched) >= 7 or not url.startswith("http"):
            return None
        if any(h in urllib.parse.urlparse(url).netloc.lower() for h in SKIP_SOURCES):
            return None
        fetched.add(url)
        try:
            if not allowed(url):
                tried.append([url, "robots"])
                return None
            final, ctype, h = get(url, ua=UA_STUDY, timeout=15)
        except Exception as e:
            tried.append([url, type(e).__name__])
            return None
        if "html" not in ctype and "text" not in ctype:
            return None
        for e in emails_in(h):
            cands.append((score(e, kind, dev_domains), e, final, kind))
        return final, h
    homes = []
    for kind, url in pages:
        r = visit(kind, url)
        if r and kind in ("website", "support"):
            homes.append(r)
    if not cands:                           # one hop on the developer's own site: contact / imprint pages
        for final, h in homes:
            host = urllib.parse.urlparse(final).netloc
            for href in HREF.findall(h):
                u = urllib.parse.urljoin(final, html.unescape(href))
                if urllib.parse.urlparse(u).netloc == host and FOLLOW.search(urllib.parse.urlparse(u).path):
                    visit("contact", u)
    cands.sort(key=lambda c: -c[0])
    best = {}
    for s, e, src, kind in cands:
        best.setdefault(e, (s, src, kind))
    ranked = sorted(best.items(), key=lambda x: -x[1][0])
    if not ranked:
        return {"email": None, "tried": tried[:5]}
    e, (s, src, kind) = ranked[0]
    return {"email": e, "source": src, "page": kind, "score": s,
            "alternates": [[x, v[1]] for x, v in ranked[1:3]]}

def stage_emails():
    frame = load(FRAME, None)["developers"]
    links = load(LINKS, {})
    done = load(EMAILS, {})
    todo = []
    for d in frame:
        rec = dict(links.get(d["key"], {}))
        rec.pop("from", None)
        if d.get("sellerUrl"):
            rec.setdefault("website", d["sellerUrl"])
        sig = sorted(rec.values())
        prev = done.get(d["key"])
        if sig and not (prev and (prev.get("email") or prev.get("searched") == sig)):
            todo.append((d["key"], rec, sig))
    print(f"emails: {len(done)} done, {len(todo)} to search")
    with ThreadPoolExecutor(12) as ex:
        futs = {ex.submit(find_address, rec): (k, sig) for k, rec, sig in todo}
        for n, f in enumerate(as_completed(futs), 1):
            k, sig = futs[f]
            try:
                done[k] = {**f.result(), "searched": sig}
            except Exception as e:
                done[k] = {"email": None, "error": type(e).__name__, "searched": sig}
            if n % 100 == 0:
                save(EMAILS, done)
                print(f"  {n}/{len(todo)}", flush=True)
    save(EMAILS, done)

# ---------------------------------------------------------------- report
def stage_report():
    fr = load(FRAME, {"developers": []})
    links, emails = load(LINKS, {}), load(EMAILS, {})
    devs = fr["developers"]
    print("frame built", fr.get("built"), "| apps", fr.get("n_apps"), "| live", fr.get("n_live"))
    print("developer×category records:", len(devs))
    by = {}
    for d in devs:
        g = by.setdefault(d["group"], [0, 0, 0])
        g[0] += 1
        g[1] += bool(links.get(d["key"], {}).get("from"))
        g[2] += bool(emails.get(d["key"], {}).get("email"))
    print(f'{"group":28} {"devs":>6} {"links":>6} {"email":>6}')
    for g, (n, l, e) in sorted(by.items()):
        print(f"{g:28} {n:6} {l:6} {e:6}  ({e / n:.0%})")
    addrs = [v["email"] for v in emails.values() if v.get("email")]
    print("distinct addresses:", len(set(addrs)), "of", len(addrs), "found")
    pages = {}
    for v in emails.values():
        if v.get("email"):
            pages[v["page"]] = pages.get(v["page"], 0) + 1
    print("source page:", pages)
    review = [k for k, v in emails.items() if v.get("email") and needs_review(v)]
    print("needs a look (address not on the developer's own domain, not a personal mailbox):", len(review))

def needs_review(v):
    dom = v["email"].partition("@")[2]
    src = urllib.parse.urlparse(v.get("source", "")).netloc
    return dom not in FREEMAIL and regdomain(dom) != regdomain(src) and v.get("score", 0) < 40

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    {"--frame": stage_frame, "--links": stage_links, "--emails": stage_emails,
     "--report": stage_report}[sys.argv[1]]()
