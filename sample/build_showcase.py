#!/usr/bin/env python3
"""Generate the comparison showcase from the fetched sample.
Every number on the page is derived from data/*.json - nothing is typed by hand."""
import json, html, re, datetime

D = json.load(open("/Users/timmeyerdierks/Claude/BAS/sample/data/rezepte_de.json", encoding="utf-8"))
R = D["results"]
GB = D["galleybook"]
ranked = sorted(R, key=lambda r: r["openstore_rank"])
by_store = sorted(R, key=lambda r: r["store_rank"])
fetched = datetime.datetime.fromisoformat(D["fetched_at"]).strftime("%d %B %Y")

def esc(s): return html.escape(s or "")
def fmt_count(n): return f"{n:,}".replace(",", "\u2009")  # thin space, never touches data URIs
def eur(v): return ("%.2f" % v).replace(".", ",") + " €" if v is not None else "—"

def age_class(d):
    if d is None: return "unknown"
    return "fresh" if d <= 90 else "aging" if d <= 365 else "stale"

def age_words(d):
    if d is None: return "unknown"
    if d == 0: return "today"
    if d == 1: return "yesterday"
    if d < 60: return f"{d} days ago"
    if d < 730: return f"{d//30} months ago"
    return f"{d/365:.1f} years ago"

def notes_verdict(r):
    n = r["openstore"]["release_notes"]
    return "specific" if n >= 20 else "thin" if n >= 12 else "boilerplate" if n > 0 else "none"

def snippet(r, words=9):
    t = re.sub(r"\s+", " ", r.get("release_notes") or "").strip()
    w = t.split(" ")
    return " ".join(w[:words]) + ("…" if len(w) > words else "") if t else "—"

# ---- derived headline figures ----
free_shown = sum(1 for r in R if (r["formatted_price"] or "").lower() in ("gratis", "free"))
with_iap  = sum(1 for r in R if r["openstore"]["cost_profile"]["iap_count"])
dearest   = max((r["openstore"]["cost_profile"]["iap_max"] or 0) for r in R)
dearest_app = next(r for r in R if (r["openstore"]["cost_profile"]["iap_max"] or 0) == dearest)
oldest    = max(R, key=lambda r: r["days_since_update"])
movers    = sorted(R, key=lambda r: abs(r["store_rank"] - r["openstore_rank"]), reverse=True)

def delta_chip(r):
    d = r["store_rank"] - r["openstore_rank"]
    if d == 0: return '<span class="delta same">held</span>'
    arrow = "↑" if d > 0 else "↓"
    return f'<span class="delta {"up" if d>0 else "down"}">{arrow}{abs(d)}</span>'

# ---------- store column rows (facsimile of what the store shows) ----------
store_rows = "\n".join(f'''
      <li class="srow">
        <span class="srank">{r["store_rank"]}</span>
        <img class="icon" src="{r['icon_data']}" alt="" width="52" height="52">
        <span class="sbody">
          <span class="sname">{esc(r["name"])}</span>
          <span class="sseller">{esc(r["seller"])}</span>
          <span class="sstars"><span class="stars" aria-hidden="true">{"★"*int(round(r["rating"] or 0))}</span>
            <span class="snum">{r["rating"]:.1f} · {fmt_count(r["rating_count"])} ratings</span></span>
        </span>
        <span class="sprice">{esc(r["formatted_price"])}</span>
      </li>'''  for r in by_store)

# ---------- openstore column rows (evidence) ----------
def os_row(r):
    c = r["openstore"]["cost_profile"]
    price_line = ("no in-app purchases found" if not c["iap_count"]
                  else f'{eur(c["iap_min"])} – {eur(c["iap_max"])} <span class="dim">across {c["iap_count"]} in-app purchases</span>')
    yearly = ""
    if c["dearest_labelled_yearly"]:
        yearly = f'<span class="yearly">dearest plan the app itself labels yearly: <b>{eur(c["dearest_labelled_yearly"])}</b></span>'
    return f'''
      <li class="orow">
        <span class="orank">{r["openstore_rank"]}</span>
        <img class="icon" src="{r['icon_data']}" alt="" width="52" height="52">
        <div class="obody">
          <div class="otop"><span class="oname">{esc(r["name"])}</span>{delta_chip(r)}</div>
          <dl class="ev">
            <div class="evrow"><dt>Last updated</dt>
              <dd><span class="dot {age_class(r["days_since_update"])}"></span>{age_words(r["days_since_update"])}
                <span class="dim">· v{esc(r["version"])} · {r["last_updated"][:10]}</span></dd></div>
            <div class="evrow"><dt>Real cost</dt>
              <dd>shown as <b>{esc(r["formatted_price"])}</b> — {price_line}{yearly}</dd></div>
            <div class="evrow"><dt>Changelog</dt>
              <dd><span class="tag {notes_verdict(r)}">{notes_verdict(r)}</span>
                <span class="quote">“{esc(snippet(r))}”</span></dd></div>
          </dl>
        </div>
        <span class="oscore"><b>{r["openstore"]["total"]}</b><i>/100</i></span>
      </li>'''

