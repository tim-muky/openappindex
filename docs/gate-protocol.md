# GO/NO-GO gate protocol — GAL-518

**Fix this document before running anything.** Its only purpose is to make the result
impossible to rationalise afterwards. If the thresholds are set after seeing the data, the
experiment is worthless — and a funder who asks "when did you decide what counted as
success?" will spot that immediately.

**Status:** thresholds and queries frozen as of 2026-08-21. Amended 2026-08-23 (query
weighting), twice on 2026-08-31 (the index changed: snippets/structured data, then ten
non-cooking apps removed), on 2026-09-11 (a false price corrected in the served index) and on
2026-09-23 (the second category published in the repository) — all dated, all before scoring.
A standing write-up of where each leg stands is kept in `gate-result.md`; this document holds
the frozen thresholds and is authoritative where the two differ.

**AMENDED 2026-08-23, with reason, before any post-launch run.** The baseline (19 responses,
see `openappindex-assistant-baseline-report.md`) showed the query set was mis-weighted:

- **Lookups are already well served.** ChatGPT answered single-app questions correctly from
  apps.apple.com — Kitchen Stories €7.99/€79.99 exact, Mein Rezeptebuch v1.6 8 March 2025
  exact. We will not be cited for questions Apple's own page already answers.
- **Enumeration is where every assistant failed.** Asked which apps are stale or expensive,
  both told the user to check manually or returned apps that do not exist in the market.

Therefore the **scored set is re-weighted toward enumeration**: group C (entity lookups) drops
from 3 queries to 1, and two enumeration queries are added to group A. The *wording* of every
retained query is unchanged, so baseline and post-launch runs stay comparable — only the
weighting of what counts toward the GO threshold changes.

The GO/NO-GO thresholds themselves are **unchanged**. This amendment was made before any
post-launch data existed; had it been made afterwards it would have invalidated the experiment.

**AMENDED 2026-08-31 — the index itself changed mid-window, recorded before scoring.**

Search Console data for 2026-08-23→29 (192 impressions, 3 clicks, 65 distinct pages) showed two
things worth fixing: the app pages were ranking for cost queries at around position 9 and never
being clicked, because the title answered a maintenance question while the query asked what the
app costs; and the JSON-LD emitted `price: "0"` for every free-to-download app, including apps
with in-app purchases up to €49.99 — the exact claim this index exists to correct, in the one
layer machines actually read.

Both were changed on **2026-08-31**: titles and descriptions now lead with the measured in-app
price range, and free-with-IAP apps emit an `AggregateOffer` spanning the download price to the
highest measured in-app purchase. Source lines were corrected at the same time to carry each
app's recorded read date instead of the build date.

**Queries, thresholds and scoring are unchanged.** The baseline is unaffected — it measures
unaided assistants and never depended on what this site serves.

**What it changes is attribution, and only in one direction.** The machine-readable layer is
better than it was when the indexing clock started on 2026-08-24, so:

- a **GO** is weaker evidence than a clean run would have given: it cannot be separated from
  "the structured data got better on 2026-08-31";
- a **NO-GO** is *stronger* evidence, because it would mean assistants ignored the index in its
  improved form.

Record the date of every citation against this change. A citation dated before 2026-08-31 tests
the original pages; one after tests these.

**AMENDED 2026-08-31 (second amendment this date) — ten non-cooking apps removed from the served index.**

The v4 precision rules (`sample/precision_check.py`, written for the hop-2 closure finds) were
run against the served corpus and found ten entries that pass the keyword classifier but are
not cooking apps: nine press products — cooking-magazine ePapers, among them Landlust,
ZauberTopf Magazine and kochen & genießen — and one kids-franchise game filed under Education.
Nine of the ten carried in-app purchases (magazine subscriptions), so they sat inside the
published price figures, not just the page count. This is the same class of error as the
pharmacy contamination, and it was corrected the same way: removed, recomputed, published.

