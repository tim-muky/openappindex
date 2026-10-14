# Google Play: the two categories, measured on the other store

**Written 2026-10-14, before any Play data was collected.** As with the
[gate](gate-protocol.md) and the [sleep category](second-category-findings.md), the rules
below are fixed before the data exists. Amendments are dated, explained, and made before the
data they would affect.

## What this measures

The same two categories as on iOS, cooking and sleep & meditation, in the German Google Play
store (`gl=DE`, `hl=de`):

1. **How many apps** each category holds, as far as the method below reaches.
2. **Listed free, and charging anyway:** the share listed at €0 that sells in-app purchases,
   and the highest price Play shows per item.
3. **Maintenance:** the date of the last update.
4. **Reach, which Apple never shows:** Play's download ranges ("10 Mio.+").
5. **Both stores:** how many of our iOS apps also exist on Play.

## What Play shows, and what it doesn't

Read on 2026-10-14 from two pages (Chefkoch, Yazio):

- **Shown:** name, developer and the developer's website, Play category, rating count, price,
  whether the app has in-app purchases, the **lowest and highest in-app price per item** (not
  the list of items Apple shows), "contains ads", the last update date, the download range,
  the full description, about seven linked "similar" apps, and a link to the developer's page.
- **Not shown:** the first release date. On Play, "new" can't be defined by release date as on
  iOS. The new-and-small definition of the developer study does not carry over.

## How apps are found

Play's search pages are closed to crawlers (`Disallow: /store/search` in
play.google.com/robots.txt), so the iOS route through 25 search queries is not available.
Instead:

1. **Seeds:** the apps listed on the Play category pages Food & Drink, Health & Fitness,
   Lifestyle and Medical (about 50 each).
2. **Closure:** from every app classified into a category, follow its similar apps and its
   developer's page. Stop when a full hop adds fewer than **2%** new in-category apps, or after
   **hop 6**, whichever comes first.
3. **Second seed source, used as a recall test:** links to Play that the developers of our
   iOS apps publish on their own websites. Before they are added as seeds, we report the share
   of them the closure already reached. That share is the recall estimate for step 2. It
   matters because Play's graph starts at popular apps, and small apps are exactly the ones a
   graph from the top can miss.

## How apps are classified

The same classifiers as on iOS, unchanged: cooking v4 (`sample/classify.py`) and sleep &
meditation v3 (`sleep/precision_v3.py`), on the German name and description. Play categories
are mapped to the Apple genre names those rules use, before any page is read:

| Play category | Apple genre used by the rules |
|---|---|
| `GAME_*` | Games |
| ENTERTAINMENT | Entertainment |
| TOOLS | Utilities |
| PHOTOGRAPHY, VIDEO_PLAYERS | Photo & Video |
| TRAVEL_AND_LOCAL, MAPS_AND_NAVIGATION | Travel |
| FINANCE | Finance |
| BUSINESS | Business |
| NEWS_AND_MAGAZINES | Magazines & Newspapers |
| BOOKS_AND_REFERENCE | Book |
| SHOPPING | Shopping |
| EDUCATION | Education |
| FOOD_AND_DRINK | Food & Drink |
| HEALTH_AND_FITNESS | Health & Fitness |
| LIFESTYLE | Lifestyle |
| MEDICAL | Medical |
| MUSIC_AND_AUDIO | Music |
| any other | its Play name, unmapped (no rule excludes it) |

A manual precision check follows the iOS procedure. Any new rule it produces is dated and
applied to every hop alike.

## How the pages are read

- Only pages Play's robots.txt allows for all crawlers: app pages (`/store/apps/details`),
  category pages and developer pages. No search pages, no data-safety pages.
- One request at a time, at least **3 seconds** apart. On HTTP 429 or 503, a pause of at least
  30 minutes. No parallel machines or rotating addresses.
- The crawler names itself (`openAPPindex-bot`, with a link to the method page). Play serves
  it the same page as a browser (checked 2026-10-14).
- Every record carries the date it was read.

## What is published, and what is not

- Published: the same kinds of facts as for iOS, dated. Missing values stay missing.
- Not published: descriptions (the developers' copyright), average ratings (we publish no
  scores), and the developer's email address. Play shows one, but it is **not collected**.
- Play facts appear next to iOS facts only where the same app is matched on both stores. The
  matching rule (developer, website domain, name) is written down before the first match is
  published.

## Known limits

- The closure starts from popular apps. The recall test (seed source 3) measures how much that
  misses; it is reported next to every count.
- Play shows a price range per item, not the list of items, so the iOS figure "highest in-app
  purchase" corresponds to the top of Play's range.
- Download ranges are buckets ("100+", "10 Mio.+"), never exact counts.
- No first release date on Play.
