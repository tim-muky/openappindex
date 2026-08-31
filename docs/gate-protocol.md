# GO/NO-GO gate protocol — GAL-518

**Fix this document before running anything.** Its only purpose is to make the result
impossible to rationalise afterwards. If the thresholds are set after seeing the data, the
experiment is worthless — and a funder who asks "when did you decide what counted as
success?" will spot that immediately.

**Status:** thresholds and queries frozen as of 2026-08-21. Amended 2026-08-23 (query
weighting) and twice on 2026-08-31 (the index changed: snippets/structured data, then ten
non-cooking apps removed) — all dated, all before scoring.

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
