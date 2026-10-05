// What is recorded, per request, and nothing else:
//   blob1 path · blob2 visitor class · blob3 crawler name · blob4 referrer host
//   blob5 country (Cloudflare's 2-letter code) · double1 HTTP status
// Not recorded: IP address, full user agent, query string, cookies.

const CRAWLERS = [
  // AI crawlers and assistant fetchers
  ["GPTBot", "ai"], ["OAI-SearchBot", "ai"], ["ChatGPT-User", "ai"],
  ["ClaudeBot", "ai"], ["Claude-SearchBot", "ai"], ["Claude-User", "ai"],
  ["PerplexityBot", "ai"], ["Perplexity-User", "ai"], ["Google-Extended", "ai"],
  ["Applebot-Extended", "ai"], ["meta-externalagent", "ai"], ["Amazonbot", "ai"],
  ["cohere-ai", "ai"], ["Bytespider", "ai"], ["MistralAI-User", "ai"], ["CCBot", "ai"],
  ["DuckAssistBot", "ai"],
  // search engines
  ["bingbot", "search"], ["Googlebot", "search"], ["Applebot", "search"],
  ["DuckDuckBot", "search"], ["YandexBot", "search"], ["Baiduspider", "search"],
  ["Brave", "search"], ["Qwantbot", "search"], ["SeznamBot", "search"],
];

function classify(ua) {
  if (!ua) return ["unknown", ""];
  for (const [name, cls] of CRAWLERS) if (ua.includes(name)) return [cls, name];
  if (/bot|crawl|spider|fetch|curl|wget|python|httpclient|monitor|preview/i.test(ua)) return ["other-bot", ""];
  return ["human", ""];
}

function refHost(ref, ownHost) {
  try {
    const h = new URL(ref).hostname;
    return h === ownHost ? "(internal)" : h;
  } catch { return ""; }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // www → apex, as Vercel did (308).
    if (url.hostname === "www.openappindex.org") {
      url.hostname = "openappindex.org";
      return Response.redirect(url.toString(), 308);
    }

    // Directory index on a trailing slash; a directory without one gets a 308 to it,
    // so /de and /de/ are no longer two URLs for one page (GAL-565).
    let res;
    if (url.pathname.endsWith("/")) {
      res = await env.ASSETS.fetch(new Request(new URL(url.pathname + "index.html", url), request));
    } else {
      res = await env.ASSETS.fetch(request);
      if (res.status === 404 && !/\.[a-z0-9]+$/i.test(url.pathname)) {
        const idx = await env.ASSETS.fetch(new Request(new URL(url.pathname + "/index.html", url), request));
        if (idx.status === 200) {
          url.pathname += "/";
          res = Response.redirect(url.toString(), 308);
        }
      }
    }
    if (res.status === 404) {
      res = new Response("Not found\n", { status: 404, headers: { "content-type": "text/plain; charset=utf-8" } });
    }

    const [cls, crawler] = classify(request.headers.get("user-agent") || "");
    try {
      env.LOG.writeDataPoint({
        blobs: [url.pathname, cls, crawler, refHost(request.headers.get("referer") || "", "openappindex.org"),
                (request.cf && request.cf.country) || ""],
        doubles: [res.status],
        indexes: [cls],
      });
    } catch (e) { /* logging must never break serving */ }
    return res;
  },
};