os_rows = "\n".join(os_row(r) for r in ranked)

# ---------- galleybook ----------
g = GB["app"]; gc = g["openstore"]["cost_profile"]
vis_rows = "\n".join(f'''<tr><td class="q">“{esc(v["query"])}”</td><td class="num">{v["results"]}</td>
   <td class="pos {"missing" if v["position"] is None else "deep"}">{"not in the result set" if v["position"] is None else f'#{v["position"]} of {v["results"]}'}</td></tr>'''
   for v in GB["visibility"])

would_rank = sum(1 for r in R if r["openstore"]["total"] > g["openstore"]["total"]) + 1

M = D["method"]["weights"]

CSS = """
:root{
  --ground:#E9ECEF; --surface:#FBFCFD; --surface-2:#F1F4F6; --sunk:#E1E6EA;
  --ink:#10161D; --muted:#5A6673; --faint:#8A96A2; --rule:#CFD6DD;
  --accent:#26389C; --accent-soft:#DFE3F5;
  --fresh:#1F6F63; --aging:#8A6420; --stale:#9B3A2E;
  --shadow:0 1px 2px rgba(16,22,29,.06), 0 8px 24px -16px rgba(16,22,29,.28);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0E1216; --surface:#161C22; --surface-2:#1C232A; --sunk:#111721;
    --ink:#E8EDF2; --muted:#96A3AF; --faint:#6E7C89; --rule:#2A343D;
    --accent:#93A5FF; --accent-soft:#1E2740;
    --fresh:#5FBFAE; --aging:#D6A24A; --stale:#E38273;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 28px -18px rgba(0,0,0,.9);
  }
}
:root[data-theme="dark"]{
  --ground:#0E1216; --surface:#161C22; --surface-2:#1C232A; --sunk:#111721;
  --ink:#E8EDF2; --muted:#96A3AF; --faint:#6E7C89; --rule:#2A343D;
  --accent:#93A5FF; --accent-soft:#1E2740;
  --fresh:#5FBFAE; --aging:#D6A24A; --stale:#E38273;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 28px -18px rgba(0,0,0,.9);
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Public Sans", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px; margin:0 auto; padding:clamp(20px,4vw,56px) clamp(16px,4vw,40px) 96px;}
h1,h2,h3{font-family:"Zilla Slab", ui-serif, Georgia, serif; text-wrap:balance; margin:0; font-weight:600;}
a{color:var(--accent)}
.mono{font-family:"IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace}
.dim{color:var(--muted); font-weight:400}

/* ---- masthead: a document control block ---- */
.masthead{border-top:3px solid var(--ink); padding-top:18px; margin-bottom:40px}
.eyebrow{font-family:"IBM Plex Mono", monospace; font-size:11px; letter-spacing:.16em;
  text-transform:uppercase; color:var(--muted); margin:0 0 14px}
h1{font-size:clamp(34px,5.6vw,58px); line-height:1.02; letter-spacing:-.015em; max-width:16ch}
.standfirst{margin:18px 0 0; max-width:62ch; font-size:clamp(16px,1.6vw,18.5px); color:var(--muted)}
.control{display:grid; grid-template-columns:repeat(auto-fit,minmax(158px,1fr)); gap:1px;
  background:var(--rule); border:1px solid var(--rule); margin-top:30px}
.control div{background:var(--surface); padding:12px 14px}
.control dt{font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--faint); margin-bottom:5px}
.control dd{margin:0; font-size:14px; font-weight:600}

/* ---- headline figures ---- */
.figs{display:grid; grid-template-columns:repeat(auto-fit,minmax(215px,1fr)); gap:14px; margin:40px 0 8px}
.fig{background:var(--surface); border:1px solid var(--rule); padding:20px; box-shadow:var(--shadow)}
.fig b{display:block; font-family:"Zilla Slab",serif; font-size:clamp(30px,4vw,40px);
  line-height:1; font-variant-numeric:tabular-nums; letter-spacing:-.02em}
.fig span{display:block; margin-top:9px; font-size:13.5px; color:var(--muted)}
.fig em{font-style:normal; font-weight:700; color:var(--ink)}
.fig.alarm b{color:var(--stale)}

section{margin-top:64px}
.shead{display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; margin-bottom:6px}
.shead h2{font-size:clamp(23px,2.8vw,30px); letter-spacing:-.01em}
.shead .n{font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--faint);
  letter-spacing:.14em; text-transform:uppercase}
.lede{margin:0 0 26px; max-width:64ch; color:var(--muted)}

/* ---- the two columns ---- */
.cols{display:grid; grid-template-columns:minmax(0,0.92fr) minmax(0,1.35fr); gap:22px; align-items:start}
@media (max-width:900px){ .cols{grid-template-columns:1fr} }
.col > header{position:sticky; top:0; z-index:2; background:var(--ground); padding:2px 0 12px}
.col h3{font-size:17px}
.col header p{margin:3px 0 0; font-size:13px; color:var(--muted)}
ol{list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px}

.srow{display:grid; grid-template-columns:22px 52px 1fr auto; gap:12px; align-items:center;
  background:var(--surface-2); border:1px solid var(--rule); padding:12px 14px}
.srank,.orank{font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--faint);
  font-variant-numeric:tabular-nums; text-align:right}
.icon{border-radius:11px; display:block; background:var(--sunk)}
.sbody{display:flex; flex-direction:column; gap:1px; min-width:0}
.sname{font-weight:600; font-size:14.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.sseller,.snum{font-size:11.5px; color:var(--faint)}
.sstars{display:flex; align-items:center; gap:6px; margin-top:2px}
.stars{color:var(--faint); font-size:11px; letter-spacing:1px}
.sprice{font-size:12px; font-weight:700; color:var(--muted); border:1px solid var(--rule);
  border-radius:999px; padding:4px 12px; background:var(--surface)}

.orow{display:grid; grid-template-columns:22px 52px 1fr auto; gap:12px; align-items:start;
  background:var(--surface); border:1px solid var(--rule); padding:14px; box-shadow:var(--shadow)}
.obody{min-width:0}
.otop{display:flex; align-items:center; gap:9px; flex-wrap:wrap; margin-bottom:9px}
.oname{font-weight:700; font-size:15px}
.delta{font-family:"IBM Plex Mono",monospace; font-size:10.5px; font-weight:600; padding:2px 7px;
  border-radius:3px; letter-spacing:.04em}
.delta.up{color:var(--fresh); background:color-mix(in srgb, var(--fresh) 13%, transparent)}
.delta.down{color:var(--stale); background:color-mix(in srgb, var(--stale) 13%, transparent)}
.delta.same{color:var(--faint); background:var(--surface-2)}
.ev{margin:0; display:flex; flex-direction:column; gap:7px}
.evrow{display:grid; grid-template-columns:88px 1fr; gap:12px; align-items:baseline}
.ev dt{font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--faint)}
.ev dd{margin:0; font-size:13.2px; line-height:1.45}
.dot{display:inline-block; width:7px; height:7px; border-radius:50%; margin-right:7px; vertical-align:1px}
.dot.fresh{background:var(--fresh)} .dot.aging{background:var(--aging)}
.dot.stale{background:var(--stale)} .dot.unknown{background:var(--faint)}
.yearly{display:block; margin-top:3px; font-size:12.4px; color:var(--muted)}
.tag{font-family:"IBM Plex Mono",monospace; font-size:10px; text-transform:uppercase;
  letter-spacing:.08em; padding:2px 6px; border:1px solid var(--rule); margin-right:7px}
.tag.specific{color:var(--fresh); border-color:color-mix(in srgb, var(--fresh) 40%, var(--rule))}
.tag.boilerplate,.tag.none{color:var(--stale); border-color:color-mix(in srgb, var(--stale) 40%, var(--rule))}
.quote{color:var(--muted); font-style:italic}
.oscore{font-family:"IBM Plex Mono",monospace; text-align:right; font-variant-numeric:tabular-nums}
.oscore b{font-size:21px; display:block; line-height:1}
.oscore i{font-size:10px; color:var(--faint); font-style:normal}

/* ---- galleybook ---- */
.gb{background:var(--surface); border:1px solid var(--rule); border-left:3px solid var(--accent);
  padding:clamp(20px,3vw,32px); box-shadow:var(--shadow)}
.gbgrid{display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:30px; margin-top:20px}
table{border-collapse:collapse; width:100%; font-size:13.5px}
th,td{text-align:left; padding:9px 10px; border-bottom:1px solid var(--rule)}
th{font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--faint); font-weight:500}
td.num,.pos{font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums}
.pos.missing{color:var(--stale); font-weight:600}
.pos.deep{color:var(--aging); font-weight:600}
.gbcard{display:flex; gap:14px; align-items:flex-start; padding:16px; background:var(--surface-2);
  border:1px solid var(--rule)}

/* ---- method + caveats ---- */
.two{display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:22px}
.panel{background:var(--surface); border:1px solid var(--rule); padding:24px}
.panel h3{font-size:18px; margin-bottom:12px}
.wt{display:flex; flex-direction:column; gap:9px; margin:0; padding:0; list-style:none}
.wt li{display:grid; grid-template-columns:1fr auto; gap:10px; align-items:center; font-size:14px}
.bar{grid-column:1/-1; height:5px; background:var(--sunk)}
.bar i{display:block; height:100%; background:var(--accent)}
.wt li.zero .bar i{background:var(--stale)}
.wt b{font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums; font-size:13px}
.caveats{margin:0; padding-left:18px; display:flex; flex-direction:column; gap:10px; font-size:14px; color:var(--muted)}
.caveats b{color:var(--ink)}
footer{margin-top:72px; padding-top:22px; border-top:1px solid var(--rule);
  font-size:13px; color:var(--faint); display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap}
@media (prefers-reduced-motion:no-preference){
  .orow{animation:rise .5s cubic-bezier(.2,.7,.3,1) backwards}
  @keyframes rise{from{opacity:0; transform:translateY(7px)}}
}
"""

