# openAPPindex — method sample v0

A reproducible side-by-side: what the App Store returns for a query, and what the
same apps look like ranked on maintenance and true cost.

Built entirely from public sources. No estimates, no invented values — where a
field cannot be read it is recorded as null and excluded from scoring.

## Run it

```
python3 fetch_sample.py rezepte de 15   # → data/rezepte_de.json
python3 score.py                        # applies the v0 ranking, writes back
python3 build_showcase.py               # → showcase.html
```

## Sources

| What | Where |
|---|---|
| Ranking + app metadata | `https://itunes.apple.com/search` (public iTunes Search API) |
| In-app purchase names and prices | App Store product page, `serialized-server-data` JSON |

## Ranking v0

| Signal | Weight |
|---|---|
| Maintenance — days since the last published version | 50 |
| Cost visibility — money hidden behind the price word shown in search | 30 |
| Changelog — does it say what changed? | 20 |
| Downloads, rating count, ad spend | **0** |

Cost visibility penalises the *gap*, not the price: an app that costs €40 and says
so is not marked down for costing money.

## Known limits

- The iTunes Search API is a proxy for in-app search: no paid placements, no
  personalisation. The real store is further from the right-hand column, not closer.
- Absence from these results is not proof of absence in the App Store app.
- Billing periods are not published reliably, so nothing is annualised. Yearly
  figures appear only where an app labels its own plan as yearly.
- Twelve apps, one query, one country, one day. A method sample, not a study.
