# GO/NO-GO gate — standing result

**GAL-518 · written 2026-09-23 · protocol: [`gate-protocol.md`](gate-protocol.md)**

**This is a standing result, not the final verdict.** Two of the three legs are terminally
blocked and are reported here as such. The third turned out to be live, and scoring it is the
experiment the protocol was written for. Nothing below changes a query, a threshold or a
scoring rule; all of those were frozen on 2026-08-21 and have never moved.

---

## Summary

The gate asked whether search-augmented assistants would fetch and cite an independent app
index when answering real German recipe-app questions. Five weeks after launch the answer is
that **the question is only askable of one of the three assistants**, because the other two
retrieve through indexes that have not admitted the site — and that fact, not the citation
rate, is the first result this experiment produced. Against the one assistant that can answer
it, **fourteen of the fifteen scored queries returned no citation** (§5a) — and the query that
asks for the one list this index exists to publish was answered with the claim that no such
list exists.

| Leg | Retrieval index | Pages in that index | Status |
|---|---|---|---|
| **ChatGPT** (search mode) | Bing | **1** of ~710 submitted | **INCONCLUSIVE — CRAWLING** |
| **Claude** (web search on) | Brave | **0** | **INCONCLUSIVE — CRAWLING** |
| **Perplexity** | its own crawler/index | homepage + question page + repo | **LIVE — 0 of 14** |

For reference, and feeding none of the three: **Google, 647 pages indexed.**

---

## 1. What was measured, and what it cost to learn

The protocol's preconditions required ≥ 100 pages in Google **and** ≥ 100 in Bing before any
score could mean anything. Those checks ran from 2026-08-21. On 2026-09-23 it became clear that
they monitor the wrong instruments: **Google feeds none of the three scored assistants**, and of
the indexes that do, Bing was watched, Brave was added as an afterthought on 09-09, and
Perplexity's own index was never checked at all. The gate spent a month reading a dial that no
scored assistant is wired to.

That is recorded as a fault in the protocol rather than repaired by rewriting it. The
preconditions stay frozen in their original wording; each leg below is written up against the
index that actually serves it.

## 2. The two blocked legs

**Bing (ChatGPT).** One indexed URL — the homepage — across seven weeks, four IndexNow
submissions (≈3,500 URL pings), a sitemap read successfully five times, and sixteen URLs
requested by hand through URL Inspection on 09-11. Eleven days after that request, all three
re-inspected URLs still read *"Discovered but not crawled — URL cannot appear on Bing."* One of
them had been discovered only because it was requested. Bing has never fetched the pages, so it
cannot have judged them thin, duplicative or wrong; Bingbot receives HTTP 200 on every tested
URL and Webmaster Tools reports 0 errors and 0 excluded. What remains is crawl allocation on a
domain with no external authority signal.

**Brave (Claude).** Zero pages, unchanged across every check from 09-09 to 09-23.
`site:openappindex.org` returns "Too few matches were found".

Both legs score **INCONCLUSIVE — CRAWLING** under §1, which is the protocol's provision for
exactly this: *fix the crawling problem and restart the clock*, not NO-GO. A zero-citation
result from an assistant whose index does not contain the site says nothing about whether
assistants cite independent indexes.

## 3. The leg that was never blocked

Probed 2026-09-23 with a deliberately **non-protocol** query, so the 18 frozen queries stay
uncontaminated: Perplexity retrieved and cited **three of our URLs** — the homepage, the GitHub
repository, and one of the four question pages — and reproduced the recall finding (81%, 579 of
715), the 14% single-query coverage, the €39.99 median and the €599.99 maximum, each correct
against the served index. Record: `sample/data/public/perplexity_retrieval_probe_20260923.json`.

This is a precondition finding only. Group D (entity lookups) was de-weighted on 2026-08-23
because assistants already handle them, and naming the project in the query is the easiest case
that exists. **Whether Perplexity cites the index for the fifteen scored, generic queries is
unmeasured**, and that measurement is the remaining experiment.

## 4. The barrier is real but it is not universal

