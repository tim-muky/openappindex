# What AI assistants get wrong about app costs — and why

**A measured baseline, 23 August 2026.** 19 responses captured from Perplexity, ChatGPT and
Claude on German-language questions about recipe apps, every factual claim checked against the
prices and dates Apple publishes.

Captured **before** openAPPindex was indexed by any search engine, so it records the state of
the world without us in it.

---

## Summary

Assistants are not uniformly bad at app questions. They are **precisely and predictably** bad,
and the variable is not the model — it is which source the answer reaches.

- When an answer cites **apps.apple.com**, it is usually right, sometimes exactly right.
- When it cites **the app's own marketing** or an SEO listicle, it is wrong — and the errors
  mostly understate what the user will pay.
- Asked to **enumerate** apps by a property (which are maintained, which are expensive), every
  assistant failed. Two of them told the user to go and check each App Store page by hand.

The gap is not knowledge. It is that **no queryable index of app maintenance and true cost
exists**, so a question spanning apps has no source to be right from.

---

## The finding, in one query

Query: **„Kostenlose Rezept-App ohne versteckte Kosten"** — a person explicitly asking to
avoid hidden costs.

Perplexity's top two recommendations:

| Presented as | What Apple publishes |
|---|---|
| **Samsung Food** — „Komplett kostenlos, kein Abo, keine versteckten Kosten" | in-app purchases **€7.99 – 69.99** |
| **Nutrola** — „beste kostenlose Rezept-App 2026", cited to *nutrola's own website* | in-app purchases **€1.99 – 349.99**, incl. a €349.99 Lifetime tier |

Two further recommendations, Flavorish and Aldenté, are not in the German App Store at all.
A fifth, My ReciNote, billed as „100% kostenlos", carries €2.99–7.99.

The question was answered with the two apps carrying the largest hidden costs in the category,
one of them citing itself as the evidence for its own recommendation.

---

## The mechanism, demonstrated three independent ways

**1. Same model, same second, two answers.** ChatGPT served an A/B comparison on
„Welche Rezept-Apps haben teure In-App-Käufe?".

| | Response A | Response B |
|---|---|---|
| Sources | apps.apple.com | Nutrola ×4, Swoodie, Mium |
| Kitchen Stories | **€79.99 — exact** | — |
| KptnCook | **„bis 59,99" — exact** | — |
| Crouton | — | „über €30" — Apple publishes **€0.99–12.99** |
| SideChef | — | named as most expensive — **not in the German store** |
| BigOven, Mealime | — | given monthly prices — **neither has any in-app purchase** |
| Currency | EUR, correct market | USD, for a German query |

Model, prompt and moment held constant. Source was the only variable, and it decided
correctness.

**2. Same assistant, adjacent queries, opposite quality.** Perplexity's best answer of thirteen
(Recipe Keeper €22.99 exact, Paprika correct) cited `apps.apple`, *teltarif* and
*iphone-ticker*. Its worst answer, one query earlier, cited *nutrola* four times.

**3. Same app, three descriptions, one session.** Samsung Food, per Perplexity:
„Vollständig kostenlos" → „Komplett kostenlos, keine versteckten Kosten" → „Werbefreiheit +
KI nur im Abo". The last is roughly right. Nothing about the app changed.

---

## Verification works. Enumeration does not.

| Question | Result |
|---|---|
| „Ist Mein Rezeptebuch noch aktuell?" — **ChatGPT** | **„Version 1.6 vom 8. März 2025"** — exact, with a correct read that development is slow |
| Same question — **Perplexity** | „Ich konnte im Apple App Store keine passende App finden" → answered from the **Android** listing → concluded „wird gepflegt". The iOS app is **532 days stale**. |
| „Welche Koch-Apps wurden seit Jahren nicht aktualisiert?" — **Perplexity** | Named no German app. Told the user to open each App Store page and check the version history manually. |
| Same question — **ChatGPT** | Named four apps with dates — **all cooking games**. One date wrong by ten months. Offered to build a proper list; did not build one. |

Neither named a single genuinely stale recipe app. Ours, measured, with dates:

| App | Days since last update | Ratings |
|---|---|---|
| Rezepte Kochbuch | 1,711 | 368 |
| Rezept des Tages | 1,711 | 152 |
| Low Carb Rezepte & Abnehm App | 1,661 | 52 |
| SuperCook Rezepte nach Zutaten | 1,530 | 140 |
| Grillrezepte 2 | 1,250 | 1,277 |

---

## Apps cited as evidence for themselves

Five separate instances: *nutrola* sourcing Nutrola's quality (and, separately, SideChef's
price — a competitor's); *recipeone* sourcing „Recipe One is best overall"; *blinner* three
times in its own category; *fond* for Fond; *vimafitness* for Vima.

This is the ordinary economics of the app store arriving in the AI layer. The developer who
buys visibility also produces the content that becomes the assistant's source. Nothing in the
pipeline distinguishes a measurement from a marketing claim.

---

## What the assistants got right, and it matters

Understating the counter-evidence would make this report worthless.

- **ChatGPT is good at lookups.** Kitchen Stories €7.99/€79.99 exact. Mein Rezeptebuch v1.6,
  8 March 2025, exact. Kitchen Stories' last update „31. Juli 2026", exact.
- **Perplexity is right when it reaches the right page.** Kitchen Stories €7.99/€79.99 exact.
  Recipe Keeper €22.99 exact. Paprika correctly described as a one-time purchase with no
  subscription.
- **Both hedge honestly at times.** ChatGPT said outright that ReciMe's price „wird in der
  gefundenen deutschen App-Store-Seite nicht angezeigt" rather than inventing one.

The implication for anyone building here: **do not compete on lookups.** Apple's own page is
already the source, and the assistants find it. The gap is enumeration.

---

## Limitations, stated plainly

- **19 responses, not a study.** One run per query where the protocol asks for two.
- **Logged-in sessions.** An anonymous visitor may see different results.
- **Perplexity's free quota interrupted the run twice**; 13 of 18 planned queries completed.
- **The Claude response was captured and scored by Claude.** It is recorded, and it is the
  weakest evidence here for exactly that reason. Perplexity and ChatGPT carry the argument.
- **Single point in time.** Assistants are non-deterministic; these are snapshots, dated.
- **One query is contaminated** („galleybook App") because that app's store listing was
  changed the same week. Excluded from all conclusions.

---

## Why this is publishable regardless of what happens next

This baseline was captured to serve as the control condition for a citation experiment. It
turned out to stand on its own: it documents, with dated and reproducible evidence, that the
opacity of the app store propagates through vendor SEO into the answers consumers now rely on
— and that the questions people most need answered are the ones no assistant can answer.

Raw records: `sample/data/gate_baseline_perplexity.json`,
`sample/data/gate_baseline_chatgpt.json`. Every price and date checkable against the App Store
product pages, read 19–23 August 2026.
