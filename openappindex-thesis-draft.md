# Constructed Opacity

### A thesis on why the mobile app economy fails the tests of a fair and transparent market — and why that failure is profitable

*Draft v0.1 · openAPPindex · September 2026*

*Status: working draft for internal discussion. Every empirical claim marked "our measurement" is
reproducible from the published scripts and carries its measurement date; third-party and company
figures are attributed inline; the literature is cited in full at the end. Follows the openAPPindex
evidence rules: dated facts, stated denominators, no verdicts on named apps.*

---

## The thesis

**The mobile app economy fails the minimum conditions economics sets for a fair and transparent
market — symmetric information, contestable entry, and prices that state true costs — and it fails
them by construction, not by accident. Its discovery layer, its advertising layer, and its billing
layer are operated by the same short list of vertically interlocked firms, which form an oligopoly
whose revenues grow with the opacity of the market they intermediate. The resulting equilibrium is
allocatively, productively, and dynamically inefficient, and the costs fall on everyone outside the
oligopoly: consumers pay in money and attention, developers pay in rents for visibility, and
society pays in misdirected innovation. Because the inefficiency is the revenue model, the market
cannot be expected to correct itself; correction requires independent measurement infrastructure
from outside it.**

Four claims, defended in order:

1. **Inefficient in information** — the discovery mechanism suppresses most of the relevant
   information (§2).
2. **Inefficient in prices** — the displayed price systematically misstates the true price (§3).
3. **Oligopolistic in structure** — distribution is a duopoly and paid discovery a tight
   oligopoly, run by the same firms that tax the transactions they intermediate (§4).
4. **Harmful in aggregate** — the equilibrium destroys measurable welfare and cannot self-correct
   (§5–§6).

---

## 1. What economics demands of a fair market

The benchmark is old and explicit. The first welfare theorem delivers efficiency only under
conditions that include full information and free entry; every deviation from those conditions is
a named field of economics with known welfare losses.

Three strands define the test we apply:

- **Information economics.** Stigler (1961) established that information is a costly good and
  that search costs alone sustain price dispersion. Diamond (1971) sharpened this into a paradox:
  with even *small* search costs, the competitive equilibrium collapses to the monopoly price,
  because no consumer finds it worthwhile to check one more seller. Akerlof (1970) showed the
  quality-side analogue: when buyers cannot observe quality, good products are driven out and the
  market degrades or unravels.
- **Price transparency.** Gabaix and Laibson (2006) showed that firms can *shroud* attributes —
  hide part of the price — and that shrouding survives competition: a rival who unshrouds and
  advertises honest prices educates consumers who then buy the shrouded product anyway, so
  transparency is punished in equilibrium. Ellison and Ellison (2009) documented deliberate
  obfuscation raising margins in one of the most price-competitive markets on the internet; Blake,
  Moshary, Sweeney and Tadelis (2021) showed by randomized experiment on StubHub that revealing
  fees only at checkout raised consumer spending by roughly 21%.
- **Platform and attention economics.** Rochet and Tirole (2003) and Armstrong (2006) formalized
  two-sided markets: platforms set structurally skewed prices across the sides they connect, and
  competition *between* platforms does not guarantee efficiency *on* them. Prat and Valletti
  (2022) modeled the modern version — "attention brokers" that control access to consumers and
  sell it to producers — and showed that concentration among brokers tightens the attention
  bottleneck, raises ad prices, excludes entrants, and lowers consumer welfare in the product
  markets downstream. The policy literature (Crémer, de Montjoye and Schweitzer 2019; Furman et
  al. 2019; Stigler Center 2019; CMA 2020) converges on the same diagnosis: digital gatekeepers
  hold entrenched, self-reinforcing positions that ordinary competition does not erode.

A market is *fair* in this tradition when success correlates with quality and price rather than
with privileged access to the buyer; *transparent* when participants can learn what exists and
what it costs at reasonable expense. These are measurable properties. We measured them.

---

## 2. The information failure: a market that hides its own supply