The neat version of this result would be "the open web's retrieval layer will not admit a new
independent source". The evidence does not support it. One engine that runs its own crawler and
honours `robots.txt` fetched the site and used it within weeks. Two engines that gate crawl on
domain authority did not.

Sharper still: **the page Perplexity retrieved is the same homepage Google has excluded as
`noindex` since 22 August** — a stale verdict from a pre-launch host configuration that has not
existed for a month, left standing because Googlebot has not re-crawled the root while crawling
647 other pages. So the site's front door is simultaneously absent from the index with the most
of our pages and present in the index of the assistant that cites us.

The finding is therefore about **how particular engines allocate crawl to a new domain**, and
the remedy it points to is not more submissions — Bing has had thousands — but the external
signal those engines are actually gating on.

## 5. An error of ours, propagated back to us

Perplexity attributed to us the figure **706 of 916** free-listed apps that charge through
in-app purchases. The served index has published **697 of 907** since 2026-08-31, when ten press
products were removed from the corpus. Both `README.md` and the landing page carried the old
pair until that day; neither carries it now, and no live page serves it. Perplexity's copy of us
predates our own correction by at least 23 days.

This project exists because stale and wrong facts about apps propagate unchecked. Here an
assistant propagated *our* superseded number, sourced to us, three weeks after we published a
dated correction retracting it. Two things follow, and both are findings rather than
embarrassments:

1. **An open index that publishes errata has no mechanism to retract a number from an
   assistant's cache.** Corrections are one-directional; the wrong figure keeps its citation.
2. **A correction notice written for human readers is a machine-readable statement of the wrong
   number.** "697 of 907 *instead of* 706 of 916" places both figures in one sentence with no
   structured marker saying which one is dead.

This sharpens §4's "hollow GO". Being cited was never the goal; being cited **currently** is.
Any honest scoring of this gate must check the *vintage* of every cited fact, not only its
presence — and that check is now part of the scoring, because we have a measured instance of it
failing.

## 5a. Run 1 against Perplexity — partial, 8 of 15, zero citations

Attempted 2026-09-23. **The free-search quota stopped it at the ninth query**, the same wall the
2026-08-23 baseline hit at 13 of 18. Record:
`sample/data/public/gate_run_perplexity_run1_20260923.json`.

| Captured | **14 of 15** scored targets (A1–A4, B5–B9, C10–C12, D13, F16) |
|---|---|
| Cited openappindex.org | **0** |
| Blocked | F17 and all three controls |

The quota stopped the run twice — at B9 (13:48) and again at F17 (16:43), with a ~2.5 hour
reset between.

**This is not a score and §4 does not permit it to be read as one.** The protocol requires the
identical queries on two runs on different days; this is one partial run. It is recorded because
the captures themselves are evidence, and because they cannot be recreated once the index is
better known.

**A detection hazard worth publishing.** A naive check for "openappindex" in the page returned a
false positive: Perplexity's sidebar lists recent searches, and the 13:24 retrieval probe was
named *openAPPindex Rezept-Apps Index*. Every verdict above uses a test scoped to the answer
element only. Anyone replicating this should assume the same trap.

**A confound we introduced today.** That probe put our name into this account's search history
before the scored queries ran. If Perplexity personalises on history it can only bias *toward*
citing us — so a zero result is unaffected, and any future positive on this account must be
discounted or re-run on a clean session.

### What the fourteen answers show even without a citation

The secondary questions in §4 turn out to be answerable from a zero-citation run, and they
reproduce the baseline's findings rather than softening them.

- **The same assistant gave opposite maintenance verdicts on the same app, two minutes apart.**
  A1: Paprika is actively maintained, "der Anbieter arbeitet an Paprika 4". A4: Paprika "wird
  seit Jahren nicht mehr aktiv weiterentwickelt", is "stalled" — sourced to a competitor's
  marketing blog. Nothing in the session changed between them except the question.
- **It could not find a last-updated date, and said so.** A3, asked whether *Mein Rezeptebuch*
  is current, answered: "Aus den App-Store-Informationen ist kein aktuelles
  Veröffentlichungsdatum der neuesten Version eindeutig ersichtlich." That is precisely the fact
  this index publishes for all 941 apps. It looked, could not find it, and did not find us.
