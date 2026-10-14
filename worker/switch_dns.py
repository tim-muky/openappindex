#!/usr/bin/env python3
"""
Move openappindex.org from Vercel to the Cloudflare Worker (launch, 2026-10-14).

    python3 worker/switch_dns.py --check      # token valid? which records point to Vercel? (read-only)
    python3 worker/switch_dns.py --switch     # back up + delete the Vercel records, wrangler deploy, verify
    python3 worker/switch_dns.py --restore    # re-create the backed-up Vercel records (rollback)

Workers custom domains (wrangler.jsonc: custom_domain: true) refuse a hostname that already has
DNS records, so the two Vercel records (apex A 76.76.21.21, www CNAME cname.vercel-dns.com) are
deleted right before `wrangler deploy`, which then creates the Worker's own. Downtime is the
minute between the two. The deleted records are saved to worker/dns-backup-<date>.json first.

The API token (Zone → DNS → Edit, openappindex.org only) is read from
~/.config/cloudflare_dns_token and never printed. For --restore, the Worker's custom domains must
be removed first (dashboard: Workers → openappindex → Settings → Domains & Routes), otherwise the
hostnames are still taken.
"""
import json, os, subprocess, sys, time, urllib.request, urllib.error
from datetime import date

ZONE = "openappindex.org"
API = "https://api.cloudflare.com/client/v4"
HERE = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(HERE, f"dns-backup-{date.today().isoformat()}.json")
VERCEL = ("76.76.21.21", "vercel-dns.com")
CHECK_PATHS = ["/", "/datenschutz.html", "/fonts/fonts.css", "/data/", "/sitemap.xml", "/methode.html"]

def token():
    p = os.path.expanduser("~/.config/cloudflare_dns_token")
    if not os.path.exists(p):
        sys.exit("No token at ~/.config/cloudflare_dns_token")
    return open(p).read().strip()

def api(method, path, body=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        r = json.loads(e.read() or b"{}")
    if not r.get("success"):
        sys.exit(f"API {method} {path} failed: {r.get('errors')}")
    return r["result"]

def zone_id():
    z = api("GET", f"/zones?name={ZONE}")
    if not z:
        sys.exit(f"Token cannot see zone {ZONE}")
    return z[0]["id"]

def vercel_records(zid):
    recs = api("GET", f"/zones/{zid}/dns_records?per_page=100")
    hosts = {ZONE, "www." + ZONE}
    return [r for r in recs if r["name"] in hosts and r["type"] in ("A", "AAAA", "CNAME")
            and any(v in r["content"] for v in VERCEL)]

def served_by():
    try:
        req = urllib.request.Request(f"https://{ZONE}/", method="HEAD", headers={"User-Agent": "openAPPindex-launch-check"})
        h = urllib.request.urlopen(req, timeout=15).headers
        return "vercel" if h.get("x-vercel-id") else ("cloudflare-worker" if h.get("cf-ray") else h.get("server"))
    except Exception as e:
        return f"error: {type(e).__name__}"

def check():
    v = api("GET", "/user/tokens/verify")
    print("token:", v.get("status"))
    zid = zone_id()
    recs = vercel_records(zid)
    print(f"zone {ZONE}: {len(recs)} record(s) pointing to Vercel")
    for r in recs:
        print(f"  {r['type']:5} {r['name']:24} {r['content']}  proxied={r['proxied']}")
    print("currently served by:", served_by())

def switch():
    zid = zone_id()
    recs = vercel_records(zid)
    if not recs:
        sys.exit("No Vercel records found — nothing to switch (already switched?)")
    json.dump(recs, open(BACKUP, "w"), indent=1)
    print(f"backed up {len(recs)} record(s) to {BACKUP}")
    for r in recs:
        api("DELETE", f"/zones/{zid}/dns_records/{r['id']}")
        print(f"  deleted {r['type']} {r['name']}")
    t0 = time.time()
    d = subprocess.run(["npx", "wrangler", "deploy"], cwd=HERE)
    if d.returncode != 0:
        print("wrangler deploy FAILED — restoring the Vercel records")
        restore()
        sys.exit(1)
    for _ in range(40):
        if served_by() == "cloudflare-worker":
            break
        time.sleep(15)
    print(f"served by: {served_by()} ({time.time() - t0:.0f} s after the delete)")
    for p in CHECK_PATHS:
        try:
            s = urllib.request.urlopen(urllib.request.Request(f"https://{ZONE}{p}", headers={"User-Agent": "openAPPindex-launch-check"}), timeout=20).status
        except urllib.error.HTTPError as e:
            s = e.code
        print(f"  {s} {p}")

def restore():
    zid = zone_id()
    files = sorted(f for f in os.listdir(HERE) if f.startswith("dns-backup-"))
    if not files:
        sys.exit("No backup file")
    for r in json.load(open(os.path.join(HERE, files[-1]))):
        api("POST", f"/zones/{zid}/dns_records", {k: r[k] for k in ("type", "name", "content", "ttl", "proxied")})
        print(f"  re-created {r['type']} {r['name']} -> {r['content']}")

if __name__ == "__main__":
    {"--check": check, "--switch": switch, "--restore": restore}.get(
        (sys.argv[1:] or [""])[0], lambda: sys.exit(__doc__))()
