# openAPPindex

**An open index of mobile apps, ranked by how well they are maintained and what they
actually cost — never by who paid.**

[openappindex.org](https://openappindex.org) · [the manifesto](docs/manifesto-en.md) ·
[method](https://openappindex.org/methode.html)

---

## The finding this repository reproduces

App stores decide what two billion people can find, and answer one question: what matches
these words, weighted by popularity. We measured one category of one store as completely
as we could reach it — cooking apps in the German App Store.

| | |
|---|---|
| Cooking apps found | **951** (lower bound) |
| Absent from the store's own results for the obvious query | **81%** (579 of 715) |
| Coverage of the single best search query | **14%** of what 25 queries find |
| Listed "free" but charging in-app | **77%** (706 of 916) |
| Median highest in-app purchase | **€39.99** |
| Largest single in-app purchase found | **€599.99** |

Every figure is reproducible from the scripts here against public Apple endpoints. No paid
tooling, no access anyone else lacks.

## Reproduce it

```bash
python3 sample/build_corpus.py        # 25-query sweep  -> data/corpus_de.json
python3 sample/enrich_prices.py       # product pages   -> data/prices_de.json
python3 sample/closure_crawl.py       # similar-apps graph closure
python3 sample/build_site.py          # generate the site
python3 sample/export_public.py       # publishable dataset
```

Nothing needs an API key. Product pages rate-limit at roughly one request per 2.5s — the
scripts respect that and are resumable.

## What is in here

| Path | |
|---|---|
| `sample/build_corpus.py` | query sweep over the iTunes Search API |
| `sample/enrich_prices.py` | reads Apple's published in-app purchase list per app |
| `sample/closure_crawl.py` | walks the store's own "similar apps" graph |
| `sample/build_site.py` | generates the served site (store facts only) |
| `sample/export_public.py` | builds the publishable dataset |
| `sample/data/public/` | **the dataset** — facts only, CC BY 4.0 |
| `docs/` | manifesto, method, gate protocol, findings |

## The rules this project holds itself to

- **Evidence, not verdicts.** Dated facts with sources. No scores, no grades, no labels.
- **Nothing is estimated to fill a gap.** A missing value is published as missing.
- **No annualising.** Apple does not publish billing periods reliably, so €599.99 is
  always "highest single in-app purchase", never "per year".
- **No pay-to-play, ever.** There is no placement to buy, at any price, for anyone.
- **We publish our errors.** See below.

## Errors we made, and published

Classifying "what counts as a cooking app" was the hardest part, and we got it wrong twice
before it was right.

1. The German word *Rezept* means both **recipe** and **medical prescription**, so the
   first count swept in pharmacy apps — Shop Apotheke, DocMorris, Doctolib.
2. *Kochen* and *Backen* also match cooking **games**; and children's cooking games are
   filed under **Education**, not Games, so a third pass was needed.

Across all three classifiers the headline moved **82.4% → 82.8% → 81.0%**. The finding does
not depend on where the line was drawn. Keyword classification has limits; they are stated
on the method page rather than hidden.

## Data and licences

- **Code**: AGPL-3.0
- **Dataset** (`sample/data/public/`): CC BY 4.0 — factual records about publicly listed
  apps. **App descriptions and release-note text are deliberately excluded**: they are the
  copyright of their developers, and republishing them wholesale would contradict the rule
  this project applies to its own pages. Regenerate them locally if you need them.

## Corrections

If something here is wrong — particularly if you build an app that appears in the data —
write to **korrektur@openappindex.org**. Every notice is checked and corrections are
published with a date.

## Status

Pre-alpha. One category, one storefront, one country. A citation-validation experiment
with thresholds frozen in advance is scheduled for September 2026
([protocol](docs/gate-protocol.md)); its result, including a negative one, will be published.
