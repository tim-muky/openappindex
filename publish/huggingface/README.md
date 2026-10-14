---
pretty_name: openAPPindex — German iOS App Store, cooking and sleep categories
license: cc-by-4.0
language:
  - de
  - en
task_categories:
  - table-question-answering
size_categories:
  - 1K<n<10K
tags:
  - app-store
  - ios
  - in-app-purchases
  - price-transparency
  - search
  - platform-markets
  - germany
  - open-data
configs:
  - config_name: cooking_sweep
    default: true
    data_files:
      - split: train
        path: cooking/corpus_de.json
    field: apps
  - config_name: cooking_closure
    data_files:
      - split: train
        path: cooking/closure_apps.json
  - config_name: cooking_prices
    data_files:
      - split: train
        path: cooking/prices_de.json
  - config_name: corrections
    data_files:
      - split: train
        path: cooking/corrections.json
  - config_name: sleep_category
    data_files:
      - split: train
        path: sleep/category_sleep_de.json
  - config_name: sleep_prices
    data_files:
      - split: train
        path: sleep/prices_sleep_de.json
---

# openAPPindex — German iOS App Store: cooking and sleep categories

An open dataset of **dated facts** about two categories of apps on the German iOS App Store:
which apps exist in the category, which of them the store's own search returns, and what Apple
publishes about their prices and in-app purchases.

