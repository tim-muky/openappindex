# Search Without Recall: Preliminary Evidence on Discovery Failure and Price Opacity in a Mobile Application Market

**The openAPPindex project** · openappindex.org
Working paper, draft v0.1 · September 2026

*Status: preliminary and incomplete. This paper is circulated to invite discussion, replication
and criticism. It is not submitted for any degree or peer-reviewed publication. All measurements
described here are reproducible from scripts and raw data published at openappindex.org/methode,
and the corrections we made to our own classification are documented there as well.*

**Keywords:** search costs, platform markets, price transparency, app stores, gatekeepers
**JEL codes:** D82, D83, L13, L86

---

## Abstract

We measure two properties of a mobile application marketplace that economic theory treats as
preconditions for efficient outcomes: whether the supply of products is discoverable, and whether
displayed prices state true costs. Using the full cooking-app category of the German iOS App
Store as a test case (measurements taken 19 August to 1 September 2026), we find that 81% of
apps whose own store description identifies them as recipe apps (579 of 715) do not appear in
any of 25 German-language recipe searches, and that at most 92 of at least 991 apps in the
category ever reach the first screen of any query. Ranking positions correlate with indexed
metadata rather than with observable quality signals. Separately, 77% of the 907 category apps
listed as free (German „Gratis") charge for use through in-app purchases, with a median highest
purchase of €39.99. We relate these observations to the literatures on consumer search,
shrouded prices and platform gatekeeping, and argue that they are consistent with a structural
account in which the operators of distribution and advertising jointly profit from low market
transparency. We then replicate the price measurement on a second, structurally dissimilar
category — 3,578 sleep and meditation apps on the same storefront, measured 1–2 September 2026 —
and recover the same 77% charging behind a free listing and the same €39.99 median highest
purchase, while discovery failure is if anything worse (88% of sweep-classified apps absent
from the single obvious query, against 81%). The dataset remains narrow:
two categories, one storefront, one platform, a short window. We state this limitation
prominently and outline the replication programme the findings require, in particular an
extension to Google Play, whose different search architecture makes it a natural comparison
case.

---

## 1. Introduction

Textbook welfare results rest on assumptions that are rarely tested against particular markets:
participants can learn what is on offer, and prices convey what buyers will pay. Mobile
application stores are a useful setting in which to test both assumptions directly, for three
reasons. The supply is enumerable in principle, since every product is a listing with a public
page. The discovery mechanism is a single search engine controlled by the market operator. And
the displayed price is a standardised label chosen by the operator's interface, not by the
seller alone.

This paper reports a small, complete measurement of one category in one store: cooking apps in
the German iOS App Store. We attempted to enumerate the entire category rather than sample it,
first through a systematic search sweep and then by crawling the store's own recommendation
graph, and we then read the published price information of every app found. The exercise
produced two findings that we did not expect in their magnitude.

First, search misses most of the market. The large majority of apps that describe themselves as
recipe apps are unreachable through recipe-related search, and the set of apps that is reachable
is small, stable over time, and largely invariant to the query asked. Second, the displayed
price is uninformative for most of the category: roughly three quarters of apps labelled as free
charge money once opened, at price points the store's category view never displays.

We are deliberately cautious about generality. These are measurements of one category on one
storefront over two weeks, made by a small project, with a category boundary that we had to
correct four times before the figures stabilised (Section 3.3). We present them as preliminary
evidence and as a method that others can run, not as settled fact. Their interest lies in the
pattern they form when read against three established literatures: consumer search theory, which
predicts that even modest discovery frictions concentrate outcomes; the economics of shrouded
prices, which predicts that hidden charges persist under competition; and the platform
literature, which explains why the operator of a two-sided market may not have an incentive to
remove either friction. Section 6 sets out what a broader dataset, in particular Google Play
data, could confirm or overturn.

## 2. Related work

Four strands of literature frame the measurements.

**Consumer search and rankings.** Stigler (1961) treats information as a costly good; Diamond
(1971) shows that small search costs can move equilibrium prices to the monopoly level, because
no individual consumer finds further search worthwhile. In ranked online environments the
friction takes a specific form: position itself influences choices independently of relevance.
Ursu (2018) identifies this effect causally in hotel search data. For app markets specifically,
Ershov (2024) uses a natural experiment in the Google Play store to show that discovery costs
and congestion externalities shape entry and the quality of entrants, and Teng (2026),
exploiting a 2019 change in the U.S. Apple App Store's search algorithm, finds that rankings
significantly affect both app demand and developers' quality provision, and that the
self-preferencing embedded in the pre-change algorithm modestly reduced consumer welfare and
third-party profits. An early descriptive antecedent is Zhong and Michahelles (2013), who showed
that Google Play adoption follows a superstar rather than long-tail distribution and noted that
"the discovery of niche apps is still an intractable task." Industry data are consistent with
steep positional decay: Sensor Tower's *State of ASO* reports roughly 61% of search-driven
installs going to the top three results and under 4% beyond rank 30.

**Price opacity.** Gabaix and Laibson (2006) show that firms can shroud part of a price and that
shrouding survives competition, because a rival who discloses honestly loses the myopic customers
it educates. Ellison and Ellison (2009) document deliberate obfuscation raising margins in a
highly price-competitive online market. Blake, Moshary, Sweeney and Tadelis (2021) provide
experimental magnitudes: on StubHub, revealing fees only at checkout raised consumer spending by
approximately 21% and worsened the quality of choices. Dranove and Jin (2010) survey the
disclosure and certification literature and find that credible third-party measurement can
correct outcomes where self-disclosure fails.

**Platforms and gatekeeping.** Rochet and Tirole (2003) and Armstrong (2006) establish that
two-sided platforms set structurally skewed prices and that competition between platforms does
not guarantee efficiency on them. Wang and Wright (2017) analyse ad-valorem platform fees. Prat
and Valletti (2022) model platforms as attention brokers and show that concentration among them
tightens the bottleneck through which producers reach consumers, raising advertising prices and
harming entrants. Empirically, Decarolis and Rovigatti (2021) show that concentration measurably
moves online advertising auction outcomes, and the Competition and Markets Authority (2020)
found approximately 80% of UK search and display advertising expenditure accruing to two firms.
Policy reports (Crémer, de Montjoye and Schweitzer 2019; Furman et al. 2019; Stigler Center
2019) converge on the diagnosis that digital gatekeeper positions are entrenched; under the EU
Digital Markets Act (Regulation (EU) 2022/1925), Alphabet, Apple, Meta and ByteDance are
designated gatekeepers. Wen and Zhu (2019) and Zhu and Liu (2018) document how platform owners'
dual role distorts the behaviour of the complementors who depend on them. For app stores
specifically, Jamison, Tęcza and Wang (2026) estimate the effects of first-party entry on
direct rivals using a stacked difference-in-differences design over a Sensor Tower panel of
roughly 406,900 apps (2012–2021): on iOS, rivals' downloads and revenue fall by 53.7% and 58.6%
at their height within two years of Apple's entry, while equivalent entry on Google Play shows
no statistically significant effects — evidence both that the platform's conduct moves market
outcomes and that the two stores behave differently. On the advertising side, Ju, Zhao and Aral
(2026) use a global shutoff of paid install advertising at a major U.S. mobile game developer to
show that paid installs raise store rankings, which in turn generate organic installs (a 20–30%
organic decline after the shutoff, with the effect fully mediated by rank): in app stores, paid
acquisition purchases organic visibility itself. Beyond app stores, regulators have published
the structured analyses closest to our question: the Netherlands Authority for Consumers and
Markets (2019) examined Apple's and Google's incentive and ability to influence the availability
and findability of apps; the CMA (2022) found the two firms hold entrenched market power over
native app distribution (over 90% of UK native app downloads in 2020); and the ACCC (2021)
reached parallel conclusions for Australia. None of these measures category recall.

**Algorithm audits and machine-mediated discovery.** Methodologically, this study is an external
algorithm audit in the tradition reviewed by Bandy (2021): repeated, dated queries by an outside
party against a ranking system whose internals are unobservable. Web search engines and
recommender systems have been audited this way for a decade; we are not aware of a published
algorithm audit of app store search. The operator's side of the curtain is visible in
Christakopoulou et al. (2026), an Apple paper describing the App Store ranker as optimizing
behavioral and textual relevance and validating changes by a worldwide A/B test on conversion
rate — a published statement that the ranking objective is conversion, with the largest
improvements from synthetic relevance labels arising in tail queries where behavioral signals
are sparse. Finally, Motger et al. (2025) evaluate five commercial large language models as an
emerging app-discovery channel across thousands of queries, finding ranking criteria only
partially aligned with store metrics, stable top recommendations within models, and low
agreement between models — early evidence on the channel to which the discovery question is
migrating.

To our knowledge, no published study enumerates a complete store category and measures the share
of it reachable through search, and none measures "free" labelling against published in-app
price lists at category scale. We state this as an absence we could not fill by searching, not
as a certainty, and would welcome correction. Our contribution is not theoretical: it is a
small, complete, dated measurement of recall and price transparency in one real category, with
published instruments, intended to connect these literatures to observable magnitudes.

## 3. Data and method

### 3.1 Enumerating the category

We define the target population as applications available on the German iOS storefront whose
store listing identifies them as cooking or recipe applications. Enumeration proceeded in two
stages.

*Stage one: search sweep (19 August 2026).* We ran 25 German-language queries covering the
category's vocabulary (recipes, cooking, baking, meal planning, and appliance- and diet-specific
terms) against the store's search interface and recorded every result with its position. The
sweep returned 1,312 distinct apps, of which 715 were classified as cooking apps whose own
German description identifies them as recipe apps. The best single query surfaced 14% of the
apps the whole sweep found; 62.5% of swept apps were reachable through exactly one of the 25
queries.

