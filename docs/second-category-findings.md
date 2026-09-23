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
| Apps in the classified category | 941 (≥991 incl. price-unverified) | **3,578** |
| Absent from the single obvious query | 81% (579 of 715, *rezepte*) | **88%** (1,013 of 1,155) |
| Reachable only through the similar-apps graph | 28% (276 of ≥991) | **68%** (2,423 of 3,578) |
| Listed as *Gratis* | 96% (907 of 941) | **96%** (3,417 of 3,578) |
| …of those read, charge through in-app purchases | **77%** (697 of 907) | **77%** (2,581 of 3,351) |
| Median highest single in-app purchase | **€39.99** | **€39.99** |
| Largest single in-app purchase behind *Gratis* | €599.99 | **€1,199.99** |

Both recall rows are computed the same way in both categories: the first over the apps the
sweep itself classified, against one query; the second over the whole closed category. The
obvious query is *rezepte* for cooking and *schlaf* for sleep; using *meditation* instead
gives 86% (995 of 1,155).

Two categories chosen for their dissimilarity, measured seven weeks apart with the same frozen
instrument, return **the same 77% and the same median — to the cent.**

## What we will and will not claim

**We claim:** the specific objection that cooking is unrepresentative does not survive contact
with the second category, *on the price findings*. The first attempt to refute the result failed
to refute it.

**We do not claim** that this is now general. It is two categories, not twenty. Both are
consumer-facing and both sit on the same storefront. A category with professional buyers or a
handful of strong brands is still unmeasured. We would rather someone other than us ran the
third one.

**The prediction we made was wrong, in the interesting direction.** We chose a concentrated
category expecting that if discovery failure were a symptom of fragmentation it would weaken
here. It did not weaken. On the comparable measure the second category is **less** discoverable
than the first — 88% absent from the obvious query against 81%, and 68% reachable only through
the recommendation graph against 28%. Concentration at the head of a category does not make its
tail findable; on this evidence it coincides with a larger invisible tail, not a smaller one.

**We do not annualise.** €1,199.99 is the price of one purchasable item as Apple publishes it.
The developer labels it a yearly subscription; we report that label and do not convert it,
because Apple does not publish billing periods reliably enough to convert anything.

## Three corrections, published with the finding

A September draft of this section, written the day after the measurement, carried **two wrong
numbers**. Both were caught when the figures were recomputed from the raw data for publication,
and neither ever reached the site:

1. **The maximum was given as €999.99. It is €1,199.99** — a German meditation app listed as
   *Gratis* with a €1,199.99 item. The draft figure appears to have been read off an incomplete
   pass; the app was present in all three classification versions and was never borderline.
2. **The cooking free-listed share was given as 92%. It is 96%** (907 of 941) — the same as the
   sleep category, not four points below it.

**A third, corrected the same day it was published (2026-09-23).** The first version of this
page and of §6 of the working paper compared this category's 68% against cooking's 81% as
though they were one measure, and concluded that the second category is *more* discoverable.
**They are two different measures and the conclusion was backwards.** Cooking's 81% is absence
from a single query (*rezepte*), counted over the apps the sweep classified; the 68% is the
share of the whole closed category reachable only through the recommendation graph. Computed
like for like, the second category is **less** discoverable on both: 88% against 81% for the
single obvious query, 68% against 28% for graph-only reachability. The table above now carries
both measures for both categories. The error was ours, it was live for about an hour, and it
inverted the finding — which is exactly why we recompute headlines from raw data rather than
from our own prose.

None of the three changed a price headline. We publish them because a project whose entire
claim is honest measurement does not get to quietly fix its own arithmetic, and because the
pattern is the one we keep finding in ourselves: the errors show up in the summary, not in the
pipeline.

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