Removed from the site on **2026-08-31** (941 app pages, sitemap 716 → 707). Every affected
figure was recomputed on the corrected basis and the landing page, method page and README
updated: 951 → 941 apps; free-listed with in-app purchases 706 of 916 → **697 of 907 — the
headline stays 77%**; median highest in-app price €39.99 and maximum €599.99 unchanged. The
recall figure (81%, 579 of 715) keeps its dated 19–21 Aug basis: the per-app search-result
lists were not retained, so it cannot be recomputed, and the method page already shows the
finding held at 81–83% across three classifier boundaries. The correction is published on the
method page, dated.

**Attribution: same direction as the first amendment, now slightly stronger.** The index an
assistant sees from today is again better than the one the indexing clock started on — and ten
URLs that were live for a week are now 404. A GO remains the weaker reading; a NO-GO remains
the stronger one. The two same-day changes share one date, so citation dating against
2026-08-31 covers both.

**Enumeration ground truth:** `sample/data/gate_ground_truth.json` was frozen 2026-08-25 on the
951-app basis. Before scoring F16/F17, check whether any of the ten removed apps appear in it
and re-derive those answers on the 941 basis if so — noting the re-derivation, not silently.

---

## What is being tested

Whether search-augmented assistants **fetch and cite an independent app index** when answering
real DACH recipe-app questions — and whether their answers get factually better as a result.

Not being tested (deliberately, per the minimal-gate scope): review-derived claims, enrichment
quality, MCP tool-calling. Those come after a GO.

---

## 1. Preconditions — check before the result means anything

The single biggest way this experiment fails for the wrong reason is that **the pages were
never indexed**. A zero-citation result from an uncrawled site says nothing about the thesis.
Do not score the gate until all four are true:

- [ ] Site live at openappindex.org with a complete Impressum
- [ ] `sitemap.xml` submitted to Google Search Console and Bing Webmaster Tools, and both
      report it as read
- [ ] `site:openappindex.org` returns **≥ 100 pages in Google** and **≥ 100 in Bing**
- [ ] At least 14 days elapsed since submission

If the indexation checks fail, the result is **INCONCLUSIVE — CRAWLING**, not NO-GO. Fix the
crawling problem and restart the clock. Record which precondition failed.

**Precondition status, checked 2026-08-31.** Google is indexing: Search Console reports
impressions from **2026-08-25**, one day after submission, across 65 distinct pages — 192
impressions and 3 clicks in the first week, concentrated on German cost queries. Bing is not:
`site:openappindex.org` returned nothing in Bing or in DuckDuckGo (Bing-backed) on 2026-08-31,
seven days after submission. The ≥ 100-pages-in-**both** check is therefore **not met**, and the
authoritative counts — Search Console's Indexing → Pages report and Bing Webmaster Tools — are
still outstanding. On today's evidence the gate would score **INCONCLUSIVE — CRAWLING**, which
is why the Bing side is the thing to fix first.

**Precondition observation added 2026-09-09 — Brave Search.** Claude's web search retrieves
via Brave Search, which the preconditions above never monitored: they check Google and Bing
only, so one of the three scored assistants runs on an index this protocol was not watching.
Checked 2026-09-09: `site:openappindex.org` on search.brave.com returns **zero results**
("too few matches"), and Bing likewise still returns no pages, 16 days after sitemap
submission — while Bingbot-user-agent fetches of every tested URL return HTTP 200, so nothing
on our side blocks the crawler. Recorded as a precondition observation only; queries,
thresholds and scoring are unchanged. It sharpens the attribution note: a zero-citation
result from Claude cannot be separated from Brave never having indexed the site, exactly as
a zero from ChatGPT cannot be separated from Bing's empty index. Same date, recorded for the
crawl clock: the sitemap's 710 URLs were submitted via IndexNow (HTTP 200, logged in
`sample/data/indexnow_log.json`) — a crawl-visibility step, not a change to what the index
serves.

**Precondition observation added 2026-09-09 (later same day) — authoritative Bing count.** Bing
Webmaster Tools was verified for the domain today, so the count the entries above kept deferring
to "outstanding" is now read directly: BWT **Site Explorer reports 1 indexed URL** (the
homepage; last crawled 2026-09-02, discovered 2026-08-21), 0 errors, 0 excluded. This
supersedes the `site:` probe as the authoritative Bing-side signal and confirms the Bing leg
sits at **1 of the required ≥100 — INCONCLUSIVE — CRAWLING** — unchanged since 2026-09-07. The
crawl pipeline underneath is healthy and active: sitemap read 2026-09-07 (710 URLs, status
Success) and Bingbot fetching normally. This is ordinary indexation lag on a new domain, not a
serving fault. Precondition observation only; queries, thresholds and scoring unchanged.