**The finding (ours, DE App Store, cooking-app category, 19 Aug – 1 Sep 2026; scripts public):**
of 715 apps whose own German store description identifies them as recipe apps, **81% (579) never
appear** in any of 25 German-language recipe searches. Walking the store's own "similar apps"
links instead of searching grew the category by a third in one hop; the closure is **at least 991
cooking apps**, of which **92 — 9% — ever reach any first screen** of any query. Ten apps hold
39% of all first-30 slots across all 25 queries; re-running every query 13 days later left a
median **92% of each first screen unchanged**. The mechanism is documented, ordinary engineering:
iOS search indexes roughly 160 characters of metadata — name, subtitle, keyword field — and does
not index the description at all, so an app with 5,507 ratings and the query in its *subtitle*
can be absent from the 168 results for that query while a 12-rating app whose *name* is the query
holds position 8.

**What the literature says this is:**

- This is **Stigler's search-cost problem with the sign flipped**. In Stigler (1961) search costs
  are a natural friction the market grinds down over time. Here the friction is *set by the
  market's operator*: the store chooses what is indexed, how deep results go, and what ranks. The
  cost of discovering the 91% is not high — it is effectively infinite, because no user action
  reaches it. Sensor Tower's *State of ASO* puts ~61% of search-driven installs in the top three
  results and under 4% beyond rank 30; conditional on that behavior, an unranked app does not have
  a high search cost, it has no channel at all.
