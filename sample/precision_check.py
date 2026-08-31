#!/usr/bin/env python3
"""
Precision check (GAL-511) - classification v4 candidate.

v3 asks "does the description talk about cooking?". Deep in the zero-rating
tail that stops being enough: apps that merely mention cooking words - a
magazine's ePaper, a restaurant's ordering app, a kids-game publisher's
franchise - become a visible share of the finds. These rules catch the three
categorical error classes observed in the hop-2 delta (2026-08-31), layered on
top of v3. They are rules, not judgement: every exclusion states which rule
fired, so a wrong exclusion is findable and correctable.

    python3 precision_check.py            check the 48 hop-2 finds
    python3 precision_check.py --served   report what v4 would flag in the
                                          served corpus (report only; changing
                                          the served set is a separate, dated
                                          decision)
"""
import json, re, sys

# --- v3, unchanged (mirrors build_site.py) ----------------------------------
RECIPE = re.compile(r"rezept|kochbuch|kochen|backen", re.I)
PHARMA = re.compile(r"apothek|e-?rezept|medikament|arzt|ärzt|verschreib|krankenkasse", re.I)
COOK   = re.compile(r"koch|back|zutat|essen|mahlzeit|gericht|k[üu]che|ern[äa]hrung|"
                    r"lebensmittel|einkaufsliste|men[üu]|speise|food|recipe", re.I)
EXCLUDE_GENRE = {"Games", "Entertainment", "Utilities", "Photo & Video", "Travel",
                 "Finance", "Business"}
KIDS_V3 = re.compile(r"spiel|kinder|kids|kleinkind|toddler|kiddo", re.I)

def v3(name, desc, genre):
    t = (name or "") + " " + (desc or "")
    if not RECIPE.search(t):            return False
    if genre in EXCLUDE_GENRE:          return False
    if genre in ("Education", "Medical") and KIDS_V3.search(name or ""):
        return False
    ph, ck = len(PHARMA.findall(t)), len(COOK.findall(t))
    if ph >= 3 and ph > ck:             return False
    return ck >= 2

# --- v4 additions ------------------------------------------------------------
# Rule M: press products are not apps about cooking, however many recipes they
# print. Caught by genre alone (tina ePaper).
GENRE_PRESS = {"Magazines & Newspapers", "News", "Book"}

# Rule K: the v3 kids check misses franchise titles that avoid the word "Spiel"
# ("Baby Pandas Stadt", "Vorschulwissen"). Widened name check, still gated on
# the non-cooking genres so a cookbook "für Kinder" survives.
KIDS_V4 = re.compile(r"spiel|kinder|kids|kleinkind|toddler|kiddo|baby|panda|vorschul", re.I)

# Rule V: a single venue's app - restaurant, canteen, bakery chain - describes
# visiting or ordering from a business, not cooking. One signal can appear in a
# genuine recipe app ("wie im Restaurant"); two independent ones have not.
VENUE = [re.compile(p, re.I) for p in (
    # "Speiseplan" and "Vorteil" removed after a false hit on a genuine recipe
    # app (Detox Diet Food Recipes, 2026-08-31): both are ordinary recipe-app
    # marketing German. "Speisekarte", Treue/Coupon/Rabatt are not.
    r"filial", r"speisekarte", r"betriebsrestaurant", r"catering",
    r"im lokal|vor ort|an ihren arbeitsplatz|nach hause", r"zum mitnehmen|abhol",
    r"liefer(service|n)", r"reservier", r"bestell", r"bargeldlos|bezahlen",
    r"treue|coupon|rabatt", r"unser(e[mrn]?)? (restaurant|team|küche|betrieb)",
    r"willkommen (bei|im|in der)")]

def v4_excluded(rec):
    """Returns the fired rule as a short string, or None if the app survives."""
    name, desc, genre = rec.get("trackName"), rec.get("description"), rec.get("primaryGenreName")
    if genre in GENRE_PRESS:
        return f"M: genre {genre}"
    # Education only: a Lifestyle app named "Beikost - Baby BLW & Brei" is a
    # genuine baby-food recipe app (false hit found 2026-08-31); every real
    # kids-franchise case observed sits in Education.
    if genre == "Education" and KIDS_V4.search(name or ""):
        return f"K: kids-franchise name in genre {genre}"
    hits = [p.pattern for p in VENUE if p.search(desc or "")]
    if len(hits) >= 2:
        return "V: venue signals " + ", ".join(hits[:4])
    return None

if __name__ == "__main__":
    if "--served" in sys.argv:
        C = json.load(open("data/corpus_de.json", encoding="utf-8"))["apps"]
        meta = json.load(open("data/new_apps_meta.json", encoding="utf-8"))
        served = [a for a in list(C) + list(meta.values())
                  if v3(a.get("trackName"), a.get("description"), a.get("primaryGenreName"))]
        flagged = [(a, v4_excluded(a)) for a in served]
        flagged = [(a, r) for a, r in flagged if r]
        print(f"served-basis apps checked: {len(served)} · v4 would flag: {len(flagged)}\n")
        for a, r in sorted(flagged, key=lambda x: x[1]):
            print(f"  {a['trackName'][:44]:<46} {r[:70]}")
    else:
        d = json.load(open("data/closure_hop2_cook_meta.json", encoding="utf-8"))
        keep, drop = [], []
        for rec in sorted(d.values(), key=lambda x: x["trackName"].lower()):
            r = v4_excluded(rec)
            (drop if r else keep).append((rec, r))
        print(f"hop-2 finds: {len(d)} · survive v4: {len(keep)} · excluded: {len(drop)}\n")
        for rec, r in drop:
            print(f"  OUT {rec['trackName'][:40]:<42} {r[:70]}")
        print()
        for rec, _ in keep:
            print(f"  ok  {rec['trackName']}")
        json.dump({str(r["trackId"]): r for r, _ in keep},
                  open("data/closure_hop2_precise.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("\nwrote data/closure_hop2_precise.json")
