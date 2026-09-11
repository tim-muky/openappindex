#!/usr/bin/env python3
"""
openAPPindex - serving layer (GAL-515), minimal gate build.

STORE FACTS ONLY (GAL-517 resolution 2026-08-20):
  published: name, developer, category, version, last-updated date, store price
             label, Apple's published in-app purchase list, the developer's own
             release notes.
  NOT published: user reviews, review-derived claims, verdicts, scores, labels.

Every figure carries its source and the date it was read. Lists state their
ordering rule inline, because an unexplained order reads as a judgement.
"""
import json, re, html, datetime, os, shutil, unicodedata

BASE = "https://openappindex.org"

# ---------------------------------------------------------------------------
# IMPRESSUM (§ 5 DDG) - fill these in before the site goes live.
# Responsible party: Tim Meyerdierks privately, pre-incorporation.
# Transfers to the gUG at incorporation (GAL-527) - change these four lines then.
# ---------------------------------------------------------------------------
IMPRESSUM = {
    "name":   "Tim Meyerdierks",
    "street": "Sonnenburger Straße 54",
    "city":   "10437 Berlin",
    "country":"Deutschland",
    "email":  "hallo@openappindex.org",
    "notice": "korrektur@openappindex.org",
    "phone":  None,                          # deliberately omitted; email + notice route suffice
}
IMPRESSUM_READY = "STRASSE" not in IMPRESSUM["street"] and "PLZ" not in IMPRESSUM["city"]
OUT = "site"

# Wipe generated output first. Without this, pages for apps a corrected classifier
# no longer includes stay on disk and keep being served — which is how 211 pharmacy
# and game pages survived a rebuild on 2026-08-24.
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
TODAY = datetime.date.today().isoformat()
NOW = datetime.datetime.now(datetime.timezone.utc)

# The clock says when this ran, never when a fact was read. Rebuilding must not
# re-date a measurement nobody took again: source lines carry the recorded read
# date, and the build date is used only for sitemap lastmod.
BUILD_DATE = TODAY
CORPUS_READ = datetime.date.fromtimestamp(
    os.path.getmtime("data/corpus_de.json")).isoformat()

C = json.load(open("data/corpus_de.json", encoding="utf-8"))

# --- classification v4 -------------------------------------------------------
# Three corrections, all found by our own checks and all documented on the
# methods page:
#   1. German "Rezept" means recipe AND medical prescription -> pharmacy apps
#   2. "Kochen/Backen" also matches cooking GAMES, which are not recipe apps
#   3. (2026-08-31) press products (ePaper/magazines that print recipes), a
#      kids-franchise title in Education, and single-venue apps also pass the
#      keyword test. Rules M and K below; the venue rule is not yet precise
#      enough to apply here (see sample/precision_check.py).
# Keyword classification has known limits; they are stated publicly rather than
# hidden. See methode.html.
RECIPE = re.compile(r"rezept|kochbuch|kochen|backen", re.I)
PHARMA = re.compile(r"apothek|e-?rezept|medikament|arzt|ärzt|verschreib|krankenkasse", re.I)
COOK   = re.compile(r"koch|back|zutat|essen|mahlzeit|gericht|k[üu]che|ern[äa]hrung|"
                    r"lebensmittel|einkaufsliste|men[üu]|speise|food|recipe", re.I)
EXCLUDE_GENRE = {"Games", "Entertainment", "Utilities", "Photo & Video", "Travel",
                 "Finance", "Business",
                 # v4 rule M: press products are not apps about cooking,
                 # however many recipes they print
                 "Magazines & Newspapers", "News", "Book"}

# Children's cooking games are filed under Education, not Games — a third
# classifier correction, found 2026-08-24.
KIDS_GAME = re.compile(r"spiel|kinder|kids|kleinkind|toddler|kiddo", re.I)
# v4 rule K (2026-08-31): franchise titles avoid the word "Spiel" ("Baby Pandas
# Stadt", "Vorschulwissen"). Education only — a Lifestyle app named "Beikost -
# Baby BLW & Brei" is a genuine baby-food recipe app.
KIDS_V4 = re.compile(r"spiel|kinder|kids|kleinkind|toddler|kiddo|baby|panda|vorschul", re.I)

def is_cooking_app(name, desc, genre):
    t = (name or "") + " " + (desc or "")
    if not RECIPE.search(t):            return False
    if genre in EXCLUDE_GENRE:          return False
    if genre in ("Education", "Medical") and KIDS_GAME.search(name or ""):
        return False
    if genre == "Education" and KIDS_V4.search(name or ""):
        return False
    ph, ck = len(PHARMA.findall(t)), len(COOK.findall(t))
    if ph >= 3 and ph > ck:             return False
    return ck >= 2

apps = [a for a in C["apps"]
        if is_cooking_app(a.get("trackName"), a.get("description"), a.get("primaryGenreName"))]

# fold in what the closure crawl discovered
if os.path.exists("data/new_apps_meta.json"):
    _new = json.load(open("data/new_apps_meta.json", encoding="utf-8"))
    apps += [a for a in _new.values()
             if is_cooking_app(a.get("trackName"), a.get("description"), a.get("primaryGenreName"))]

prices = {}
for _f in ("data/prices_de.json", "data/new_apps_prices.json"):
    if os.path.exists(_f):
        for r in json.load(open(_f, encoding="utf-8")):
            prices[r["track_id"]] = r

