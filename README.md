# openAPPindex

**An open index of mobile apps, ranked by how well they are maintained and what they
actually cost — never by who paid.**

[openappindex.org](https://openappindex.org) · [the manifesto](docs/manifesto-en.md) ·
[method](https://openappindex.org/methode.html)

---

## The finding this repository reproduces

App stores decide what two billion people can find, and answer one question: what matches
these words, weighted by popularity. We measured **two categories** of the German App Store as
completely as we could reach them — cooking apps, then sleep and meditation apps, the second
chosen to be structurally unlike the first and to break the result if it was breakable.

| | Cooking | Sleep & meditation |
|---|---|---|
| Apps in the classified category | **941** (≥991 incl. price-unverified) | **3,578** |
| Absent from the single obvious query | **81%** (579 of 715) | **88%** (1,013 of 1,155) |
| Reachable only via the similar-apps graph | **28%** (276 of ≥991) | **68%** (2,423 of 3,578) |
| Listed "free" | **96%** (907 of 941) | **96%** (3,417 of 3,578) |
| …of those, charging in-app | **77%** (697 of 907) | **77%** (2,581 of 3,351) |
| Median highest in-app purchase | **€39.99** | **€39.99** |
| Largest single in-app purchase | **€599.99** | **€1,199.99** |

**Price opacity replicated to the cent. Discovery failure replicated and got worse.** We picked
a concentrated category expecting discovery to improve there; it did not. The full write-up is
[the second-category findings](docs/second-category-findings.md).

Every figure is reproducible from the scripts here against public Apple endpoints. No paid
tooling, no access anyone else lacks.

*Corrected 2026-08-31: ten entries that passed the keyword classifier but are press products
(nine cooking-magazine ePapers) or a kids game were removed, and every affected figure was
recomputed on the corrected basis — the correction moved no headline percentage. The rules
that caught them are in `sample/precision_check.py`; the correction is published on the
[method page](https://openappindex.org/methode.html).*

## Reproduce it

Cooking:

```bash
cd sample                             # every script resolves data/ relative to here
python3 build_corpus.py               # 25-query sweep  -> data/corpus_de.json
python3 enrich_prices.py              # product pages   -> data/prices_de.json
python3 closure_crawl.py              # similar-apps graph closure
python3 build_site.py                 # generate the site
python3 export_public.py              # publishable dataset
```

Sleep & meditation:

```bash
cd sleep
python3 build_corpus.py               # 25-query German sweep
python3 classify.py                   # category classification
python3 closure_hopn.py               # hops over the similar-apps graph
python3 apply_v3.py                   # uniform precision filter across all hops
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
| `sample/gate_capture.py` | capture harness for the assistant baseline |
| `sample/gate_ground_truth.py` | answer key for the two enumeration queries |
| `sleep/` | the second category — same pipeline, frozen rules, four graph hops |
| `docs/second-category-findings.md` | **the replication** — two categories side by side |
| `docs/working-paper.md` | the full paper, both categories |
| `docs/gate-result.md` | where the citation experiment actually stands |
| `docs/` | manifesto, method, gate protocol, findings |

## The rules this project holds itself to

- **Evidence, not verdicts.** Dated facts with sources. No scores, no grades, no labels.
- **Nothing is estimated to fill a gap.** A missing value is published as missing.
- **No annualising.** Apple does not publish billing periods reliably, so €1,199.99 is
  always "highest single in-app purchase", never "per year" — even where the developer's own
  label for the item says *Jahresabo*. We report the label and do not convert it.
- **No pay-to-play, ever.** There is no placement to buy, at any price, for anyone.
- **We publish our errors.** See below.

## Errors we made, and published

Classifying "what counts as a category" was the hardest part, and we kept getting it wrong.

1. The German word *Rezept* means both **recipe** and **medical prescription**, so the
   first count swept in pharmacy apps — Shop Apotheke, DocMorris, Doctolib.
2. *Kochen* and *Backen* also match cooking **games**; and children's cooking games are
   filed under **Education**, not Games, so a third pass was needed.
3. A fourth pass (31 Aug 2026) removed nine cooking-magazine ePapers and a kids game whose
   subscription prices had contaminated the price figures.
4. The second category brought its own homonym traps: German *wickel* hides inside
   *entwickelt*, English *slim* inside *Muslim*. Each was word-bounded the day it was found.
5. A false download price (2026-09-11): the JSON-LD on every app page announced
   `"price": "0.00"` because a numeric field Apple does not return fell back to zero. Right
   for 919 free apps, **wrong for 22 paid ones** — the exact failure this index exists to
   expose, in the one layer we do not read ourselves.
6. Publishing the second category (23 Sep 2026), we compared two different recall measures as
   though they were one and **inverted the conclusion** — reporting the concentrated category
   as more discoverable when it is less. Corrected the same day, within the hour, and
   documented in [the findings](docs/second-category-findings.md).

Across the classifier passes the cooking headline moved **82.4% → 82.8% → 81.0%** and the
price headline never moved off **77%**. The findings do not depend on where the line was
drawn. Keyword classification has limits; they are stated on the method page rather than
hidden.

## Data and licences

- **Code**: AGPL-3.0 ([LICENSE](LICENSE))
- **Dataset** (`sample/data/public/`): CC BY 4.0 ([LICENSE-DATA](LICENSE-DATA)) — factual records about publicly listed
  apps. **App descriptions and release-note text are deliberately excluded**: they are the
  copyright of their developers, and republishing them wholesale would contradict the rule
  this project applies to its own pages. Regenerate them locally if you need them.

## Corrections

If something here is wrong — particularly if you build an app that appears in the data —
write to **korrektur@openappindex.org**. Every notice is checked and corrections are
published with a date.

## Status

Pre-alpha. **Two categories**, one storefront, one country.

A citation-validation experiment with thresholds frozen in advance
([protocol](docs/gate-protocol.md)) is part-run. Its standing result
([gate-result.md](docs/gate-result.md)): of the three assistants scored, two retrieve through
indexes that have not admitted the site — Bing holds **1** page of ~710 submitted, Brave **0** —
so those legs are *inconclusive on crawling*, not negative. The third, Perplexity, retrieves and
cites the index, and is unscored. Google, which feeds none of the three, holds 647 pages.

That result was not the one the protocol anticipated, and it is published as it stands, with
every amendment dated before the data existed.
