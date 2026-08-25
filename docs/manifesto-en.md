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
That one step found **248 more cooking apps** nobody's search had surfaced: the category grew
by **35% in a single hop**, and it has not stopped growing.

The map is not badly drawn. Most of the streets are not on it.

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

While we had the whole category open, we read what each app actually charges. Of 916 cooking
apps listed as **„Gratis"** in the German App Store:

- **706 — 77% — charge money once opened.**
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

**Three corrections, published.** Deciding what counts as a cooking app turned out to be the
hardest part, and we got it wrong twice before this draft. First we matched the German word
*Rezept* — which means both **recipe** and **medical prescription** — and swept in pharmacy apps:
Shop Apotheke, DocMorris, Doctolib. Then we found that *Kochen* and *Backen* also match cooking
**games** — Cooking Fever, Pizza Ready — and that children's cooking games are filed under
Education rather than Games, so a third pass was needed.

Each pass was caught in a pre-publication check, and every figure here is from the third.
What matters is what happened to the headline across all three: **82.4% → 82.8% → 81.0%.**
The finding does not depend on where we drew the line. Keyword classification has limits and
we state them on the method page rather than hiding them. We publish our errors because a
project claiming honest measurement has no other option.

**Why two of these figures count different things.** The 81% is measured against the 715 apps
a search sweep found. An app we discovered by following the store's own "similar apps" links was
never in a search result to begin with, so counting it in a "never appears in search" statistic
would be circular. The price figures use all 951 apps we know of, because a price is a price
however we came across the app. Both denominators are stated wherever the figures appear.

## Where every number comes from

| Claim | Source | Read |
|---|---|---|
| 81% of cooking apps absent from „Rezepte" (579 of 715); 14% single-query coverage; 62.5% reachable by one query | Our measurement, 25-query sweep, DE storefront | 19 Aug 2026 |
| +248 apps (+35%) from one hop over the similar-apps graph | Our measurement, closure crawl, 866 seed pages | 21 Aug 2026 |
| 77% of „Gratis" apps charge in-app (706 of 916); median top price €39.99; max €599.99 | Our measurement, App Store product pages | 20–24 Aug 2026 |
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

*Draft v0.7. Every figure is either our own measurement, reproducible from published scripts,
or a company's own published number quoted accurately and attributed. The manifesto attacks
the **system** and names a company only when quoting that company's own figures. Apps are named only as measured
examples of what the search does or does not return — never as an accusation against the app.*