*Stage two: recommendation-graph crawl (21 August – 1 September 2026).* Because a search sweep
can only find what search returns, we then crawled the store's own "similar apps" links,
starting from the swept set and following links until growth was exhausted. The first hop added
243 cooking apps not surfaced by any query; the second hop added 50. Growth fell from +35% to
+5% in one step, which we read as approaching closure. The resulting lower bound for the
category is 991 cooking apps, of which 941 are served by our index with price data and 50
remain price-unverified.

### 3.2 Price reading

For each of the 941 indexed apps we read the published in-app purchase list from the store's own
product pages (20–23 August 2026, basis corrected 31 August). We record the highest single
listed in-app purchase per app. We do not annualise: the store does not reliably publish billing
periods, so a figure such as €599.99 is reported as a highest single purchase, never as a yearly
price.

### 3.3 Classification and corrections

Deciding what counts as a cooking app was the largest source of error and we document our
failures because they bound the reliability of the figures. Our first classifier matched the
German word *Rezept*, which means both recipe and medical prescription, and wrongly included
pharmacy applications. A second pass removed cooking games matching *Kochen* and *Backen*; a
third caught children's cooking games filed under Education; a fourth (31 August 2026) caught
cooking-magazine ePaper apps whose subscription prices had contaminated the price figures. Across
the four passes the headline search figure moved from 82.4% to 82.8% to 81.0%, and the price
figure remained at 77%. We take the stability of the headlines under reclassification as
evidence that the findings do not depend on where the category boundary is drawn, while noting
that keyword classification has limits that only manual review or a second rater could quantify.

