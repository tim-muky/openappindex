#!/usr/bin/env python3
"""Rebuild the sweep, keeping full records so signals can be computed offline."""
import json, time, urllib.request, urllib.parse, collections
UA=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
QUERIES=["rezepte","rezept","kochen","kochbuch","rezepte speichern","rezepte sammeln",
  "rezepte verwalten","eigene rezepte","kochrezepte","backen","essensplaner",
  "wochenplan essen","meal planner deutsch","einkaufsliste rezepte","rezepte app",
  "digitales kochbuch","rezepte scannen","rezeptsammlung","kochbuch digital",
  "was koche ich heute","vegetarische rezepte","schnelle rezepte","rezepte organisieren",
  "lieblingsrezepte","rezepte importieren"]
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
          open("data/corpus_de.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("corpus:",len(apps),"apps ->",round(len(open('data/corpus_de.json','rb').read())/1024/1024,1),"MB")
