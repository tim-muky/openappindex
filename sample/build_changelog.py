#!/usr/bin/env python3
"""
Weekly "what changed" — the diff between two dated snapshots, as data and as pages.

    python3 build_changelog.py data/public/snapshots/A.json data/public/snapshots/B.json
        Writes data/public/changelog/<ISO week of B>.json.

    (from build_site.py)  render_all(OUT)
        Renders /de/aenderungen/ (index of weeks), one page per week, and an
        Atom feed, from every JSON in data/public/changelog/.

Rules this page holds itself to (docs/manifesto, evidence rules):
  - dated facts only; every list states its sorting rule on the page
  - no selection: every change that meets a stated threshold appears, or none does
  - a missing value is "nicht erhoben" and is excluded from every count — never
    estimated, never zero
  - "nicht mehr gefunden" is what the read returned, not a statement about the app
  - no annualising of in-app prices; old -> new, both with their read date
  - corrections to our own data appear in the same list as the app facts
"""
import json, os, sys, glob, datetime
from site_common import (BASE, esc, app_slug, de_date, eur, write_page)

CL_DIR = "data/public/changelog"
CORR = "data/public/corrections.json"
NOTES_THRESHOLDS = (100, 400)   # release-note length bands, stated on the page
DORMANT_DAYS = 365              # an update after this long gets its own line

def iso_week(d):
    y, w, _ = datetime.date.fromisoformat(d).isocalendar()
    return f"{y}-W{w:02d}"

def _days(a, b):
    return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days

def _band(n):
    if n is None: return None
    if n == 0: return "keine"
    if n < NOTES_THRESHOLDS[0]: return f"unter {NOTES_THRESHOLDS[0]} Zeichen"
    if n < NOTES_THRESHOLDS[1]: return f"{NOTES_THRESHOLDS[0]}–{NOTES_THRESHOLDS[1]} Zeichen"
    return f"über {NOTES_THRESHOLDS[1]} Zeichen"

def diff(A, B):
    a, b = A["apps"], B["apps"]
    both_iap = A["collected"].get("in_app_purchases") and B["collected"].get("in_app_purchases")
    out = {"week": iso_week(B["read_at"]), "from": A["read_at"], "to": B["read_at"],
           "classifier": B.get("classifier"), "storefront": B.get("storefront"),
           "in_app_purchases_compared": bool(both_iap),
           "new": [], "gone": [], "updated": [], "price": [], "iap": [], "notes": [],
           "not_collected": {"apps_not_found_on_read": 0, "in_app_purchases_not_read": None},
           "corrections": []}
    def item(tid, r):
        return {"id": int(tid), "name": r["n"], "developer": r["dev"], "slug": app_slug(r["n"], tid)}
    for tid, r in b.items():
        if tid not in a:
            out["new"].append({**item(tid, r), "released": r.get("rel"), "version": r.get("v"), "updated": r.get("upd")})
            continue
        p = a[tid]
        if p.get("ok") and not r.get("ok"):
            out["gone"].append({**item(tid, p), "last_seen": p.get("read") or A["read_at"], "read_at": r.get("read") or B["read_at"]})
            continue
        if not r.get("ok"):
            continue
        if (p.get("v") != r.get("v") or p.get("upd") != r.get("upd")) and r.get("upd"):
            gap = _days(p["upd"], r["upd"]) if p.get("upd") else None
            out["updated"].append({**item(tid, r), "version_from": p.get("v"), "version_to": r.get("v"),
                                   "updated_from": p.get("upd"), "updated_to": r.get("upd"),
                                   "from_read": p.get("read") or A["read_at"], "to_read": r.get("read") or B["read_at"],
                                   "days_since_previous": gap})
        if p.get("price") != r.get("price") and r.get("price") is not None and p.get("price") is not None:
            out["price"].append({**item(tid, r), "from": p["price"], "to": r["price"],
                                 "from_read": p.get("read") or A["read_at"], "to_read": r.get("read") or B["read_at"]})
        if both_iap and p.get("iap_read") and r.get("iap_read") and \
           (p.get("iap_max") != r.get("iap_max") or p.get("iap_min") != r.get("iap_min") or p.get("iap_n") != r.get("iap_n")):
            out["iap"].append({**item(tid, r), "from": {"n": p["iap_n"], "min": p["iap_min"], "max": p["iap_max"], "read": p["iap_read"]},
                               "to": {"n": r["iap_n"], "min": r["iap_min"], "max": r["iap_max"], "read": r["iap_read"]}})
        if p.get("notes_len") is not None and r.get("notes_len") is not None and _band(p["notes_len"]) != _band(r["notes_len"]):
            out["notes"].append({**item(tid, r), "from": _band(p["notes_len"]), "to": _band(r["notes_len"]),
                                 "from_len": p["notes_len"], "to_len": r["notes_len"]})
    out["not_collected"]["apps_not_found_on_read"] = sum(1 for r in b.values() if not r.get("ok"))
    if B["collected"].get("in_app_purchases"):
        out["not_collected"]["in_app_purchases_not_read"] = sum(1 for r in b.values() if r.get("ok") and not r.get("iap_read"))
    if os.path.exists(CORR):
        out["corrections"] = [c for c in json.load(open(CORR, encoding="utf-8"))
                              if A["read_at"] < c["date"] <= B["read_at"]]
    out["new"].sort(key=lambda x: x.get("released") or "", reverse=True)
    out["gone"].sort(key=lambda x: x["name"].lower())
    out["updated"].sort(key=lambda x: (x.get("updated_to") or "", x["name"].lower()), reverse=True)
    out["price"].sort(key=lambda x: x["name"].lower())
    out["iap"].sort(key=lambda x: x["name"].lower())
    out["notes"].sort(key=lambda x: x["name"].lower())
    out["counts"] = {k: len(out[k]) for k in ("new", "gone", "updated", "price", "iap", "notes", "corrections")}
    out["apps_in_index"] = len(b)
    return out

