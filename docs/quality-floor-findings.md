# Can a neutral spam filter exist?

Investigation, 19 August 2026. Corpus: 1,312 German-storefront apps gathered from a
25-query sweep; 845 of them German-language listings with descriptions long enough to
measure. Scripts: `sample/spam_signals.py`, `sample/spam_refine.py`, `sample/spam_rule.py`.

**The constraint.** Opening up recall means dropping Apple's popularity gate — which is,
among other things, Apple's crude spam filter. So openAPPindex needs its own. But it may not
use downloads, ratings or revenue: those are exactly what the store ranks on, and
re-importing them re-imports the bias the project exists to oppose. Every signal must be
computable from an app's own published artefacts, measured identically for a one-person app
and a corporation, and explainable to the developer it demotes in one dated sentence.

## Result: the obvious filters do not work

**Keyword-stuffing ratios fail.** The distribution is far too tight to threshold: median
0.047, p95 0.079, p99 0.103. The single highest stuffing score among established apps
belongs to **Paprika Rezept-Manager 3** (0.113, 2,132 ratings) — a paid, well-regarded
recipe manager. Category-term saturation is worse: the top of that ranking is small honest
indie apps (Mizept, FlavorVault, Kurkum) sitting alongside **Dr. Oetker** at 7.52 mentions
per 100 words. German recipe apps say "Rezept" a lot because that is the German word for the
thing. **No threshold separates spam from legitimate copy.**

**Duplicate-text detection fires on the innocent.** 13 apps share >50% of their description
with a *different* seller. All 13 are German pharmacy **E-Rezept** apps — individual
pharmacies shipping a white-labelled e-prescription app from a common vendor template.
Identical text, different sellers, entirely legitimate. (They are in the corpus at all
because *Rezept* means both "recipe" and "prescription".) A naive similarity filter would
have demoted thirteen pharmacies.

**And the conjunction rule collapses.** Requiring 3+ structural conditions
(shared text, developer clones, never updated, no changelog, no reviews, poor vocabulary)
flags 38 apps — 2.9%, with every control staying clean: Paprika 0, galleybook 0, Chefkoch 0,
Dr. Oetker 0, and the small `Kochbuch - Rezepte speichern` 0. Promising — until you notice
which condition is doing the work. **Remove `no_reviews_at_all` — the one popularity proxy —
and the rule catches 1 app in 1,312.** That one is a pharmacy app.

> A popularity-free spam filter built from these signals catches essentially nothing.
> Any version that catches more is detecting obscurity, not junk.

## What the data says to do instead

**1. Don't filter. Disclose.** Never remove anything from the result set. Attach the
structural fact and show it: "shares 98% of its description with 6 other listings",
"no changelog since release". For the pharmacy apps a user reads that and instantly
understands why. Disclosure survives being wrong; removal does not.

**2. Fix the real gap — maintenance needs a track record, not a timestamp.** The genuine
problem is not old junk, it is *fresh* junk. Of the 38 flagged apps, **27 were updated
within the last 180 days** (median 32 days) — freshly-shipped, zero-review, no-changelog
listings, several obviously AI-generated. The v0 care score would rank them *highly*,
because a single recent release date is indistinguishable from real maintenance.

The fix is to score **update history, not last-update date**: how many releases, over what
period, with what changelog substance. Fourteen releases over eighteen months is
categorically different from one release ever — and it is behavioural, popularity-free, and
just as achievable for a solo developer. Apple publishes version history on the product
page; openAPPindex should capture it, and its own repeated crawls generate the series over time.

**3. Give new apps a state, not a penalty.** An app with no track record yet is neither good
nor bad — it is *unproven*, and should be labelled and ranked as such. A new honest app and
a new junk app look identical on day one because they **are** identical on day one. Only
time separates them, and time is exactly what a standing index has and a search query does not.

## What this costs

The conservative bias is deliberate: this design lets junk through rather than demote
anything legitimate. `100 leckere leckere Rezepte` (zero ratings, 99 repetitions of
"Rezept") is caught by nothing here. That is the right trade for a project whose whole claim
is that the incumbent gatekeeper demotes unfairly — but it must be stated openly, because
the first critique will be "your index is full of garbage". The answer is that the garbage
is visible, dated, and sorted below anything with a track record.

## Open questions

- Version-history depth needs a scraper and a back-fill strategy — how far back does Apple
  publish, and what does the series look like for a typical indie app?
- Is "unproven" a rank position, a separate shelf, or a filter the user toggles?
- Does disclosure of duplicate text carry defamation risk in DE when the sharing is
  innocent? One for the Fachanwalt pass — factual and dated, but it reads as an accusation.
