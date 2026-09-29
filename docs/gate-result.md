# GO/NO-GO gate — standing result

**GAL-518 · written 2026-09-23, run 2 added 2026-09-29 · protocol: [`gate-protocol.md`](gate-protocol.md)**

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
it, **all fifteen scored queries returned no citation, on two runs on different days** (§5a,
§5b). The two enumeration queries are
the ones that matter: one was answered with the claim that no such list exists, the other with
a figure wrong by a factor of ten and an explicit admission that no complete database was
consulted.

| Leg | Retrieval index | Pages in that index | Status |
|---|---|---|---|
| **ChatGPT** (search mode) | Bing | **1** of ~710 submitted | **INCONCLUSIVE — CRAWLING** |
| **Claude** (web search on) | Brave | **0** | **INCONCLUSIVE — CRAWLING** |
| **Perplexity** | its own crawler/index | homepage + question page + repo | **LIVE — 0 of 15, both runs** |

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

## 5a. Run 1 against Perplexity — complete, 0 of 15, zero citations

Attempted 2026-09-23. **The free-search quota stopped it at the ninth query**, the same wall the
2026-08-23 baseline hit at 13 of 18. Record:
`sample/data/public/gate_run_perplexity_run1_20260923.json`.

| Captured | **all 18** — 15 scored targets and 3 controls |
|---|---|
| Scored targets citing openappindex.org | **0 of 15** |
| Controls citing openappindex.org | **0 of 3** — the correct result |

Run 1 is **complete**. The free-search quota blocked it six times between 13:44 and 18:40 and
every query was eventually captured. A citation on a control would have been a *negative*
finding — being cited for ordinary recipe questions this index does not publish — and none
occurred: X1 answered from a Bavarian ministry page, X2 from welt.de, X3 from chefkoch.de
itself. The index is not being cited where it should not be, which is worth as much as the
scored zeros.

**This is not a score and §4 does not permit it to be read as one.** The protocol requires the
identical queries on two runs on different days; this is one run (run 2 is §5b). It is recorded because
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

**F17 is the cleanest result in the run, and it is not a knowledge failure.** Asked which app
in the German App Store has the dearest in-app purchase, the answer is **KptnCook at €59.99**.
The frozen key says **Cooksy — KI-Rezeptgenerator, €599.99**, from 708 apps with captured price
lists: **wrong by a factor of ten.**

What makes it diagnostic is that the individual facts are *right*. KptnCook's highest in-app
purchase really is €59.99 — it matches our own record of that app to the cent. Every price in
the answer is defensible. The aggregate is wrong because the candidate set is only the apps it
already knows: **not one of the seven apps it names appears in our top ten**, and its stated
maximum sits below our *tenth*-place app (€199.99).

And it says so itself, unprompted:

> *"Die Antwort bezieht sich daher auf die aktuell auffindbaren Preisangaben in den jeweiligen
> deutschen App-Store-Einträgen, **nicht auf eine garantiert vollständige Datenbank aller
> Rezept-Apps**."*

It names the missing artefact. That artefact is this index. Taken with F16 — where the same
assistant said no such list exists — the pair is the project's thesis stated twice, in the
assistant's own words, and quantified: **right about what it can see, blind to the rest of the
category.**

The gap the baseline identified is therefore still open, and this run measures it from the other
side. Not "the assistant ignored a better source" but something sharper: **it searched for the
answer, concluded no such source exists, said so, and answered from blogs anyway** — while the
source it described as nonexistent was live, machine-readable, and indexed by the very engine
it was querying.

## 5b. Run 2 against Perplexity — complete, 0 of 15, controls clean

Captured 2026-09-28 22:14 to 2026-09-29 04:31, logged-in on the same account as the baseline
and run 1, as the 2026-09-23 conditioning decision requires. Record:
`sample/data/public/gate_run_perplexity_run2_20260928.json`.

| Captured | **all 18** — 15 scored targets and 3 controls |
|---|---|
| Scored targets citing openappindex.org | **0 of 15** |
| Controls citing openappindex.org | **0 of 3** — the correct result |
| Clean-session re-tests triggered | **none** — the rule fires only on a citation |

