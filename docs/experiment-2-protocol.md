# Experiment 2 — authority, admission, citation

**Written 2026-10-05. To be frozen by a public commit before the launch on 2026-10-14.** The
thresholds below were set by Tim Meyerdierks on 2026-10-05, before any data from this experiment
existed. As with the [GO/NO-GO gate](gate-protocol.md), the point of writing this first is that
the result cannot be rationalised afterwards. Amendments are dated, explained, and made before the
data they would affect.

---

## Why this experiment exists

The gate (GAL-518) asked whether search-augmented assistants would cite an independent app index.
It could not be scored as designed. Two of its three assistants retrieve through indexes that had
barely admitted the site: Bing 25 pages and Brave 0 on 2026-10-05, against ≥ 100 required. The
third, Perplexity, returned 0 citations in 30 scored answers, and may itself discover pages
through Bing (`gate-protocol.md` §1, observation of 2026-10-05). *(Added 2026-10-13, before
the freeze: the probe of 2026-10-07 counted against that observation under the rule fixed before it
ran; see the reading of 2026-10-13 in `gate-protocol.md` §1. The test below stays in place.)*

Bing's own diagnosis was *"Your site does not have enough inbound links from high quality
domains."* So the gate's result points at a chain the gate never measured:

> **external links → admission to retrieval indexes → citation by assistants**

The gate's §6 says that if it fails, the next question is to be "decided fresh". This is that
question. The gate measured whether citation happens on its own. This experiment measures whether
the chain holds once the first link in it is supplied deliberately.

## The intervention

From 2026-10-14, in this order, each step logged with its date in `experiment-2-log.md`:

1. **Data layer:** a Zenodo DOI for the dataset and the working paper, a Hugging Face dataset, and
   a GitHub README that leads with the findings.
2. **Press:** one German outlet and one Show HN post.
3. **Research:** contact with platform-regulation and consumer-protection researchers.

Nothing is paid for. No link is bought, exchanged or requested in return for anything. Wikipedia
and Wikidata are not edited by us.

## What is measured

| Instrument | What | When |
|---|---|---|
| Bing Webmaster Tools, Site Explorer | indexed URLs on openappindex.org, dated by crawl date | weekly |
| Brave Search, `site:openappindex.org` | result count | weekly |
| Google Search Console | indexed pages; the four original question pages | weekly |
| BWT AI Performance | Copilot and partner citations | weekly |
| Referring domains | see definition below | weekly |
| Cloudflare request log (from deployment) | referrers; requests from AI crawlers by user agent | continuous |
| Zenodo, Hugging Face, GitHub | views, downloads, stars | weekly |
| **Assistant runs** | the frozen 15 scored queries + 3 controls from `gate-protocol.md` §2, wording unchanged | monthly, two runs on different days |

**Assistant runs.** Perplexity, ChatGPT with search, and Claude with web search, each on its
consumer product. Every capture records the account state (logged-in or not, and whether the
account's history contains this project). Perplexity is run on a session without the project in
its history, because the gate's account was observed shaping answers from earlier searches
(`gate-result.md` §5b). Captures are checked inside the answer element only; the sidebar trap of
2026-09-23 applies.

**Testing the Bing hypothesis.** On every Perplexity run day, BWT Search Performance is read for
impressions whose query text matches a scored query issued that day. If they appear, Perplexity's
retrieval goes through Bing, and the Perplexity leg is gated by Bing. That reading is recorded and
does not count toward the bar.

## Definitions

- **Citation:** the answer, its inline citations or its source list link to any openAPPindex
  host: `openappindex.org`, the project's Zenodo records, its Hugging Face dataset, or
  `github.com/tim-muky/openappindex`. **Any host counts** (decided 2026-10-05). Citations of the
  domain itself are reported separately next to the headline every time.
- **Scored query:** one of the 15 target queries. Citations on the 3 controls count *against*
  the experiment, as in the gate.
- **Referring domain:** a registrable domain that is not ours and links to a page on
  openappindex.org, as reported by BWT Backlinks, GSC Links or the Cloudflare referrer log, and
  confirmed by fetching the linking page. *Not ours* excludes the project's GitHub, Zenodo and
  Hugging Face pages, galleybook's properties, and any account Tim controls. Social-media posts
  count only if the linking page can be fetched without logging in.

## The bar — frozen

Horizon **2027-01-15**. Readings are also taken on 2026-11-15 and 2026-12-15; they are reported
but not scored.

| Result | Condition on 2027-01-15 |
|---|---|
| **WORKS** | **≥ 10 referring domains** AND **Bing ≥ 100 indexed URLs** AND **≥ 1 citation (any host) on a scored query, by any assistant** |
| **PARTIAL — CHAIN BREAKS** | one or two of the three conditions met. The report names the condition that failed. That is the finding. |
| **DOES NOT WORK** | none of the three met |

Any citation on a control query is reported as a negative result, whatever the outcome above.

**What each partial outcome means, written now so it cannot be chosen later:**

- *Links but no admission* (≥ 10 domains, Bing < 100): the retrieval indexes gate on something
  other than the links we could earn. More links is not the next step.
- *Admission but no citation* (Bing ≥ 100, 0 citations): being retrievable is not sufficient.
  The gate's thesis fails on the leg it was built to test, now with its precondition met.
- *Citation without the authority signals* (≥ 1 citation, < 10 domains): citation does not run
  through this chain. Report which host was cited and by which assistant.

## Honest confounds

- **We caused the links.** That is the intervention, not a confound. It does mean the result says
  nothing about organic discovery.
- **The index changes during the experiment.** Weekly data refreshes and the changelog (GAL-578)
  alter pages throughout. A citation is dated against the state of the cited page on that day.
- **Assistants change.** Model and retrieval updates during the window cannot be separated from
  our intervention. Report the dates of any publicly announced retrieval changes.
- **n is small.** One citation is enough to meet the third condition. Report counts, never
  percentages.
- **The person running the experiment also builds a recipe app (galleybook).** galleybook is not
  part of any query (`galleybook App` was retired from the gate on 2026-08-23), and the funding
  policy forbids it any non-public data.

## Publishing the result

Whatever the outcome, it is published with the raw captures, at the latest on 2027-01-31, in the
repository and on the site.
