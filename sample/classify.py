#!/usr/bin/env python3
"""
Classification v4 — is this a cooking/recipe app?

One classifier, imported by every script that counts. Three corrections, all
found by our own checks and all documented on the methods page:
  1. German "Rezept" means recipe AND medical prescription -> pharmacy apps
  2. "Kochen/Backen" also matches cooking GAMES, which are not recipe apps
  3. (2026-08-31) press products (ePaper/magazines that print recipes), a
     kids-franchise title in Education, and single-venue apps also pass the
     keyword test. Rules M and K below; the venue rule is not yet precise
     enough to apply here (see sample/precision_check.py).
Keyword classification has known limits; they are stated publicly rather than
hidden. See methode.html.
"""
import re

RECIPE = re.compile(r"rezept|kochbuch|kochen|backen", re.I)
PHARMA = re.compile(r"apothek|e-?rezept|medikament|arzt|ärzt|verschreib|krankenkasse", re.I)
COOK   = re.compile(r"koch|back|zutat|essen|mahlzeit|gericht|k[üu]che|ern[äa]hrung|"
                    r"lebensmittel|einkaufsliste|men[üu]|speise|food|recipe", re.I)
EXCLUDE_GENRE = {"Games", "Entertainment", "Utilities", "Photo & Video", "Travel",
                 "Finance", "Business",
                 # v4 rule M: press products are not apps about cooking,
                 # however many recipes they print
                 "Magazines & Newspapers", "News", "Book"}

# Children's cooking games are filed under Education, not Games — a third
# classifier correction, found 2026-08-24.
KIDS_GAME = re.compile(r"spiel|kinder|kids|kleinkind|toddler|kiddo", re.I)
# v4 rule K (2026-08-31): franchise titles avoid the word "Spiel" ("Baby Pandas
# Stadt", "Vorschulwissen"). Education only — a Lifestyle app named "Beikost -
# Baby BLW & Brei" is a genuine baby-food recipe app.
KIDS_V4 = re.compile(r"spiel|kinder|kids|kleinkind|toddler|kiddo|baby|panda|vorschul", re.I)

CLASSIFIER_VERSION = "v4"

def is_cooking_app(name, desc, genre):
    t = (name or "") + " " + (desc or "")
    if not RECIPE.search(t):            return False
    if genre in EXCLUDE_GENRE:          return False
    if genre in ("Education", "Medical") and KIDS_GAME.search(name or ""):
        return False
    if genre == "Education" and KIDS_V4.search(name or ""):
        return False
    ph, ck = len(PHARMA.findall(t)), len(COOK.findall(t))
    if ph >= 3 and ph > ck:             return False
    return ck >= 2
