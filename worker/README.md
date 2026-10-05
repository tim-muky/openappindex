# Serving Worker (GAL-558)

Serves `sample/site/` from Cloudflare and records one anonymous data point per request
(path, visitor class, crawler name, referrer host, country, status) in Workers Analytics
Engine. No IP address, no full user agent, no cookies, no client-side script.

Why not Cloudflare in front of Vercel: Vercel advises against a reverse proxy in front of its
deployments. Serving the static files from Cloudflare directly removes the extra hop.

## One-time setup (Tim)
1. `npx wrangler login` (opens the browser; Cloudflare account that holds the openappindex.org zone).
2. In the Cloudflare dashboard, DNS for openappindex.org: delete the `A` record to 76.76.21.21
   and the `www` record pointing at Vercel. Wrangler creates the custom-domain records on deploy.
   Keep the MX/TXT records (email forwarding).

## Deploy (Claude, after every build)
```
cd sample && python3 build_site.py && cd ../worker && npx wrangler deploy
```

## Read the log
SQL API: `POST https://api.cloudflare.com/client/v4/accounts/<account_id>/analytics_engine/sql`
with an API token that has *Account Analytics Read*. Example:
```sql
SELECT blob2 AS class, blob3 AS crawler, count() AS n
FROM openappindex_requests WHERE timestamp > NOW() - INTERVAL '7' DAY
GROUP BY class, crawler ORDER BY n DESC
```

## Limits (Workers Free, checked 2026-10-05)
100,000 requests/day; 20,000 asset files; 25 MiB per file; Analytics Engine 100,000 data
points/day written. A front-page Hacker News day can approach the request limit; Workers Paid
removes it.

## Rollback
Re-create the `A` record to 76.76.21.21 (Vercel) and remove the Worker's custom domains. The
Vercel project "site" stays deployed as the fallback.
