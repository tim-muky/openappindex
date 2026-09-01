#!/usr/bin/env python3
"""Sleep/meditation category sweep — mechanics identical to sample/build_corpus.py.

Queries frozen 2026-09-01 in openappindex-sleep-category-protocol.md, before any
counting. Full records kept so signals can be computed offline.
"""
import json, time, urllib.request, urllib.parse, collections
UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
QUERIES=["schlaf","schlafen","besser schlafen","einschlafen","einschlafhilfe",
  "schlaf app","schlaftracker","schlafanalyse","schlafzyklus wecker",
  "schlafgeschichten","einschlafgeräusche","weisses rauschen",
  "naturgeräusche schlafen","entspannungsmusik","meditation","meditieren lernen",
  "meditation deutsch","meditation gegen stress","geführte meditation",
  "achtsamkeit","entspannung","atemübungen","stress abbauen","innere ruhe",
  "hypnose schlafen"]
KEEP=("trackId","trackName","sellerName","artistId","description","releaseNotes",
      "releaseDate","currentVersionReleaseDate","version","averageUserRating",
      "userRatingCount","formattedPrice","primaryGenreName","genres","trackViewUrl",
      "artworkUrl100","languageCodesISO2A","fileSizeBytes")
apps={}; seen=collections.defaultdict(list)
for q in QUERIES:
    url="https://itunes.apple.com/search?term="+urllib.parse.quote(q)+"&country=de&entity=software&limit=200"
    try:
        res=json.loads(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=30).read())["results"]
    except Exception as e:
        print("!",q,e); continue
    for pos,r in enumerate(res,1):
        apps[r["trackId"]]={k:r.get(k) for k in KEEP}
        seen[r["trackId"]].append({"query":q,"position":pos})
    time.sleep(0.4)
for tid,a in apps.items(): a["seen_in"]=seen[tid]
json.dump({"queries":QUERIES,"storefront":"de","apps":list(apps.values())},
          open("data/corpus_sleep_de.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("corpus:",len(apps),"apps ->",round(len(open('data/corpus_sleep_de.json','rb').read())/1024/1024,1),"MB")