# ---------------------------------------------------------------- rendering
def load_weeks():
    ws = []
    for f in sorted(glob.glob(f"{CL_DIR}/*.json")):
        ws.append(json.load(open(f, encoding="utf-8")))
    return sorted(ws, key=lambda w: w["to"], reverse=True)

# Set by build_site.py: trackId -> the slug the app page is actually served at. Slugs come
# from the name at first indexing; a renamed app keeps its URL, so a slug rebuilt from the
# new name would 404 (found 2026-10-07: galleybook and 70+ others).
SLUGS = {}

def _link(x):
    s = SLUGS.get(int(x["id"])) if SLUGS else x["slug"]
    if not s:                      # no page in the index for this app: name only, no dead link
        return esc(x["name"])
    return f"<a href='{BASE}/de/app/{esc(s)}/'>{esc(x['name'])}</a>"

def _section(title, rule, rows):
    if not rows:
        return ""
    return (f"<h2>{esc(title)}</h2><div class='rule'><strong>Sortierregel:</strong> {esc(rule)}</div>"
            f"<ol>{''.join(rows)}</ol>")

def _card(x, meta):
    return f"<li class='card'><h3>{_link(x)}</h3><p class='meta'>{meta}</p></li>"

def week_body(w, all_weeks):
    c = w["counts"]
    parts = [f"<nav class='bc'><a href='{BASE}/'>openAPPindex</a> › <a href='{BASE}/de/'>Deutschland</a> › "
             f"<a href='{BASE}/de/aenderungen/'>Änderungen</a> › {esc(w['week'])}</nav>",
             f"<h1>Was sich geändert hat: Woche {esc(w['week'])}</h1>",
             f"<p class='lede'>Vergleich zweier datierter Lesungen des Index: {de_date(w['from'])} und {de_date(w['to'])}. "
             f"{w['apps_in_index']} Apps im Index. Jede Zeile ist eine Tatsache aus öffentlichen Store-Daten mit Datum — "
             f"keine Bewertung.</p>"]
    summary = (f"<table><tbody>"
               f"<tr><th>Neu im Index</th><td>{c['new']}</td></tr>"
               f"<tr><th>Bei der Lesung nicht mehr gefunden</th><td>{c['gone']}</td></tr>"
               f"<tr><th>Neue Version veröffentlicht</th><td>{c['updated']}</td></tr>"
               f"<tr><th>Preisangabe im Store geändert</th><td>{c['price']}</td></tr>"
               f"<tr><th>In-App-Käufe geändert</th><td>{c['iap'] if w['in_app_purchases_compared'] else 'nicht verglichen — in einer der beiden Lesungen nicht erhoben'}</td></tr>"
               f"<tr><th>Umfang der Versionshinweise geändert</th><td>{c['notes']}</td></tr>"
               f"<tr><th>Korrekturen an unseren eigenen Daten</th><td>{c['corrections']}</td></tr>"
               f"</tbody></table>")
    parts.append(summary)
    if not any(c.values()):
        parts.append("<p>In dieser Woche hat sich bei keiner App im Index eine der erhobenen Angaben geändert.</p>")

    parts.append(_section("Neu im Index", "Nach Erstveröffentlichung im Store, neueste zuerst. Aufgenommen wird, was die veröffentlichte Abgrenzungsregel erfüllt — keine Auswahl.",
        [_card(x, f"{esc(x['developer'])} · Erstveröffentlichung {de_date(x.get('released'))} · Version {esc(x.get('version'))}, zuletzt aktualisiert {de_date(x.get('updated'))}") for x in w["new"]]))
    parts.append(_section("Bei der Lesung nicht mehr gefunden", "Alphabetisch. Die Lookup-Schnittstelle hat diese App am Lesetag nicht zurückgegeben. Das ist der Befund der Lesung, keine Aussage über die App.",
        [_card(x, f"{esc(x['developer'])} · zuletzt gefunden am {de_date(x['last_seen'])}, nicht gefunden am {de_date(x['read_at'])}") for x in w["gone"]]))
    upd_rows = []
    for x in w["updated"]:
        gap = x.get("days_since_previous")
        g = f" · {gap} Tage nach der vorherigen Version" if gap is not None else ""
        if gap is not None and gap >= DORMANT_DAYS:
            g = f" · <strong>{gap} Tage</strong> nach der vorherigen Version"
        upd_rows.append(_card(x, f"{esc(x['developer'])} · Version {esc(x['version_from'])} (Lesung {de_date(x['from_read'])}) → "
                                 f"{esc(x['version_to'])} (Lesung {de_date(x['to_read'])}) · veröffentlicht {de_date(x['updated_to'])}{g}"))
    parts.append(_section("Neue Version veröffentlicht", f"Nach dem von Apple veröffentlichten Datum der neuen Version, neueste zuerst. Liegt die vorherige Version mehr als {DORMANT_DAYS} Tage zurück, ist die Zahl hervorgehoben — es bleibt eine Zahl.", upd_rows))
    parts.append(_section("Preisangabe im Store geändert", "Alphabetisch. Die Preisangabe ist das Preiswort bzw. der Download-Preis, wie der Store ihn ausweist; beide Werte tragen das Datum ihrer Lesung.",
        [_card(x, f"{esc(x['developer'])} · „{esc(x['from'])}“ ({de_date(x['from_read'])}) → „{esc(x['to'])}“ ({de_date(x['to_read'])})") for x in w["price"]]))
    def _iap(s):
        if s["n"] == 0: return "keine In-App-Käufe ausgewiesen"
        if s["min"] is None: return f"{s['n']} In-App-Käufe, Preise nicht lesbar"
        return f"{s['n']} In-App-Käufe, {eur(s['min'])} bis {eur(s['max'])}"
    parts.append(_section("In-App-Käufe geändert", "Alphabetisch. Anzahl und Spanne der auf der Produktseite ausgewiesenen In-App-Käufe, jeweils mit Lesedatum. Einzelpreise, nie auf ein Jahr hochgerechnet.",
        [_card(x, f"{esc(x['developer'])} · {_iap(x['from'])} ({de_date(x['from']['read'])}) → {_iap(x['to'])} ({de_date(x['to']['read'])})") for x in w["iap"]]))
    parts.append(_section("Umfang der Versionshinweise geändert", f"Alphabetisch. Bänder: keine / unter {NOTES_THRESHOLDS[0]} Zeichen / {NOTES_THRESHOLDS[0]}–{NOTES_THRESHOLDS[1]} Zeichen / über {NOTES_THRESHOLDS[1]} Zeichen. Gemessen wird die Länge des Anbietertextes, nicht sein Inhalt.",
        [_card(x, f"{esc(x['developer'])} · {esc(x['from'])} ({x['from_len']}) → {esc(x['to'])} ({x['to_len']})") for x in w["notes"]]))
    if w["corrections"]:
        parts.append("<h2>Korrekturen an unseren eigenen Daten</h2><div class='rule'><strong>Sortierregel:</strong> Nach Datum. Jede Korrektur an Abgrenzung, Zählung oder Auslieferung wird hier ausgewiesen, im selben Verzeichnis wie die App-Fakten.</div><ol>"
                     + "".join(f"<li class='card'><h3>{esc(x['title'])}</h3><p class='meta'>{de_date(x['date'])} · {esc(x['summary'])} · <a href='{esc(x['url'])}'>Methode</a></p></li>" for x in w["corrections"])
                     + "</ol>")
    nc = w["not_collected"]
    nc_txt = f"{nc['apps_not_found_on_read']} Apps wurden bei der Lesung am {de_date(w['to'])} nicht gefunden und sind aus allen Zählungen oben ausgenommen."
    if nc.get("in_app_purchases_not_read") is not None:
        nc_txt += f" Für {nc['in_app_purchases_not_read']} Apps wurde die Produktseite nicht gelesen; ihre In-App-Käufe gelten als nicht erhoben."
    if not w["in_app_purchases_compared"]:
        nc_txt += " In-App-Käufe wurden in dieser Woche nicht verglichen, weil sie in mindestens einer der beiden Lesungen nicht erhoben wurden."
    parts.append(f"<h2>Nicht erhoben</h2><p>{nc_txt} Geschätzt wird nichts.</p>")
    others = [x for x in all_weeks if x["week"] != w["week"]]
    if others:
        parts.append("<h2>Weitere Wochen</h2><ol>" + "".join(
            f"<li class='card'><h3><a href='{BASE}/de/aenderungen/{esc(x['week'])}/'>Woche {esc(x['week'])}</a></h3>"
            f"<p class='meta'>{de_date(x['from'])} → {de_date(x['to'])}</p></li>" for x in others[:8]) + "</ol>")
    parts.append(f"<p class='src'>Quelle: iTunes Lookup API und Produktseiten im App Store, Storefront Deutschland. "
                 f"Lesungen am {w['from']} und {w['to']}. Abgrenzung {esc(w.get('classifier') or '')}. "
                 f"Rohdaten: <a href='https://github.com/tim-muky/openappindex/tree/main/sample/data/public/changelog'>changelog/{esc(w['week'])}.json</a>.</p>")
    return "\n".join(parts)

