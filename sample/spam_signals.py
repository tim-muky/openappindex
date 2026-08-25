#!/usr/bin/env python3
"""
What would a NEUTRAL spam filter look like?

Constraint: it may not use popularity. Downloads, rating counts and revenue are
exactly what the store already uses, and re-importing them re-imports the bias.
So every signal here must be computable from an app's own published artefacts,
measurable the same way for a one-person app and a corporation, and explainable
to the developer it demotes in a single dated sentence.

Signals computed:
  S1 keyword stuffing      - how much of the description is one repeated term
  S2 vocabulary poverty    - type/token ratio of the description
  S3 duplicate description - near-identical text shared across apps
  S4 catalogue cloning     - one developer shipping many near-identical apps
  S5 never maintained      - shipped once, never updated since release
  S6 changelog silence     - no release notes at all

None of these is a verdict on its own. The question this script answers is
whether they separate keyword-stuffed junk from small honest apps - because a
filter that cannot tell those apart is just popularity in a different coat.
"""
import json, re, collections, statistics, hashlib

C = json.load(open("data/corpus_de.json", encoding="utf-8"))["apps"]
WORD = re.compile(r"[a-zà-ÿäöüß]+", re.I)

def words(t): return WORD.findall((t or "").lower())

def shingles(t, n=6):
    w = words(t)
    return {hashlib.md5(" ".join(w[i:i+n]).encode()).hexdigest()[:12]
            for i in range(max(0, len(w)-n+1))}

# ---------- per-app signals ----------
by_dev = collections.defaultdict(list)
for a in C:
    by_dev[a.get("artistId")].append(a)

sh_index = collections.defaultdict(set)      # shingle -> app ids
for a in C:
    a["_sh"] = shingles(a.get("description"))
    for s in a["_sh"]:
        sh_index[s].add(a["trackId"])

def dup_score(a):
    """max jaccard-ish overlap with any OTHER developer's app"""
    cand = collections.Counter()
    for s in a["_sh"]:
        for t in sh_index[s]:
            if t != a["trackId"]:
                cand[t] += 1
    if not cand or not a["_sh"]: return 0.0, None
    tid, shared = cand.most_common(1)[0]
    other = next(x for x in C if x["trackId"] == tid)
    return round(shared / max(1, len(a["_sh"])), 3), other

for a in C:
    w = words(a.get("description"))
    a["s1_stuffing"] = round(collections.Counter(w).most_common(1)[0][1] / len(w), 3) if w else 0
    a["s2_ttr"] = round(len(set(w)) / len(w), 3) if w else 0
    d, other = dup_score(a)
    a["s3_dup"] = d
    a["s3_dup_with"] = other["trackName"] if other else None
    a["s3_dup_same_dev"] = bool(other and other.get("artistId") == a.get("artistId"))
    sibs = by_dev[a.get("artistId")]
    clones = sum(1 for s in sibs if s["trackId"] != a["trackId"]
                 and len(a["_sh"] & s["_sh"]) / max(1, len(a["_sh"])) > 0.5)
    a["s4_dev_apps"] = len(sibs); a["s4_clones"] = clones
    a["s5_never_updated"] = (a.get("releaseDate") or "")[:10] == (a.get("currentVersionReleaseDate") or "")[:10]
    a["s6_no_notes"] = not (a.get("releaseNotes") or "").strip()

for a in C:
    del a["_sh"]

# ---------- distributions ----------
def pct(v, p): 
    s = sorted(v); return round(s[int(len(s)*p)], 3)
st = [a["s1_stuffing"] for a in C]; ttr = [a["s2_ttr"] for a in C]
print(f"corpus: {len(C)} apps")
print(f"S1 stuffing   median {statistics.median(st):.3f}  p90 {pct(st,.9)}  p99 {pct(st,.99)}  max {max(st)}")
print(f"S2 ttr        median {statistics.median(ttr):.3f}  p10 {pct(ttr,.1)}  p01 {pct(ttr,.01)}  min {min(ttr)}")
print(f"S3 dup>0.5 across different developers: {sum(1 for a in C if a['s3_dup']>0.5 and not a['s3_dup_same_dev'])}")
print(f"S4 apps whose developer ships >=3 near-clones: {sum(1 for a in C if a['s4_clones']>=3)}")
print(f"S5 never updated since release: {sum(1 for a in C if a['s5_never_updated'])} ({100*sum(1 for a in C if a['s5_never_updated'])/len(C):.0f}%)")
print(f"S6 no release notes at all:     {sum(1 for a in C if a['s6_no_notes'])} ({100*sum(1 for a in C if a['s6_no_notes'])/len(C):.0f}%)")

print("\n--- worst keyword stuffing (S1) ---")
for a in sorted(C, key=lambda x: -x["s1_stuffing"])[:8]:
    print(f"  {a['s1_stuffing']:.3f} ttr={a['s2_ttr']:.2f} ratings={a['userRatingCount'] or 0:>5}  {a['trackName'][:44]}")

print("\n--- biggest clone factories (S4) ---")
devs = sorted({a['sellerName']: (a['s4_dev_apps'], a['s4_clones']) for a in C if a['s4_clones'] >= 2}.items(),
              key=lambda kv: -kv[1][1])[:8]
for name, (n, cl) in devs:
    print(f"  {cl:>3} near-clones of {n:>3} apps in corpus   {name[:42]}")

json.dump(C, open("data/corpus_scored.json", "w", encoding="utf-8"), ensure_ascii=False)