def esc(s): return html.escape(s or "", quote=True)

def slug(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = s.replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s or "app")[:60]

def days_since(iso):
    if not iso: return None
    return (NOW - datetime.datetime.fromisoformat(iso.replace("Z","+00:00"))).days

def de_date(iso):
    return datetime.datetime.fromisoformat(iso.replace("Z","+00:00")).strftime("%d.%m.%Y") if iso else "unbekannt"

def de_elapsed(d):
    if d is None: return "unbekannt"
    if d == 0: return "heute"
    if d == 1: return "gestern"
    if d < 60: return f"vor {d} Tagen"
    if d < 730: return f"vor {d//30} Monaten"
    return f"vor {d//365} Jahren und {(d%365)//30} Monaten"

def eur(v): return ("%.2f" % v).replace(".", ",") + " €"

def eur_range(lo, hi):
    if lo == hi: return eur(lo)
    return ("%.2f" % lo).replace(".", ",") + "–" + ("%.2f" % hi).replace(".", ",") + " €"

def parse_eur(s):
    m = re.search(r"(\d+(?:[.,]\d+)?)", (s or "").replace("\xa0"," "))
    return float(m.group(1).replace(",", ".")) if m else None

for a in apps:
    a["slug"] = f"{slug(a['trackName'])}-{a['trackId']}"
    a["days"] = days_since(a.get("currentVersionReleaseDate"))
    p = prices.get(a["trackId"], {})
    a["subtitle"] = p.get("subtitle")
    iaps = p.get("in_app_purchases")
    a["iaps"] = iaps
    vals = sorted(v for v in (parse_eur(i["price"]) for i in (iaps or [])) if v is not None)
    a["iap_min"], a["iap_max"] = (vals[0], vals[-1]) if vals else (None, None)
    a["price_known"] = bool(p.get("read_ok"))
    a["read_at"] = (p.get("read_at") or "")[:10] or None

# "Stand" of the dataset is the most recent recorded read, not today.
DATA_STAND = max([a["read_at"] for a in apps if a["read_at"]] or [CORPUS_READ])

