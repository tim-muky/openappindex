#!/usr/bin/env python3
"""
Shared pieces of the served site: the page shell, formatting helpers, slugs.

build_site.py owns the index; build_changelog.py renders the weekly change
pages. Both must produce the same shell, the same slugs and the same German
date formatting, so those live here and nowhere else. This module has no side
effects on import (build_site.py wipes the output directory on import, which is
why it cannot be imported by anything).
"""
import re, html, datetime, os, unicodedata

BASE = "https://openappindex.org"
NOW = datetime.datetime.now(datetime.timezone.utc)

def esc(s): return html.escape(s or "", quote=True)

def slug(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = s.replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s or "app")[:60]

def app_slug(name, track_id):
    return f"{slug(name)}-{track_id}"

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

def write_page(out_dir, path, title, desc, body, ld=""):
    full = os.path.join(out_dir, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    canon = BASE + "/" + path.replace("index.html", "")
    open(full, "w", encoding="utf-8").write(SHELL.format(
        title=esc(title), desc=esc(desc), canon=esc(canon), body=body, ld=ld, base=BASE))
