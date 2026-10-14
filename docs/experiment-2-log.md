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
