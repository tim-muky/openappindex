# openAPPindex dataset — sleep & meditation, German iOS App Store

3,578 apps, measured 1–2 September 2026. Licence: **CC BY 4.0**
(https://creativecommons.org/licenses/by/4.0/). Attribution: openAPPindex — https://openappindex.org

Factual records about publicly listed apps, read from public Apple endpoints and dated.
Built by `sleep/export_public.py`; every headline figure is recomputed from these files by
`sleep/verify_public.py`.

## Files

- `category_sleep_de.json` — one record per app in the final v3 category. Lookup API fields
  (`trackId`, `trackName`, `sellerName`, `artistId`, `primaryGenreName`, `genres`, `version`,
  `releaseDate`, `currentVersionReleaseDate`, `formattedPrice` = the store's own price label,
  `averageUserRating`, `userRatingCount`, `languageCodesISO2A`, `trackViewUrl`);
  `description_length`, `release_notes_present`, `release_notes_length` (measurements only);
  `found_via` — `query_sweep` (hop 0, with every query and result position the app appeared at)
  or `similar_apps_graph` (hop 1–4, with the app it was first reached from);
  `classification` (`v3`).
- `prices_sleep_de.json` — one product-page read per app: `read_at`, `read_ok`, and
  `in_app_purchases` (name + price exactly as Apple shows them).

## Rules

- **Missing stays null.** `read_ok: false` means the page was not collected. `read_ok: true`
  with `in_app_purchases: null` means the page was read and showed no in-app purchase list.
  Nothing is estimated, inferred, or zero-filled.
- **No annualising.** An in-app purchase price is the price of one item. Apple does not publish
  billing periods reliably, so none is converted.
- **Deliberately omitted:** app descriptions and release-note text (the developers' copyright),
  product-page subtitles, icons. Regenerate full records locally with the scripts in `sleep/`.
- Fields this pipeline never collected (`price`, `currency`, `minimumOsVersion`) are absent.

Corrections: korrektur@openappindex.org