**2026-09-11 — the 09-09 reading above was wrong, and the gate date is moved.** Bing held at 1
indexed URL across four checks (09-07, 09-09, 09-10, 09-11) and Brave at 0. BWT URL Inspection
was then run per URL, and it contradicts the "ordinary indexation lag" characterisation recorded
on 09-09: a representative app page and a question page both return **"Discovered but not
crawled — URL cannot appear on Bing"** (discovered 2026-09-01). That verdict rules out the two
explanations that mattered. It is **not** a content-quality rejection — Bing has never fetched
the pages, so it cannot have judged them thin or duplicative, and the near-identical-app-page
worry does not apply. It is **not** technical — `www` 308-redirects to the apex, the canonical
is self-referential, Bingbot receives HTTP 200 on app and question pages alike, and BWT reports
0 errors and 0 excluded. What remains is **crawl-budget starvation**, which on a new domain is
largely trust allocation. Waiting would not have fixed it.

**Decision, same date: the crawl clock is extended and the ~2026-09-15 gate date is dropped.**
Scoring on the 15th would have returned INCONCLUSIVE — CRAWLING on the ChatGPT (Bing) and Claude
(Brave) legs, which §1 already provides for: fix the crawling problem and restart the clock.
Indexation is re-assessed ~2026-09-29, with a backstop of **2026-10-13** — score what is
testable then and report the rest as INCONCLUSIVE — CRAWLING, leaving margin before the funding
deadlines. **Queries, thresholds and scoring are unchanged; this moves only the clock, and it is
recorded before any post-launch data has been seen.**

**Action taken 2026-09-11 — 16 URLs explicitly requested for indexing** through BWT URL
Inspection: the four question pages, and twelve app pages chosen from the frozen ground truth
rather than by hand — the ten highest published in-app purchases (the F17 answer set, headed by
Cooksy at €599.99) and two of the oldest unmaintained apps (the F16 answer set). All returned
"URL submitted successfully". The daily request quota is 100 URLs, so this is a lever at scale.
Like the IndexNow submission, it is a crawl-visibility step: no page content changed and the
freeze is untouched. If these URLs index, the blocker was budget; if Bing still declines after
an explicit request, the constraint is authority and that is a different problem.

**Two limitations found while doing it, recorded because they qualify figures published
elsewhere.** First, the app pages returned *two* states, not one: most read "Discovered but not
crawled", but one URL present in the submitted `sitemap.xml` read **"Not discovered — the
inspected URL is not known to Bing"**. So the Sitemaps report's "710 URLs discovered" does not
mean all 710 entered Bing's discovery set; discovery is partial, and any claim about how much of
this index an engine has seen must rest on per-URL inspection rather than that figure. Second,
the submitted sitemap includes an app page only where in-app purchases were captured, which
excludes most of the 96 stale apps — the evidence base for F16. The F16 answer remains served
through the question page, so the enumeration stays answerable, but the per-app evidence behind
it is not separately indexable. Both are recorded, not changed: the sitemap inclusion rule is
frozen with the rest of the index until the gate closes.

**AMENDED 2026-09-11 (fourth amendment) — a false price was corrected in the served index.**

An audit of the machine-readable layer found that every app page published a **fabricated
download price**. `build_site.py` read a numeric `price` field that Apple's Search API does not
return for this corpus — no record of 1,312 carries it — and a `or 0` fallback silently
substituted `0.00`. For the 919 free apps the value was coincidentally right. For **22 paid
apps it was false**: the visible page correctly said, for example, `5,99 €`, while the JSON-LD
in the same document announced `"price": "0.00"`. That is the precise failure this index exists
to expose — "free" asserted for an app that charges — and it stood in the one layer we do not
read ourselves. It is also the same defect class as the 2026-08-31 amendment, which fixed the
free-with-in-app-purchase case and left the paid-download case behind.

