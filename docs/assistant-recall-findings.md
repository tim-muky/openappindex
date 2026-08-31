# Do AI assistants fix the store's discovery problem?

Investigation, 23–26 August 2026. Corpus: 87 verbatim assistant answers to 18 frozen queries,
captured across Perplexity, ChatGPT (search) and Claude (web search) in two runs on separate
days, before openappindex.org was indexed. Protocol: [`gate-protocol.md`](gate-protocol.md).
Ground truth: Apple's published product pages, read 20 August 2026, plus live lookups on the
dates named below. Scripts: `sample/gate_capture.py`, `sample/gate_ground_truth.py`.

**The question.** The App Store ranks by popularity and answers only "what matches these
words". If people increasingly ask an assistant instead, does the assistant escape that
constraint — or inherit it? The naive expectation is that assistants return the same handful
of apps the store already surfaces. They do not. What they do instead is worse in a way that
is easy to miss.

## They reach deeper into the tail than the store does

Across the 41 answers to questions that ask for a recommendation, the assistants named **53
distinct apps from our 951-app corpus — 5.6% of the category**.

| | |
|---|---|
| Named apps appearing in the store's own results for „Rezepte" | **14 of 53** |
| Named apps in the store's **top 10** for that query | **3** — Chefkoch, KptnCook, Mein Rezeptebuch |
| Median rank of a named app in that search | **47** |
| Median rating count of named apps | **6** |
| Median rating count of all 951 cooking apps | **10** |

The most-named app across the whole study is **Paprika Rezept-Manager 3** — 45 mentions,
position 30 in the store's own search, 2,132 ratings. The fourth most-named is **Mela** (22
mentions), which does not appear in the store's „Rezepte" results at all. Also repeatedly
named: Cove (3 ratings), kobuu (5), Swoodie (0), Mise (0), MealTime (0), TasteBuddy (8).

The apps assistants recommend are, by rating count, **less popular than the category median**.
Whatever else is true, they are not echoing the store's front page.

## But the shortlist is just as narrow, and the bias moved

5.6% of the category is not discovery. It is a different small set, selected by a different
mechanism — and the mechanism is visible in the citations.

The recurring sources behind recommendations are `nutrola.app`, `fond.kitchen`, `flavor365`,
`Swoodie`, `foodiejournal`, `recipeone` — competitor and vendor marketing pages. Two
consequences we measured:

- **Mise** was recommended as the subscription-free option by two independent assistants on
  the same day (Perplexity B5, ChatGPT B6). Apple publishes four in-app purchases for it,
  the highest **€179.99** — the largest amount attached to any recommended app in the study.
- **A competitor's false claim propagated.** `fond.kitchen` states that Paprika has shipped
  no major feature since 2018. Claude repeated it three times, Perplexity once. Apple's data:
  Paprika was updated **2026-07-16**, 41 days before the query. Claude identified the source
  correctly on one of four occasions — "ein direkter Wettbewerber, der seine eigene App
  verkaufen will" — and repeated it uncritically the other three.

Popularity ranking is replaced by marketing-visibility ranking. Both are narrow; only one of
them is auditable.

## The failure the store does not have

The store shows the correct price on the page you land on. The assistants, asked the two
questions this project exists to answer, get them wrong in ways a reader cannot detect.