SHELL = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<style>
:root{{--bg:#fbfcfd;--ink:#10161d;--mut:#5a6673;--rule:#cfd6dd;--acc:#26389c;--card:#fff}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0e1216;--ink:#e8edf2;--mut:#96a3af;--rule:#2a343d;--acc:#93a5ff;--card:#161c22}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}}
.w{{max-width:820px;margin:0 auto;padding:28px 20px 80px}}
a{{color:var(--acc)}}
h1{{font-size:1.9rem;line-height:1.2;margin:.2em 0}}
h2{{font-size:1.25rem;margin:2em 0 .5em}}
h3{{font-size:1.05rem;margin:1.6em 0 .4em}}
.lede{{font-size:1.05rem;color:var(--mut)}}
nav.bc{{font-size:.85rem;color:var(--mut);margin-bottom:1.5em}}
table{{border-collapse:collapse;width:100%;margin:1em 0;font-size:.94rem}}
th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--rule);vertical-align:top}}
th{{font-weight:600;width:38%;color:var(--mut)}}
.src{{font-size:.78rem;color:var(--mut)}}
.card{{background:var(--card);border:1px solid var(--rule);padding:16px;margin:10px 0}}
.card h3{{margin:0 0 .3em;font-size:1.05rem}}
.meta{{font-size:.88rem;color:var(--mut)}}
.rule{{background:var(--card);border-left:3px solid var(--acc);padding:12px 14px;margin:1.5em 0;font-size:.9rem}}
footer{{margin-top:3em;padding-top:1.2em;border-top:1px solid var(--rule);font-size:.82rem;color:var(--mut)}}
ol{{padding-left:0;list-style:none}}
blockquote{{margin:.6em 0;padding-left:12px;border-left:2px solid var(--rule);color:var(--mut);font-size:.92rem}}
</style>
{ld}
</head>
<body><div class="w">
{body}
<footer>
<p><strong>openAPPindex</strong> — ein unabhängiger, offener Index mobiler Apps. Wir nehmen von keiner App Geld an.
Alle Angaben stammen aus öffentlich zugänglichen Daten des App Store und tragen das Datum ihrer Erhebung.</p>
<p>Diese Seite wurde automatisiert aus öffentlichen App-Store-Daten erstellt. Sie enthält keine Bewertung und keine
Nutzerrezensionen — nur datierte Tatsachen und deren Quelle.</p>
<p>Fehler gefunden? Korrekturen an <a href="mailto:korrektur@openappindex.org">korrektur@openappindex.org</a> —
wir korrigieren datiert und nachvollziehbar. · <a href="{base}/impressum.html">Impressum &amp; Kontakt</a> ·
<a href="{base}/methode.html">Methode</a> &middot;
<a href="{base}/manifest.html">Manifest</a> &middot;
<a href="{base}/paper.html">Working Paper</a></p>
</footer>
</div></body></html>"""

def page(path, title, desc, body, ld=""):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    canon = BASE + "/" + path.replace("index.html", "")
    open(full, "w", encoding="utf-8").write(SHELL.format(
        title=esc(title), desc=esc(desc), canon=esc(canon), body=body, ld=ld, base=BASE))

# ---------------- app pages ----------------
def app_page(a):
    d, name = a["days"], a["trackName"]
    upd = f"{de_date(a.get('currentVersionReleaseDate'))} ({de_elapsed(d)})"
    if a["iaps"]:
        cost = (f"Im App Store als „{esc(a.get('formattedPrice'))}“ gelistet. Die Produktseite weist "
                f"<strong>{len(a['iaps'])} In-App-Käufe</strong> aus, von {eur(a['iap_min'])} bis {eur(a['iap_max'])}.")
    elif a["price_known"]:
        cost = f"Im App Store als „{esc(a.get('formattedPrice'))}“ gelistet. Auf der Produktseite sind keine In-App-Käufe ausgewiesen."
    else:
        cost = (f"Im App Store als „{esc(a.get('formattedPrice'))}“ gelistet. "
                f"<em>In-App-Käufe: nicht erhoben</em> — diese Angabe fehlt, sie wird nicht geschätzt.")

    iap_rows = ""
    if a["iaps"]:
        iap_rows = "<h2>Ausgewiesene In-App-Käufe</h2><table><tbody>" + "".join(
            f"<tr><th>{esc(i['name'])}</th><td>{esc(i['price'])}</td></tr>" for i in a["iaps"]
        ) + f"</tbody></table><p class='src'>Quelle: Produktseite im App Store, erhoben am {a['read_at'] or CORPUS_READ}.</p>"

    notes = ""
    n = re.sub(r"\s+", " ", (a.get("releaseNotes") or "")).strip()
    if n:
        notes = (f"<h2>Was der Anbieter zur letzten Version schreibt</h2>"
                 f"<blockquote>{esc(n[:400])}{'…' if len(n)>400 else ''}</blockquote>"
                 f"<p class='src'>Eigene Versionshinweise des Anbieters zu Version {esc(a.get('version'))}, "
                 f"veröffentlicht am {de_date(a.get('currentVersionReleaseDate'))}.</p>")

    # The download price is read from the store's own price string. Apple's Search API
    # returns no numeric price field for this corpus, so any number here has to come from
    # formattedPrice. It must never be defaulted: `or 0` published "free" for 22 paid apps
    # until 2026-09-11. Where the store price was not captured at all, no number is emitted.
    fp = (a.get("formattedPrice") or "").strip()
    dl = 0.0 if fp.lower() in ("gratis", "free") else parse_eur(fp)
    dl_txt = fp or "nicht erhoben"
    if a["iaps"] and a["iap_min"] is not None:
        # Download and each in-app purchase are separate offers; the range is measured,
        # never annualised and never inferred. An unknown download price narrows the
        # range to the measured in-app purchases rather than assuming a free download.
        lo = a["iap_min"] if dl is None else min(dl, a["iap_min"])
        offers = {"@type":"AggregateOffer","priceCurrency":"EUR",
                  "lowPrice":"%.2f" % lo,
                  "highPrice":"%.2f" % (a["iap_max"] if dl is None else max(dl, a["iap_max"])),
                  "offerCount":len(a["iaps"]) + (0 if dl is None else 1),
                  "description":(f"Download {dl_txt}; {len(a['iaps'])} auf der "
                                 f"Produktseite ausgewiesene In-App-Käufe von {eur(a['iap_min'])} "
                                 f"bis {eur(a['iap_max'])}, erhoben am {a['read_at']}.")}
    elif a["price_known"]:
        offers = {"@type":"Offer","priceCurrency":"EUR",
                  "description":(f"Download {dl_txt}; auf der Produktseite sind "
                                 f"keine In-App-Käufe ausgewiesen (erhoben am {a['read_at']}).")}
        if dl is not None: offers["price"] = "%.2f" % dl
    else:
        offers = {"@type":"Offer","priceCurrency":"EUR",
                  "description":(f"Download {dl_txt}; In-App-Käufe nicht erhoben — "
                                 f"dieser Wert wird nicht geschätzt.")}
        if dl is not None: offers["price"] = "%.2f" % dl

    ld = json.dumps({"@context":"https://schema.org","@type":"MobileApplication",
        "name":name,"applicationCategory":a.get("primaryGenreName"),"operatingSystem":"iOS",
        "softwareVersion":a.get("version"),"dateModified":(a.get("currentVersionReleaseDate") or "")[:10],
        "author":{"@type":"Organization","name":a.get("sellerName")},
        "offers":offers,
        "url":f"{BASE}/de/app/{a['slug']}/","sameAs":a.get("trackViewUrl")}, ensure_ascii=False)

    body = f"""<nav class="bc"><a href="{BASE}/">openAPPindex</a> › <a href="{BASE}/de/">Deutschland</a> › Apps</nav>