- The consequences are **Diamond (1971) at scale**. Diamond showed small search costs hand sellers
  monopoly power. A discovery layer that is, in practice, three results deep hands the *holders of
  those three slots* the corresponding rents — which is precisely why the top slot is auctioned
  (Apple's own sales material claims "conversion rates over 60%" for it). The rent is real,
  priced hourly, and collected by the party that created the scarcity.
- Rankings are not a neutral mirror of preferences. Ursu (2018) showed causally that position
  itself — independent of relevance — drives what consumers examine and buy. So a ranking that
  rewards 160 characters of metadata does not merely *reflect* a concentrated market; it
  *manufactures* one. Our overlap measurements make the point empirically: two different queries'
  first screens share a median of 5% of their apps, while the same ten apps sit atop everything —
  the shelf does not respond to the question asked.
- **Akerlof's lemons dynamic operates on the quality dimension the store does not display.** The
  two signals a buyer sees — a star average and the word "Gratis" — say nothing about whether an
  app is still maintained. A star average is a monument to the past; it keeps selling an app whose
  developer stopped caring years ago (our index shows apps last updated 1,700+ days ago
  billing subscriptions today). When care is unobservable, the return to care falls, and the
  market selects for what *is* observable: metadata engineering and ad budgets. That is adverse
  selection against maintenance — lemons, with extra steps.
- Ershov (2024) provides the closest controlled evidence: in Google Play data, discovery
  frictions and congestion externalities directly shape entry and entrant quality — visibility,
  not quality, is the binding constraint in app markets. Our measurement of the same phenomenon
  from the outside: the median app found by search has a handful of ratings; the median app found
  *only* by following the store's own links has zero. The invisible majority is not a tail of
  junk; it is simply unlit.

**Verdict on claim 1:** a market in which 9% of verified supply is ever visible, in which
visibility is orthogonal to quality and stable across queries and weeks, fails the information
condition not marginally but categorically. The literature's term for what fills the gap is
*rent*, and §4 shows who collects it.

---

## 3. The price failure: "Gratis" as a shrouded attribute

**The finding (ours, 20–23 Aug 2026, basis corrected 31 Aug; denominator: the 907 cooking apps
listed as „Gratis" among the 941 the index serves):** **77% of apps labeled „Gratis" charge money
once opened.** The median app's highest single in-app purchase is **€39.99**; twenty-six exceed
€100; the largest is €599.99. No individual developer is lying — the prices are published, on a
page reached after the choice is substantially made. The *store* displays the word and not the
number, and takes a 15–30% commission on the difference between them.

**What the literature says this is:**

- A textbook **shrouded attribute** (Gabaix and Laibson 2006). The base good is advertised at
  zero; the true cost sits in an add-on revealed late. Gabaix and Laibson's central result
  explains the 77%: shrouding is an *equilibrium*, not a scattering of bad actors. A developer
  who prices honestly up front loses the install to a "Gratis" rival before the buyer ever sees
  either price list; unshrouding is punished, so honest pricing is selected *against*. When 77%
  of a category shrouds, that is the theory's prediction confirmed, not exceeded.
- The **magnitude** of the harm is experimentally established. Blake et al. (2021) randomized
  fee disclosure timing on StubHub: back-loading fees raised spending ~21% and degraded the
  quality of choices. The app store's architecture back-loads essentially *all* of the price for
  77% of the category — and unlike StubHub's checkout, the subscription price arrives after
  onboarding, inside the product, at maximum psychological commitment.
- Ellison and Ellison (2009) supply the strategic frame: obfuscation is an investment that raises
  margins by frustrating comparison. Here the obfuscation is not even the developer's investment —
  it is the *store's display choice*, uniform across two million apps, and the store is paid in
  proportion to what obfuscation extracts. An intermediary that earns an ad-valorem commission on
  shrouded prices has a direct, mechanical stake in shrouding (on the distortive potential of
  ad-valorem platform fees, see Wang and Wright 2017).

**Verdict on claim 2:** the single most decision-relevant fact about a product — what it costs —
is systematically misstated at the point of decision, in an equilibrium the literature predicted,
under a fee structure that pays the market operator for the misstatement. The transparency
condition fails, and the failure has an owner.

---

## 4. The structure: an interlocked oligopoly, taxed at every step

Strip the market to its plumbing and count the firms.

- **Distribution** is a duopoly. Two stores mediate effectively all mobile software distribution
  in the West; on iOS, one. The policy literature is unambiguous that these positions are
  entrenched and not contestable (Crémer et al. 2019; Furman et al. 2019; CMA 2020), and the EU
  has made the finding legal fact: Alphabet, Apple, Meta and ByteDance are all designated
  gatekeepers under the Digital Markets Act (Regulation (EU) 2022/1925) — the same four firms
  this section counts.
- **Paid discovery** is a tight oligopoly. Google, Meta and TikTok together take roughly two
  thirds of mobile ad spend (industry aggregate; single secondary source, treat as indicative);
  Google booked about $295bn in advertising in 2025, Meta $196bn, TikTok around $32bn (company
  reporting / eMarketer). Apple auctions the top of its own search results — an ads business
  estimated near $7.4bn — and since March 2026 places multiple ad slots inside a single result
  page (Apple developer communication). The CMA (2020) found ~80% of UK search and display spend
  going to two firms and concluded competition in these markets is "weak to the detriment of
  consumers"; Prat and Valletti (2022) supply the mechanism — concentrated attention brokers
  tighten the bottleneck, raise ad prices, and exclude entrants from product markets. (Decarolis
  and Rovigatti 2021 show, from the other side, how much auction outcomes move with concentration:
  market power in ad markets is real enough that buyer-side consolidation measurably shifts
  prices.)
- **The same firms hold multiple roles at once.** Apple and Google each: operate the store,
  design the search that makes organic visibility scarce, sell the ad slots that relieve the
  scarcity, and take 15–30% of the revenue the purchased visibility produces. This is the
  conflicted dual role — referee, bookmaker, and toll collector — that the self-preferencing
  literature identifies as structurally corrosive: platform owners that compete with or tax their
  complementors distort complementor entry and innovation even without overt abuse (Zhu and Liu
  2018; Wen and Zhu 2019). Meta and TikTok hold no store at all and need none: they charge for
  access to the users the stores made hard to reach organically. The four firms are not a cartel
  and do not need to be one; their incentives are aligned by construction, each collecting a
  different toll on the same forced detour.

Formally: the discovery layer is a two-sided market (Rochet–Tirole 2003; Armstrong 2006) in
which the platform's profit-maximizing structure is exactly what we measure — organic visibility
kept scarce and unresponsive (§2), the scarcity sold by auction, and the seller side taxed
ad valorem. Two-sided-market theory is explicit that this can be privately optimal and socially
inefficient at once; the sides do not internalize each other's losses, and the platform
internalizes only what it can bill.

**Verdict on claim 3:** "oligopoly" is not rhetoric here; it is the count. Two firms control
distribution, three to four control paid reach, the intersection of those sets designs the
information environment of §2 and §3, and each is a legally designated gatekeeper. The market's
opacity is not a bug in this structure. It is the product.

---

## 5. The harm: what the equilibrium costs

**The aggregate accounting (2025 figures, attributed):** consumers spent roughly **$166bn** across
the App Store and Google Play (Business of Apps / store reporting). Developers spent **$78bn on
user acquisition** — $109bn on app marketing in total, up 13% year over year (AppsFlyer). In-app
advertising *inside* apps was worth a further **$151bn** (Business of Apps). For every €2 a
person spends on apps, close to €1 is spent by somebody trying to be found — money that never
touches the software.

The literature gives each part of this a name:

1. **Rent-seeking waste.** Visibility spend does not create value; it reallocates a fixed prize —
   the same finite installs — between contestants (Tullock 1967). Advertising that is persuasive
   and positional rather than informative is exactly the case where oligopoly generates *excessive*
   advertising relative to the social optimum (Dixit and Norman 1978). A $78bn arms race over
   ~$166bn of demand, with the arms dealer also running the battlefield, is rent dissipation at a
   ratio the rent-seeking literature would call spectacular.
2. **Allocative inefficiency.** §2's information failure means the match between user and app is
   made on 160 characters of metadata and ad budget, not on quality or fit; §3's price failure
   means the buyer's willingness-to-pay is elicited against a false price. Both mechanisms
   misallocate — the wrong apps are chosen, at prices that would not have been accepted if stated.
   Blake et al.'s 21% is a measured lower bound on the second distortion in a milder setting.
3. **Productive inefficiency and quality erosion.** The developer must recover the visibility
   spend from a higher price or more in-app advertising — the $151bn attention invoice. Product
   effort is substituted away from maintenance (unobservable, unrewarded — §2's lemons dynamic)
   toward metadata engineering and ad operations. The app gets *worse in order to afford being
   found.* Ershov (2024) documents the mechanism's grip on entry and entrant quality; Rosen's
   (1981) superstar economics explains the outcome distribution — tiny visibility advantages
   compound into extreme revenue concentration disconnected from proportionate quality
   differences.
4. **Dynamic harm.** Entry is deterred not by incumbents' efficiency but by the toll structure:
   a new entrant of arbitrary quality starts invisible (§2), must buy reach from the oligopoly
   (§4), and surrenders 15–30% of the proceeds. The gatekeeper reports (Crémer et al. 2019;
   Furman et al. 2019; Stigler Center 2019) all identify this innovation tax as the deepest cost —
   the products never built because the year of engineering was, as our manifesto puts it, the
   cheap part. This sits inside the broader documented rise of market power and markups across
   the economy (De Loecker, Eeckhout and Unger 2020), of which platform gatekeeping is the
   sharpest instance.
5. **The harm is regressive and attention-denominated.** The consumer pays three times: in the
   shrouded price, in the ad load that funds the visibility war, and in the degraded quality of
   the match. The attention cost falls hardest on users of "free" apps — disproportionately those
   with the least money — which is the distributional pattern the attention-broker literature
   predicts (Prat and Valletti 2022).

**Verdict on claim 4:** by every standard welfare category — allocative, productive, dynamic,
distributional — the equilibrium destroys value for every participant outside the oligopoly. The
sums are not marginal: the visibility war plus the attention invoice ($78bn + $151bn) are
together larger than the consumer spend they contest ($166bn).

---

## 6. Why it will not fix itself — and what follows

Three self-sealing mechanisms, each independently documented:

- **The behavioral loop.** A search that is three results deep teaches users not to scroll;
  users who do not scroll make the top slots worth everything; slots worth everything get
  auctioned; auctioned results get worse, which teaches users — correctly — not to scroll. Our
  13-day stability measurement (median 92% of each first screen unchanged; the same seven-app
  core) shows the loop at rest: there is nothing for an explorer to find.
- **The shrouded-price trap.** Gabaix–Laibson equilibrium: no developer can profitably defect to
  honest pricing, and the intermediary that could impose transparency is paid ad valorem on the
  shrouding. The only actor able to fix §3 is the one actor paid not to.
- **The corpus inheritance.** The question *which app should I use?* is migrating to AI
  assistants — the natural reset. But an assistant recommends from a corpus, and the available
  corpus is the one the store already distorted: incumbents loud enough to be in the training
  data. Our assistant-baseline measurements find the assistants recommending the same visible
  minority from memory. Absent an alternative corpus, the gatekeeper is replaced and the bias is
  inherited — harder to see, and no longer even auditable query by query.

The economics of disclosure points at the remedy. Dranove and Jin (2010), surveying the
certification and disclosure literature, find that credible third-party measurement changes
seller behavior and market outcomes where self-disclosure and platform disclosure fail — and that
the credibility of the certifier (independence, method transparency, no seller payments) is the
binding constraint. That is the institutional gap openAPPindex is built to fill: not a better
ranking inside the distorted candidate set, but the candidate set itself — recall before ranking —
with every fact dated, sourced, denominated, and reproducible, readable by people and by the
assistants that will make the next decade's recommendations. The stores became bottlenecks
because nobody outside could measure them. The thesis of this paper is that the measurement
itself is the missing market institution.

---

## 7. Honest limits and counterarguments

Stated per our evidence rules, because a thesis that hides its weaknesses commits the failure it
describes.

- **Scope.** Our measurements cover one category (cooking), one storefront (DE), one platform
  (iOS), over two weeks in August–September 2026. The mechanisms — 160 indexed characters,
  auctioned top slots, "Gratis" labeling, 15–30% commission — are store-wide by construction,
  but the *magnitudes* (81%, 77%, 9%) are category-specific until replicated. Replication in
  further categories is the immediate research program.
- **The curation defense.** Stores did solve real problems: malware, payment fraud, distribution
  cost. The pre-2008 counterfactual was worse on those axes. The thesis does not deny this; it
  observes that security curation does not require opaque discovery or shrouded pricing — the
  bundle is chosen, not forced.
- **Advertising as information.** Becker and Murphy (1993) model advertising as a complement to
  the good, not waste. This defense fits informative advertising in open media; it fits poorly a
  positional auction for a slot above organic results the same firm ranks, where the spend's
  function is displacement — the Dixit–Norman and Tullock cases, not the Becker–Murphy one.
- **Two-sided pricing skew can be efficient.** Rochet–Tirole warn against naive one-sided
  intuitions; a zero consumer price with seller-side fees is not inefficient per se. Granted —
  the thesis's claim is not that sellers pay and buyers don't, but that the *information
  environment* both sides transact in is degraded by the party pricing it.
- **Concentration numbers vary by source.** The "two thirds of mobile ad spend" figure is a
  single secondary aggregate and is labeled indicative here as everywhere we use it; the
  company-reported revenue figures and the CMA's 80% UK finding carry the structural argument on
  their own.

None of these limits touches the core: the welfare theorems' conditions are violated, the
violations are measurable, the violators are four designated gatekeepers, and the violation is
their revenue.

---

## References

**Our measurements** — openAPPindex, DE App Store cooking category, 19 Aug – 1 Sep 2026. Method,
scripts, raw data and published corrections: openappindex.org/methode. Denominators and dates as
stated inline; see the manifesto v0.8 source table for the claim-by-claim register.

**Literature**

- Akerlof, G. (1970). "The Market for 'Lemons': Quality Uncertainty and the Market Mechanism." *Quarterly Journal of Economics* 84(3), 488–500.
- Armstrong, M. (2006). "Competition in Two-Sided Markets." *RAND Journal of Economics* 37(3), 668–691.
- Becker, G., and K. Murphy (1993). "A Simple Theory of Advertising as a Good or Bad." *Quarterly Journal of Economics* 108(4), 941–964.
- Blake, T., S. Moshary, K. Sweeney, and S. Tadelis (2021). "Price Salience and Product Choice." *Marketing Science* 40(4), 619–636.
- Competition and Markets Authority (2020). *Online Platforms and Digital Advertising: Market Study Final Report.* London, 1 July 2020.
- Crémer, J., Y.-A. de Montjoye, and H. Schweitzer (2019). *Competition Policy for the Digital Era.* Report for the European Commission.
- De Loecker, J., J. Eeckhout, and G. Unger (2020). "The Rise of Market Power and the Macroeconomic Implications." *Quarterly Journal of Economics* 135(2), 561–644.
- Decarolis, F., and G. Rovigatti (2021). "From Mad Men to Maths Men: Concentration and Buyer Power in Online Advertising." *American Economic Review* 111(10), 3299–3327.
- Diamond, P. (1971). "A Model of Price Adjustment." *Journal of Economic Theory* 3(2), 156–168.
- Dixit, A., and V. Norman (1978). "Advertising and Welfare." *Bell Journal of Economics* 9(1), 1–17.
- Dranove, D., and G. Z. Jin (2010). "Quality Disclosure and Certification: Theory and Practice." *Journal of Economic Literature* 48(4), 935–963.
- Ellison, G., and S. F. Ellison (2009). "Search, Obfuscation, and Price Elasticity on the Internet." *Econometrica* 77(2), 427–452.
- Ershov, D. (2024). "Variety-Based Congestion in Online Markets: Evidence from Mobile Apps." *American Economic Journal: Microeconomics* 16(2).
- European Union (2022). Regulation (EU) 2022/1925 (Digital Markets Act); gatekeeper designations, September 2023.
- Furman, J., et al. (2019). *Unlocking Digital Competition: Report of the Digital Competition Expert Panel.* HM Treasury.
- Gabaix, X., and D. Laibson (2006). "Shrouded Attributes, Consumer Myopia, and Information Suppression in Competitive Markets." *Quarterly Journal of Economics* 121(2), 505–540.
- Prat, A., and T. Valletti (2022). "Attention Oligopoly." *American Economic Journal: Microeconomics* 14(3), 530–557.
- Rochet, J.-C., and J. Tirole (2003). "Platform Competition in Two-Sided Markets." *Journal of the European Economic Association* 1(4), 990–1029.
- Rosen, S. (1981). "The Economics of Superstars." *American Economic Review* 71(5), 845–858.
- Stigler, G. (1961). "The Economics of Information." *Journal of Political Economy* 69(3), 213–225.
- Stigler Center (2019). *Committee for the Study of Digital Platforms: Market Structure and Antitrust Subcommittee Report.* University of Chicago.
- Tullock, G. (1967). "The Welfare Costs of Tariffs, Monopolies, and Theft." *Western Economic Journal* 5(3), 224–232.
- Ursu, R. M. (2018). "The Power of Rankings: Quantifying the Effect of Rankings on Online Consumer Search and Purchase Decisions." *Marketing Science* 37(4), 530–552.
- Wang, Z., and J. Wright (2017). "Ad Valorem Platform Fees, Indirect Taxation, and Efficient Price Discrimination." *RAND Journal of Economics* 48(2), 467–484.
- Wen, W., and F. Zhu (2019). "Threat of Platform-Owner Entry and Complementor Responses: Evidence from the Mobile App Market." *Strategic Management Journal* 40(9), 1336–1367.
- Zhu, F., and Q. Liu (2018). "Competing with Complementors: An Empirical Look at Amazon.com." *Strategic Management Journal* 39(10), 2618–2642.

**Industry figures quoted** (attributed inline where used): AppsFlyer ($78bn UA / $109bn app
marketing, 2025); Business of Apps / store reporting ($166bn consumer spend; $151bn in-app
advertising, 2025); company reporting and eMarketer (Google ~$295bn, Meta $196bn, TikTok ~$32bn
advertising revenue, 2025); Apple Ads sales material ("conversion rates over 60%"); Apple 2025
App Store Transparency Report (2,172,472 apps); Sensor Tower *State of ASO* (~61% of search
installs to top three; <4% past rank 30); Apple and Google published terms (15–30% commission).

---

*Draft v0.1. The thesis attacks the system and names companies only via their own published
figures or their legal designation as gatekeepers. Named apps appear only as dated, measured
examples. Where a figure rests on a single secondary source it is labeled indicative inline.*