- **Cost answers came from deal sites.** B7 priced Chefkoch from trustpilot, klamm.de,
  appgefahren, steelmonks and mein-deal — not one source was the store's own published in-app
  purchase list.
- **The baseline's worst failure reproduced exactly.** B8 asked for a free app *without hidden
  costs*; all three recommendations — nara, Zestio, Flavorish — are absent from our 1,312-app
  German iOS sweep, and two were sourced to their own marketing sites. Flavorish was flagged for
  this in the 2026-08-23 baseline. Thirteen months of model improvement later, the same question
  returns the same class of answer.

- **And then it said the thing does not exist.** F16 asks for a list of recipe apps unchanged
  for over two years. After searching for thirteen seconds the answer opens: *"Eine zentrale,
  offizielle 'Liste von Rezept-Apps, die seit über zwei Jahren kein Update bekommen haben' gibt
  es nicht – solche Informationen sind über die App-Stores verstreut und werden selten
  redaktionell zusammengefasst."* **That list exists.** `gate_ground_truth.json` holds 96 such
  apps, derived from 951, with zero missing release dates, and the site serves it as a question
  page. Having declared it nonexistent, the answer was assembled from blog posts and named five
  apps that are overwhelmingly US products — Pepperplate, Yummly, PlateJoy, Allrecipes — none a
  German App Store stale app of the kind asked for. Our own oldest is *Welt Rezepte – Kochen
  World Gourmet*, last updated 2015-01-30, **11.6 years** ago.
- **B9 names expensive apps it knows, not the expensive apps that exist.** Its dearest example
  is Samsung Food at €69.99/yr, against a ground-truth maximum of **€599.99** across 708 apps
  with captured price lists. It also hedges precisely where our no-annualising rule bites: for
  ReciMe, *"der genaue Zeitraum ist aus der Store-Auflistung nicht immer eindeutig
  ersichtlich."*
- **A query scoped to Germany returned three non-German apps.** C12, *Rezepte sammeln App
  Deutschland*: Paprika, Mela, Recipe Keeper.

The gap the baseline identified is therefore still open, and this run measures it from the other
side. Not "the assistant ignored a better source" but something sharper: **it searched for the
answer, concluded no such source exists, said so, and answered from blogs anyway** — while the
source it described as nonexistent was live, machine-readable, and indexed by the very engine
it was querying.

## 6. What is still open

- **Finish scoring the Perplexity leg.** Run 1 covered 8 of 15 before the quota stopped it
  (§5a); it needs completing and then repeating on a different day, per §4. On the free tier
  that is roughly four sittings. Zero citations so far, from eight.
- **Run 2 is captured logged-in**, matching the baseline's condition, under the rule fixed in
  the protocol on 2026-09-23: any query that cites openappindex.org is re-tested on a clean,
  logged-out session, and counts toward the §4 threshold only if the citation survives. A
  citation that does not survive is reported separately as history-assisted, never in the
  headline count.
- **The homepage re-crawl in Google** — indexing requested and "Validate fix" started
  2026-09-23; outcome pending.
- **Bing and Brave** — no action available that has not already been taken four times. These
  legs close as INCONCLUSIVE — CRAWLING unless an external authority signal changes them.

## 7. What this result is worth saying plainly

The experiment set out to test whether an independent index gets cited. It found, first, that
**two of the three assistants could not have cited it whatever it published**, and second, that
the one that did cite it **cited a figure we had already corrected**. Neither is the result the
protocol anticipated. Both are more useful than the citation rate would have been, and both were
reachable only because the thresholds were frozen before the data existed.

The gate has not been scored. It has, for the first time, become scoreable.

---

*Every claim above is dated and traceable to a record in this repository or to Bing Webmaster
Tools and Google Search Console readings quoted in `gate-protocol.md` §1. Where this document
and the protocol disagree, the protocol is authoritative — it holds the frozen thresholds.*