<h1>{esc(name)}</h1>
<p class="lede">{esc(a.get('subtitle') or a.get('sellerName'))}</p>
<h2>Wird diese App noch gepflegt?</h2>
<p>Die zuletzt veröffentlichte Version ist <strong>{esc(a.get('version'))}</strong>, erschienen am
<strong>{upd}</strong>. Das ist das von Apple veröffentlichte Datum der letzten Aktualisierung — eine Bewertung
sprechen wir nicht aus.</p>
<h2>Was kostet die App wirklich?</h2>
<p>{cost}</p>
<table><tbody>
<tr><th>Anbieter</th><td>{esc(a.get('sellerName'))}</td></tr>
<tr><th>Kategorie</th><td>{esc(a.get('primaryGenreName'))}</td></tr>
<tr><th>Version</th><td>{esc(a.get('version'))}</td></tr>
<tr><th>Zuletzt aktualisiert</th><td>{upd}</td></tr>
<tr><th>Erstveröffentlichung</th><td>{de_date(a.get('releaseDate'))}</td></tr>
<tr><th>Preisangabe im Store</th><td>{esc(a.get('formattedPrice'))}</td></tr>
<tr><th>Im App Store ansehen</th><td><a href="{esc(a.get('trackViewUrl'))}" rel="nofollow">Produktseite</a></td></tr>
</tbody></table>
<p class="src">Quelle: iTunes Search API (erhoben am {CORPUS_READ}) und Produktseite im App Store
(Storefront Deutschland, erhoben am {a['read_at'] or 'nicht erhoben'}).</p>
{iap_rows}{notes}
<div class="rule">Diese Seite enthält bewusst <strong>keine Nutzerrezensionen und keine Bewertung</strong>.
Sie zeigt datierte Tatsachen aus öffentlichen Store-Daten. Den Schluss ziehen Sie.</div>"""
    upd_de = de_date(a.get("currentVersionReleaseDate"))
    if a["iaps"] and a["iap_min"] is not None:
        ttl = f"{name}: In-App-Käufe {eur_range(a['iap_min'], a['iap_max'])} | openAPPindex"
        dsc = (f"Im Store als „{a.get('formattedPrice')}“ gelistet, tatsächlich {len(a['iaps'])} "
               f"In-App-Käufe von {eur_range(a['iap_min'], a['iap_max'])}. Zuletzt aktualisiert am "
               f"{upd_de}. Datierte Store-Fakten, keine Bewertung.")
    elif a["price_known"]:
        ttl = f"{name}: keine In-App-Käufe ausgewiesen | openAPPindex"
        dsc = (f"Im Store als „{a.get('formattedPrice')}“ gelistet; auf der Produktseite sind keine "
               f"In-App-Käufe ausgewiesen. Zuletzt aktualisiert am {upd_de}. Datierte Store-Fakten, "
               f"keine Bewertung.")
    else:
        ttl = f"{name} — zuletzt aktualisiert {upd_de} | openAPPindex"
        dsc = (f"{name}: zuletzt aktualisiert am {upd_de}, Version {a.get('version')}. In-App-Käufe "
               f"nicht erhoben — nicht geschätzt. Datierte Store-Fakten, keine Bewertung.")
    page(f"de/app/{a['slug']}/index.html", ttl, dsc,
         body, f'<script type="application/ld+json">{ld}</script>')

for a in apps: app_page(a)

# ---------------- question pages ----------------
def card(a, extra=""):
    return (f"<li class='card'><h3><a href='{BASE}/de/app/{a['slug']}/'>{esc(a['trackName'])}</a></h3>"
            f"<p class='meta'>{esc(a.get('sellerName'))} · zuletzt aktualisiert "
            f"{de_date(a.get('currentVersionReleaseDate'))} ({de_elapsed(a['days'])}){extra}</p></li>")

def qpage(fn, title, h1, question, rule, items, desc):
    ld = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{
        "@type":"Question","name":question,"acceptedAnswer":{"@type":"Answer","text":rule}}]}, ensure_ascii=False)
    body = (f"<nav class='bc'><a href='{BASE}/'>openAPPindex</a> › <a href='{BASE}/de/'>Deutschland</a> › Fragen</nav>"
            f"<h1>{esc(h1)}</h1><p class='lede'>{esc(desc)}</p>"
            f"<div class='rule'><strong>Sortierregel:</strong> {rule}</div>"
            f"<ol>{''.join(items)}</ol>"
            f"<p class='src'>Grundlage: {len(apps)} Apps im deutschen App Store, deren eigene Beschreibung sie als "
            f"Rezept- oder Koch-App ausweist. Erhoben am {DATA_STAND}.</p>")
    page(f"de/frage/{fn}.html", title, desc, body, f'<script type="application/ld+json">{ld}</script>')

maintained = sorted([a for a in apps if a["days"] is not None], key=lambda x: x["days"])[:60]
qpage("welche-rezept-app-wird-noch-gepflegt",
      "Welche Rezept-App wird noch gepflegt? | openAPPindex",
      "Welche Rezept-App wird noch gepflegt?",
      "Welche Rezept-App wird noch gepflegt?",
      "Sortiert nach dem von Apple veröffentlichten Datum der letzten Aktualisierung, neueste zuerst. "
      "Downloadzahlen und Bewertungen fließen nicht ein.",
      [card(a) for a in maintained],
      "Rezept-Apps im deutschen App Store, sortiert nach dem Datum ihrer letzten Aktualisierung.")

stale = sorted([a for a in apps if a["days"] and a["days"] > 365], key=lambda x: -x["days"])[:60]
qpage("rezept-apps-lange-nicht-aktualisiert",
      "Welche Rezept-Apps wurden lange nicht aktualisiert? | openAPPindex",
      "Rezept-Apps, die seit über einem Jahr nicht aktualisiert wurden",
      "Welche Rezept-Apps wurden lange nicht aktualisiert?",
      "Alle Apps, deren letzte von Apple veröffentlichte Aktualisierung mehr als 365 Tage zurückliegt, "
      "älteste zuerst. Das ist eine Datumsangabe, keine Aussage über die Qualität der App.",
      [card(a) for a in stale],
      "Rezept-Apps im deutschen App Store, deren letzte Aktualisierung über ein Jahr zurückliegt.")

hidden = sorted([a for a in apps if a["iap_max"] and (a.get("formattedPrice") or "").lower() in ("gratis","free")],
                key=lambda x: -x["iap_max"])[:60]
qpage("gratis-rezept-app-was-kostet-sie-wirklich",
      "„Gratis“ im Store — was kostet die Rezept-App wirklich? | openAPPindex",
      "Als „Gratis“ gelistet — und was tatsächlich im Kaufmenü steht",
      "Was kostet eine als gratis gelistete Rezept-App wirklich?",
      "Apps, die im Store als „Gratis“ erscheinen und auf ihrer Produktseite In-App-Käufe ausweisen, "
      "sortiert nach dem höchsten ausgewiesenen Einzelpreis. Alle Preise sind die von Apple veröffentlichten Angaben.",
      [card(a, f" · In-App-Käufe {eur(a['iap_min'])}–{eur(a['iap_max'])}") for a in hidden],
      "Rezept-Apps, die als gratis gelistet sind, mit den tatsächlich ausgewiesenen In-App-Preisen.")

noiap = sorted([a for a in apps if a["price_known"] and not a["iaps"] and a["days"] is not None],
               key=lambda x: x["days"])[:60]
qpage("rezept-app-ohne-abo-und-ohne-in-app-kaeufe",
      "Rezept-Apps ohne In-App-Käufe | openAPPindex",
      "Rezept-Apps, für die keine In-App-Käufe ausgewiesen sind",
      "Gibt es Rezept-Apps ohne Abo und ohne In-App-Käufe?",
      "Apps, auf deren Produktseite Apple keine In-App-Käufe ausweist, sortiert nach dem Datum der letzten "
      "Aktualisierung. Fehlt die Angabe, steht es hier — geschätzt wird nichts.",
      [card(a) for a in noiap],
      "Rezept-Apps im deutschen App Store ohne ausgewiesene In-App-Käufe.")

QS = [("welche-rezept-app-wird-noch-gepflegt","Welche Rezept-App wird noch gepflegt?"),
      ("rezept-apps-lange-nicht-aktualisiert","Welche wurden lange nicht aktualisiert?"),
      ("gratis-rezept-app-was-kostet-sie-wirklich","„Gratis“ — was kostet sie wirklich?"),
      ("rezept-app-ohne-abo-und-ohne-in-app-kaeufe","Welche kommen ohne In-App-Käufe aus?")]

# ---------------- index pages ----------------
qlinks = "".join(f"<li class='card'><h3><a href='{BASE}/de/frage/{f}.html'>{esc(t)}</a></h3></li>" for f,t in QS)
withiap = sum(1 for a in apps if a["iaps"])
intro = f"""<h1>openAPPindex</h1>
<p class="lede">Ein unabhängiger, offener Index mobiler Apps. Sortiert danach, wie gut eine App gepflegt wird
und was sie tatsächlich kostet — nie danach, wer bezahlt hat.</p>
<p>Der App Store zeigt zwei Signale: einen Sternedurchschnitt und ein Preiswort. Beide beantworten nicht die
zwei Fragen, die zählen: <strong>Wird diese App noch gepflegt, und was kostet sie am Ende wirklich?</strong>
Dieser Index trägt die öffentlich verfügbaren Antworten zusammen, mit Datum und Quelle.</p>
<h2>Fragen, die dieser Index beantwortet</h2><ol>{qlinks}</ol>
<h2>Datenbestand</h2>
<p><strong>{len(apps)} Apps</strong> im deutschen App Store, deren eigene Store-Beschreibung sie als Rezept- oder
Koch-App ausweist. Für <strong>{withiap}</strong> davon sind die auf der Produktseite ausgewiesenen In-App-Käufe
erfasst. Stand: {DATA_STAND}.</p>
<div class="rule">Wir nehmen von keiner App Geld an. Es gibt keine bezahlte Platzierung.
Diese Seiten enthalten keine Nutzerrezensionen und keine Bewertungen — nur datierte Tatsachen mit Quellenangabe.</div>"""
page("de/index.html", "openAPPindex — Deutschland",
     "Rezept-Apps im deutschen App Store: Pflegezustand und tatsächliche Kosten, datiert und mit Quelle.", intro)

page("methode.html", "Methode — openAPPindex", "Wie dieser Index erhoben und sortiert wird.", f"""
<h1>Methode</h1>
<p class="lede">Alles hier ist nachprüfbar. Wenn nicht, gehört es nicht auf die Seite.</p>
<h2>Woher die Daten stammen</h2>
<table><tbody>
<tr><th>Ranking und Metadaten</th><td>Öffentliche iTunes Search API</td></tr>
<tr><th>Untertitel und In-App-Preise</th><td>Produktseite im App Store</td></tr>
</tbody></table>
<h2>Was wir veröffentlichen — und was nicht</h2>
<p>Veröffentlicht werden ausschließlich von Apple publizierte Angaben: Name, Anbieter, Kategorie, Version,
Datum der letzten Aktualisierung, Preisangabe, ausgewiesene In-App-Käufe und die Versionshinweise des Anbieters.</p>
<p><strong>Nicht veröffentlicht</strong> werden Nutzerrezensionen, daraus abgeleitete Aussagen sowie Bewertungen,
Noten oder Etiketten jeder Art. Fehlt eine Angabe, steht das dort — geschätzt wird nichts.</p>
<h2>Wie wir „Rezept-App&ldquo; abgrenzen &mdash; und wo das ungenau ist</h2>
<p>Wir ordnen Apps anhand ihres eigenen Store-Textes und ihrer Store-Kategorie zu. Dieses
Verfahren hat Grenzen, und wir benennen sie, statt sie zu verschweigen. Zwei Fehler haben wir
selbst gefunden und korrigiert:</p>
<p><strong>1. Das Wort „Rezept&ldquo;.</strong> Im Deutschen bedeutet es sowohl Kochrezept als
auch &auml;rztliche Verordnung. Unsere erste Z&auml;hlung enthielt deshalb Apotheken- und
E-Rezept-Apps. Sie sind jetzt ausgeschlossen.</p>
<p><strong>2. Kochspiele.</strong> Begriffe wie „Kochen&ldquo; und „Backen&ldquo; treffen auch
Spiele. Diese sind jetzt &uuml;ber die Store-Kategorie ausgeschlossen.</p>
<p><strong>3. Zeitschriften und Einzelanbieter</strong> <em>(korrigiert am 31.08.2026)</em>.
Auch ePaper-Ausgaben von Kochzeitschriften und die App eines einzelnen Kinderspiel-Anbieters
bestehen den Stichworttest &mdash; sie sind Presseprodukte bzw. Spiele, keine Koch-Apps. Zehn
solche Eintr&auml;ge waren bis zum 31.08.2026 in diesem Index enthalten und sind jetzt
entfernt; die betroffenen Kennzahlen wurden auf der korrigierten Basis neu berechnet
(941 statt 951 Apps; 697 von 907 statt 706 von 916 gratis gelistet mit In-App-K&auml;ufen &mdash;
der Anteil bleibt 77&nbsp;%).</p>
<p>Die zentrale Feststellung &mdash; wie viele Apps in der Store-Suche nicht auftauchen &mdash;
lag &uuml;ber drei verschiedene Abgrenzungen hinweg zwischen 81 und 83 Prozent. Das Ergebnis
h&auml;ngt also nicht an der Abgrenzung. Wo wir dennoch falsch liegen:
<a href="mailto:korrektur@openappindex.org">korrektur@openappindex.org</a>.</p>
<h2>Korrektur an den maschinenlesbaren Daten <em>(11.09.2026)</em></h2>
<p>Jede App-Seite enth&auml;lt neben dem sichtbaren Text auch strukturierte Daten
(JSON-LD), die Suchmaschinen und Sprachmodelle auslesen. Dort stand f&uuml;r den
Download-Preis bis zum 11.09.2026 <strong>bei jeder App <code>0.00&nbsp;&euro;</code></strong>,
weil ein nicht vorhandener Zahlenwert stillschweigend durch Null ersetzt wurde. F&uuml;r
die 919 gratis angebotenen Apps stimmte das zuf&auml;llig &mdash; f&uuml;r
<strong>22 kostenpflichtige Apps war es falsch</strong>: Ihre Seite nannte im Text
korrekt etwa &bdquo;5,99&nbsp;&euro;&ldquo;, w&auml;hrend die maschinenlesbare Ebene
&bdquo;kostenlos&ldquo; meldete. Das ist genau der Fehler, den dieser Index sichtbar
machen soll, und er stand in der einen Schicht, die wir selbst nicht lesen.</p>
<p>Seit dem 11.09.2026 wird der Download-Preis aus der Preisangabe des Stores gelesen.
Ist dort keine Angabe erfasst, wird <strong>gar kein Zahlenwert ver&ouml;ffentlicht</strong>
&mdash; gesch&auml;tzt wird nichts. Alle 941 App-Seiten wurden neu erzeugt und gepr&uuml;ft.</p>
<h2>Wie sortiert wird</h2>
<p>Jede Liste nennt ihre Sortierregel auf der Seite selbst. Downloadzahlen, Bewertungssterne und Werbebudget
fließen in keine Sortierung ein.</p>
<h2>Korrekturen</h2>
<p>Fehler bitte an <a href="mailto:korrektur@openappindex.org">korrektur@openappindex.org</a>. Korrekturen werden
mit Datum ausgewiesen.</p>""")

banner = "" if IMPRESSUM_READY else (
    '<div class="rule"><strong>Diese Seite ist noch nicht vollst\u00e4ndig.</strong> Die Anschrift nach '
    '\u00a7 5 DDG fehlt. Die Website darf in diesem Zustand nicht \u00f6ffentlich zug\u00e4nglich gemacht werden.</div>')
page("impressum.html", "Impressum & Kontakt \u2014 openAPPindex",
     "Impressum nach \u00a7 5 DDG, Kontakt f\u00fcr Hinweise und Korrekturen.", f"""
{banner}
<h1>Impressum</h1>
<h2>Angaben gem\u00e4\u00df \u00a7 5 DDG</h2>
<p>{esc(IMPRESSUM['name'])}<br>
{esc(IMPRESSUM['street'])}<br>
{esc(IMPRESSUM['city'])}<br>
{esc(IMPRESSUM['country'])}</p>
<h2>Kontakt</h2>
<p>E-Mail: <a href="mailto:{IMPRESSUM['email']}">{IMPRESSUM['email']}</a></p>
<p class="src">Eine Telefonnummer wird nicht angegeben. Nach st\u00e4ndiger Rechtsprechung gen\u00fcgt ein zweiter,
gleichwertig schneller elektronischer Kontaktweg \u2014 hier die oben genannte E-Mail-Adresse sowie die
Hinweisstelle f\u00fcr Korrekturen.</p>
<h2>Verantwortlich f\u00fcr den Inhalt</h2>
<p>{esc(IMPRESSUM['name'])}, Anschrift wie oben.</p>
<h2>Hinweise und Korrekturen (Melde- und Abhilfeverfahren)</h2>
<p>Sie halten eine Angabe auf diesen Seiten f\u00fcr unrichtig oder unvollst\u00e4ndig \u2014 etwa als Anbieterin oder
Anbieter einer hier aufgef\u00fchrten App? Schreiben Sie an
<a href="mailto:{IMPRESSUM['notice']}">{IMPRESSUM['notice']}</a>. Wir pr\u00fcfen jeden Hinweis, korrigieren
nachweisbare Fehler und weisen die Korrektur mit Datum aus.</p>
<p>Alle Angaben auf diesen Seiten stammen aus \u00f6ffentlich zug\u00e4nglichen Daten des App Store und tragen das
Datum ihrer Erhebung. Es werden keine Nutzerrezensionen und keine Bewertungen ver\u00f6ffentlicht.</p>
<h2>Hinweis nach EU-KI-Verordnung</h2>
<p>Die Inhalte dieser Seiten werden automatisiert aus \u00f6ffentlich zug\u00e4nglichen App-Store-Daten erzeugt.</p>
<h2>Haftung f\u00fcr Links</h2>
<p>Diese Seiten verlinken auf die jeweiligen Produktseiten im App Store. F\u00fcr deren Inhalte sind
ausschlie\u00dflich die Betreiber der verlinkten Seiten verantwortlich.</p>""")

# ---------------- machine surfaces ----------------
os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/robots.txt","w").write(
"""User-agent: *
Allow: /

