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
import json, re, datetime, os, shutil
from classify import is_cooking_app
from site_common import (BASE, NOW, esc, slug, days_since, de_date, de_elapsed, eur, eur_range,
                         parse_eur, SHELL, write_page, og_tags)
import build_changelog

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

# The maintainer's own app (docs/funding-policy.md §3): its page must say so.
OWN_APPS = {6764606059}   # galleybook

# Wipe generated output first. Without this, pages for apps a corrected classifier
# no longer includes stay on disk and keep being served — which is how 211 pharmacy
# and game pages survived a rebuild on 2026-08-24.
# The Vercel project link (.vercel/) lives in the output directory and must survive
# the wipe, or the next `vercel deploy` silently creates a new, unlinked project.
if os.path.isdir(OUT):
    _keep = os.path.join(OUT, ".vercel")
    if os.path.isdir(_keep):
        shutil.move(_keep, OUT + ".vercel.keep")
    shutil.rmtree(OUT)
    os.makedirs(OUT)
    if os.path.isdir(OUT + ".vercel.keep"):
        shutil.move(OUT + ".vercel.keep", _keep)
TODAY = datetime.date.today().isoformat()

# The clock says when this ran, never when a fact was read. Rebuilding must not
# re-date a measurement nobody took again: source lines carry the recorded read
# date, and the build date is used only for sitemap lastmod.
BUILD_DATE = TODAY
CORPUS_READ = datetime.date.fromtimestamp(
    os.path.getmtime("data/corpus_de.json")).isoformat()

C = json.load(open("data/corpus_de.json", encoding="utf-8"))

# --- classification v4: one classifier for every script that counts -> classify.py

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

# The latest weekly snapshot (GAL-578) is newer than the corpus for version, last-update
# date and store price label. Those three are taken from it, each with its own read date.
# In-app purchase lists are not re-read weekly, so prices keep their product-page read
# date. Release notes are shown only while the version they belong to is still current.
SNAP, SNAP_READ = {}, None
_sd = os.path.join("data", "public", "snapshots")
if os.path.isdir(_sd):
    for _fn in sorted(os.listdir(_sd), reverse=True):
        _s = json.load(open(os.path.join(_sd, _fn), encoding="utf-8"))
        if _s.get("collected", {}).get("lookup") and _s.get("read_at", "") > CORPUS_READ:
            SNAP, SNAP_READ = _s["apps"], _s["read_at"]
            break

for a in apps:
    a["slug"] = f"{slug(a['trackName'])}-{a['trackId']}"
    a["lookup_read"] = CORPUS_READ
    a["notes_version"], a["notes_date"] = a.get("version"), a.get("currentVersionReleaseDate")
    a["not_found_on"] = None
    _r = SNAP.get(str(a["trackId"]))
    if _r and _r.get("ok"):
        if _r.get("v"): a["version"] = _r["v"]
        if _r.get("upd"): a["currentVersionReleaseDate"] = _r["upd"] + "T00:00:00Z"
        if _r.get("price"): a["formattedPrice"] = _r["price"]
        a["lookup_read"] = _r.get("read") or SNAP_READ
    elif _r:
        a["not_found_on"] = _r.get("read") or SNAP_READ
    a["days"] = days_since(a.get("currentVersionReleaseDate"))
    # Age of the last update on the day it was read: what the question pages count with,
    # so a claim like "not updated for over a year" is true of the read it rests on.
    _u = (a.get("currentVersionReleaseDate") or "")[:10]
    a["age"] = ((datetime.date.fromisoformat(a["lookup_read"]) - datetime.date.fromisoformat(_u)).days
                if _u else None)
    p = prices.get(a["trackId"], {})
    a["subtitle"] = p.get("subtitle")
    iaps = p.get("in_app_purchases")
    a["iaps"] = iaps
    vals = sorted(v for v in (parse_eur(i["price"]) for i in (iaps or [])) if v is not None)
    a["iap_min"], a["iap_max"] = (vals[0], vals[-1]) if vals else (None, None)
    a["price_known"] = bool(p.get("read_ok"))
    a["read_at"] = (p.get("read_at") or "")[:10] or None

# "Stand" of the dataset is the most recent recorded read, not today.
DATA_STAND = max([a["read_at"] for a in apps if a["read_at"]] or [CORPUS_READ])     # prices
LOOKUP_STAND = max(a["lookup_read"] for a in apps)                                    # versions, dates

def page(path, title, desc, body, ld="", lang="de"):
    write_page(OUT, path, title, desc, body, ld, lang)

# ---------------- app pages ----------------
# GAL-560: every app page links to its alphabetical neighbours, to the other apps of
# the same developer and to the A–Z index, so the whole index is one connected graph
# and no page depends on a capped list to be found.
AZ = sorted(apps, key=lambda a: (a["trackName"] or "").casefold())
AZ_POS = {a["trackId"]: i for i, a in enumerate(AZ)}
BY_SELLER = {}
for _a in AZ: BY_SELLER.setdefault(_a.get("sellerName"), []).append(_a)