def render_all(out_dir):
    weeks = load_weeks()
    if not weeks:
        return []
    for w in weeks:
        ld = json.dumps({"@context": "https://schema.org", "@type": "WebPage",
                         "name": f"Was sich geändert hat: Woche {w['week']}",
                         "datePublished": w["to"], "dateModified": w["to"], "inLanguage": "de",
                         "isPartOf": {"@type": "WebSite", "name": "openAPPindex", "url": BASE},
                         "url": f"{BASE}/de/aenderungen/{w['week']}/"}, ensure_ascii=False)
        c = w["counts"]
        desc = (f"Änderungen im Index zwischen {de_date(w['from'])} und {de_date(w['to'])}: {c['new']} neu, "
                f"{c['updated']} neue Versionen, {c['price']} Preisänderungen, {c['gone']} nicht mehr gefunden. "
                f"Datierte Store-Fakten, keine Bewertung.")
        write_page(out_dir, f"de/aenderungen/{w['week']}/index.html",
                   f"Was sich geändert hat: Woche {w['week']} | openAPPindex", desc, week_body(w, weeks),
                   f'<script type="application/ld+json">{ld}</script>')
    idx = (f"<nav class='bc'><a href='{BASE}/'>openAPPindex</a> › <a href='{BASE}/de/'>Deutschland</a> › Änderungen</nav>"
           f"<h1>Was sich im Index geändert hat</h1>"
           f"<p class='lede'>Wöchentlicher Vergleich zweier datierter Lesungen: neue Apps, neue Versionen, geänderte Preise, "
           f"nicht mehr gefundene Apps — und Korrekturen an unseren eigenen Daten.</p>"
           f"<div class='rule'><strong>Sortierregel:</strong> Nach Woche, neueste zuerst. Jede Woche listet jede Änderung, "
           f"die eine auf der Seite genannte Schwelle erfüllt — es gibt keine Auswahl.</div><ol>"
           + "".join(f"<li class='card'><h3><a href='{BASE}/de/aenderungen/{esc(w['week'])}/'>Woche {esc(w['week'])}</a></h3>"
                     f"<p class='meta'>{de_date(w['from'])} → {de_date(w['to'])} · {w['counts']['new']} neu · "
                     f"{w['counts']['updated']} neue Versionen · {w['counts']['price']} Preisänderungen · "
                     f"{w['counts']['gone']} nicht mehr gefunden · {w['counts']['corrections']} Korrekturen</p></li>" for w in weeks)
           + f"</ol><p class='src'>Feed: <a href='{BASE}/de/aenderungen/feed.xml'>feed.xml</a> (Atom).</p>")
    write_page(out_dir, "de/aenderungen/index.html", "Was sich im Index geändert hat | openAPPindex",
               "Wöchentliche, datierte Änderungen im openAPPindex: neue Apps, neue Versionen, Preisänderungen, Korrekturen.", idx)
    # Atom feed — a distribution channel that needs no account and gives crawlers a revisit signal
    fd = os.path.join(out_dir, "de/aenderungen/feed.xml")
    with open(fd, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">\n')
        f.write(f"<title>openAPPindex — was sich geändert hat</title>\n<id>{BASE}/de/aenderungen/</id>\n")
        f.write(f"<link href='{BASE}/de/aenderungen/'/>\n<link rel='self' href='{BASE}/de/aenderungen/feed.xml'/>\n")
        f.write(f"<updated>{weeks[0]['to']}T00:00:00Z</updated>\n<author><name>openAPPindex</name></author>\n")
        for w in weeks:
            c = w["counts"]
            f.write(f"<entry><title>Woche {esc(w['week'])}: {c['new']} neu, {c['updated']} neue Versionen, {c['price']} Preisänderungen</title>\n"
                    f"<id>{BASE}/de/aenderungen/{w['week']}/</id><link href='{BASE}/de/aenderungen/{w['week']}/'/>\n"
                    f"<updated>{w['to']}T00:00:00Z</updated><published>{w['to']}T00:00:00Z</published>\n"
                    f"<summary>Vergleich der Lesungen vom {w['from']} und {w['to']}: {c['new']} neu im Index, "
                    f"{c['gone']} nicht mehr gefunden, {c['updated']} neue Versionen, {c['price']} Preisänderungen, "
                    f"{c['corrections']} Korrekturen. Datierte Store-Fakten, keine Bewertung.</summary></entry>\n")
        f.write("</feed>\n")
    return weeks

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    A = json.load(open(sys.argv[1], encoding="utf-8"))
    B = json.load(open(sys.argv[2], encoding="utf-8"))
    if A["read_at"] >= B["read_at"]:
        sys.exit("A must be the earlier snapshot")
    d = diff(A, B)
    os.makedirs(CL_DIR, exist_ok=True)
    out = f"{CL_DIR}/{d['week']}.json"
    json.dump(d, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{out}: {d['counts']} · not collected: {d['not_collected']}")