The download price is now read from the store's own price string. Where no store price was
captured, **no number is emitted at all** rather than a default — nothing is estimated to fill a
gap. All 941 app pages were regenerated and checked: no published price now contradicts its own
page. The correction is published and dated on the method page.

**Attribution: the same direction as every previous amendment.** The index an assistant sees
from today is more accurate than the one the indexing clock started on, so a **GO** remains the
weaker reading — it cannot be separated from "the data got more accurate on 2026-09-11" — and a
**NO-GO** remains the stronger one. Queries, thresholds and scoring are unchanged. This is
recorded before any post-launch data has been seen, and before the gate is scored.

A correction is not an improvement withheld by the freeze: leaving a known false price in the
served index while asking anyone to trust the evidence rules would cost more than the amendment
does.

**Precondition observation added 2026-09-22 — the explicit indexing requests did not move Bing.**
Read directly from Bing Webmaster Tools, eleven days after the sixteen URLs were requested on
09-11 and one week before the ~09-29 re-assessment. Site Explorer still reports **1 indexed
URL** (the homepage; last crawled 2026-09-11, HTTP 304), 0 errors, 0 warnings, 0 excluded, and
Search Performance shows 0 impressions and 0 clicks across the whole window — unchanged since
09-07. Three of the sixteen requested URLs were re-inspected, chosen to cover each kind of page
in the request: the F17 head (Cooksy, discovered 09-04), one of the four question pages
(discovered 09-04) and one F16 app page (Das Kochfieber-Kochbuch, discovered **09-11**). All
three read **"Discovered but not crawled — URL cannot appear on Bing."** The Kochfieber date is
the request date: that page sits in the submitted sitemap but had never entered Bing's discovery
set until it was requested by hand, which confirms the partial-discovery limitation recorded on
09-11 — and it then stalled at the same point as every other page.

**By the criterion set on 09-11, this is the authority reading, not the budget one.** The
request path works — it creates a discovery record — and Bing still declined to fetch a single
one of the sixteen in eleven days. The pipeline underneath is healthy and the counts rule out
a serving fault: the sitemap was re-read on **2026-09-19** (status Success, 710 URLs), and BWT's
IndexNow report lists four submissions received (709, ~1.4K, 710 and 710 URLs on 09-01, 09-02,
09-09 and 09-11) with no errors. Nothing on this side is blocking the crawl; Bing is choosing
not to spend it here.

**Brave, checked the same day:** `site:openappindex.org` on search.brave.com still returns
"Too few matches were found" — 0 pages, unchanged since 09-09.

**Method note, recorded because it qualifies any future `site:` figure.** The public Bing
result page is not a usable instrument from this machine: with the `site:` operator it returned
decoy results to both a browser session and a plain HTTP fetch, and a control query
(`site:github.com openappindex`) came back as furniture listings. This is anti-automation
serving, not an index reading. The 09-09 entry already made BWT the authoritative Bing-side
signal; today's observation is why the `site:` probe should not be cited for Bing at all.

**What this leaves for the ~09-29 re-assessment.** Both non-Google legs stand exactly where the
09-11 decision left them, and nothing observed today suggests either will cross ≥100 pages by
09-29 or by the 10-13 backstop through waiting alone. On today's evidence the ChatGPT (Bing) and
Claude (Brave) legs score **INCONCLUSIVE — CRAWLING** at both dates; the Google leg was not read
today (Search Console) and stays outstanding. Whether to spend the remaining weeks on
crawl-visibility steps or to score on the backstop as planned is the re-assessment's decision,
not today's. No visibility-affecting step was taken today; queries, thresholds and scoring are
unchanged.

**Precondition observation added 2026-09-23 — the Google leg clears ≥100, and the homepage is
not in the index.** Read from Search Console (report last updated 09-18), the day after the
Bing reading above. **647 pages indexed**, against the ≥100 the preconditions require — so the
Google side of the third check is met, the first leg to meet it. The sitemap was last read
2026-09-15 (Success, 710 URLs discovered). Search performance over the whole window since
launch: 5 web-search clicks.