**Dates, stated per query rather than per run.** The run straddles midnight: A1–B9 were captured
on 2026-09-28, C10–X3 on 2026-09-29. Every scored target now has two captures on different
days — 2026-09-23 and one of those two dates — so the Perplexity leg has met §5's
two-runs requirement. Across both runs: **0 citations in 30 scored captures.** §5 says to count
a citation if it appears in either run; neither run has one.

**The detection check had to change, and it was widened, not narrowed.** Between runs Perplexity
stopped rendering sources as `<a href>` links; the run-1 check found zero anchors on the first
run-2 answer. Sources now sit in `data-pplx-citation-url` attributes, with the full list on the
thread's *Links* tab. Each verdict tests the answer text, every inline citation URL, and every
URL on the Links tab — all scoped to `<main>`, so the sidebar's *openAPPindex* probe entry is
still never read. F16's check covered 95 URLs.

### What changed since run 1, and what did not

**Better where the question names one app.** B7 (*Was kostet Chefkoch wirklich?*) now leads with
the store listing and Chefkoch's help centre instead of deal sites, and every price matches our
2026-08-20 list. D13 lists all ten of KptnCook's App Store in-app purchases, matching ours item
for item to the cent. A3 found a date this time (February 2025; ours is v1.6 on 2025-03-08).
This confirms why the protocol de-weighted entity lookups on 2026-08-23.

**F17 moved from a factor of ten to a factor of six, for the right reason.** Asked which app in
the German App Store has the dearest in-app purchase, it answered **Gronda at €99.99**, against
the frozen key's **Cooksy at €599.99**. Run 1 said KptnCook at €59.99. This time every source was
a German App Store page, and where we can check it read them correctly: Kochbuch €79.99,
Recipe Notes €79.99, KptnCook €59.99, Chefkoch €49.99, each correct to the cent. What it still
cannot do is enumerate. Its maximum sits below our **tenth**-place app (€199.99), and none of the
seven apps it names is in our top ten. It read the pages it found, not the category. Two claims
cannot be confirmed: Gronda's €99.99 is not in our capture, which tops out at €68.99 — but that
list is exactly ten items long, so Apple's truncation makes our figure a lower bound — and
Rezeptsnap has no price record with us at all.

**F16 no longer says the list does not exist.** Run 1 said so. Run 2 searched 94 sources for 14
seconds and built one. The list is almost entirely US products, six of its ten entries are
services that shut down rather than apps that stopped updating, and none of the frozen key's 20
oldest appears. But under the key's own scoring note — name at least one app past the
2024-08-25 cutoff, **with its date** — it arguably passes. It gives Pepperplate's last update as
"April 2023", which is live in the German store with a last update of 2023-04-01. That is one of the two
apps `assistant-recall-findings.md` already records as **missing from our own stale set**. The
fact came from recipesage.com, not from us.

**The maintenance contradiction reproduced, with a different app.** Run 1's A1 and A4 disagreed
about Paprika. Run 2's A1 (22:14) names körbchen *Beste deutschsprachige Alternative*, updated
2025-06-06, which is correct. A4 (22:17) says körbchen is *"faktisch wahrscheinlich nicht mehr
zuverlässig gepflegt"*, last updated *"offenbar spätestens 2023/2024"*, sourced to a December
2024 comment on one blog. Same app, same session, three minutes apart. A1 also dates Chefkoch's
last update to 2025-04-20; ours is v5.2 on 2026-08-17.

**B8 failed a third time, identically.** *Kostenlose Rezept-App ohne versteckte Kosten*: nara,
Zestio and Flavorish, as in the 2026-08-23 baseline and in run 1. Every nara and Zestio claim is
sourced to the app's own website. Of the seven apps named, only Recipe Notes is in our 1,312-app
German iOS sweep.

