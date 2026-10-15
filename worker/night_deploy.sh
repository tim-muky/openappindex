#!/bin/zsh
# Unattended deploy of the current build to the openappindex Worker, with automatic rollback.
#   worker/night_deploy.sh            deploy now
#   worker/night_deploy.sh 02:00      wait until that local time, then deploy
# Steps: rebuild -> remember the live version -> wrangler deploy -> check every sitemap URL
# -> roll back to the remembered version if any check fails -> IndexNow on success.
# Everything is logged to worker/deploy-logs/<date>.log (ignored by git).
set -u
REPO=/Users/timmeyerdierks/Claude/BAS
LOGDIR=$REPO/worker/deploy-logs; mkdir -p $LOGDIR
LOG=$LOGDIR/$(date +%Y-%m-%d_%H%M).log
exec > >(tee -a $LOG) 2>&1

if [[ $# -ge 1 ]]; then
  target=$(date -j -f "%H:%M" "$1" +%s); now=$(date +%s)
  (( target <= now )) && target=$(( target + 86400 ))
  echo "$(date '+%F %T') waiting until $(date -r $target '+%F %T')"
  sleep $(( target - now ))
fi

echo "$(date '+%F %T') start"
cd $REPO/sample && python3 build_site.py | tail -2 || { echo "BUILD FAILED - nothing deployed"; exit 1; }

cd $REPO/worker
PREV=""
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -s -m 15 -o /dev/null https://example.com; then
    PREV=$(npx wrangler deployments list 2>/dev/null | grep -o '(100%) [0-9a-f-]\{36\}' | tail -1 | awk '{print $2}')
    [[ -n "$PREV" ]] && break
    echo "$(date '+%F %T') network up, but the live version could not be read (try $i)"
  else
    echo "$(date '+%F %T') no network (try $i)"
  fi
  sleep 60
done
echo "live version before deploy: ${PREV:-unknown}"
[[ -z "$PREV" ]] && { echo "Could not read the live version - not deploying without a rollback target"; exit 1; }

npx wrangler deploy 2>&1 | grep -E "Uploaded|Deployed|Current Version|ERROR|✘" || true
sleep 20
NOW_V=$(npx wrangler deployments list 2>/dev/null | grep -o '(100%) [0-9a-f-]\{36\}' | tail -1 | awk '{print $2}')
if [[ "$NOW_V" == "$PREV" ]]; then
  echo "$(date '+%F %T') DEPLOY DID NOT HAPPEN - the live version is unchanged ($PREV). Nothing else done."
  exit 1
fi
echo "live version after deploy: $NOW_V"

BAD=$(python3 - <<'EOF'
import re, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
paths = re.findall(r"<loc>https://openappindex\.org([^<]*)</loc>", open("/Users/timmeyerdierks/Claude/BAS/sample/site/sitemap.xml").read())
def st(p):
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request("https://openappindex.org" + p, headers={"User-Agent": "openAPPindex-deploycheck-bot"}), timeout=20).status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception:
            code = 0
    return code
with ThreadPoolExecutor(8) as ex:
    res = list(zip(paths, ex.map(st, paths)))
bad = [p for p, s in res if s != 200]
print(len(bad))
print(f"checked {len(res)} URLs, {len(bad)} not 200: {bad[:10]}", file=__import__('sys').stderr)
EOF
)
if [[ "$BAD" != "0" ]]; then
  echo "$(date '+%F %T') CHECK FAILED ($BAD URLs) - rolling back to $PREV"
  npx wrangler rollback "$PREV" -m "night_deploy: automatic rollback after failed URL check" -y 2>&1 | tail -3
  exit 1
fi
echo "$(date '+%F %T') all sitemap URLs return 200"
cd $REPO/sample && python3 indexnow_submit.py 2>&1 | tail -1
echo "$(date '+%F %T') done"