**75 pages are not indexed, in four groups, and one of them is the homepage.** Three are 404s —
Landlust, ZauberTopf Magazine and Rezepte pur ePaper, three of the ten press products removed on
2026-08-31, behaving exactly as that amendment intended. 51 are "Discovered – currently not
indexed" and 17 "Crawled – currently not indexed", both ordinary for a young domain of this
size. The remaining four are **"Excluded by 'noindex' tag" — and all four are the same page**:
the homepage in its four protocol/host variants (`http`/`https` × apex/`www`), last crawled
21–22 August. URL Inspection on the apex reads "Indexing allowed? **No: 'noindex' detected in
'robots' meta tag**", from the crawl of **22 August 2026**.

**The tag is gone and has been for some time; the verdict is stale.** Checked the same day: the
live homepage serves no `robots` meta tag and no `X-Robots-Tag` header, `robots.txt` allows all
agents, the `www` and `http` variants 308-redirect to the apex, and the canonical is
self-referential. Search Console's own live test returns **"URL is available to Google — Page
can be indexed."** The tag never existed in this repository — `git log -S noindex` across all
history returns nothing — so it was a pre-launch host-level state, not something the build
emitted. What has kept the homepage out since is that **Googlebot has not re-crawled it in a
month** while crawling 647 other pages, so the 22-August verdict still stands in the index.

**This is a confound and it must be written into the result.** For the entire indexing
window the index's front door — the page carrying the headline figures and the links to the
method page, the manifesto and the working paper — has been absent from Google, the one engine
that crawled this site properly. Any assistant that reaches the web through Google therefore
found nothing at the domain root to cite, whatever it would have done with the page.
*(Corrected 2026-09-23 — this paragraph first read "the Google-backed leg", which is wrong;
see the correction below. None of the three scored assistants retrieves through Google.)*
Unlike the amendments recorded above, this one does **not** cut in the direction that makes a
NO-GO stronger; it weakens a NO-GO on this leg specifically, and it applies to the whole window
rather than from a dated change onward. The per-app and question pages are unaffected — those
647 are indexed and are what the scored queries actually target — so the gate remains
scoreable; the qualification attaches to the homepage and to any claim that rests on an
assistant reaching the site through its root.

**Action taken 2026-09-23, recorded as a visibility step.** Indexing was requested for
`https://openappindex.org/` through URL Inspection ("URL was added to a priority crawl queue"),
and "Validate fix" was started on the noindex issue, which asks Google to re-check all four
variants (**validation started 2026-09-23**). No page content changed and the freeze is
untouched — this is the same class of step as the 09-09 IndexNow submission and the 09-11 Bing
requests. Whether the homepage returns to the index before the ~09-29 re-assessment is itself
evidence: Google has crawled 647 pages here, so unlike the Bing case there is no question of
whether it is willing to fetch from this domain.

**Standing after both readings.** Google 647 ✓, Bing 1 ✗, Brave 0 ✗ — the precondition requires
≥100 in Google **and** Bing, so it is still not met and the gate does not yet score. The ChatGPT
(Bing) and Claude (Brave) legs remain **INCONCLUSIVE — CRAWLING**. Queries, thresholds and
scoring are unchanged. *(This paragraph originally continued "the Google-backed leg is genuinely
testable at the 10-13 backstop"; that clause was wrong and is corrected below, dated
2026-09-23.)*

**CORRECTION 2026-09-23 — "the Google-backed leg" was wrong, and the preconditions monitor the
wrong indexes.** The observation recorded yesterday twice referred to a "Google-backed leg" that
would be testable at the backstop. There is no such leg. The three scored assistants are
Perplexity, ChatGPT (search mode) and Claude (web search on); **none of them retrieves
through Google.** ChatGPT searches through Bing and Claude through Brave, both recorded on
09-09, and Perplexity operates its own crawler and index, which this protocol has never named
or monitored.
The two sentences are struck above rather than deleted, per the rule this project applies to
every other error it has published.