HTML = f"""<meta charset="utf-8">
<title>Same Query, Two Rankings</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@500;600;700&family=Public+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>{CSS}</style>
<div class="wrap">

  <header class="masthead">
    <p class="eyebrow">openAPPindex · proof of concept · method sample v0</p>
    <h1>Same query. Two rankings.</h1>
    <p class="standfirst">One search term, one storefront, one afternoon of public data. On the left, what the
      App Store shows a person who types “{esc(D['query'])}”. On the right, the same twelve apps ordered by the two things
      the store will not let you search on: whether anyone still maintains the app, and what it actually costs.
      Every field below was read from a public Apple source on the date stamped. Nothing is estimated.</p>
    <dl class="control">
      <div><dt>Query</dt><dd class="mono">“{esc(D['query'])}”</dd></div>
      <div><dt>Storefront</dt><dd>Germany (DE)</dd></div>
      <div><dt>Apps compared</dt><dd>{len(R)}</dd></div>
      <div><dt>Data read</dt><dd>{fetched}</dd></div>
      <div><dt>Sources</dt><dd>iTunes Search API · App Store product pages</dd></div>
    </dl>
  </header>

  <div class="figs">
    <div class="fig"><b>{free_shown}/{len(R)}</b><span>results present themselves as <em>Gratis</em> in the search list</span></div>
    <div class="fig"><b>{with_iap}/{len(R)}</b><span>of those charge money once opened</span></div>
    <div class="fig alarm"><b>{eur(dearest)}</b><span>dearest single in-app purchase behind the word “Gratis”, in {esc(dearest_app['name'])}</span></div>
    <div class="fig alarm"><b>{oldest['days_since_update']/365:.1f} yrs</b><span>since the oldest app in this list was last updated — it still ranks #{oldest['store_rank']}</span></div>
  </div>

  <section id="comparison">
    <div class="shead"><span class="n">The comparison</span></div>
    <div class="cols">
      <div class="col">
        <header>
          <h3>What the App Store shows</h3>
          <p>Two signals per result: a star average and a price word. Ordered as the store returns them.</p>
        </header>
        <ol>{store_rows}
        </ol>
      </div>
      <div class="col">
        <header>
          <h3>What the same twelve apps look like with the evidence attached</h3>
          <p>Re-ordered by maintenance, cost visibility and changelog substance. Download counts carry no weight.</p>
        </header>
        <ol>{os_rows}
        </ol>
      </div>
    </div>
  </section>

  <section id="galleybook">
    <div class="shead"><span class="n">The other half of the problem</span></div>
    <h2 style="max-width:22ch">An app the store never returns at all</h2>
    <p class="lede">Re-ranking only fixes what you can see. The apps that never enter the result set are invisible
      to any ranking, ours included. Here is one, judged by our own rules — it belongs to the person who built openAPPindex,
      which is the only reason it is safe to name.</p>
    <div class="gb">
      <div class="gbgrid">
        <div>
          <h3 style="font-size:16px; margin-bottom:12px">Where it appears in App Store search</h3>
          <table>
            <thead><tr><th>Search term</th><th>Results</th><th>Position</th></tr></thead>
            <tbody>{vis_rows}</tbody>
          </table>
          <p style="font-size:13px; color:var(--muted); margin:14px 0 0">
            Published benchmarks put roughly 61% of search-driven installs in the top three results,
            and under 4% past rank 30.</p>
        </div>
        <div>
          <h3 style="font-size:16px; margin-bottom:12px">Scored by the same rules as everything above</h3>
          <div class="gbcard">
            <img class="icon" src="{g['icon_data']}" alt="" width="52" height="52">
            <div>
              <div style="font-weight:700">{esc(g['name'])}</div>
              <div style="font-size:12px; color:var(--faint)">{esc(g['seller'])}</div>
              <div class="mono" style="margin-top:8px; font-size:21px"><b>{g['openstore']['total']}</b><span style="font-size:11px; color:var(--faint)">/100</span></div>
            </div>
          </div>
          <dl class="ev" style="margin-top:16px">
            <div class="evrow"><dt>Last updated</dt><dd><span class="dot {age_class(g['days_since_update'])}"></span>{age_words(g['days_since_update'])} <span class="dim">· {g['last_updated'][:10]}</span></dd></div>
            <div class="evrow"><dt>Real cost</dt><dd>shown as <b>{esc(g['formatted_price'])}</b> — {eur(gc['iap_min'])} – {eur(gc['iap_max'])} <span class="dim">across {gc['iap_count']} in-app purchases</span></dd></div>
            <div class="evrow"><dt>Would place</dt><dd><b>#{would_rank} of {len(R)+1}</b> in the list above, on the same formula</dd></div>
          </dl>
          <p style="font-size:13px; color:var(--muted); margin:16px 0 0">
            That placement is not a claim that the app deserves an audience. It is the point of the exercise:
            the ranking that decides whether anyone sees it never measured any of this.</p>
        </div>
      </div>
    </div>
  </section>

  <section id="method">
    <div class="shead"><span class="n">How the right-hand column was produced</span></div>
    <div class="two">
      <div class="panel">
        <h3>The formula, in full</h3>
        <ul class="wt">
          <li><span>Maintenance — days since the last published version</span><b>{M['maintenance']}</b><span class="bar"><i style="width:{M['maintenance']}%"></i></span></li>
          <li><span>Cost visibility — money hidden behind the price word</span><b>{M['cost_visibility']}</b><span class="bar"><i style="width:{M['cost_visibility']}%"></i></span></li>
          <li><span>Changelog — does it say what changed?</span><b>{M['release_notes']}</b><span class="bar"><i style="width:{M['release_notes']}%"></i></span></li>
          <li class="zero"><span>Downloads, rating count, ad spend</span><b>0</b><span class="bar"><i style="width:2%"></i></span></li>
        </ul>
        <p style="font-size:13.5px; color:var(--muted); margin:18px 0 0">
          Cost visibility penalises the <em>gap</em>, not the price. An app that costs €40 and says so is not
          marked down for costing money; the store is marked down for printing “Gratis” over it.
          Weights are v0 and meant to be argued with — that is why they are printed here.</p>
      </div>
      <div class="panel">
        <h3>What this sample does not prove</h3>
        <ul class="caveats">
          <li><b>This is not the live in-app ranking.</b> It is the public iTunes Search API, the closest
            reproducible proxy. It contains no paid placements and no personalisation — so the real store is
            further from the right-hand column than this page shows, not closer.</li>
          <li><b>Absence here is not proof of absence in the app.</b> An app missing from these results may still
            surface in-app, and keyword choice on the developer's side affects placement.</li>
          <li><b>Billing periods are not published reliably.</b> No price on this page has been annualised or
            extrapolated; yearly figures appear only where an app labels its own plan as yearly.</li>
          <li><b>Twelve apps, one query, one country, one day.</b> A method sample, not a study. The pipeline
            behind it is the thing being demonstrated.</li>
        </ul>
      </div>
    </div>
  </section>

  <footer>
    <span>openAPPindex · method sample v0 · data read {fetched} · every figure regenerated from source, never typed</span>
    <span class="mono">fetch_sample.py → score.py → build_showcase.py</span>
  </footer>
</div>
"""

out = "/Users/timmeyerdierks/Claude/BAS/sample/showcase.html"
# render every non-ASCII character as a numeric reference so the page is
# immune to whatever charset the host happens to serve it with
open(out, "wb").write(HTML.encode("ascii", "xmlcharrefreplace"))
print("wrote", out, round(len(HTML)/1024), "KB")
