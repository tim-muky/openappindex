#!/usr/bin/env python3
"""Classification v1 for the sleep/meditation corpus.

Rules frozen 2026-09-01 in openappindex-sleep-category-protocol.md, before the
sweep ran. Mirrors the shape of cooking's v3 (sample/precision_check.py): core
keyword, genre excludes, one disambiguation counter, context threshold.

Prints counts plus every borderline record with the rule that decided it, so a
wrong classification is findable and correctable. Writes the surviving slice to
data/sleep_slice.json.
"""
import json, re, collections

CORE   = re.compile(r"schlaf|einschlaf|meditat|entspann|achtsam|beruhig", re.I)
MONITOR= re.compile(r"babyphone|babyfon|überwach|kamera|apnoe|cpap|diagnose|praxis|termin|arzt|ärzt", re.I)
SLEEPCTX=re.compile(r"schlaf|ruhe|stress|atem|meditation|traum|geräusch|klang|sound|musik|hypnose|"
                    r"erhol|müde|entspann|achtsam|mindful|gedanken|beruhig", re.I)
EXCLUDE_GENRE={"Games","Finance","Business","Travel","Shopping","News",
               "Magazines & Newspapers","Food & Drink","Photo & Video"}

def v1(rec):
    """Returns (in_category: bool, reason: str)."""
    name, desc, genre = rec.get("trackName"), rec.get("description"), rec.get("primaryGenreName")
    t = (name or "") + " " + (desc or "")
    if not CORE.search(t):          return False, "no core keyword"
    if genre in EXCLUDE_GENRE:      return False, f"genre {genre}"
    mon, ctx = len(MONITOR.findall(t)), len(SLEEPCTX.findall(t))
    if mon >= 3 and mon > ctx:      return False, f"monitor/medical signals {mon} > context {ctx}"
    if ctx < 2:                     return False, f"context hits {ctx} < 2"
    return True, f"context {ctx}"

if __name__ == "__main__":
    C = json.load(open("data/corpus_sleep_de.json", encoding="utf-8"))["apps"]
    kept, dropped = [], []
    for a in C:
        ok, why = v1(a)
        (kept if ok else dropped).append((a, why))

    print(f"sweep saw {len(C)} distinct apps · in category (v1): {len(kept)} · out: {len(dropped)}\n")
    def bucket(w):
        if w.startswith("genre"):   return w
        if w.startswith("monitor"): return "monitor/medical counter"
        if w.startswith("context"): return "context hits < 2"
        return w
    reasons = collections.Counter(bucket(w) for _, w in dropped)
    for r, n in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"  out · {r:<28} {n}")

    gen = collections.Counter(a.get("primaryGenreName") for a, _ in kept)
    print("\nkept, by genre:")
    for g, n in gen.most_common():
        print(f"  {g:<24} {n}")

    # Borderline lists for the manual precision inspection (protocol step 3):
    print("\n-- monitor/medical counter fired (excluded) --")
    for a, w in dropped:
        if w.startswith("monitor"):
            print(f"  OUT {a['trackName'][:50]:<52} {w}")
    print("\n-- kept despite >=1 monitor/medical hit (check these) --")
    for a, w in kept:
        t=(a.get("trackName") or "")+" "+(a.get("description") or "")
        if MONITOR.search(t):
            print(f"  ok? {a['trackName'][:50]:<52} {w}")

    json.dump([a for a, _ in kept], open("data/sleep_slice.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\nwrote data/sleep_slice.json ({len(kept)} apps)")
