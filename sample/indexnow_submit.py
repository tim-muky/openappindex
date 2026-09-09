#!/usr/bin/env python3
"""Submit the curated sitemap URL set to IndexNow (Bing, Yandex, Seznam, Naver).

Run AFTER a deploy — the endpoint verifies the key file and the URLs against the
live site, so submitting before publishing wastes the ping. Appends a dated
record to data/indexnow_log.json; the gate protocol requires every
visibility-affecting step to be datable.
"""
import json,os,re,sys,datetime,urllib.request

HOST="openappindex.org"
# The key is whatever build_site.py served — read it from the output so the
# submission can never drift from the published proof file.
keyfiles=[l for l in os.listdir("site") if re.fullmatch(r"[0-9a-f]{32}\.txt",l)]
if len(keyfiles)!=1: sys.exit("!! expected exactly one IndexNow key file in site/")
KEY=open("site/"+keyfiles[0]).read().strip()

urls=re.findall(r"<loc>(.*?)</loc>",open("site/sitemap.xml",encoding="utf-8").read())
if not urls: sys.exit("!! sitemap.xml has no URLs — build first")
if len(urls)>10000: sys.exit("!! IndexNow caps one POST at 10,000 URLs — split before submitting")

body=json.dumps({"host":HOST,"key":KEY,"keyLocation":f"https://{HOST}/{KEY}.txt","urlList":urls}).encode()
rec={"at":datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),"n":len(urls)}
if "--dry-run" in sys.argv:
    rec["status"]="dry-run"; print(f"dry-run: would submit {len(urls)} URLs for {HOST}")
else:
    try:
        r=urllib.request.urlopen(urllib.request.Request("https://api.indexnow.org/indexnow",
            data=body,headers={"Content-Type":"application/json; charset=utf-8"}),timeout=40)
        rec["status"]=r.status
    except urllib.error.HTTPError as e:
        rec["status"]=e.code; rec["error"]=e.read().decode("utf-8","replace")[:300]
    print(f"IndexNow: {rec['status']} for {len(urls)} URLs")

try: log=json.load(open("data/indexnow_log.json",encoding="utf-8"))
except FileNotFoundError: log=[]
log.append(rec)
json.dump(log,open("data/indexnow_log.json","w",encoding="utf-8"),indent=1)