**The mis-specification is older than the sentence, and it is the more important half.** The
precondition at the top of §1 requires "≥ 100 pages in Google **and** ≥ 100 in Bing". Those are
the two indexes the gate has measured since 08-21 — but Google feeds none of the three scored
assistants, and the indexes that do feed them are Bing (one leg), Brave (one leg, added as an
observation only on 09-09) and Perplexity's own (never checked at all). So the 647-page Google
result, which yesterday's entry treated as the first leg to clear the bar, clears a bar that no
scored assistant stands behind. The gate has been watching the wrong instrument for a month.
This is recorded as a fault in the protocol, not repaired by rewriting it: the preconditions
stay frozen in their original wording, and the scoring writes up each leg against the index
that actually serves it.

**Precondition finding, same date — the index IS in Perplexity's retrieval set.** Probed with a
deliberately **non-protocol** entity query ("openAPPindex Rezept-Apps Index"), so the 18 frozen
queries stay uncontaminated; the full record is
`sample/data/public/perplexity_retrieval_probe_20260923.json`. Perplexity reported
"Gesucht, Inhalt abgerufen", cited 10 sources, and among them **three of ours**: the
homepage, the GitHub
repository, and one of the four question
pages
(`/de/frage/rezept-app-ohne-abo-und-ohne-in-app-kaeufe.html`). It reproduced the recall finding
(81%, 579 of 715), the 14% single-query coverage, the €39.99 median and the €599.99 maximum,
all correct against the served index.

**So the third leg is not blocked — it is live, and it was never blocked.** Note what this
costs the neat version of the story: the homepage Perplexity retrieved is the same page Google
has excluded as `noindex` since 22 August. An engine running its own crawler reached content
that the engine with 647 of our pages does not hold. The barrier recorded on 09-11 and 09-22 is
real for Bing and Brave and it is **not** universal — which makes it a statement about how
particular engines allocate crawl to a new domain, not about the open web as such. Any write-up
must say so.

**One figure came back stale, and it is the one we corrected.** Perplexity told the probe that
**706 of 916** free-listed apps charge through in-app purchases. The served index has published
**697 of 907** since 2026-08-31, when ten press products were removed; both `README.md` and the
landing page carried the old pair until commit `573263c` that day and neither carries it now. No
live page serves 706 of 916 today. Perplexity's copy of us therefore predates the correction by
at least 23 days, and the number it attributes to us is precisely the number we published a
dated correction to retract.

**That is a finding this project should publish against itself.** The index exists because
stale and wrong facts about apps propagate unchecked; here an assistant propagated *our*
superseded figure, sourced to us, three weeks after we corrected it. An open index that
publishes errata has no mechanism to pull a retracted number out of an assistant's cache, and a
correction notice written for human readers ("697 of 907 **instead of** 706 of 916") is a
machine-readable statement of the wrong number sitting next to the right one. It also sharpens
§4's "hollow GO": being cited is not the finding, being cited *currently* is. What to do about
it — dated JSON-LD on corrections, a machine-readable errata feed, `dateModified` discipline —
is design work for after the gate, recorded here so the observation is not lost.

**What this does to the gate.** It does not score it and it does not end it. The Perplexity leg
now has a met precondition in substance, so the 15 scored queries can be run against it and
produce a real GO / WEAK / NO-GO for that leg — which is the experiment this protocol was
written for, and it has been runnable for longer than we knew. The entity probe above is
explicitly *not* evidence for that: group D was de-weighted on 08-23 because assistants already
answer entity lookups, and naming the project in the query is the easiest case there is.
Whether Perplexity cites the index for "Welche Rezept-App wird noch aktiv gepflegt?" is
unmeasured. Queries, thresholds and scoring are unchanged.

**AMENDED 2026-09-23 (fifth amendment) — the second category is published in the repository,
and the repository is a cited surface.**

The sleep/meditation measurement has been under embargo since 2026-09-01 under a rule that tied
publication to the gate closing on 2026-09-15 — a date dropped on 09-11. The embargo has
therefore had no end condition for twelve days. It is lifted today by dated decision: the
finding is published as `docs/second-category-findings.md` and as §6 of
`docs/working-paper.md`, with the abstract and the "one category" limitation rewritten to match.

**This is recorded as an amendment because the repository is not a neutral surface.** The
retrieval probe run the same day found Perplexity citing `github.com/tim-muky/openappindex`
alongside two openappindex.org pages. Publishing here therefore changes something at least one
scored assistant reads, and the change cannot be treated as invisible to the experiment merely
because it is not on the served domain.

