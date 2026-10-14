# Experiment 2 — intervention and reading log

Every outreach step and every reading, dated, as `experiment-2-protocol.md` requires. Newest last.

| Date | Kind | What | Source / record |
|---|---|---|---|
| 2026-10-05 | reading (baseline) | Bing 25 indexed, 5 impressions, 0 clicks; Brave 0; BWT AI 0 citations; GitHub 0 stars; referring domains: not yet counted | `gate-protocol.md` §1, 2026-10-05 |
| 2026-10-13 | reading (gate backstop) | Bing 46 indexed; Brave 0; Google 532 (report of 10-09); BWT AI 0 citations to 10-11; Perplexity-via-Bing probe: not supported | `gate-protocol.md` §1, 2026-10-13 |
| 2026-10-13 | freeze | This protocol frozen by public commit on main | commit 0f42526 |
| 2026-10-14 | launch | Post-gate bundle merged and pushed: second category, thesis, data page, question pages, changelog W42, self-hosted fonts, privacy notice | commit cb4402b |
| 2026-10-14 | archive | GitHub release v0.1.0 → Zenodo: version DOI 10.5281/zenodo.23367151, concept DOI 10.5281/zenodo.23367150 | github.com/tim-muky/openappindex/releases/tag/v0.1.0 |
| 2026-10-14 | archive | Hugging Face dataset `openappindex/app-store-de`, public: cooking (sweep, closure, prices, corrections, snapshots to 10-13, changelog to W42) and sleep (category, prices) | huggingface.co/datasets/openappindex/app-store-de |
| 2026-10-14 | hosting | openappindex.org moved from Vercel to a Cloudflare Worker (anonymous request counting, no IP stored; see /datenschutz.html). The first attempt at ~14:15 CEST was rolled back automatically within seconds because Analytics Engine was not yet enabled. Second attempt: Vercel records deleted ~14:21, Worker custom domains live at public resolvers by 14:32, so the site was unreachable for about 10 minutes, longer for resolvers that had cached the gap. All 723 sitemap URLs returned 200 afterwards | `worker/`, `worker/switch_dns.py` |
| 2026-10-14 | submission | IndexNow: 723 URLs, HTTP 200 | `sample/indexnow_submit.py` |
| 2026-10-14 | reading | Bing Site Explorer: 46 indexed = homepage 1, question pages 4 of 7 (the three added today not yet), app pages 40 of 941, other 1; no document page (paper, manifesto, method, thesis, data) and not /de/. Bing backlinks: none. Google Search Console: 0 external links; 532 indexed (report of 10-09); "crawled, not indexed" are app pages | BWT, GSC |
| 2026-10-14 | baseline (before any link exists) | Bing grew 25 → 37 → 46 indexed between 10-05 and 10-14, about 9 a week. If that pace held, Bing would pass 100 around the end of November without any intervention. Any "Bing ≥ 100" on 2027-01-15 is read against this line: the trend, not the link count, is the counterfactual | readings above |
| 2026-10-14 | site change (amendment, not a link) | One batch, deployed in the night to 2026-10-15: the seven question pages linked from the homepage and from every app page they list (before: one internal link each); /data/ and /thesis.html linked from every page (before: none); structured data ties the site to its DOI, Hugging Face copy and ORCID. No content or figure changed. Logged as a change to the treated site, so its effect stays separable from the earned links that start on 2026-10-20 | commit after this entry; `worker/night_deploy.sh` log |
