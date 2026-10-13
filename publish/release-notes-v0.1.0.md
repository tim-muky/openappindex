First archived release of openAPPindex: an independent, open index of two categories of the German iOS App Store. Zenodo mints the DOI for this release.

**What is in it**
- **Dataset (CC BY 4.0, see LICENSE-DATA).** `sample/data/public/` holds the cooking category: 941 apps, swept 2026-08-19, graph crawl to 2026-09-01, prices read 2026-08-20 to 08-23, and weekly snapshots up to 2026-10-13. `sleep/data/public/` holds the sleep and meditation category: 3,578 apps, read 2026-09-01 to 09-02.
  - Every record carries the date it was read.
  - A missing value is published as missing, never as zero.
  - App descriptions and release-note text are not included.
- **Code (AGPL-3.0-only).** The collection pipeline (`sample/`, `sleep/`), the static site generator, and the Cloudflare Worker that serves openappindex.org.
- **Papers and protocols.**
  - `docs/working-paper.md`.
  - `docs/thesis.md`.
  - The citation experiment: `docs/gate-protocol.md`, frozen 2026-08-21, and its result in `docs/gate-result.md`, closed 2026-10-13.
  - The follow-up `docs/experiment-2-protocol.md`, frozen 2026-10-13.
- **Corrections.** `sample/data/public/corrections.json` and the dated amendments in each document.

**Limits.** Two categories, one storefront, one platform. Category membership comes from a keyword classifier with four documented correction passes. Apple lists at most ten in-app purchases per product page, so maxima are lower bounds.

Corrections: korrektur@openappindex.org. Each notice is checked, and corrections are published with a date.