def related(a):
    i = AZ_POS[a["trackId"]]
    prv, nxt = AZ[i-1], AZ[(i+1) % len(AZ)]
    same = [b for b in BY_SELLER.get(a.get("sellerName"), []) if b is not a][:12]
    out = "<h2>Im Index weiterlesen</h2>"
    if same:
        out += (f"<p>Weitere Apps von {esc(a.get('sellerName'))}: "
                + ", ".join(f"<a href='{BASE}/de/app/{b['slug']}/'>{esc(b['trackName'])}</a>" for b in same) + ".</p>")
    out += (f"<p>Alphabetisch davor: <a href='{BASE}/de/app/{prv['slug']}/'>{esc(prv['trackName'])}</a> · "
            f"danach: <a href='{BASE}/de/app/{nxt['slug']}/'>{esc(nxt['trackName'])}</a> · "
            f"<a href='{BASE}/de/app/'>alle {len(apps)} Apps von A bis Z</a></p>")
    return out

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
    if n and a["notes_version"] == a.get("version"):
        notes = (f"<h2>Was der Anbieter zur letzten Version schreibt</h2>"
                 f"<blockquote>{esc(n[:400])}{'…' if len(n)>400 else ''}</blockquote>"
                 f"<p class='src'>Eigene Versionshinweise des Anbieters zu Version {esc(a['notes_version'])}, "
                 f"veröffentlicht am {de_date(a['notes_date'])}.</p>")
    if a["not_found_on"]:
        notes += (f"<div class='rule'>Bei der Lesung am {de_date(a['not_found_on'])} lieferte Apples Schnittstelle "
                  f"für den deutschen Store zu dieser App keinen Eintrag. Das kann heißen, dass sie nicht mehr "
                  f"angeboten wird; wir schließen es nicht daraus. Die Angaben unten stammen aus der Lesung vom "
                  f"{de_date(a['lookup_read'])}.</div>")

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

    own = ""
    if a["trackId"] in OWN_APPS:
        own = (f'<div class="rule"><strong>Offenlegung:</strong> Diese App wird von Tim Meyerdierks entwickelt '
               f'und verkauft, der auch openAPPindex betreibt. Sie wird nach denselben veröffentlichten Regeln '
               f'erhoben wie jede andere App und erhält keine Daten, die nicht öffentlich sind '
               f'(<a href="{BASE}/funding.html">Finanzierungsregeln</a>, Abschnitt 3).</div>')
    body = f"""<nav class="bc"><a href="{BASE}/">openAPPindex</a> › <a href="{BASE}/de/">Deutschland</a> › <a href="{BASE}/de/app/">Apps</a></nav>
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
<p class="src">Quelle: iTunes Search API (erhoben am {a['lookup_read']}) und Produktseite im App Store
(Storefront Deutschland, erhoben am {a['read_at'] or 'nicht erhoben'}).</p>
{iap_rows}{notes}{own}
{related(a)}
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

# The A–Z index /de/app/ — 404'd until 2026-10-14, though every breadcrumb pointed at it.
def _letter(a):
    c = (a["trackName"] or "#")[0].upper()
    c = {"Ä":"A","Ö":"O","Ü":"U"}.get(c, c)
    return c if "A" <= c <= "Z" else "#"
_groups = {}
for _a in AZ: _groups.setdefault(_letter(_a), []).append(_a)
_az_body = (f"<nav class='bc'><a href='{BASE}/'>openAPPindex</a> › <a href='{BASE}/de/'>Deutschland</a> › Apps</nav>"
            f"<h1>Alle {len(apps)} Rezept- und Koch-Apps von A bis Z</h1>"
            f"<div class='rule'><strong>Sortierregel:</strong> alphabetisch nach dem Namen im App Store. "
            f"Keine Gewichtung, keine Auswahl.</div>"
            "<p>" + " · ".join(f"<a href='#{k}'>{k}</a>" for k in sorted(_groups)) + "</p>"
            + "".join(f"<h2 id='{k}'>{k}</h2><p>" + " · ".join(
                f"<a href='{BASE}/de/app/{b['slug']}/'>{esc(b['trackName'])}</a>" for b in _groups[k]) + "</p>"
                for k in sorted(_groups))
            + f"<p class='src'>Grundlage: iTunes Search API und App-Store-Produktseiten, Storefront Deutschland, "
              f"Stand {DATA_STAND}.</p>")
page("de/app/index.html", "Alle Rezept-Apps von A bis Z | openAPPindex",
     f"Alle {len(apps)} Rezept- und Koch-Apps im deutschen App Store, alphabetisch, mit Pflegezustand und Kosten.",
     _az_body)

# ---------------- question pages ----------------
def card(a, extra=""):
    return (f"<li class='card'><h3><a href='{BASE}/de/app/{a['slug']}/'>{esc(a['trackName'])}</a></h3>"
            f"<p class='meta'>{esc(a.get('sellerName'))} · zuletzt aktualisiert "
            f"{de_date(a.get('currentVersionReleaseDate'))} ({de_elapsed(a['days'])}){extra}</p></li>")

def qpage(fn, title, h1, question, rule, listed, desc, answer, extra=lambda a: ""):
    # GAL-551: the FAQ answer carries the answer itself — counts and the first entries,
    # each with its date — not the sorting rule. GAL-552: the list is also emitted as an
    # ItemList, so a machine reader gets the order and the URLs without parsing HTML.
    # GAL-560: lists are complete. A 60-item cap left 715 of 941 app pages unlinked.
    ld = [{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{
              "@type":"Question","name":question,
              "acceptedAnswer":{"@type":"Answer","text":answer}}]},
          {"@context":"https://schema.org","@type":"ItemList","name":h1,
           "description":re.sub(r"<[^>]+>","",rule),"numberOfItems":len(listed),
           "itemListOrder":"https://schema.org/ItemListOrderDescending",
           "itemListElement":[{"@type":"ListItem","position":i+1,"name":a["trackName"],
                               "url":f"{BASE}/de/app/{a['slug']}/"} for i,a in enumerate(listed[:100])]}]
    body = (f"<nav class='bc'><a href='{BASE}/'>openAPPindex</a> › <a href='{BASE}/de/'>Deutschland</a> › Fragen</nav>"
            f"<h1>{esc(h1)}</h1><p class='lede'>{esc(desc)}</p>"
            f"<h2>Die Antwort</h2><p>{esc(answer)}</p>"
            f"<div class='rule'><strong>Sortierregel:</strong> {rule}</div>"
            f"<h2>Alle {len(listed)} Apps</h2><ol>{''.join(card(a, extra(a)) for a in listed)}</ol>"
            f"<p class='src'>Grundlage: {len(apps)} Apps im deutschen App Store, deren eigene Beschreibung sie als "
            f"Rezept- oder Koch-App ausweist. Versionen und Aktualisierungsdaten gelesen am {LOOKUP_STAND}, "
            f"In-App-Käufe am {DATA_STAND}. Apps, die Apples Schnittstelle bei der letzten Lesung nicht mehr "
            f"lieferte, sind nicht aufgeführt. "
            f"<a href='{BASE}/de/app/'>Alle Apps von A bis Z</a>.</p>")
    page(f"de/frage/{fn}.html", title, desc, body,
         "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld))

def upd(a): return de_date(a.get("currentVersionReleaseDate"))
def names(lst, fmt, n=5): return "; ".join(fmt(a) for a in lst[:n])

listed_apps = [a for a in apps if not a["not_found_on"]]
by_recency = sorted([a for a in listed_apps if a["days"] is not None], key=lambda x: x["days"])
recent_365 = [a for a in by_recency if a["age"] is not None and a["age"] <= 365]
qpage("welche-rezept-app-wird-noch-gepflegt",
      "Welche Rezept-App wird noch gepflegt? | openAPPindex",
      "Welche Rezept-App wird noch gepflegt?",
      "Welche Rezept-App wird noch gepflegt?",
      "Alle Apps, sortiert nach dem von Apple veröffentlichten Datum der letzten Aktualisierung, neueste zuerst. "
      "Downloadzahlen und Bewertungen fließen nicht ein.",
      by_recency,
      "Rezept-Apps im deutschen App Store, sortiert nach dem Datum ihrer letzten Aktualisierung.",
      f"Von {len(by_recency)} Rezept- und Koch-Apps im deutschen App Store wurden {len(recent_365)} in den "
      f"365 Tagen vor der Lesung am {LOOKUP_STAND} aktualisiert. Zuletzt aktualisiert: "
      + names(by_recency, lambda a: f"{a['trackName']} ({upd(a)})") + ". Das Datum der letzten "
      "Aktualisierung sagt, dass eine App gepflegt wird, nicht wie gut sie ist.")

stale = sorted([a for a in listed_apps if a["age"] and a["age"] > 365], key=lambda x: -x["age"])
qpage("rezept-apps-lange-nicht-aktualisiert",
      "Welche Rezept-Apps wurden lange nicht aktualisiert? | openAPPindex",
      "Rezept-Apps, die seit über einem Jahr nicht aktualisiert wurden",
      "Welche Rezept-Apps wurden lange nicht aktualisiert?",
      "Alle Apps, deren letzte von Apple veröffentlichte Aktualisierung mehr als 365 Tage zurückliegt, "
      "älteste zuerst. Das ist eine Datumsangabe, keine Aussage über die Qualität der App.",
      stale,
      "Rezept-Apps im deutschen App Store, deren letzte Aktualisierung über ein Jahr zurückliegt.",
      f"{len(stale)} von {len(listed_apps)} Rezept- und Koch-Apps im deutschen App Store wurden seit über einem Jahr "
      f"nicht aktualisiert, {sum(1 for a in stale if a['age'] > 730)} davon seit über zwei Jahren "
      f"(Lesung vom {LOOKUP_STAND}). Am längsten nicht aktualisiert: "
      + names(stale, lambda a: f"{a['trackName']} (zuletzt {upd(a)})") + ".")

hidden = sorted([a for a in listed_apps if a["iap_max"] and (a.get("formattedPrice") or "").lower() in ("gratis","free")],
                key=lambda x: -x["iap_max"])
free_listed = sum(1 for a in apps if (a.get("formattedPrice") or "").lower() in ("gratis","free") and a["price_known"])
qpage("gratis-rezept-app-was-kostet-sie-wirklich",
      "„Gratis“ im Store — was kostet die Rezept-App wirklich? | openAPPindex",
      "Als „Gratis“ gelistet — und was tatsächlich im Kaufmenü steht",
      "Was kostet eine als gratis gelistete Rezept-App wirklich?",
      "Apps, die im Store als „Gratis“ erscheinen und auf ihrer Produktseite In-App-Käufe ausweisen, "
      "sortiert nach dem höchsten ausgewiesenen Einzelpreis. Alle Preise sind die von Apple veröffentlichten Angaben.",
      hidden,
      "Rezept-Apps, die als gratis gelistet sind, mit den tatsächlich ausgewiesenen In-App-Preisen.",
      f"{len(hidden)} von {free_listed} als „Gratis“ gelisteten Rezept-Apps mit erhobener Preisliste weisen "
      f"In-App-Käufe aus (Erhebung {DATA_STAND}). Die höchsten einzelnen In-App-Käufe: "
      + names(hidden, lambda a: f"{a['trackName']} ({eur(a['iap_max'])})") + ". Das sind einzelne "
      "Kaufpositionen, wie Apple sie veröffentlicht, keine Jahreskosten.",
      extra=lambda a: f" · In-App-Käufe {eur(a['iap_min'])}–{eur(a['iap_max'])}")

noiap = sorted([a for a in listed_apps if a["price_known"] and not a["iaps"] and a["days"] is not None],
               key=lambda x: x["days"])
qpage("rezept-app-ohne-abo-und-ohne-in-app-kaeufe",
      "Rezept-Apps ohne In-App-Käufe | openAPPindex",
      "Rezept-Apps, für die keine In-App-Käufe ausgewiesen sind",
      "Gibt es Rezept-Apps ohne Abo und ohne In-App-Käufe?",
      "Apps, auf deren Produktseite Apple keine In-App-Käufe ausweist, sortiert nach dem Datum der letzten "
      "Aktualisierung. Fehlt die Angabe, steht es hier — geschätzt wird nichts.",
      noiap,
      "Rezept-Apps im deutschen App Store ohne ausgewiesene In-App-Käufe.",
      f"Ja: Für {len(noiap)} Rezept- und Koch-Apps im deutschen App Store weist die Produktseite keine "
      f"In-App-Käufe aus (Erhebung {DATA_STAND}). Davon zuletzt aktualisiert: "
      + names(noiap, lambda a: f"{a['trackName']} ({upd(a)}, Store-Preis {a.get('formattedPrice')})")
      + ". Ob eine App ein Abo außerhalb des App Store verkauft, zeigt die Produktseite nicht.")

# ---- GAL-566: pages for gate queries B6, C10, C11/C12, which had no page at all ----
# These lists rest on what each developer's own store text says, not on a test of the
# app. Every card therefore shows the exact sentence or purchase item that matched, so
# the reader sees the evidence and the rule, not our reading of it.
def _quote(m):
    t = re.sub(r"\s+", " ", m.group(0)).strip(" -•·*:")
    return t if len(t) <= 180 else t[:177] + "…"
_WEB = re.compile(r"[^.!?\n]*\b(?:(?:aus|von)\s+(?:jeder|allen|beliebigen)?\s*(?:Webseiten?|Websites?|Internetseiten?|Blogs?|Food-?Blogs?)"
                  r"|import\w*\s+[^.!?\n]{0,40}\b(?:Webseiten?|Websites?|Website-Links?|Links?|URLs?|Internet|Blogs?)"
                  r"|(?:Webseiten?|Websites?|Website-Links?|Links?|URLs?|Blogs?)\s+[^.!?\n]{0,40}\bimport\w*"
                  r"|(?:import|save|clip)\w*\s+recipes?\s+from\s+(?:any\s+)?(?:website|web|blog|url|link))\b[^.!?\n]*", re.I)
_OWN = re.compile(r"[^.!?\n]*\b(?:eigenen?\s+Rezepte|(?:Rezepte|Lieblingsrezepte)\s+(?:sammeln|speichern|verwalten|organisieren)"
                  r"|(?:your|own)\s+recipes?\s+(?:collection|organi[sz]er|manager)|digitale[sn]?\s+(?:Rezeptbuch|Kochbuch))\b[^.!?\n]*", re.I)
_ONCE = re.compile(r"\b(?:einmalig\w*|Einmalkauf|lifetime|lebenslang\w*|Vollversion|forever|for\s+life)\b", re.I)
_SUBS = re.compile(r"\b(?:Abo\w*|Monat\w*|monatlich|jährlich|Woche\w*|wöchentlich|month\w*|year\w*|week\w*|annual\w*|subscription\w*)\b", re.I)
for a in apps:
    d = a.get("description") or ""
    m = _WEB.search(d); a["q_web"] = _quote(m) if m else None
    m = _OWN.search(d); a["q_own"] = _quote(m) if m else None
    a["q_once"] = [i for i in (a["iaps"] or []) if _ONCE.search(i["name"]) and not _SUBS.search(i["name"])]

web = [a for a in by_recency if a["q_web"]]
qpage("app-rezepte-von-webseiten-speichern",
      "App zum Speichern von Rezepten aus Webseiten | openAPPindex",
      "Rezept-Apps, deren Store-Beschreibung den Import aus Webseiten nennt",
      "Welche App speichert Rezepte von Webseiten?",
      "Apps, deren eigene Beschreibung im App Store den Import oder das Speichern von Rezepten aus Webseiten, Links "
      "oder Blogs nennt, sortiert nach dem Datum der letzten Aktualisierung, neueste zuerst. Der zitierte Satz ist "
      "die Angabe des Anbieters; ob die Funktion hält, was er verspricht, haben wir nicht geprüft.",
      web,
      "Rezept-Apps im deutschen App Store, deren Beschreibung den Import von Rezepten aus Webseiten nennt.",
      f"{len(web)} von {len(listed_apps)} Rezept- und Koch-Apps im deutschen App Store nennen in ihrer Store-Beschreibung "
      f"den Import von Rezepten aus Webseiten, Links oder Blogs (Beschreibungen gelesen am {CORPUS_READ}). Zuletzt aktualisiert: "
      + names(web, lambda a: f"{a['trackName']} ({upd(a)})") + ". Das ist die Angabe der Anbieter, kein Funktionstest.",
      extra=lambda a: f" · Anbieter: „{esc(a['q_web'])}“")

own = [a for a in by_recency if a["q_own"]]
qpage("app-eigene-rezepte-sammeln-und-verwalten",
      "App, um eigene Rezepte zu sammeln und zu verwalten | openAPPindex",
      "Rezept-Apps, deren Store-Beschreibung das Sammeln eigener Rezepte nennt",
      "Welche App verwaltet eigene Rezepte?",
      "Apps, deren eigene Beschreibung im App Store das Anlegen, Sammeln, Speichern oder Verwalten eigener Rezepte "
      "nennt, sortiert nach dem Datum der letzten Aktualisierung, neueste zuerst. Keine Rangfolge nach Qualität: "
      "Der zitierte Satz ist die Angabe des Anbieters.",
      own,
      "Rezept-Apps im deutschen App Store, deren Beschreibung das Sammeln und Verwalten eigener Rezepte nennt.",
      f"{len(own)} von {len(listed_apps)} Rezept- und Koch-Apps im deutschen App Store nennen in ihrer Store-Beschreibung "
      f"das Sammeln oder Verwalten eigener Rezepte (Beschreibungen gelesen am {CORPUS_READ}). Zuletzt aktualisiert: "
      + names(own, lambda a: f"{a['trackName']} ({upd(a)})") + ". Was eine App kostet, steht auf ihrer Seite im Index.",
      extra=lambda a: f" · Anbieter: „{esc(a['q_own'])}“")

once = [a for a in listed_apps if a["q_once"]]
paid_once = [a for a in listed_apps if a["price_known"] and not a["iaps"]
             and (a.get("formattedPrice") or "").lower() not in ("gratis", "free")]
once_all = sorted(once + paid_once, key=lambda x: x["days"] if x["days"] is not None else 99999)
def _once_txt(a):
    if a["q_once"]:
        return " · Kaufposition: " + "; ".join(f"„{esc(i['name'].strip())}“ {esc(i['price'])}" for i in a["q_once"][:3])
    return f" · Kaufpreis {esc(a.get('formattedPrice'))}, keine In-App-Käufe ausgewiesen"
qpage("rezept-app-einmalig-bezahlen-statt-abo",
      "Rezept-App einmal bezahlen statt Abo | openAPPindex",
      "Rezept-Apps mit Einmalkauf: Kaufpreis ohne In-App-Käufe oder eine als einmalig bezeichnete Kaufposition",
      "Welche Rezept-Apps kann man einmalig bezahlen statt im Abo?",
      "Zwei Gruppen, sortiert nach dem Datum der letzten Aktualisierung: Apps mit Kaufpreis im Store, für die keine "
      "In-App-Käufe ausgewiesen sind, und Apps mit einer In-App-Kaufposition, deren Name sie als Einmalkauf bezeichnet "
      "(„Lifetime“, „lebenslang“, „einmalig“, „Vollversion“). Die Bezeichnung stammt vom Anbieter. Apple veröffentlicht "
      "nicht, ob eine Kaufposition ein Abo ist; dieselbe App kann daneben Abos anbieten.",
      once_all,
      "Rezept-Apps im deutschen App Store, die einen Einmalkauf ausweisen.",
      f"{len(paid_once)} Rezept- und Koch-Apps im deutschen App Store kosten einen einmaligen Kaufpreis und weisen keine "
      f"In-App-Käufe aus; bei {len(once)} weiteren nennt mindestens eine Kaufposition einen Einmalkauf (Erhebung "
      f"{DATA_STAND}). Beispiele: " + names(once_all, lambda a: f"{a['trackName']}" + (
          f" („{a['q_once'][0]['name'].strip()}“, {a['q_once'][0]['price']})" if a["q_once"]
          else f" (Kaufpreis {a.get('formattedPrice')})")) + ". Die Bezeichnungen stammen von den Anbietern.",
      extra=_once_txt)

QS = [("welche-rezept-app-wird-noch-gepflegt","Welche Rezept-App wird noch gepflegt?"),
      ("rezept-apps-lange-nicht-aktualisiert","Welche wurden lange nicht aktualisiert?"),
      ("gratis-rezept-app-was-kostet-sie-wirklich","„Gratis“ — was kostet sie wirklich?"),
      ("rezept-app-ohne-abo-und-ohne-in-app-kaeufe","Welche kommen ohne In-App-Käufe aus?"),
      ("rezept-app-einmalig-bezahlen-statt-abo","Welche kann man einmal bezahlen statt im Abo?"),
      ("app-rezepte-von-webseiten-speichern","Welche speichern Rezepte von Webseiten?"),
      ("app-eigene-rezepte-sammeln-und-verwalten","Welche verwalten eigene Rezepte?")]

# ---------------- weekly changelog (GAL-578) ----------------
# Rendered only when data/public/changelog/*.json exists; until then the site is byte-identical.
build_changelog.SLUGS = {a["trackId"]: a["slug"] for a in apps}
WEEKS = build_changelog.render_all(OUT)
cl_link = ("" if not WEEKS else
           f"<h2>Was sich geändert hat</h2><ol><li class='card'><h3><a href='{BASE}/de/aenderungen/'>"
           f"Wöchentliche Änderungen im Index</a></h3><p class='meta'>Zuletzt: Woche {esc(WEEKS[0]['week'])}, "
           f"Lesung vom {de_date(WEEKS[0]['to'])}</p></li></ol>")

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
{cl_link}<h2>Datenbestand</h2>
<p><strong>{len(apps)} Apps</strong> im deutschen App Store, deren eigene Store-Beschreibung sie als Rezept- oder
Koch-App ausweist. Für <strong>{withiap}</strong> davon sind die auf der Produktseite ausgewiesenen In-App-Käufe
erfasst. Stand: {DATA_STAND}.</p>
<div class="rule">Keine Platzierung ist käuflich, zu keinem Preis. Wer uns finanziert, ist öffentlich
(<a href="{BASE}/funding.html">Finanzierungsregeln</a>, englisch).
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
{"" if not WEEKS else """<h2>Was sich w&ouml;chentlich &auml;ndert</h2>
<p>Unter <a href="/de/aenderungen/">/de/aenderungen/</a> vergleichen wir jede Woche zwei datierte
Lesungen des Index: neue Apps, neue Versionen, ge&auml;nderte Preisangaben, Apps, die die
Lookup-Schnittstelle nicht mehr zur&uuml;ckgibt &mdash; und jede Korrektur an unseren eigenen
Daten, in derselben Liste. Jede Zeile tr&auml;gt das Datum ihrer Lesung. Es gibt keine Auswahl:
jede &Auml;nderung, die eine auf der Seite genannte Schwelle erf&uuml;llt, erscheint. Wird eine
Angabe in einer Woche nicht erhoben (etwa In-App-K&auml;ufe, deren Produktseiten nicht gelesen
wurden), steht das dort; verglichen wird sie dann nicht.</p>
"""}<h2>Wie sortiert wird</h2>
<p>Jede Liste nennt ihre Sortierregel auf der Seite selbst. Downloadzahlen, Bewertungssterne und Werbebudget
fließen in keine Sortierung ein.</p>
<h2>Das Zitier-Experiment: Ergebnis vom 13.10.2026</h2>
<p>Ob KI-Assistenten mit Websuche einen unabhängigen App-Index zitieren, haben wir mit vorab
eingefrorenen Fragen und Schwellen gemessen (Protokoll vom 21.08.2026). Ergebnis zum Stichtag
13.10.2026: <strong>nicht entscheidbar, weil die Seite nicht ausreichend indexiert war</strong>
(INCONCLUSIVE — CRAWLING). Das Protokoll verlangte mindestens 100 indexierte Seiten bei Google und
Bing. Bing hielt 46, Brave 0. ChatGPT sucht über Bing, Claude über Brave, deshalb konnten diese
beiden Teile nicht gewertet werden. Perplexity kannte die Seite und zitierte sie in 0 von 30
gewerteten Antworten.</p>
<p class="src">Vollständiges Ergebnis: <a href="https://github.com/tim-muky/openappindex/blob/main/docs/gate-result.md">gate-result.md</a> ·
Protokoll: <a href="https://github.com/tim-muky/openappindex/blob/main/docs/gate-protocol.md">gate-protocol.md</a> ·
Folgeexperiment: <a href="https://github.com/tim-muky/openappindex/blob/main/docs/experiment-2-protocol.md">Experiment 2</a></p>
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

# ---------------- the dataset on the domain (GAL-561) ----------------
# The CC BY 4.0 export, served next to the pages that cite it, so a reader (or a
# crawler) can check a figure against the file without leaving the domain.
PUBLIC_FILES = [("corpus_de.json", "Alle Apps der 25-Abfragen-Erhebung (Kochen), Store-Fakten ohne Beschreibungstexte"),
                ("closure_apps.json", "Apps, die nur über den „Ähnliche Apps“-Graphen gefunden wurden (Kochen)"),
                ("prices_de.json", "Ausgewiesene In-App-Käufe je App, mit Erhebungsdatum (Kochen)"),
                ("corrections.json", "Datierte Korrekturen am Index")]
os.makedirs(f"{OUT}/data", exist_ok=True)
_served = []
for _fn, _what in PUBLIC_FILES:
    _src = os.path.join("data", "public", _fn)
    if os.path.exists(_src):
        shutil.copy(_src, f"{OUT}/data/{_fn}")
        _served.append((_fn, _what, os.path.getsize(_src)))
_sleep_pub = os.path.join("..", "sleep", "data", "public")
if os.path.isdir(_sleep_pub):
    os.makedirs(f"{OUT}/data/sleep", exist_ok=True)
    for _fn in sorted(os.listdir(_sleep_pub)):
        if _fn.endswith(".json"):
            shutil.copy(os.path.join(_sleep_pub, _fn), f"{OUT}/data/sleep/{_fn}")
            _what = {"category_sleep_de.json": "Alle 3.578 Apps der Kategorie Schlaf & Meditation, mit Fundweg (Abfrage oder Graph-Schritt)",
                     "prices_sleep_de.json": "Ausgewiesene In-App-Käufe je App, mit Erhebungsdatum (Schlaf & Meditation)"}.get(_fn, "Schlaf & Meditation")
            _served.append((f"sleep/{_fn}", _what, os.path.getsize(os.path.join(_sleep_pub, _fn))))
DATASET_LD = {"@context":"https://schema.org","@type":"Dataset",
    "name":"openAPPindex — store facts for recipe and sleep apps, German App Store",
    "description":("Dated, factual records about every app in two categories of the German iOS App Store as far "
                   "as the store's search and its similar-apps graph reach: version, last-update date, store price "
                   "label and the in-app purchases Apple lists on each product page. No descriptions, no reviews, "
                   "no scores. Missing values are null, never estimated; prices are never annualised."),
    "url":f"{BASE}/data/","license":"https://creativecommons.org/licenses/by/4.0/",
    "isAccessibleForFree":True,"inLanguage":["de","en"],
    "creator":{"@type":"Person","name":"Tim Meyerdierks"},
    "publisher":{"@type":"Organization","name":"openAPPindex","url":BASE},
    "temporalCoverage":"2026-08-19/2026-09-02",
    "spatialCoverage":{"@type":"Place","name":"Germany (App Store storefront DE)"},
    "keywords":["app store","in-app purchases","price transparency","search recall","Germany"],
    "distribution":[{"@type":"DataDownload","encodingFormat":"application/json",
                     "contentUrl":f"{BASE}/data/{fn}","name":fn} for fn,_,_ in _served],
    "isBasedOn":"https://github.com/tim-muky/openappindex"}
page("data/index.html", "Datensatz — openAPPindex",
     "Der offene Datensatz hinter openAPPindex: Store-Fakten zu Rezept- und Schlaf-Apps im deutschen App Store, CC BY 4.0.",
     f"""<nav class='bc'><a href='{BASE}/'>openAPPindex</a> › Daten</nav>
