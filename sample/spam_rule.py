#!/usr/bin/env python3
"""
Conjunction rule: no single signal may demote. Only structural facts that
co-occur. Measures how many apps a rule of N-of-M conditions would touch,
and who they are - so the false-positive cost is visible before shipping.
"""
import json, re, collections
C=json.load(open("data/corpus_scored.json",encoding="utf-8"))
W=re.compile(r"[a-zà-ÿäöüß]+",re.I)

def conds(a):
    desc=a.get("description") or ""
    w=W.findall(desc.lower())
    return {
      "text_shared_with_other_seller": a["s3_dup"]>0.5 and not a["s3_dup_same_dev"],
      "developer_ships_near_clones":   a["s4_clones"]>=2,
      "never_updated_since_release":   a["s5_never_updated"],
      "no_changelog_ever":             a["s6_no_notes"],
      "no_reviews_at_all":             (a.get("userRatingCount") or 0)==0,
      "vocabulary_below_1pct":         a["s2_ttr"]<0.431 and len(w)>=100,
    }

for a in C:
    c=conds(a); a["_c"]=c; a["_n"]=sum(c.values())

hist=collections.Counter(a["_n"] for a in C)
print("conditions met -> apps")
for k in sorted(hist): print(f"  {k}: {hist[k]:>4}")

for N in (2,3,4):
    hit=[a for a in C if a["_n"]>=N]
    print(f"\n=== rule: >={N} conditions -> {len(hit)} apps ({100*len(hit)/len(C):.1f}% of corpus) ===")
    for a in sorted(hit,key=lambda x:-x["_n"])[:8]:
        why=", ".join(k for k,v in a["_c"].items() if v)
        print(f"  {a['trackName'][:38]:<40} ratings={a.get('userRatingCount') or 0:>5}  [{why}]")

print("\n--- controls: do known-legitimate apps stay clean? ---")
for name in ["Paprika","galleybook","Chefkoch","Malteser Apotheke","Falken Apotheke",
             "Mizept","FlavorVault","Dr. Oetker","100 leckere","Kochbuch - Rezepte"]:
    for a in C:
        if a["trackName"].lower().startswith(name.lower()[:10]):
            why=", ".join(k for k,v in a["_c"].items() if v) or "clean"
            print(f"  {a['_n']} cond  {a['trackName'][:36]:<38} [{why}]")
            break