**What did and did not change.** The served index — openappindex.org — is **unchanged**: no app
page, question page, figure or claim on the site has moved, and the 3,578 sleep apps are **not**
deployed as pages. That restraint is deliberate and not only about the freeze: adding several
thousand near-identical app pages to a domain that Bing is already declining to crawl is the
most reliable way to convert a crawl-budget problem into a content-quality one. What changed is
the repository's documentation.

**Attribution.** The direction is the familiar one: an assistant reading the repository from
today sees a stronger evidence base than the one the indexing clock started on, so a **GO**
becomes the weaker reading and a **NO-GO** the stronger. Any citation must be dated against
2026-09-23 as well as against 2026-08-31. Queries, thresholds and scoring are unchanged, and
this is recorded before the Perplexity leg — the one leg that can still be scored — has been
run.

**Two figures were corrected in the course of publishing, before anything was served.** The
September draft gave the largest single in-app purchase as €999.99 (it is **€1,199.99**) and the
cooking free-listed share as 92% (it is **96%**, 907 of 941). Both were caught by recomputing
every headline from the raw data rather than trusting the draft, both are published in the
findings document itself, and neither changed a headline. They are noted here because the draft
existed inside the embargo, and an embargo is not a reason for an error to go unrecorded once
lifted.

**Decision 2026-09-23 — how run 2 is conditioned, recorded before run 2 exists.** The
retrieval probe run this morning put "openAPPindex" into the scored account's Perplexity
search history before run 1's queries, and the sidebar that history renders also produced a
false-positive citation detection (both recorded in `gate-result.md` §5a). The obvious remedy —
run 2 on a clean, logged-out session — was considered and **rejected as the default**, for a
reason worth stating:

**It would trade a known confound for an unknown one.** The 2026-08-23 baseline was captured
logged-in, and its own caveats say so ("an anonymous visitor may see different results").
§4's
secondary measures — freshness, cost accuracy, recall — are all comparisons *against that
baseline*. An anonymous run 2 would not be condition-matched to it, so any movement in those
measures could not be attributed to the index rather than to the session change. The history
confound, by contrast, has a known sign: it can only bias *toward* citing us.

**So the rule adopted is conditional, and it is fixed now rather than after seeing results.**
Run 2 is captured **logged-in**, matching the baseline. **Any scored query that cites
openappindex.org — in either run — is then re-tested on a clean, logged-out session, and the
citation counts toward the §4 threshold only if it survives that re-test.** A query that cites
us logged-in but not clean is recorded as a history-assisted citation and reported separately,
never in the headline count.

This costs nothing while the result stands at zero, which it does after eight queries, and it
places the expensive clean-session work exactly where rigour is needed. It also leaves the
asymmetry honest: the confound cannot manufacture a NO-GO, only a GO, and the GO path is the
one that now carries the extra check.

Queries, thresholds and scoring are unchanged. What is fixed here is a capture condition and an
evidentiary rule for citations, both set before the citations they govern exist.

---

## 2. The query set (frozen)

15 target queries plus 3 controls. German, because the index is German and the market is DACH.

### A. Maintenance — the question no store answers
1. `Welche Rezept-App wird noch aktiv gepflegt?`
2. `Rezept-App die noch Updates bekommt`
3. `Ist Mein Rezeptebuch noch aktuell?`
4. `Welche Koch-Apps wurden seit Jahren nicht aktualisiert?`

### B. True cost — the second question no store answers
5. `Rezept-App ohne Abo`
6. `Rezepte-App einmalig bezahlen statt Abo`
7. `Was kostet Chefkoch wirklich?`
8. `Kostenlose Rezept-App ohne versteckte Kosten`
9. `Welche Rezept-Apps haben teure In-App-Käufe?`

### C. Discovery — where the store's recall failure bites
10. `App zum Speichern von Rezepten von Webseiten`
11. `Beste App um eigene Rezepte zu verwalten`
12. `Rezepte sammeln App Deutschland`