<h1>Der Datensatz</h1>
<p class="lede">Jede Zahl auf diesen Seiten lässt sich aus diesen Dateien nachrechnen. Lizenz:
<a href="https://creativecommons.org/licenses/by/4.0/deed.de">CC BY 4.0</a>, Quellenangabe
„openAPPindex, Stand {DATA_STAND}“.</p>
<table><tbody>""" + "".join(f"<tr><td><a href='{BASE}/data/{fn}'>{esc(fn)}</a></td><td>{esc(w)} · {sz/1e6:.1f} MB</td></tr>"
                            for fn, w, sz in _served) + f"""</tbody></table>
<div class="rule">Enthalten sind nur Tatsachen: Kennungen, Namen, Anbieter, Version, Datum der letzten
Aktualisierung, Preisangabe im Store und die von Apple ausgewiesenen In-App-Käufe, jeweils mit
Erhebungsdatum. Beschreibungs- und Versionshinweistexte sind bewusst nicht enthalten — sie sind
urheberrechtlich die Texte der Anbieter. Fehlende Werte sind <code>null</code>, nie 0.</div>
<p>Die Skripte, die diese Dateien erzeugen, und ihre Dokumentation:
<a href="https://github.com/tim-muky/openappindex">github.com/tim-muky/openappindex</a> (Code unter AGPL-3.0).
Korrekturen an <a href="mailto:korrektur@openappindex.org">korrektur@openappindex.org</a>.</p>""",
     f'<script type="application/ld+json">{json.dumps(DATASET_LD, ensure_ascii=False)}</script>')

# ---------------- llms.txt (GAL-562) ----------------
# Leads with the figures an assistant is asked for, links every answer surface,
# and points at llms-full.txt, which carries the category-wide extremes.
_free_listed = sum(1 for a in apps if (a.get("formattedPrice") or "").lower() in ("gratis","free") and a["price_known"])
_free_iap = sum(1 for a in apps if a["iaps"] and (a.get("formattedPrice") or "").lower() in ("gratis","free"))
_iapmax = sorted([a for a in apps if a["iap_max"]], key=lambda x: -x["iap_max"])
import statistics
_median_hi = statistics.median(a["iap_max"] for a in apps if a["iap_max"] and a["iap_max"] > 0
                               and (a.get("formattedPrice") or "").lower() in ("gratis", "free"))
_stale2 = sum(1 for a in apps if not a["not_found_on"] and a["age"] and a["age"] > 730)
open(f"{OUT}/llms.txt","w",encoding="utf-8").write(f"""# openAPPindex