User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: CCBot
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: meta-externalagent
Allow: /
User-agent: Amazonbot
Allow: /
User-agent: cohere-ai
Allow: /
User-agent: Bytespider
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: Perplexity-User
Allow: /
User-agent: MistralAI-User
Allow: /

Sitemap: %s/sitemap.xml
""" % BASE)

open(f"{OUT}/llms.txt","w",encoding="utf-8").write(f"""# openAPPindex

> Unabhängiger, offener Index mobiler Apps. Sortiert nach Pflegezustand und tatsächlichen
> Kosten, nie nach Downloadzahlen oder Werbebudget. Keine bezahlte Platzierung.

Datenbestand: {len(apps)} Rezept- und Koch-Apps im deutschen App Store, Stand {DATA_STAND}.
Für {withiap} davon sind die von Apple ausgewiesenen In-App-Käufe erfasst.

Alle Angaben stammen aus öffentlichen App-Store-Daten und tragen das Datum ihrer Erhebung.
Der Index enthält keine Nutzerrezensionen und keine Bewertungen — nur datierte Tatsachen.
Fehlende Angaben werden als fehlend ausgewiesen und nicht geschätzt.

## Fragen
""" + "".join(f"- [{t}]({BASE}/de/frage/{f}.html)\n" for f,t in QS) + f"""
## Methode
- [Methode und Quellen]({BASE}/methode.html)