Denominators differ across findings for a reason we make explicit: the 81% search-absence figure
is computed against the 715 search-swept apps, because apps discovered only through the
recommendation graph were never in a search result and including them in a "never appears in
search" statistic would be circular. Price figures use the 941 indexed apps, since a price is a
price regardless of how the app was found.

### 3.4 What we cannot observe

The store places auctioned advertising slots above organic results (per Apple's developer
communications, multiple slots within a single result page since 3 March 2026). These slots are
personalised and cannot be independently observed, by us or by anyone outside the operator. All
visibility figures below are therefore computed from organic results only and overstate, rather
than understate, the visibility of organic listings in the rendered store.

## 4. Results

### 4.1 Recall

Of the 715 self-described recipe apps found by the sweep, 579 (81.0%) appear in none of the 25
queries' result lists. Extending to the crawled category: across all 25 queries there are 674
first-30 result slots, and 92 of the at least 991 category apps (9.3%) ever occupy any of them.
The remaining 897 apps are not ranked low; they are absent.

The apps that search misses are systematically different from those it finds. The median app
surfaced by search has a small number of ratings; the median app found only through the
recommendation graph has zero. Search does not sample the category; it samples its most
established stratum.

### 4.2 Concentration and stability of the visible set

The visible set is small, concentrated and stable. Ten apps hold 39% of all first-30 slots
across the 25 queries. One app appears in 16 of the 25 first-30 lists, including queries for
meal planning and baking, and ranks first for six distinct queries. Two queries' first-30 lists
share a median of only 5% of their apps, and 63% of apps that ever enter a first-30 list do so
for exactly one query: varying the question varies the periphery, not the core. Re-running all
25 queries after 13 days (1 September 2026) left a median 92% of each first screen unchanged,
with an identical seven-app core.

