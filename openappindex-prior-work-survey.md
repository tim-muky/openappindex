# Prior work survey: who has measured this before?

*openAPPindex working note · 1 September 2026*

*Purpose: establish whether any structured analysis comparable to ours has been published, and
map the scientific literature on or adjacent to the topic, before circulating the working paper.
Method: targeted literature search, 1 September 2026. Update, same day: all items originally
flagged ⚠ have now been read in full (or verified against the primary source) and the working
paper has been revised accordingly; verified details below.*

---

## 1. The short answer

**Nobody appears to have published our exact measurement.** We found no study, academic or
regulatory, that enumerates a complete store category and measures what fraction of it is
reachable through search (category recall), nor one that measures the share of "free"-labelled
apps carrying paid content at category scale with published instruments. The closest work
approaches the same territory from four directions without covering it: economists measure how
*ranking position* affects demand among apps that are ranked; regulators document gatekeeper
*power* without measuring recall; software-engineering researchers mine app stores at scale for
*development* insights, not market transparency; and the algorithm-audit literature supplies the
*method* without having applied it to app store search. This is good news for the paper's
contribution claim and it obliges us to position against all four strands precisely.

## 2. Directly adjacent: economics of app discovery and ranking

- **Ershov (2024), "Variety-Based Congestion in Online Markets: Evidence from Mobile Apps,"
  *AEJ: Microeconomics*.** The closest published economics paper. Uses a Google Play redesign as
  a natural experiment; shows discovery costs and congestion externalities shape entry and
  entrant quality. Measures the *consequences* of discovery friction; does not measure recall
  itself. Already cited in our draft.
- **Teng, X. (2026), "Self-Preferencing, Quality Competition, and Welfare in Mobile Application
  Markets," CESifo Working Paper 10042** (University of Munich; original version October 2022,
  this version January 2026; paper dated 30 September 2025). Read: title pages, abstract,
  introduction. The closest academic relative of our ranking findings and, per both the paper
  itself and Jamison et al. below, the *first and only* study of self-preferencing on app
  stores. Exploits Apple's 2019 U.S. search-algorithm change; finds rankings significantly
  affect app demand and developers' quality provision; a structural model implies existing
  self-preferencing slightly weakens quality competition and modestly reduces consumer welfare
  and third-party profits, with third parties' quality adjustment explaining 3% of the consumer
  welfare loss. Now cited in the working paper (§2, §5).
- **Jamison, M. A., J. Tęcza and P. H. Wang (2026), "Effects of Platform Vertical Integration
  on Direct Competitors: Evidence from the Mobile Application Market"** (working paper,
  University of Florida PURC, 3 April 2026). Read in full (front sections and results). Stacked
  difference-in-differences on a Sensor Tower monthly panel, Jan 2012 – May 2021 (Apple) and
  Jan 2014 – May 2021 (Play), ~406,900 apps covering 96% of global downloads; competitor
  "neighborhoods" defined via AlternativeTo.net; 6 Apple and 23 Google first-party apps. On
  iOS, first-party entry cuts direct rivals' downloads by 53.7% and revenue by 58.6% at their
  height 12–24 months after entry, with update frequency falling immediately and prices falling
  5.6% after one to two years; on Google Play the same design finds negative but mostly
  insignificant effects. Authors caution against one-size-fits-all ex-ante regulation. Now
  cited in the working paper (§2, §6) — the cross-store asymmetry independently strengthens the
  Play-replication argument.
- **Zhong and Michahelles (2013), "Google Play is not a long tail market," ACM SAC.** Early
  empirical demonstration that app adoption is a superstar market, not a long tail, and that
  "the discovery of niche apps is still an intractable task." Thirteen years old; describes the
  outcome distribution our recall measurement helps explain. Worth citing as the earliest
  statement of the problem.
- **Ju, H., M. Zhao and S. Aral (2026), "Advertising Spillovers in Mobile Apps: Evidence from
  Ad Shutoffs and Store Rankings" (arXiv 2504.16151, revised July 2026).** Read via abstract
  page in detail. A global shutoff of paid install ads at a major U.S. mobile game developer
  cut *organic* installs by 20–30%; panel estimates ($100 of ad spend ≈ 32 paid + 2.2 organic
  installs) match the event study, and the organic effect disappears once store rankings are
  controlled for — rankings fully mediate it. Implication for us: in app stores, paid
  acquisition purchases organic visibility itself, converting the visibility war into a
  self-financing feedback loop. Now cited in the working paper (§2, §5).
- **Rashid, M., O. Rafieian and S. Ghili (2025), "Auctions Meet Bandits: An Empirical
  Analysis" (arXiv 2508.21162).** Verified: pay-per-install sponsored-keyword auctions
  (second-price plus Thompson-sampling exploration) at a leading *Asian* mobile app store,
  focused on platform-side exploration policy. Adjacent but not needed for the current draft;
  keep on file for any future paid-discovery extension. Not cited.

## 3. Structured analyses by regulators (non-academic but directly on topic)

These are the only published *structured analyses* of app store discovery we found, and none
measures recall:

- **ACM Netherlands (2019), *Market study into mobile app stores*.** Explicitly analysed whether
  Apple and Google have "the incentive and the opportunity … to influence the availability of
  apps and the functioning thereof" — our question, answered at the level of incentives and
  interviews rather than measurement.
- **UK CMA (2022), *Mobile ecosystems market study* final report.** Apple and Google hold
  "substantial and entrenched market power" in native app distribution; over 90% of UK native
  app downloads in 2020 flowed through the two stores; the operators "unilaterally determine the
  rules of the game." Complements the CMA (2020) digital advertising study already in our
  references.
