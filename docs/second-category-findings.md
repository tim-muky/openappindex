# The same 77%, in a category chosen to be different

**A replication. Measured 1–2 September 2026, published 2026-09-23.**
**3,578 sleep and meditation apps, German iOS App Store.**

---

## Why this measurement exists

In August 2026 we measured the cooking-app category of the German App Store as completely as we
could reach it, and reported that 81% of recipe apps never appear in the store's own results for
the obvious query, and that 77% of the apps listed as *Gratis* charge money once opened.

The first serious objection to that result is the right one: **cooking apps may be special.**
It is an old, crowded, fragmented category. So we picked a second one designed to break the
finding if it was breakable — sleep and meditation apps: anchored by a few large subscription
products rather than fragmented, a different vocabulary, a different buying pattern. If price
opacity were a symptom of fragmentation, it should weaken here.

The rules were frozen before counting, exactly as in the first category, and every later change
is dated with the error that motivated it ([protocol](../openappindex-sleep-category-protocol.md)).

## What came back

| | Cooking | Sleep & meditation |
|---|---|---|
| Apps in the classified category | 941 | **3,578** |
| Never appear in any query of the 25-query sweep | 81% (579 of 715) | **68%** (2,423 of 3,578) |
| Listed as *Gratis* | 907 | **3,417 (96%)** |
| …of those, charge through in-app purchases | **77%** (697 of 907) | **77%** (2,581 of 3,351) |
| Median highest single in-app purchase | **€39.99** | **€39.99** |
| Largest single in-app purchase behind *Gratis* | €599.99 | **€1,199.99** |

Two categories chosen for their dissimilarity, measured seven weeks apart with the same frozen
instrument, return **the same 77% and the same median — to the cent.**

## What we will and will not claim

**We claim:** the specific objection that cooking is unrepresentative does not survive contact
with the second category, *on the price findings*. The first attempt to refute the result failed
to refute it.

**We do not claim** that this is now general. It is two categories, not twenty. Both are
consumer-facing, both sit on the same storefront, and the discovery figure moved a lot — 81% to
68% — which is itself informative: recall failure is sensitive to how a category is structured
in a way that price opacity appears not to be. A category with professional buyers or a handful
of strong brands is still unmeasured. We would rather someone other than us ran the third one.

**We do not annualise.** €1,199.99 is the price of one purchasable item as Apple publishes it.
The developer labels it a yearly subscription; we report that label and do not convert it,
because Apple does not publish billing periods reliably enough to convert anything.

## Two corrections, published with the finding

A September draft of this section, written the day after the measurement, carried **two wrong
numbers**. Both were caught when the figures were recomputed from the raw data for publication,
and neither ever reached the site:

1. **The maximum was given as €999.99. It is €1,199.99** — a German meditation app listed as
   *Gratis* with a €1,199.99 item. The draft figure appears to have been read off an incomplete
   pass; the app was present in all three classification versions and was never borderline.
2. **The cooking free-listed share was given as 92%. It is 96%** (907 of 941) — the same as the
   sleep category, not four points below it.

Neither error changed the headline. We publish them because a project whose entire claim is
honest measurement does not get to quietly fix its own arithmetic, and because the pattern is
the one we keep finding in ourselves: the errors show up in the summary, not in the pipeline.

## Reproduce it

Every figure above is recomputable from the scripts in [`sleep/`](../sleep/) against public
Apple endpoints. No API key, no paid tooling, no access anyone else lacks.

```bash
cd sleep
python3 build_corpus.py      # 25-query German sweep
python3 classify.py          # category classification
python3 closure_hopn.py      # hops over the similar-apps graph
python3 apply_v3.py          # uniform precision filter across all hops
```

## Corrections

If something here is wrong — particularly if you build an app that appears in the data — write
to **korrektur@openappindex.org**. Every notice is checked and corrections are published with a
date, including the two above.

---

*Method, classification rules and their dated amendments:
[`openappindex-sleep-category-protocol.md`](../openappindex-sleep-category-protocol.md).
The cooking measurement this replicates: [`working-paper.md`](working-paper.md) §4, and
[openappindex.org/methode.html](https://openappindex.org/methode.html).*
