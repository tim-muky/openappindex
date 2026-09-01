# The Map Is Missing Most of the Streets
### A manifesto for an honest app ecosystem — openAPPindex

**The app store shows you a billboard and calls it a map.**

We spent a week measuring one small corner of it: recipe apps in the German App Store. Not a
sample — the whole category, as far as we could reach it. What we found is not that the store
ranks badly. It is that the store **does not show you most of what exists.**

Of the apps whose own store description says, in German, that they are recipe apps,
**81% never appear when someone searches for „Rezepte" — 579 of 715.** Twenty-five different searches
surface 1,312 apps between them; the single best of those searches finds **14%** of that.
Nearly two thirds of the apps we found are reachable by exactly **one** of the twenty-five —
change a word and they vanish.

Then we stopped searching and walked the store's own „you might also like" links instead.
The first hop found **243 more cooking apps** nobody's search had surfaced — the category grew
by a third. The second hop, from those, found **50 more**. Growth collapsed from +35% to +5%
in one step, which means we can finally see the edge: the German App Store holds **at least
991 cooking apps**, and each hop reached deeper into the invisible — the median app found by
search has a handful of ratings; the median app found only by following links has **zero**.

The map is not badly drawn. Most of the streets are not on it — and now we know roughly how
many streets there are.

---

**Roughly 160 characters decide who exists.**

Here is the mechanism, and it is not a conspiracy — it is documented, ordinary engineering.
Search eligibility on iOS comes from an app's **name** (30 characters), its **subtitle** (30)
and a hidden **keyword field** (100). A few smaller surfaces are indexed too — in-app purchase
names, in-app event titles, and since 2025 the text inside screenshots. What an app says it
does lives in its description, and **the description is not indexed at all**.

*Backen macht glücklich* has 1,879 ratings and says „Rezept" sixteen times in its own store
description. Its name and subtitle do not contain the word. It appears in **none** of the 168
results for „Rezepte".