- **ACCC (2021), *Digital Platform Services Inquiry, Second Interim Report: App Marketplaces***
  (March 2021; verified). Finds Apple's App Store and Google's Play Store hold significant
  market power in app distribution in Australia; the two firms' mobile operating systems cover
  close to 100% of the market; flags developer access terms, payment arrangements, and alleged
  self-preferencing. Now cited in the working paper (§2).
- Context: the European Commission's 2014 intervention on "free" labelling of games with in-app
  purchases (Google dropped the label; Apple changed its download button from "Free" to "Get").
  Directly relevant to §4.4 of our paper: the *button* changed in 2014, yet we measure the
  storefront still presenting „Gratis" as the price signal in 2026, with 77% of the category
  charging. No follow-up measurement of this appears to have been published by anyone.

## 4. Software engineering and computer science

- **Martin, Sarro, Jia, Zhang and Harman (2017), "A Survey of App Store Analysis for Software
  Engineering," *IEEE TSE* 43(9).** Defines the "app store mining" field: hundreds of papers
  mining reviews, releases, and metadata — almost entirely for software-engineering ends
  (requirements, testing, release engineering), not market transparency. Establishes that
  large-scale store measurement is methodologically routine; nobody pointed it at recall.
- **Algorithm-audit literature.** Bandy (2021), "Problematic Machine Behavior: A Systematic
  Literature Review of Algorithm Audits," plus the search-engine audit methodology line
  (e.g. Ulloa et al. 2022 on scaling audits; news-search concentration audits using HHI/Gini).
  Web search engines and recommender systems have been audited this way for a decade; we found
  **no published algorithm audit of app store search**. Methodologically, our study *is* an
  external algorithm audit, and framing it in this vocabulary connects it to established
  standards (repeatability, dated snapshots, query panels).
- **Popularity-bias literature in recommender systems** (survey: Klimashevskaia et al. 2024,
  *UMUAI*): the store's "similar apps" graph and search both plausibly inherit popularity bias;
  this literature predicts our finding that search samples the established stratum.
- **Motger, Q., X. Franch, V. Gervasi and J. Marco (2025), "Evaluating LLM-Based Mobile App
  Recommendations: An Empirical Study" (arXiv 2510.18364).** Read in full (HTML). Evaluates
  five commercial LLMs (GPT-4o, Perplexity Sonar, Gemini 2.0 Flash, Claude Sonnet 4, Mistral
  Large 2) over thousands of queries. Findings: a taxonomy of 16 ranking criteria elicited from
  outputs, only 6 of which map to standard ASO metrics; top-ranked apps are stable within a
  model across runs but variability grows with depth (RBO at k=20 from 0.58 to 0.91 by model);
  agreement *between* models is low (Jaccard 0.23–0.39 at k=20). It does not quantify
  popularity bias against store data and does not measure recall — which leaves our proposed
  assistant-recall measurement open. Now cited in the working paper (§2, §6).
- **Christakopoulou, E., V. Patel, H. Velaga, S. Gaikwad, S. Suchter and V. Sundaranatha
  (2026), "Scaling Search Relevance: Augmenting App Store Ranking with LLM-Generated
  Judgments" (arXiv 2602.23234; ACM, July 2026).** Verified — an Apple team writing about the
  App Store ranker itself. The ranker optimizes behavioral relevance (clicks/downloads) plus
  textual relevance; expert relevance labels are scarce, so millions of LLM-generated labels
  were added; a worldwide A/B test showed +0.24% conversion, with the largest gains in tail
  queries "in the absence of reliable behavioral relevance labels." Valuable to us twice: the
  operator's published objective is conversion (not maintenance or accumulated assessment), and
  the operator itself documents weak signal on tail queries, which is where our invisible 91%
  lives. Now cited in the working paper (§2, §4.3).

## 5. Price-transparency side

Academic anchors are the ones already in our references (Gabaix–Laibson 2006; Ellison–Ellison
2009; Blake et al. 2021; Dranove–Jin 2010). What is missing in the literature is any
*measurement of the app-store "free" label against actual in-app price lists at category scale*.
The 2014 regulatory episode (§3) shows the issue was recognised and partially acted on; consumer
and children's-media commentary documents the harm anecdotally; we found no systematic
measurement since. Our 77% figure appears to be the first of its kind — a strong claim, so the
paper should state it as "we are not aware of a prior category-scale measurement," which is
accurate and falsifiable.

## 6. Consequences for the working paper

1. **The contribution claim survives contact with the literature**: complete-category recall
   measurement and category-scale price-label measurement both appear novel. State the novelty
   modestly and falsifiably.
2. **Add to related work**: the CESifo self-preferencing paper (closest relative), Zhong &
   Michahelles 2013 (earliest statement), ACM Netherlands 2019 + CMA 2022 (regulatory
   structured analyses), and the algorithm-audit framing (Bandy 2021) as the methodological
   home of our study.
3. **The Play-replication argument gets stronger**: the vertical-integration paper's finding
   that iOS and Play respond differently to platform behaviour is independent evidence that the
   cross-store comparison is informative, not duplicative.
4. ~~Read before citing: the five ⚠ items.~~ Done (1 September 2026): all flagged items read or
   verified against primary sources; the working paper's related work, interpretation,
   limitations and references were updated the same day. One correction from full reading: the
   arXiv 2504.16151 paper's actual title is "Advertising Spillovers in Mobile Apps," not the
   earlier working title, and the "Auctions Meet Bandits" paper concerns an Asian store's
   sponsored-keyword auctions and is filed as background rather than cited.
