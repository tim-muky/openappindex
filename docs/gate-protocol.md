# GO/NO-GO gate protocol — GAL-518

**Fix this document before running anything.** Its only purpose is to make the result
impossible to rationalise afterwards. If the thresholds are set after seeing the data, the
experiment is worthless — and a funder who asks "when did you decide what counted as
success?" will spot that immediately.

**Status:** thresholds and queries frozen as of 2026-08-21.

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

---

## 6. Publishing the result

Publish either outcome, with the raw records. A NO-GO published honestly, from a €0 experiment
that was designed to be falsifiable, is credible evidence to a funder that this project
measures things rather than asserting them. It is worth more than a quiet pivot.

If NO-GO: the fallback question is whether the index is useful to *people* even when assistants
ignore it — a different experiment, with different thresholds, decided fresh.