Result quality at the margin is itself informative. On 1 September 2026 the sixth organic
result for the query „rezepte app" was an alarm-clock application and the tenth was a dental
practice's app, while 885 cooking apps appeared in no first dozen of any query. These are
single dated observations; store results move, and ours are timestamped so they can be checked
against any later date.

### 4.3 Ranking and observable quality signals

iOS search eligibility derives from an app's name (30 characters), subtitle (30) and a hidden
keyword field (100), with some smaller surfaces; the store description is not indexed. The
consequences are visible in individual cases, which we report as dated examples and not as
judgments of the apps involved. An app with 5,507 ratings and the query term in its subtitle
(*ZauberMix für Monsieur Cuisine*) was absent from the 168 results for „Rezepte" on 19 August
2026; so were apps with 1,879, 827 and 814 ratings whose descriptions or subtitles use the term.
An app whose name is nearly identical to the query string held position 8 with 12 ratings.
Whatever the ranking optimises, on this evidence it is not proportionate to accumulated user
assessment; approximately 160 characters of indexed metadata dominate it. This reading is
consistent with the operator's own published account: Christakopoulou et al. (2026) describe the
ranker's objective as behavioral plus textual relevance, with changes validated by their effect
on conversion rate — an objective in which neither maintenance nor accumulated user assessment
appears, and in which tail queries are acknowledged to lack reliable behavioral signal.

### 4.4 Price opacity

Of 907 category apps listed in the store as „Gratis", 697 (77%) charge money through in-app
purchases. The median app's highest listed purchase is €39.99. Twenty-six apps list a single
purchase above €100, four above €200, and the largest we found is €599.99. All of these prices
are published, on pages reached after the install decision is substantially made; none appears
in the category or search views where the word „Gratis" does. No individual listing violates
store rules. The aggregate effect is that the price signal visible at the point of choice is
uninformative for three quarters of the category.

## 5. Interpretation

Read against the literature of Section 2, the four results are not independent anomalies but the
predicted outcome of a specific structure.

The recall failure (4.1) converts Stigler's search friction into something closer to exclusion:
beyond the rendered results there is no channel at higher cost, there is no channel. Given
positional install decay of the magnitude the industry reports, a market that is in practice
three results deep concentrates demand on whoever holds those results, and the operator auctions
the top of them. Apple's own advertising sales material claims conversion rates above 60% for
this placement. The stability and query-invariance of the visible set (4.2) indicate that this
concentration is not the churn of a responsive ranking but a persistent allocation, and 4.3
indicates the allocation criterion is metadata rather than quality signals. Ursu's ranking
results, Teng's demand and quality estimates for this very store, and Ershov's congestion
results supply the causal mechanisms by which such an allocation reproduces itself. Ju, Zhao
and Aral (2026) close the loop on the paid side: because paid installs raise rankings that
generate organic installs, advertising expenditure buys not only the auctioned slot but organic
visibility itself, which converts the visibility war into a self-financing feedback rather than
a one-off toll.