> An independent, open index of mobile apps: dated store facts — when an app was last updated
> and what it actually costs — for whole app-store categories, not just what search returns.
> Ein unabhängiger, offener App-Index: datierte Store-Fakten für ganze Kategorien. Keine
> bezahlte Platzierung, keine Bewertungen, nichts geschätzt.

Coverage: German iOS App Store. Recipe & cooking apps: {len(apps)} (data as of {DATA_STAND}).
Sleep & meditation apps: 3,578 (measured 1–2 Sep 2026).

Key figures (each sourced on the linked pages):
- {_free_iap} of {_free_listed} recipe apps listed as free ("Gratis") list in-app purchases. Among those {_free_iap}, the median highest single in-app purchase is {eur(_median_hi)}.
- Highest single in-app purchase among recipe apps: {_iapmax[0]['trackName'] if _iapmax else 'n/a'}, {eur(_iapmax[0]['iap_max']) if _iapmax else 'n/a'}.
- {_stale2} recipe apps had, as read on {LOOKUP_STAND}, not been updated for more than two years.
- Of the apps a 25-query sweep found, 81% of recipe apps never appear for "rezepte" and 88% of sleep apps never appear for "schlaf".
- Prices are single in-app purchase items as Apple lists them, never annualised.

## Answers (German)
""" + "".join(f"- [{t}]({BASE}/de/frage/{f}.html)\n" for f,t in QS) + f"""- [Alle Rezept-Apps von A bis Z]({BASE}/de/app/)
""" + ("" if not WEEKS else f"- [Was sich im Index geändert hat (wöchentlich)]({BASE}/de/aenderungen/)\n") + f"""
## Full data
- [llms-full.txt: every recipe app with date and prices, plus category extremes]({BASE}/llms-full.txt)
- [Dataset, CC BY 4.0]({BASE}/data/)