### D. Entity — direct lookups *(de-weighted 2026-08-23 — assistants already handle these)*
13. `KptnCook Kosten In-App-Käufe`
~~14. `Kitchen Stories Abo Preis`~~ — retired: ChatGPT answered exactly correctly at baseline
~~15. `galleybook App`~~ — retired: contaminated by that app's own listing change

### F. Enumeration — added 2026-08-23, where every assistant failed at baseline
16. `Liste von Rezept-Apps die seit über zwei Jahren kein Update bekommen haben`
17. `Welche Rezept-App im deutschen App Store hat den teuersten In-App-Kauf?`

### E. Controls — openAPPindex should NOT be cited for these
- `Rezept für Lasagne`
- `Wie lange muss ein Ei kochen?`
- `Chefkoch Rezept Käsekuchen`

A citation on a control query is a **negative** result: it means the index is being retrieved
for questions it has no business answering, which damages trust and would need fixing before
any launch.

---

## 3. Baseline — capture BEFORE the site is indexed

**This is time-critical and cannot be reconstructed later.** Once the pages are live and
crawled, the unaided answer is gone forever.

For each of the 18 queries, on **Perplexity**, **ChatGPT (search mode)** and **Claude (web
search on)**, record:

| Field | |
|---|---|
| Query | verbatim |
| Assistant + date | |
| Answer | full text, verbatim |
| Sources cited | every URL |
| Apps named | list |
| Maintenance claim | did it say anything about updates/upkeep? correct? |
| Cost claim | did it state a price? correct against our data? |

Store as `sample/data/gate_baseline.json`. The factual-accuracy columns matter as much as the
citations: if the unaided assistants are already *wrong* about maintenance and cost — and our
data says the store itself is misleading on both — that is the strongest possible argument for
the index, independent of whether we get cited.

---

## 4. Scoring — thresholds frozen in advance

Re-run the identical 18 queries after the preconditions pass. Score:

### Primary — citation
**openappindex.org appears as a cited source** in the assistant's answer.

| Result | Threshold |
|---|---|
| **GO** | cited on **≥ 3 of 15** target queries, by **≥ 1** assistant, **AND** at least one cited fact is one only we publish (a last-updated date or a real in-app price) |
| **WEAK — EXTEND** | cited on 1–2 of 15. Indexing lag is a known confound at this age. Extend 4 weeks, re-test once, then score again with the same thresholds. |
| **NO-GO** | **0 citations** across all three assistants, with preconditions passed and ≥ 6 weeks live |

### Secondary — did the answer get better?
For each query where we were cited, compare against baseline:
- **Freshness:** does the answer now reflect the current version date?
- **Cost accuracy:** does it now state the real in-app price rather than "free"?
- **Recall:** does it name any app the baseline answer did not — particularly one absent from
  Apple's own search results?

A GO on citations with **no** improvement on any of these three is a **hollow GO**: we became a
source without being a better one. Record it as such; it changes what to build next.

### Tertiary — recorded, not scored
Time-to-first-citation. Which assistant first. Which page type got cited (question page vs app
page) — this decides where to invest next.

---

## 5. Honest confounds to write into the result

- **`galleybook App` (query 15) is contaminated.** Its ASO fix (GAL-534) ships around the same
  time, so any change is not attributable to this index. Report it separately; never in the
  headline number.
- **n = 15 is small.** A single citation moves the rate by 6.7 points. Report counts, not
  percentages.
- **Assistants are non-deterministic.** Run each query twice, on different days, and record
  both. Count a citation if it appears in either run — but say so.
- **We cannot separate "assistants don't cite small indexes" from "assistants don't cite
  *this* index yet."** A NO-GO at six weeks is evidence about this attempt, not a law.
- **The index changed on 2026-08-31**, after the baseline and after indexing began — see the
  amendment at the top. Any citation must be dated against that change, and a GO cannot be
  reported as though the pages had been in their improved form throughout.

---

## 6. Publishing the result

Publish either outcome, with the raw records. A NO-GO published honestly, from a €0 experiment
that was designed to be falsifiable, is credible evidence to a funder that this project
measures things rather than asserting them. It is worth more than a quiet pivot.

If NO-GO: the fallback question is whether the index is useful to *people* even when assistants
ignore it — a different experiment, with different thresholds, decided fresh.