The price result (4.4) matches the Gabaix–Laibson shrouding equilibrium closely enough to serve
as a field observation of it: when 77% of a category shrouds, non-disclosure is the equilibrium
strategy, and their model explains why no individual developer can profitably defect to honest
labelling. Two features aggravate the standard model here. The shrouding is implemented by the
marketplace's display architecture uniformly, not chosen listing by listing; and the operator
collects an ad-valorem commission of 15–30% on the shrouded revenue, so the party that could
impose transparency is remunerated in proportion to its absence (compare Wang and Wright 2017 on
ad-valorem platform fees).

The structural reading follows. Distribution of mobile software is effectively a duopoly;
paid reach to mobile users is concentrated among a small group of advertising platforms
(industry aggregates attribute roughly two thirds of mobile advertising expenditure to Google,
Meta and TikTok; we flag this as a single-source, indicative figure, though company-reported
revenues and the CMA's UK findings support the order of magnitude). The store operators sell
advertising against their own organic results and tax the transactions that result. Developer
expenditure on user acquisition, reported by AppsFlyer at $78 billion in 2025 against roughly
$166 billion of consumer spending in the two major stores (Business of Apps), is on this reading
not a marketing anomaly but the rent generated by constructed scarcity of visibility, in the
sense of Tullock (1967) and, for advertising specifically, Dixit and Norman (1978). Prat and
Valletti (2022) describe the welfare consequences of exactly this configuration. We stress that
this section is interpretation; the measurements in Section 4 stand independently of it, and
alternative readings are discussed below.

## 6. A second category: sleep and meditation

The measurements above concern one category, and the obvious objection is that cooking apps
might be special. To test this we repeated the entire pipeline on a second, deliberately
dissimilar category on the same German iOS storefront: sleep and meditation apps, measured 1–2
September 2026. Where the recipe market is fragmented, this one is anchored by a few large
subscription products; if low transparency were a symptom of fragmentation it should weaken
here. The protocol — seed queries and classification rules frozen before counting, every later
rule change dated with the error class that motivated it — is published alongside the cooking
protocol, as are all scripts. Classification again surfaced category-specific homonym traps
(German *wickel* inside *entwickelt*; English *slim* inside *Muslim*), each recorded and
word-bounded on the day it was found.

A 25-query German sweep returned 1,766 distinct apps, of which 1,155 remain after
classification. Four hops over Apple's own similar-apps recommendation graph, each hop's finds
classified on full descriptions under identical rules, added a further 1,188, 739, 366 and 130
category apps — apps that appear in no result of any of the 25 queries. The classified category
therefore holds **at least 3,578 apps, of which 2,423 (68%) never appeared in any query of the
sweep**. The hop deltas shrink at a steepening rate (ratios 0.62, 0.49, 0.36), so the closure
converges geometrically towards a ceiling near 3,650 — unlike the cooking graph, which hop 2
effectively closed, but a bounded process in both cases.

Price opacity replicates in near-identical form. Of the 3,578 apps, **3,417 (96%) are listed as
free** (German *Gratis*). Product pages could be read for 3,351 of them; 66 are recorded as not
collected and are excluded from the percentages rather than assumed either way. **Of those
3,351, 77% charge for use through in-app purchases — the same share as in cooking — with a
median highest single purchase of €39.99, to the cent the cooking median.** The largest single
purchase found behind the word *Gratis* is **€1,199.99**, for an item the developer labels a
yearly subscription (cooking: €599.99). As in the cooking measurement no billing periods are
inferred and nothing is annualised: the figure is the price of one purchasable item as Apple
publishes it, and the developer's own label is reported, not converted.

Discovery failure replicates too, and **the prediction we made about it was wrong**. We
expected a concentrated category to be more discoverable: if recall failure were a symptom of
fragmentation, a market anchored by a few dominant products should have more of its mass inside
the queries people actually type. It does not. Measured as in Section 4.1 — absence from the
single obvious query, over the apps the sweep itself classified — **1,013 of 1,155 (88%)** of
sleep apps never appear in the results for *schlaf*, against 81% for *rezepte* in cooking
(*meditation* as the obvious query gives 86%). Measured over the whole closed category, 68% of
this category is reachable only through the recommendation graph, against 28% in cooking. On
both measures the concentrated category is **less** discoverable, not more. The closure also
needed four hops rather than two, so the tail is larger and more diffuse even though the head
is more concentrated. None of this touches the price result, which replicates exactly.

*These two measures are distinct and we keep them apart deliberately: an earlier version of this
section compared this category's 68% against cooking's 81% as if they were one measure and drew
the opposite conclusion. The correction is dated and published in
`second-category-findings.md`.*

The replication matters more than either category alone. Two categories chosen for structural
dissimilarity, measured with the same frozen instrument seven weeks apart, return **the same
77% and the same €39.99 median**. That is the point at which "cooking apps may be
unrepresentative" stops being the live objection and price opacity starts looking like a
property of how the store labels products rather than of any one market within it. It is two
categories, not twenty, and we claim no more than that; the honest reading is that the first
attempted refutation of the cooking result failed to refute it.

## 7. Limitations and the required broadening of the dataset

The dataset behind this paper is deliberately deep and correspondingly narrow, and we regard the
following limitations as binding until replication removes them.

**Two categories — the first replication is in, the limitation is narrowed rather than
removed.** The cooking result no longer stands alone: Section 6 reports the same pipeline run
over sleep and meditation apps, a category chosen for structural dissimilarity, returning the
same 77% charging behind a free listing and the same €39.99 median highest purchase. That
disposes of the specific objection that cooking is unrepresentative *on the price findings*.
It does not make the result general. Both categories are consumer-facing and both sit on the
same storefront. The recall figures differ between them in the same direction on both measures
(88% against 81% for the obvious query; 68% against 28% for graph-only reachability), which
refutes the concentration hypothesis we went in with rather than confirming it, and shows that
discovery failure varies with category structure in a way price opacity does not. Categories
with professional buyers, fewer sellers or stronger brands remain unmeasured, and replication
across several more — ideally chosen by someone other than us — is still the immediate next
step.

**One storefront and one platform.** All figures come from the German iOS storefront. Search
behaviour, category vocabulary and price levels differ across countries; more importantly, the
entire analysis covers only one of the two dominant stores. The extension we consider most
informative is to **Google Play**, for a substantive rather than merely additive reason: Play's
search architecture is generally reported to index the full store description, which iOS search
does not. The two stores therefore differ on precisely the variable our recall findings turn on.
If Play, with description indexing, shows materially higher category recall for equivalent
queries, that would support the architectural explanation of Section 5; if recall is similarly
low despite the broader index, the explanation would shift towards ranking behaviour and
positional demand decay. Either outcome is informative, which is what makes the comparison worth
running. There is direct evidence that the two stores are not interchangeable: Jamison, Tęcza
and Wang (2026) find large first-party entry effects on iOS and none on Play from the same
design, so results from one store cannot be presumed for the other. A Play extension would also
test the price-opacity result under a different fee and labelling regime, and Ershov (2024)
demonstrates that Play data can support quasi-experimental designs beyond our descriptive ones.
A further extension follows from Motger et al. (2025): the same recall measurement can be run
against language-model assistants as a discovery channel, asking what fraction of the enumerated
category any assistant ever recommends — the natural sequel once the category closure exists.

**A two-week window.** Our stability result covers 13 days. Longer longitudinal tracking is
needed to distinguish a persistently frozen visible set from slow rotation, and to observe how
rankings respond to app updates, price changes and seasonal demand.

**Classification error.** Section 3.3 documents four correction passes. The headline figures
were stable across passes, but a keyword classifier has an error rate we have not formally
quantified; a manually labelled validation sample would put confidence bounds on the 81% and 77%
figures. We note that the store's own results exhibit the same German homonym error we first
made, returning a prescription-related result at position one for a recipe query, which we
record without inferring anything beyond the observation.

**Unobservable advertising slots.** Because personalised ad placements cannot be observed
externally, our visibility figures describe the organic layer only. Any full welfare statement
about the rendered store requires data only the operators hold. This asymmetry of observability
is itself a finding of sorts, but it caps what outside measurement can establish.

**Interpretation is underdetermined.** The structural reading of Section 5 is consistent with
our data but not compelled by it. Alternative accounts deserve statement: store curation
solves real problems of malware and payment fraud that pre-store distribution did not, and
nothing in our data weighs that benefit; a defender of current search design could argue that
shallow, stable results economise on consumer attention for the typical user, at the cost of the
marginal one; and advertising can be informative rather than purely positional (Becker and
Murphy 1993), although a paid slot above organic results the same firm ranks fits the positional
case better. Deciding among these accounts requires the broader dataset described above, and
ideally operator data that external researchers currently cannot obtain.

## 8. Conclusion

In the one corner of the mobile software market we measured completely, the two informational
preconditions of an efficient market fail together: most of the supply is invisible to search,
and most displayed prices misstate the cost of use. Both failures are consistent with the
economics of search, shrouding and platform intermediation, and both are located in design
choices of the market operator rather than in the conduct of individual sellers. The magnitudes
are large enough that, if they replicate across categories and stores, they bear on current
regulatory debates about gatekeeper obligations for transparency and data access.

We circulate these results at a deliberately early stage because their chief value is
methodological: the measurements are cheap, the instruments are published, and any reader can
re-run them against the store as it stands today. Independent, dated, reproducible measurement
of marketplaces that have so far been measured only by their operators seems to us a reasonable
public good regardless of how our particular interpretation fares, and we would consider the
paper successful if it is primarily the method, and the criticism of it, that travels.

---

## References

- Akerlof, G. (1970). The Market for "Lemons": Quality Uncertainty and the Market Mechanism. *Quarterly Journal of Economics* 84(3), 488–500.
- Armstrong, M. (2006). Competition in Two-Sided Markets. *RAND Journal of Economics* 37(3), 668–691.
- Authority for Consumers and Markets [ACM] (2019). *Market Study into Mobile App Stores.* The Hague, 11 April 2019.
- Australian Competition and Consumer Commission [ACCC] (2021). *Digital Platform Services Inquiry, Second Interim Report: App Marketplaces.* March 2021.
- Bandy, J. (2021). Problematic Machine Behavior: A Systematic Literature Review of Algorithm Audits. *Proceedings of the ACM on Human-Computer Interaction* 5 (CSCW1), 1–34.
- Becker, G., and K. Murphy (1993). A Simple Theory of Advertising as a Good or Bad. *Quarterly Journal of Economics* 108(4), 941–964.
- Blake, T., S. Moshary, K. Sweeney, and S. Tadelis (2021). Price Salience and Product Choice. *Marketing Science* 40(4), 619–636.
- Christakopoulou, E., V. Patel, H. Velaga, S. Gaikwad, S. Suchter, and V. Sundaranatha (2026). Scaling Search Relevance: Augmenting App Store Ranking with LLM-Generated Judgments. arXiv:2602.23234; also published by ACM, July 2026.
- Competition and Markets Authority (2020). *Online Platforms and Digital Advertising: Market Study Final Report.* London.
- Competition and Markets Authority (2022). *Mobile Ecosystems: Market Study Final Report.* London.
- Crémer, J., Y.-A. de Montjoye, and H. Schweitzer (2019). *Competition Policy for the Digital Era.* European Commission.
- Decarolis, F., and G. Rovigatti (2021). From Mad Men to Maths Men: Concentration and Buyer Power in Online Advertising. *American Economic Review* 111(10), 3299–3327.
- Diamond, P. (1971). A Model of Price Adjustment. *Journal of Economic Theory* 3(2), 156–168.
- Dixit, A., and V. Norman (1978). Advertising and Welfare. *Bell Journal of Economics* 9(1), 1–17.
- Dranove, D., and G. Z. Jin (2010). Quality Disclosure and Certification: Theory and Practice. *Journal of Economic Literature* 48(4), 935–963.
- Ellison, G., and S. F. Ellison (2009). Search, Obfuscation, and Price Elasticity on the Internet. *Econometrica* 77(2), 427–452.
- Ershov, D. (2024). Variety-Based Congestion in Online Markets: Evidence from Mobile Apps. *American Economic Journal: Microeconomics* 16(2).
- European Union (2022). Regulation (EU) 2022/1925 (Digital Markets Act).
- Furman, J., et al. (2019). *Unlocking Digital Competition: Report of the Digital Competition Expert Panel.* HM Treasury.
- Gabaix, X., and D. Laibson (2006). Shrouded Attributes, Consumer Myopia, and Information Suppression in Competitive Markets. *Quarterly Journal of Economics* 121(2), 505–540.
- Jamison, M. A., J. Tęcza, and P. H. Wang (2026). Effects of Platform Vertical Integration on Direct Competitors: Evidence from the Mobile Application Market. Working paper, University of Florida PURC, 3 April 2026.
- Ju, H., M. Zhao, and S. Aral (2026). Advertising Spillovers in Mobile Apps: Evidence from Ad Shutoffs and Store Rankings. arXiv:2504.16151, revised July 2026.
- Motger, Q., X. Franch, V. Gervasi, and J. Marco (2025). Evaluating LLM-Based Mobile App Recommendations: An Empirical Study. arXiv:2510.18364.
- Prat, A., and T. Valletti (2022). Attention Oligopoly. *American Economic Journal: Microeconomics* 14(3), 530–557.
- Rochet, J.-C., and J. Tirole (2003). Platform Competition in Two-Sided Markets. *Journal of the European Economic Association* 1(4), 990–1029.
- Stigler, G. (1961). The Economics of Information. *Journal of Political Economy* 69(3), 213–225.
- Stigler Center (2019). *Committee for the Study of Digital Platforms: Final Report.* University of Chicago.
- Teng, X. (2026). Self-Preferencing, Quality Competition, and Welfare in Mobile Application Markets. CESifo Working Paper No. 10042 (original version October 2022; this version January 2026).
- Tullock, G. (1967). The Welfare Costs of Tariffs, Monopolies, and Theft. *Western Economic Journal* 5(3), 224–232.
- Ursu, R. M. (2018). The Power of Rankings: Quantifying the Effect of Rankings on Online Consumer Search and Purchase Decisions. *Marketing Science* 37(4), 530–552.
- Wang, Z., and J. Wright (2017). Ad Valorem Platform Fees, Indirect Taxation, and Efficient Price Discrimination. *RAND Journal of Economics* 48(2), 467–484.
- Wen, W., and F. Zhu (2019). Threat of Platform-Owner Entry and Complementor Responses: Evidence from the Mobile App Market. *Strategic Management Journal* 40(9), 1336–1367.
- Zhong, N., and F. Michahelles (2013). Google Play Is Not a Long Tail Market: An Empirical Analysis of App Adoption on the Google Play App Market. *Proceedings of ACM SAC '13*, 499–504.
- Zhu, F., and Q. Liu (2018). Competing with Complementors: An Empirical Look at Amazon.com. *Strategic Management Journal* 39(10), 2618–2642.

**Industry and company sources quoted:** AppsFlyer (user-acquisition and app-marketing
expenditure, 2025); Business of Apps and store reporting (consumer spend; in-app advertising,
2025); Sensor Tower, *State of ASO* (positional install shares); Apple Ads sales material
(top-of-search conversion claim); Apple App Store Transparency Report 2025 (store size); Apple
and Google published commission terms; Apple developer communications on result-page ad slots
(March 2026); eMarketer and company reports (advertising revenues, 2025).

**Data and code:** all queries, crawl scripts, classification rules (including the four
documented correction passes) and raw result lists: openappindex.org/methode.

---

*Correspondence: via openappindex.org. This draft is circulated for discussion. Comments,
corrections and attempted refutations are explicitly welcome and will be published alongside
the data.*