It is the data behind the working paper *Search Without Recall: Preliminary Evidence on
Discovery Failure and Price Opacity in a Mobile Application Market* (Tim Meyerdierks, draft
v0.1, September 2026) — [openappindex.org/paper.html](https://openappindex.org/paper.html).

- Website and method: [openappindex.org](https://openappindex.org) ·
  [method page](https://openappindex.org/methode.html)
- Code (AGPL-3.0) and the authoritative copy of the data:
  [github.com/tim-muky/openappindex](https://github.com/tim-muky/openappindex)
- DOI: `PLACEHOLDER — Zenodo concept DOI, added after the first GitHub release`

## What the data says, as published by the project

These figures are copied from the project's README and findings; they are reproducible from the
scripts in the repository.

| | Cooking | Sleep & meditation |
|---|---|---|
| Apps in the classified category | 941 (≥991 incl. price-unverified) | 3,578 |
| Absent from the single obvious query | 81% (579 of 715) | 88% (1,013 of 1,155) |
| Reachable only via the similar-apps graph | 28% (276 of ≥991) | 68% (2,423 of 3,578) |
| Listed "free" | 96% (907 of 941) | 96% (3,417 of 3,578) |
| …of those, charging in-app | 77% (697 of 907) | 77% (2,581 of 3,351) |
| Median highest in-app purchase | €39.99 | €39.99 |
| Largest single in-app purchase | €599.99 | €1,199.99 |

## Rules the data follows

- **Facts only.** Names, developers, categories, versions, dates, listed prices, rating counts,
  and Apple's published in-app purchase lists. There are no scores, grades or labels.
- **No descriptions, no review text.** App descriptions and release-note text are the copyright
  of their developers and are **deliberately excluded**. Only derived measurements are kept:
  `description_length`, `release_notes_present`, `release_notes_length`. No review text is
  included. Regenerate the full records locally with the repository's scripts if you need
  them.
- **Missing is missing, never zero.** A value that was not collected is `null` (or, in the
  sweep and closure files, the key is absent because Apple did not return it). It is never
  filled with `0`, an empty list, or an estimate. See *Reading missing values* below.
- **No annualised prices.** Apple does not publish billing periods reliably. An in-app purchase
  is recorded with the name and price Apple lists, including the developer's own label (for
  example *Jahresabo*); it is never converted to a per-year or per-month figure. "Highest
  in-app purchase" always means the highest single listed item.
- **Every record is dated.** Each record carries the date or timestamp it was read; a fact
  without its read date should not be quoted.

## Read dates

- **Cooking:** measured 19 August to 1 September 2026. Price records carry their own
  `read_at` timestamp. Weekly snapshots in `cooking/snapshots/` are named by their read date
  (2026-08-23, 2026-09-17) and each app record carries its own `read` date.
- **Sleep and meditation:** measured 1–2 September 2026.

## Files and subsets

All files are JSON, UTF-8. Prices are strings exactly as Apple displays them on the German
storefront (for example `"14,99 €"`, `"Gratis"`); they are not parsed into numbers here.

### Cooking (`cooking/`, from `sample/data/public/` in the repository)

| Subset / file | One row is | Notes |
|---|---|---|
| `cooking_sweep` — `corpus_de.json` | an app returned by the 25-query search sweep (iTunes Search API, storefront `de`) | The rows are under the `apps` key; the 25 queries are in `queries`. This is the **unclassified** sweep output (1,312 apps per the project's docs): it still contains apps that are not cooking apps, such as pharmacy apps matched by *Rezept*. Category membership is decided by `sample/classify.py` in the repository, not by a column here. |
| `cooking_closure` — `closure_apps.json` | an app reached by walking the store's own "similar apps" graph | Same fields as the sweep. |
| `cooking_prices` — `prices_de.json` | one read of an app's product page | `track_id`, `read_at`, `read_ok`, `subtitle`, `in_app_purchases` (list of `{name, price}`). |
| `corrections` — `corrections.json` | a dated correction to the project's own data | German text, with a link to the method page. |
| `cooking/snapshots/<date>.json` (files only, no viewer subset) | a dated snapshot of the apps served by the index | Object keyed by app id; abbreviated fields (`n` name, `dev` developer, `v` version, `upd` last update, `rel` release, `price`, `notes`/`notes_len`, `iap_n`/`iap_min`/`iap_max`, `read`, `iap_read`). `collected` states which parts were read for that snapshot. |
| `cooking/changelog/<ISO week>.json` (files only) | one week's diff between two snapshots | New, gone, updated, price changes, corrections; every line dated. |

Main fields in the sweep and closure files (Apple's iTunes Search API names): `trackId`,
`trackName`, `sellerName`, `artistId`, `primaryGenreName`, `genres`, `version`, `releaseDate`,
`currentVersionReleaseDate`, `formattedPrice`, `averageUserRating`, `userRatingCount`,
`languageCodesISO2A`, `trackViewUrl`, plus the derived `description_length`,
`release_notes_present`, `release_notes_length`.

### Sleep and meditation (`sleep/`)

3,578 apps, measured 1–2 September 2026, exported by `sleep/export_public.py`; every headline
figure is recomputed from these two files by `sleep/verify_public.py`.

- `sleep_category` — `category_sleep_de.json`: one record per app in the final (v3) category,
  with the Lookup API fields, text-length measurements, `found_via` (`query_sweep` with every
  query and result position, or `similar_apps_graph` with the hop number and the app it was
  first reached from) and `classification`.
- `sleep_prices` — `prices_sleep_de.json`: one product-page read per app — `read_at`, `read_ok`,
  and `in_app_purchases` (name and price exactly as Apple shows them). `read_ok: false` means
  not collected; `read_ok: true` with `in_app_purchases: null` means the page showed no list.

An app counts as charging in-app when at least one listed item is priced above €0 (two sleep
apps list only €0.00 items).

### Not included here

The citation-experiment records (`gate_*.json`, `perplexity_retrieval_probe_*.json`) stay in
the GitHub repository and the Zenodo archive. They describe assistant answers, not apps.

## Reading missing values

| Where | Value | Meaning |
|---|---|---|
| `prices_de.json` | `read_ok: false`, `in_app_purchases: null` | The product page was **not read**. Nothing is known. |
| `prices_de.json` | `read_ok: true`, `in_app_purchases: null` | The page was read and carried **no in-app purchase list** on that date. |
| `prices_de.json` | `read_ok: true`, `in_app_purchases: [...]` | The list as Apple published it on that date (see truncation below). |
| sweep / closure files | key absent | Apple's API did not return that field. |
| sweep / closure, loaded with `datasets` | `null` | The same absent key; the loader fills it with `null`. |
| `averageUserRating` | `0` with `userRatingCount: 0` | Apple's own value for an app with no ratings. Read it as "no ratings", not as a rating of zero. |
| snapshots | `iap_n`, `iap_min`, `iap_max`, `iap_read` = `null` | In-app purchases **not collected** for that app in that snapshot. |

## Known limitations

- **Two categories, one storefront.** Cooking and sleep/meditation, German iOS App Store
  only, one platform, a short window. Nothing here describes other categories, other
  countries, or Google Play.
- **Keyword classifier.** Category membership is decided by a keyword classifier. German
  homonyms broke it repeatedly — *Rezept* is both recipe and medical prescription; *Kochen*
  and *Backen* match cooking games; *wickel* hides inside *entwickelt*, *slim* inside
  *Muslim*. Each trap was fixed when found and every correction is published with its date
  (`corrections.json`, and the README's "Errors we made, and published").
- **Apple truncates in-app purchase lists at 10 items.** Product pages list at most ten in-app
  purchases: 203 of 1,265 price records sit at exactly ten, with none above. Where an app's
  list sits at ten, the highest in-app purchase recorded here is a **lower bound**.
- **What Apple publishes is what we have.** Apple does not publish billing periods reliably,
  so none are inferred.

## Corrections

If something here is wrong — particularly if you build an app that appears in the data — write
to **korrektur@openappindex.org**. Every notice is checked and corrections are published with a
date.

## Licence and attribution

Data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribution:
openAPPindex — https://openappindex.org. The code that produces it is AGPL-3.0 and lives in the
GitHub repository.

## Citation

```bibtex
@techreport{meyerdierks2026searchwithoutrecall,
  author      = {Meyerdierks, Tim},
  title       = {Search Without Recall: Preliminary Evidence on Discovery Failure and Price
                 Opacity in a Mobile Application Market},
  institution = {The openAPPindex project},
  type        = {Working paper, draft v0.1},
  year        = {2026},
  month       = sep,
  url         = {https://openappindex.org/paper.html},
  note        = {DOI: PLACEHOLDER}
}
```