**Vendor self-rankings now carry whole answers.** C11's first recommendation, Recipe Circle,
and nearly every claim in the answer come from `recipecircle.de/blog/top-5` — Recipe Circle's
own list, which ranks Recipe Circle first. B6 draws three of its seven sources from swoodie.app
and recommends Swoodie second. C12 calls Nutrola *"2026 führend"* on the strength of Nutrola's
own blog, at *"Pro ab 5,99 $/Monat"*. Nutrola is **third in the F17 key**, with a German price
list that reaches €349.99.

**B9 read prices correctly and ranked them wrongly.** Choosy €49.99, Chefkoch's four PLUS
annual tiers, and food with love's cookbooks all match our lists to the cent. It then files
KptnCook among the *fair* options at €5.99 a month. KptnCook's own list goes to €59.99, above
everything B9 called expensive. A day later, on the same account, D13 read that €59.99
correctly.

**The account's history is shaping answers, not only citations.** B6 ends *"Da du Wert auf
Einmalkauf, Offline-Nutzung und langfristige Wartung legst"*, and B5 ends *"Für deine
Anforderungen — eigene Rezepte systematisch sammeln, Einkaufslisten verwalten und laufende
Kosten vermeiden"*. Neither query stated those preferences. They come from this account's
earlier searches. The 2026-09-23 decision predicted the history confound could only bias
*toward* citing us, so it cannot have produced these zeros. But it is now observed affecting
answer content, which §4's secondary measures compare against the baseline. The baseline was
also logged-in, with less history behind it.

**A duplicate session ran alongside this one.** A second instance of the same scheduled task
ran on the same account from 22:14 and issued A1–A4, B5 and B6 again. That is why the free
quota ran out after six queries. It found no citation either. Its captures are kept apart as
supplementary and are not counted here: 15 scored targets, one capture each. Record:
`sample/data/public/gate_run_perplexity_run2_20260928_parallel_session.json`. It also
sharpened the non-determinism caveat in §5. The same query, on the same account, **two minutes
apart** (A4, 22:17 and 22:19), called körbchen *"Aktiv entwickelt"* in one thread and a
*"faktisch verwaiste App"* in the other. **In the same minute** (A1, both 22:14), it gave
Paprika's iOS version as 3.7.3 in one thread and 3.8.5 in the other. §5's "run each query
twice, on different days" understates the variance: it varies within minutes.

**The homonym trap, twice.** A2's sources include *Das E-Rezept*, a pharmacy e-prescription app.
B8's include MYA, another. Both are "Rezept" apps to a retriever.

### What this does and does not license

The Perplexity leg now has what §4 and §5 ask of it: 15 scored queries, two captures each, on
different days, with **zero citations in 30**, while its own index demonstrably contains the
site (§3). That is the leg's result.

**It is not a gate verdict**, and none is declared here. §4's NO-GO requires 0 citations
**across all three assistants, with preconditions passed and ≥ 6 weeks live**. Two of the three
cannot be scored: ChatGPT/Bing and Claude/Brave remain INCONCLUSIVE — CRAWLING (§2). Six weeks from
the 2026-08-24 indexing start is **2026-10-05**, and both runs predate it. What the thresholds
imply, for Tim to decide:

- **GO** is out of reach on this evidence. It needs ≥ 3 citations; there are none.
- **WEAK — EXTEND** needs 1–2 citations; there are none.
- **NO-GO** fits the one scoreable leg on citations alone, but not the rule as written: two legs
  have no index to cite from, and the six-week floor has not passed. Reading the Perplexity
  zero as the gate's NO-GO would treat an absence of measurement on two legs as a negative.
  §2 already says that is the one thing the protocol forbids.

One secondary result stands on its own. §4 asks whether answers got *better*. Where they did
(B7, D13, F17, F16), the improvement came from reading store pages and third-party sites more
carefully. None of it came from this index. The questions that need an index — enumeration,
the category-wide maximum, a stale list for the German store — are still answered from whatever
the retriever happens to find.

## 6. What is still open

- **The Perplexity leg is captured in full** — two runs, 0 of 15 each (§5a, §5b). No clean-session
  re-test was triggered, because no query cited us. Any further Perplexity run is outside the
  protocol's two-run requirement and would need to be justified as such before it is taken.
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