## Nutzung
Zitierfähig mit Quellenangabe „openAPPindex, Stand {DATA_STAND}“.
""")

with open(f"{OUT}/llms-full.txt","w",encoding="utf-8") as f:
    f.write(f"# openAPPindex — vollständiger Datenbestand (Stand {DATA_STAND})\n\n")
    f.write("Quelle: iTunes Search API + App-Store-Produktseiten, Storefront Deutschland.\n")
    f.write("Keine Rezensionen, keine Bewertungen. Fehlende Angaben sind als solche ausgewiesen.\n\n")
    for a in sorted(apps, key=lambda x: x["days"] if x["days"] is not None else 99999):
        cost = (f"In-App-Käufe {eur(a['iap_min'])}–{eur(a['iap_max'])} ({len(a['iaps'])} Positionen)"
                if a["iaps"] else ("keine In-App-Käufe ausgewiesen" if a["price_known"] else "In-App-Käufe nicht erhoben"))
        f.write(f"## {a['trackName']}\n"
                f"- Anbieter: {a.get('sellerName')}\n"
                f"- Zuletzt aktualisiert: {de_date(a.get('currentVersionReleaseDate'))} ({de_elapsed(a['days'])})\n"
                f"- Version: {a.get('version')}\n"
                f"- Preisangabe im Store: {a.get('formattedPrice')}\n"
                f"- Tatsächliche Kosten: {cost}\n"
                f"- Seite: {BASE}/de/app/{a['slug']}/\n\n")

# Submitted set = pages that carry information available nowhere else.
# App pages without in-app price data stay on the site and stay linked, but are
# not submitted: 900+ near-identical thin pages risk the whole site being
# classified as low-value, which would suppress the good pages too.
urls = ["", "de/", "methode.html", "impressum.html", "manifest.html", "manifesto.html", "paper.html"] + [f"de/frage/{f}.html" for f,_ in QS] \
       + [f"de/app/{a['slug']}/" for a in apps if a["iaps"]]
with open(f"{OUT}/sitemap.xml","w",encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9">\n'
            .replace("www.sitemap.org","www.sitemaps.org"))
    for u in urls:
        f.write(f"  <url><loc>{BASE}/{u}</loc><lastmod>{BUILD_DATE}</lastmod></url>\n")
    f.write("</urlset>\n")

# ---------------- manifesto pages ----------------
# docs/manifesto-{de,en}.md rendered through a deliberately small converter —
# the manifesto uses headings, bold/italic, lists, one table and rules, nothing
# more, and a dependency for that is not worth a clean clone breaking.
def md_html(md):
    def inline(t):
        t = esc(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
        return t
    # A heading written directly above its subtitle or text shares a block with
    # it, and everything after the heading line was silently dropped (the
    # manifesto's subtitle never rendered). Give every heading its own block.
    md = re.sub(r"(?m)^(#{1,6} .*)\n(?!\n)", r"\1\n\n", md)
    out = []
    for i, block in enumerate(re.split(r"\n\s*\n", md.strip())):
        lines = block.strip().split("\n")
        if block.strip() == "---":
            out.append("<hr>")
        elif lines[0].startswith("### "):
            # A ### directly under the title is a subtitle (the manifesto's use);
            # anywhere else it is an ordinary subsection heading (the paper's use).
            if i == 1:
                out.append(f"<p class='lede'>{inline(lines[0][4:])}</p>")
            else:
                out.append(f"<h3>{inline(lines[0][4:])}</h3>")
        elif lines[0].startswith("## "):
            out.append(f"<h2>{inline(lines[0][3:])}</h2>")
        elif lines[0].startswith("# "):
            out.append(f"<h1>{inline(lines[0][2:])}</h1>")
        elif all(l.lstrip().startswith("- ") for l in lines):
            out.append("<ul>" + "".join(f"<li>{inline(l.lstrip()[2:])}</li>" for l in lines) + "</ul>")
        elif all(l.startswith("|") for l in lines):
            rows = [[c.strip() for c in l.strip("|").split("|")] for l in lines
                    if not set(l.replace("|","").strip()) <= set("- :")]
            head, body = rows[0], rows[1:]
            out.append("<div style='overflow-x:auto'><table><thead><tr>"
                       + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
                       + "</tbody></table></div>")
        else:
            out.append(f"<p>{inline(' '.join(l.strip() for l in lines))}</p>")
    return "\n".join(out)

_docs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
for _fn, _out, _title, _desc, _other in (
    ("manifesto-de.md", "manifest.html", "Das Manifest — openAPPindex",
     "Warum ein unabhängiger, offener App-Index nötig ist — mit jeder Zahl datiert und belegt.",
     '<p class="src"><a href="/manifesto.html">Read this in English</a></p>'),
    ("manifesto-en.md", "manifesto.html", "The Manifesto — openAPPindex",
     "Why an independent, open app index is necessary — every figure dated and sourced.",
     '<p class="src"><a href="/manifest.html">Auf Deutsch lesen</a></p>'),
    ("working-paper.md", "paper.html", "Search Without Recall — openAPPindex working paper",
     "Preliminary evidence on discovery failure and price opacity in a mobile app market: "
     "81% of a category invisible to search, 77% of „free“ apps that charge. "
     "Method, data and limits stated.",
     '<p class="src"><a href="/manifesto.html">The manifesto</a> · '
     '<a href="/methode.html">Method &amp; data</a></p>')):
    _md = open(os.path.join(_docs, _fn), encoding="utf-8").read()
    page(_out, _title, _desc, _other + md_html(_md))

# IndexNow ownership key (Bing et al.). Stable across rebuilds by design — a
# changed key reads as a change of ownership. This only serves the proof file
# the protocol requires; run indexnow_submit.py after each deploy to submit.
INDEXNOW_KEY = "e595dfb6a3164c1a641ee51f09b7262e"
open(f"{OUT}/{INDEXNOW_KEY}.txt", "w").write(INDEXNOW_KEY)

# The landing page is the root. Copied in last, so no rebuild can overwrite it.
_landing = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "landing", "index.html")
if os.path.exists(_landing):
    _html = open(_landing, encoding="utf-8").read()
    if "<!doctype" not in _html.lower():
        i = _html.index("<nav>")
        _html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                 '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
                 '<meta name="description" content="An independent, open index of mobile apps. '
                 'We measured one app-store category as completely as we could reach it: 81% of '
                 'cooking apps never appear in its own search results.">\n'
                 '<link rel="canonical" href="https://openappindex.org/">\n'
                 '<link rel="alternate" hreflang="de" href="https://openappindex.org/de/">\n'
                 + _html[:i] + '\n</head>\n<body>\n' + _html[i:] + '\n</body>\n</html>\n')
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(_html)
    print("landing page installed at /")
else:
    raise SystemExit("!! landing/index.html missing — root would be wrong")

n = sum(len(fs) for _,_,fs in os.walk(OUT))
if not IMPRESSUM_READY:
    print("!! IMPRESSUM INCOMPLETE - do not deploy. Fill IMPRESSUM['street'] and ['city'] in build_site.py.")
print(f"built {n} files · {len(apps)} app pages · {len(QS)} question pages · {withiap} with in-app prices")