Behind that first gate sits a second one. A broad search returns roughly 180 results, ordered
so the least popular fall off the end — so having the word is not enough either. *ZauberMix für
Monsieur Cuisine* carries the subtitle „Rezepte für Monsieur Cuisine" and **5,507 ratings**, and
is also absent from those 168 results. So is *Krautkopf* („Saisonale vegetarische Rezepte", 827
ratings). So is *Air Fryer Club* („Heißluftfritteuse Rezepte", 814 ratings).

Meanwhile an app called *„Kochbuch – Rezepte speichern"* holds position **8** with **12
ratings**, because its name is literally the search query.

Twelve ratings at position eight; five thousand ratings nowhere at all. That is what the
ranking is measuring — not quality, not upkeep, not price. Roughly 160 characters of metadata.
These are single measurements taken on 19 August 2026; store results move, and ours are
timestamped so anyone can check them against today's.

**Whatever you ask, the same shelf.**

Perhaps different questions reach different apps? We checked. Across all twenty-five searches
there are 674 first-30 result slots. **Ten apps hold 39% of every first screen.** One of them
appears in sixteen of the twenty-five lists — including searches for meal planners and for
baking, questions it is not the answer to — and is the #1 result for six different queries.
Around that fixed core there is only churn: two searches' first-30 lists share a median of
**5%** of their apps, and 63% of everything that ever enters a first-30 does so for exactly
one query. Changing your search changes the noise. It does not reach deeper into the shelf.

We ran all twenty-five searches again thirteen days later. **A median 92% of every first
screen was identical**, and the fixed core was exactly the same seven apps. And what fills the
remaining slots is its own finding: on 1 September 2026 the sixth result for „rezepte app" was
an **alarm clock**, and the tenth was an app for a dental practice — while 885 actual recipe
apps appeared in no first dozen of anything.

Put the two measurements together. **92 of 991 cooking apps ever reach any first screen** —
and that is the generous count, from the organic list alone. The rendered store places two or
more auctioned ad slots above it (Apple's own documentation; the slots are personalised and
cannot be independently observed — by us or by anyone). Nine percent of the category is
visible. The rest exists the way an unlit street exists at night.

---

**A search this narrow teaches people to stop looking.**

Users are not lazy. They are calibrated. Roughly 61% of search-driven installs go to the top
three results; past rank 30 an app collects under 4% of what a keyword has to give. So a store
with 2.17 million apps is, in practice, three results deep.

And the best of those three is for sale. Apple markets top-of-search placement to advertisers
with **"conversion rates over 60%"** — its own figure, in its own sales material, for the single
most valuable position in mobile software, auctioned by the hour. Since March 2026 it is no
longer one slot but several inside the same result page.

That is the loop, and it is self-sealing. A narrow search stops people scrolling. Nobody
scrolling makes the top three worth everything. Being worth everything makes them worth buying.
And once bought, the results get worse — which teaches people, correctly, not to scroll.

---

**And the price on the label is not the price.**

While we had the whole category open, we read what each app actually charges. Of 907 cooking
apps listed as **„Gratis"** in the German App Store:

- **697 — 77% — charge money once opened.**
- The median app's **highest** in-app purchase is **€39.99**.
- Twenty-six have a single in-app purchase over **€100**. Four are over **€200**.
- The largest we found is **€599.99**.

Every one of those apps says *Gratis* on the shelf. Not one of them is lying, exactly. The
price is published — on a page you reach after you have already chosen. The store shows you the
word and not the number, and it earns a commission on the difference.

Two signals, then, decide what a billion people install: a star average and a price word. One
is a monument to an app's past — it says nothing about the developer who walked away eighteen
months ago while the subscription kept billing. The other is a marketing term. Neither answers
the two questions that actually matter: **is this still cared for, and what will it really
cost me?**

---

**Everyone pays for this except four companies.**

Follow what the construction forces. If the store is three results deep and the best of the
three is auctioned, then being found is no longer something you earn — it is something you buy.
So it gets bought: **$78 billion on user acquisition in 2025 alone**, $109 billion on app
marketing in total, up 13% on the year.

Set that against what people actually spend in the stores. Consumers spent roughly **$166
billion** across the App Store and Google Play in 2025. Developers spent **$78 billion** buying
visibility. For every €2 a person spends on apps, close to €1 is spent by somebody trying to be
found — money that never touches the software.

It goes to a very short list. Google, Meta and TikTok together take **67% of all mobile ad
dollars**: Google booked about **$295 billion** in advertising in 2025, Meta **$196 billion**
(up 22%), TikTok around **$32 billion**. Apple sells the top slot in its own search results and
its ad business is estimated near **$7.4 billion**.

And the developer has to earn it back. There are only two places it can come from: a higher
price, or more advertising inside the app. **In-app advertising was worth $151 billion in
2025** — that is the second invoice, and it is paid in attention rather than money. Then, on
the subscription that the ad spend produced, the store takes **15–30%**.

Count who collects at each step. Apple sells the ad slot, then takes a commission on the sale
that slot produced. Google does the same, on its own store. Meta and TikTok do not run stores
at all — they simply charge for access to the users the stores made hard to reach.

Everyone else in the picture is paying. The developer, who spends a year building and then
learns that the year was the cheap part. The user, who pays in money and again in attention,
for an app that got worse in order to afford being found. Apps become more expensive and
more crowded with advertising, and the money does not go into making them better — it goes
into making them findable in a system deliberately built to make finding hard.

This is not a market failure. It is the market working exactly as constructed, for the four
companies who built it.

**The gatekeeper is being replaced. The bias is being inherited.**

That question — *which app should I use?* — is moving to the AI assistants. It could have been
the reset. Instead they answer largely from memory, recommending the incumbents they already
knew: the ones with reach, the ones loud enough to end up in the training data. An assistant
can only recommend from a corpus. If the only corpus is the one the store was already
distorting, nothing changes — it just gets harder to see.

---

**So we are building the list instead.**

**openAPPindex** is an independent, open index of mobile apps. The important word is *index*,
not *ranking*. We do not re-sort the store's answer — **we build the candidate set the store
structurally cannot show you**, then order it by how well an app is cared for and what it
truly costs.

We read the changelog, the version history and the published price list — not the marketing
copy. We show our evidence: every figure on every page carries its source and the date it was
read, so you can check us or catch us. Where a fact is missing, the page says it is missing;
nothing is estimated to fill a gap. And we are built to be read by people **and** by the
assistants, so that when someone asks the honest question, an honest answer is available to be
cited.

We hold five lines:

- **Rank by care, not reach.** Maintenance and honesty — never downloads, never ad spend.
- **Recall before ranking.** An app that never enters the list cannot be ranked fairly. Finding
  what exists is the harder half of the job and the half nobody does.
- **Evidence, not verdicts.** We publish dated facts and let you draw the conclusion. We do not
  score apps, and we do not call anyone a scam.
- **Neutral, always.** We take no money from any app, ever. There is nothing to buy, no
  placement to sell, and every app in the index — including any the people behind it happen to
  have built — is measured by the same published rules.
- **Open.** Open source, open data, open method — including the parts that did not work. A
  public good has to be inspectable to be trusted.

Everything above is reproducible. The scripts are public, the sources are Apple's own, and
anyone who thinks we are wrong can run them and say so. That is the whole point: the app stores
became bottlenecks because nobody outside could measure them.

Now anyone can.

**Help us keep it honest.**

*— openAPPindex · openappindex.org*

---

**Four corrections, published.** Deciding what counts as a cooking app turned out to be the
hardest part, and we got it wrong three times before this draft. First we matched the German
word *Rezept* — which means both **recipe** and **medical prescription** — and swept in pharmacy
apps: Shop Apotheke, DocMorris, Doctolib. Then we found that *Kochen* and *Backen* also match
cooking **games** — Cooking Fever, Pizza Ready — and that children's cooking games are filed
under Education rather than Games, so a third pass was needed. The fourth pass, on 31 August,
caught cooking-magazine **ePapers** — Landlust, ZauberTopf — being counted as cooking apps,
their subscription prices sitting inside our price figures.

Each pass was caught by our own checks, and every figure here is from the fourth. What matters
is what happened to the headlines across all four: the search figure moved **82.4% → 82.8% →
81.0%** and the price figure stayed at **77%** through the last correction. The findings do not
depend on where we drew the line. Keyword classification has limits and we state them on the
method page rather than hiding them — where we also note, in fairness and without symmetry of
blame, that the store's own results commit the same *Rezept* error at position one. We publish
our errors because a project claiming honest measurement has no other option.

**Why these figures count different things.** The 81% is measured against the 715 apps a
search sweep found on 19 August, with that day's category boundary. An app we discovered by
following the store's own "similar apps" links was never in a search result to begin with, so
counting it in a "never appears in search" statistic would be circular. The price figures use
the 941 apps the index serves, because a price is a price however we came across the app. The
991 is the category's lower bound including 50 verified apps whose price pages we have not yet
read. Every denominator is stated where its figure appears.

## Where every number comes from

| Claim | Source | Read |
|---|---|---|
| 81% of cooking apps absent from „Rezepte" (579 of 715); 14% single-query coverage; 62.5% reachable by one query | Our measurement, 25-query sweep, DE storefront | 19 Aug 2026 |
| +243 apps (hop 1), +50 (hop 2); growth +35% → +5%; category ≥ 991 | Our measurement, closure crawl over the similar-apps graph | 21 Aug – 1 Sep 2026 |
| 77% of „Gratis" apps charge in-app (697 of 907); median top price €39.99; max €599.99 | Our measurement, App Store product pages (basis corrected 31 Aug) | 20–23 Aug 2026 |
| Ten apps hold 39% of every first screen; one app in 16 of 25 first-30 lists and #1 for six queries; median 5% overlap between two lists; 63% one-list-only | Our measurement, per-query result positions | 19 Aug 2026 |
| 92 of 991 cooking apps ever reach any first screen (organic); 897 never do | Our measurement; ad displacement modelled from Apple's published slot count, never observed | 19 Aug – 1 Sep 2026 |
| Median 92% of each first-12 list identical after 13 days; the same seven-app core on both dates | Our measurement, identical queries re-run | 19 Aug + 1 Sep 2026 |
| An alarm clock at position 6 and a dental-practice app at position 10 for „rezepte app" | Our measurement, organic API result list | 1 Sep 2026 |
| iOS search eligibility comes from name (30) + subtitle (30) + keyword field (100); the description is not indexed | Industry-documented ASO mechanics; verified across our corpus | 19 Aug 2026 |
| Named apps absent from the 168 results for „Rezepte" (ZauberMix 5,507 ratings; Backen macht glücklich 1,879; Krautkopf 827; Air Fryer Club 814) | Our measurement, DE storefront | 19 Aug 2026 |
| $78bn user acquisition, $109bn app marketing, 2025 | AppsFlyer | — |
| $166bn consumer spend across App Store + Google Play, 2025 | Business of Apps / store reporting | — |
| Google, Meta and TikTok take roughly two thirds of mobile ad spend | Industry aggregate — single secondary source, treat as indicative | 2025–26 |
| Google ~$295bn, Meta $196bn (+22%), TikTok ~$32bn advertising revenue 2025 | Company reporting and eMarketer | — |
| In-app advertising worth $151bn in 2025 | Business of Apps | — |
| Store commission 15–30% on digital goods | Apple and Google published terms | — |
| 2,172,472 apps on the App Store | Apple, 2025 App Store Transparency Report | — |
| 70% of visitors use search; ~65% of downloads follow a search; "conversion rates over 60%" for top-of-search ads | Apple Ads, "Ads on the App Store" — Apple's own sales material | — |
| Multiple ad slots inside one result page from 3 March 2026 | Apple developer communication, reported January 2026 | — |
| ~61% of search installs to the top three; under 4% past rank 30 | Sensor Tower, *State of ASO* | — |

Method, scripts and raw data: **openappindex.org/methode**

---

*Draft v0.8. Every figure is either our own measurement, reproducible from published scripts,
or a company's own published number quoted accurately and attributed. The manifesto attacks
the **system** and names a company only when quoting that company's own figures. Apps are named only as measured
examples of what the search does or does not return — never as an accusation against the app.*