## Findings and method
- [The replication across two categories]({BASE}/second-category.html)
- [Working paper]({BASE}/paper.html)
- [Method and corrections]({BASE}/methode.html)
- [Manifesto]({BASE}/manifesto.html)
- [Funding policy]({BASE}/funding.html)

## Citation
"openAPPindex, data as of {DATA_STAND}" — {BASE}
""")

with open(f"{OUT}/llms-full.txt","w",encoding="utf-8") as f:
    f.write(f"# openAPPindex — vollständiger Datenbestand (Stand {DATA_STAND})\n\n")
    f.write("Quelle: iTunes Search API + App-Store-Produktseiten, Storefront Deutschland.\n")
    f.write("Keine Rezensionen, keine Bewertungen. Fehlende Angaben sind als solche ausgewiesen.\n\n")
    f.write("## Höchste einzelne In-App-Käufe der Kategorie (Top 20)\n")
    for a in _iapmax[:20]:
        f.write(f"- {a['trackName']}: {eur(a['iap_max'])} (Store-Preis {a.get('formattedPrice')}, erhoben {a['read_at']}) — {BASE}/de/app/{a['slug']}/\n")
    f.write("\n## Am längsten nicht aktualisiert (Top 20)\n")
    for a in sorted([a for a in apps if a["days"] and not a["not_found_on"]], key=lambda x: -x["days"])[:20]:
        f.write(f"- {a['trackName']}: zuletzt {de_date(a.get('currentVersionReleaseDate'))} — {BASE}/de/app/{a['slug']}/\n")
    f.write("\n## Alle Apps, zuletzt aktualisierte zuerst\n\n")
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


# ---------------- manifesto pages ----------------
# docs/manifesto-{de,en}.md rendered through a deliberately small converter —
# the manifesto uses headings, bold/italic, lists, one table and rules, nothing
# more, and a dependency for that is not worth a clean clone breaking.
REPO = "https://github.com/tim-muky/openappindex"
def repo_href(h):
    # The docs link to each other relatively, as files in the repository. Served on
    # the domain those links would 404, so anything not absolute points at GitHub.
    if h.startswith(("http://", "https://", "/", "#", "mailto:")): return h
    # Docs that are also served on the domain link there: internal links are what lets a
    # crawler find them, and a reader stays on the site.
    served = {"working-paper.md": "/paper.html", "manifesto-en.md": "/manifesto.html",
              "manifesto-de.md": "/manifest.html", "second-category-findings.md": "/second-category.html",
              "funding-policy.md": "/funding.html", "thesis.md": "/thesis.html"}
    base, _, frag = h.partition("#")
    if base.split("/")[-1] in served and not base.startswith(".."):
        return served[base.split("/")[-1]] + (f"#{frag}" if frag else "")
    import posixpath
    target = posixpath.normpath(posixpath.join("docs", h))
    return f"{REPO}/{'tree' if h.endswith('/') else 'blob'}/main/{target}"

def md_html(md):
    def inline(t):
        t = esc(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{repo_href(m.group(2))}">{m.group(1)}</a>', t)
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
     '<a href="/methode.html">Method &amp; data</a></p>'),
    ("second-category-findings.md", "second-category.html",
     "The same 77%, in a category chosen to be different — openAPPindex",
     "Replication in 3,578 sleep and meditation apps, German App Store: 88% absent from the "
     "obvious query, 77% of „free“ apps charge, median highest in-app purchase €39.99 — the same "
     "to the cent as cooking apps.",
     '<p class="src"><a href="/paper.html">Working paper</a> · '
     '<a href="/methode.html">Method &amp; data</a></p>'),
    ("thesis.md", "thesis.html", "Constructed Opacity — openAPPindex",
     "An essay on why the mobile app economy fails the tests of a fair and transparent market, "
     "and why that failure is profitable. Every figure dated and sourced.",
     '<p class="src"><a href="/paper.html">Working paper</a> · '
     '<a href="/manifesto.html">The manifesto</a> · <a href="/methode.html">Method &amp; data</a></p>'),
    ("datenschutz-de.md", "datenschutz.html", "Datenschutzerklärung — openAPPindex",
     "Datenschutzerklärung von openappindex.org: keine Cookies, kein Tracking, anonyme Zählung ohne IP-Adresse.",
     '<p class="src"><a href="/impressum.html">Impressum</a></p>'),
    ("funding-policy.md", "funding.html", "Funding policy — openAPPindex",
     "What money can and cannot do at openAPPindex: no placement is for sale, every supporter is "
     "named, store operators are excluded.",
     '<p class="src"><a href="/manifesto.html">The manifesto</a> · '
     '<a href="/impressum.html">Impressum</a></p>')):
    _md = open(os.path.join(_docs, _fn), encoding="utf-8").read()
    page(_out, _title, _desc, _other + md_html(_md), lang="de" if _fn.endswith("-de.md") else "en")

# IndexNow ownership key (Bing et al.). Stable across rebuilds by design — a
# changed key reads as a change of ownership. This only serves the proof file
# the protocol requires; run indexnow_submit.py after each deploy to submit.
INDEXNOW_KEY = "e595dfb6a3164c1a641ee51f09b7262e"
open(f"{OUT}/{INDEXNOW_KEY}.txt", "w").write(INDEXNOW_KEY)

LANDING_DESC = ('An independent, open index of mobile apps. We measured two app-store categories as completely as we could reach them: 81% of cooking apps and 88% of sleep apps never appear for the obvious search, and 77% of apps listed as free charge in-app.')

# Self-hosted fonts (OFL), so no visitor's browser contacts Google (decided 2026-10-10).
_fonts = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "landing", "fonts")
if os.path.isdir(_fonts):
    shutil.copytree(_fonts, os.path.join(OUT, "fonts"), dirs_exist_ok=True)

# The landing page is the root. Copied in last, so no rebuild can overwrite it.
_landing = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "landing", "index.html")
if os.path.exists(_landing):
    _html = open(_landing, encoding="utf-8").read()
    if "<!doctype" not in _html.lower():
        i = _html.index("<nav>")
        _html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                 '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
                 f'<meta name="description" content="{LANDING_DESC}">\n'
                 + og_tags("openAPPindex — the map is missing most of the streets", LANDING_DESC,
                           "https://openappindex.org/", "en") +
                 '<link rel="canonical" href="https://openappindex.org/">\n'
                 '<link rel="alternate" hreflang="de" href="https://openappindex.org/de/">\n'
                 + _html[:i] + '\n</head>\n<body>\n' + _html[i:] + '\n</body>\n</html>\n')
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(_html)
    print("landing page installed at /")
else:
    raise SystemExit("!! landing/index.html missing — root would be wrong")

# The sitemap is written last: lastmod hashes the finished pages, landing included.
# Submitted set = pages that carry information available nowhere else.
# App pages without in-app price data stay on the site and stay linked, but are
# not submitted: 900+ near-identical thin pages risk the whole site being
# classified as low-value, which would suppress the good pages too.
urls = ["", "de/", "methode.html", "impressum.html", "manifest.html", "manifesto.html", "paper.html",
        "second-category.html", "funding.html", "thesis.html", "datenschutz.html", "de/app/", "data/"] + [f"de/frage/{f}.html" for f,_ in QS] \
       + [f"de/app/{a['slug']}/" for a in apps if a["iaps"]]
# GAL-553: lastmod is the date a page's content last changed, not the build clock.
# Each submitted page is hashed with its day-relative phrases ("vor 3 Tagen") removed,
# and the date moves only when the hash does. lastmod.json is tracked, so the dates
# survive a clean clone. Every URL carrying the build date tells crawlers nothing.
import hashlib
_LM_FILE = "lastmod.json"
_lm = json.load(open(_LM_FILE)) if os.path.exists(_LM_FILE) else {}
_VOLATILE = re.compile(r"\((?:vor [^)]*|heute|gestern)\)|vor \d+ (?:Tagen|Monaten|Jahren)[^<]*")
def lastmod(u):
    fp = os.path.join(OUT, u + ("index.html" if (u == "" or u.endswith("/")) else ""))
    h = hashlib.sha256(_VOLATILE.sub("", open(fp, encoding="utf-8").read()).encode()).hexdigest()
    if _lm.get(u, {}).get("sha256") != h:
        _lm[u] = {"sha256": h, "lastmod": BUILD_DATE}
    return _lm[u]["lastmod"]

with open(f"{OUT}/sitemap.xml","w",encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9">\n'
            .replace("www.sitemap.org","www.sitemaps.org"))
    for u in urls:
        f.write(f"  <url><loc>{BASE}/{u}</loc><lastmod>{lastmod(u)}</lastmod></url>\n")
    # changelog pages carry the date of the read they describe as lastmod — a real date, not the build clock
    if WEEKS:
        f.write(f"  <url><loc>{BASE}/de/aenderungen/</loc><lastmod>{WEEKS[0]['to']}</lastmod></url>\n")
        for w in WEEKS:
            f.write(f"  <url><loc>{BASE}/de/aenderungen/{w['week']}/</loc><lastmod>{w['to']}</lastmod></url>\n")
    f.write("</urlset>\n")
json.dump(_lm, open(_LM_FILE, "w"), indent=0, sort_keys=True)

n = sum(len(fs) for _,_,fs in os.walk(OUT))
if not IMPRESSUM_READY:
    print("!! IMPRESSUM INCOMPLETE - do not deploy. Fill IMPRESSUM['street'] and ['city'] in build_site.py.")
print(f"built {n} files · {len(apps)} app pages · {len(QS)} question pages · {withiap} with in-app prices")