**Cost.** Five separate claims that Samsung Food has no hidden costs or is free, across two
assistants and four days; Apple publishes €7.99 and €69.99. ChatGPT answered
„Kostenlose Rezept-App ohne versteckte Kosten" with Kitchen Stories (up to €79.99) and
Chefkoch (up to €49.99) — after naming a genuinely free app, kobuu, the previous day and
dropping it. On B7, ChatGPT told the user Chefkoch's monthly price „wird nicht öffentlich auf
der Infoseite genannt". Apple publishes it on a page anyone can open: `Chefkoch PLUS,
Monatsabo — 5,99 €`.

**Maintenance.** Perplexity's A2 gave five update dates and **all five were wrong**, the worst
by 4.2 years: SuperCook, listed under „aktuell gepflegte Rezept-Apps (mit jüngsten Updates)",
was last updated 2022-06-15 and sits at rank 29 of our 96-app stale set. In the other
direction, ChatGPT's first run dated MiNoms to 28 January 2024 — an entry from the version
history — when the current version shipped 2026-07-18.

**Enumeration is the hard failure.** Asked which app has the most expensive in-app purchase,
ChatGPT reported a ceiling of **€99.99 in both runs**, citing four apps in run 1 and four
entirely different apps in run 2. Our corpus contains **29 apps above that line**, up to
€599.99. Asked to list apps unmaintained for over two years, its second run made **no false
claim at all** — it verified a version history and correctly excluded an app — and found
**1 of 96**, while telling the reader „die Auswahl ist kleiner als man zunächst denkt". One
in ten cooking apps in the German App Store qualifies.

## What separates the right answers from the wrong ones

Not model capability. Source.

Within a single ChatGPT session, the same app was dated twice: **A4 said Chefkoch's iOS
version was updated 29 April 2026**, sourced to a third-party tracker. **A2 said August 2026,
version 5.2**, sourced to the App Store. The second is correct (2026-08-17). Same model, same
morning, same question type; the only variable is which page was read.

The same split runs through Perplexity. Its C10 and C11 named payment models for seven apps
without a single amount and got **all seven right**, matching Apple's own product names
(„AnyList-Complete-Abo", „Recipe Keeper Pro"). Its C12 added amounts to the same apps and
**two of three became wrong** — Recipe Keeper described correctly as a one-time Pro purchase
in C10, then priced at „ca. 10 €" in C12 when Apple publishes €22.99.

**Durable properties — payment model, platform, feature set — are answered reliably. Live
values — last-updated date and price — are not, unless the product page was actually read.**
Those two live values are what this index collects.

## What this changes

The finding is not "assistants are unreliable about apps". On structural questions they are
good, and on single-app lookups they are usually right: `KptnCook Kosten In-App-Käufe` was
answered correctly by all three systems in every run, and ChatGPT's first run reproduced
Apple's entire published price list for it.

The finding is narrower and harder to dismiss:

1. **Assistants break the store's popularity monopoly** — they surface long-tail apps the
   store buries, which is genuinely new.
2. **They replace it with a marketing-visibility monopoly** — 5.6% of the category, selected
   largely by who published the most SEO.
3. **They degrade the two facts that decide whether an app is worth installing** — and they
   present those facts with the same confidence as the ones they get right.

An index does not compete with the assistants on any of this. It supplies the layer that is
missing underneath them: every app in the category, each with a dated price and a dated
maintenance record, from the source that publishes them.

## Side finding: three platforms, three lines on reproducing a recipe

One control query — `Chefkoch Rezept Käsekuchen` — asks for content that belongs to a named
publisher. It was included to detect false-positive retrieval, not to test copyright handling,
but the three systems answered it three different ways on the same day:

| | Behaviour |
|---|---|
| **Perplexity** | Reproduced the recipe in full — ingredient list and method — naming the Chefkoch user (blondeangel716) and the recipe title |
| **ChatGPT** | Gave four recipe titles with ratings and rating counts. Metadata only, no recipe text, with an offer to retrieve it on request |
| **Claude** | Declined the source text — "Den Originaltext von Chefkoch kann ich nicht wiedergeben" — and supplied its own recipe from other sources. Same behaviour in both runs |

This project's own rule is that measured figures and metadata may be published while the
developer's copyrighted text may not: the dataset carries `description_length` and
`release_notes_present` instead of the descriptions and release notes themselves. That places
it between the ChatGPT and Claude positions, and it means the exclusion is not an unusually
strict reading — two of three major platforms draw the line at or beyond the same place, on an
identical request, unprompted.

Recorded here because the content framing is an open item in both funding applications, and
because it is evidence rather than assertion.

## Limits of this finding

- **n is small.** 87 answers, 18 queries, one category, one storefront. Counts, not rates.
- **Two of three assistants ran on free tiers.** Perplexity's quota ended mid-protocol twice
  (13 of 18 on 23 August, 9 of 18 on 26 August); a paid tier may behave differently.
- **The named-app analysis counts mentions, not endorsements.** Figures above are computed
  over recommendation questions only (A1, A2, B5, B6, B8, C10, C11, C12); including the
  „which apps are stale" questions changes the corpus share from 5.6% to 7.7% and the median
  rating count from 6 to 5.
- **Our own coverage is incomplete.** Ten apps named by assistants are live in the German App
  Store and absent from our 951: Foodiaz, Trivet, Plan to Eat, Pepperplate, ResX, Dishly,
  SideChef, NYT Cooking, CookTrace, Recipe Swipe. Two of them — Pepperplate (last updated
  2023-04-01) and Recipe Swipe (2019-09-07) — belong in our 96-app stale set and are not in
  it. **The 96 is a lower bound, and on those two questions an assistant found what we
  missed.**
- **Errors of our own, corrected in the record.** We initially reported that Apple publishes
  zero in-app purchases for Mela; in fact Mela is excluded from the corpus by a classifier
  that requires a German signal word, and its page was never read. "Not collected" was
  reported as "zero" — the inference this project forbids. Corrected 26 August 2026 across
  all affected records. The same coercion affected kobuu, whose free status stands but on
  different evidence: its page was read and carries no In-App marker.
- **Apple truncates.** Product pages list at most ten in-app purchases: 203 of 1,265 price
  records sit at exactly ten, with none above. Where an app is truncated, our maximum is a
  lower bound — including Cooksy's €599.99. The assistants read the same censored page.
