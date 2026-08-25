#!/usr/bin/env python3
"""Second pass: does any signal actually separate junk from small honest apps?"""
import json, re, collections, statistics
C=json.load(open("data/corpus_scored.json",encoding="utf-8"))
WORD=re.compile(r"[a-zà-ÿäöüß]+",re.I)
def words(t): return WORD.findall((t or "").lower())

# restrict to the population the filter would actually run on:
# German-language listings with a description long enough to measure
DE=[a for a in C if "DE" in (a.get("languageCodesISO2A") or []) and len(words(a.get("description")))>=100]
print(f"population: {len(DE)} German listings with >=100-word descriptions (of {len(C)})\n")

st=[a["s1_stuffing"] for a in DE]
print(f"S1 stuffing on this population: median {statistics.median(st):.3f} "
      f"p95 {sorted(st)[int(len(st)*.95)]:.3f} p99 {sorted(st)[int(len(st)*.99)]:.3f} max {max(st):.3f}")

# category-term saturation: how often the *category noun* repeats per 100 words
CAT=re.compile(r"rezept",re.I)
for a in DE:
    w=words(a.get("description"))
    a["cat_per100"]=round(100*len(CAT.findall(a.get("description") or ""))/max(1,len(w)),2)
sat=[a["cat_per100"] for a in DE]
print(f"category-term saturation: median {statistics.median(sat):.2f}/100w  "
      f"p95 {sorted(sat)[int(len(sat)*.95)]:.2f}  p99 {sorted(sat)[int(len(sat)*.99)]:.2f}  max {max(sat):.2f}\n")

print("--- top category-term saturation ---")
for a in sorted(DE,key=lambda x:-x["cat_per100"])[:10]:
    flag=" <-- also duplicate text" if a["s3_dup"]>0.5 else ""
    print(f"  {a['cat_per100']:>5.2f}/100w  ttr={a['s2_ttr']:.2f} ratings={a['userRatingCount'] or 0:>5}  {a['trackName'][:40]}{flag}")

print("\n--- known-good controls: where do legitimate apps sit? ---")
for name in ["Paprika Rezept-Manager 3","galleybook","Chefkoch","KptnCook","Kitchen Stories","Mein Rezeptebuch"]:
    for a in DE:
        if a["trackName"].lower().startswith(name.lower()[:12]):
            print(f"  {a['cat_per100']:>5.2f}/100w  stuffing={a['s1_stuffing']:.3f} ttr={a['s2_ttr']:.2f} dup={a['s3_dup']:.2f}  {a['trackName'][:40]}")
            break

print("\n--- S3: identical marketing text across DIFFERENT developers ---")
dups=[a for a in C if a["s3_dup"]>0.5 and not a["s3_dup_same_dev"]]
for a in sorted(dups,key=lambda x:-x["s3_dup"])[:10]:
    print(f"  overlap {a['s3_dup']:.2f}  {a['trackName'][:34]:<36} ({a['sellerName'][:22]})  ==  {(a['s3_dup_with'] or '')[:30]}")

# precision check: what fraction of flagged apps are ALSO unmaintained / noteless?
def flagged(a): return a["s3_dup"]>0.5 and not a["s3_dup_same_dev"]
f=[a for a in C if flagged(a)]
if f:
    print(f"\nof {len(f)} duplicate-text apps: {sum(1 for a in f if a['s5_never_updated'])} never updated, "
          f"{sum(1 for a in f if a['s6_no_notes'])} have no release notes, "
          f"median ratings {statistics.median([a['userRatingCount'] or 0 for a in f]):.0f}")
