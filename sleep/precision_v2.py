#!/usr/bin/env python3
"""
Precision layer v2 for the sleep/meditation slice — the analogue of cooking's v4
(sample/precision_check.py). Written 2026-09-01 AFTER inspecting the v1 slice,
each rule motivated by an observed error class, layered on top of the frozen v1
(classify.py). Rules, not judgement: every exclusion states which rule fired.

Observed error classes (2026-09-01, from reading descriptions in the v1 slice):

  T  baby-care logbooks — feeding/diaper/growth trackers that log sleep as one
     field among many ("Baby Tracker Pro", "Stillen App & Baby Tracker").
     Baby SLEEP-AID apps (white noise, lullabies) are genuine and must survive.
  BM baby monitors the v1 counter missed via English naming ("Cloud Baby Monitor").
  D  hardware companions — the app operates a purchased device: smart ring,
     wearable band, CPAP machine, wake-up light, sound plush (Oura, WHOOP,
     Withings, DreamMapper, SleepMapper, myHummy, FontaFit).
  G  general health-analytics coaches — heart rate/HRV/blood pressure/longevity
     dashboards where sleep is one metric (CardioBot, Welltory, Hearty, Bevel).
  P  pregnancy/birth apps — incl. hypnobirthing (keleya, mamly, Die Friedliche
     Geburt, Wehen Timer ConTe).
  H  purpose-specific hypnosis/cessation — weight loss, smoking, flight anxiety,
     IBS ("Get Slim & Fit! Hypnose", "Rauchfrei", "Flugangst überwinden").
     Sleep/nap hypnosis survives.
  C  clinical mental-health therapy programs (MindDoc, HelloBetter, 7 Cups,
     Kaia COPD) — therapy platforms, not relaxation aids.
  Y  fitness/yoga workout apps (Asana Rebel, "Yoga for Weight Loss").
  U  clock/timer utilities with no sleep-aid claim (ClockZ, Timer+, AppBox Pro,
     Super Alarm morning-routine). Sleep-cycle alarms survive.
  GE genre additions: Sports (freediving apnea trainers), Navigation (anchor
     alarms) — no genuine sleep app was observed in either.

    python3 precision_v2.py          report + write data/sleep_slice_v2.json
"""
import json, re, collections

def G(*pats): return [re.compile(p, re.I) for p in pats]

# Each rule: a list of signal GROUPS; it fires when >= `need` DISTINCT groups hit.
# The wickel/entwickelt trap (found 2026-09-01, first run of this file): plain
# `wickel` matches inside "entwickelt"/"Entwicklung" and flagged meditation apps
# as baby logbooks. \b guard added; the German-homonym list grows by one.
RULES = [
  ("T: baby-care logbook", 2, G(r"windel|\bwickel", r"stillen|füttern|abpump|fläschchen|flasche|beikost",
                                r"wachstum|meilenstein")),
  ("BM: baby monitor", 1, G(r"babyphone|babyfon|baby.?monitor")),
  ("D: hardware companion", 2, G(r"smart.?ring|wearable|armband", r"cpap|beatmung|maske",
                                 r"gekoppelt|koppeln|kopplung|verbinde.{0,20}gerät",
                                 r"wake.?up.?light|lichtwecker|somneo|smartsleep",
                                 r"unsere[nm]? (gerät|uhr|mechanismus)|kompatible[nm]? (gerät|uhr|mechanism)",
                                 # device ecosystems observed in this corpus, 2026-09-01
                                 r"\boura\b|\bwhoop\b|withings|fitbit|fontastic")),
  ("G: health-analytics coach", 3, G(r"herzfrequenz|puls", r"blutdruck", r"hrv|herzfrequenzvariabilität",
                                     r"ekg|blutzucker", r"longevity|lebenserwartung", r"kalorien|ernährung")),
  ("P: pregnancy/birth", 2, G(r"schwanger", r"geburt", r"wehen|hypnobirthing")),
  # H is name-based: a purpose-specific hypnosis/cessation app states its purpose
  # in its title; description boilerplate (a publisher listing its other titles)
  # and `hypnose` counting as a sleep-aid word made description-weighing unusable.
  # \bslim\b: bare `slim` matched inside "Slime" and "Muslim" (found 2026-09-01,
  # excluding a Muslim meditation app) — the substring-trap list grows again.
  ("H: purpose hypnosis/cessation (name)", 1, G(r"rauchfrei|nichtraucher|rauchen|\bslim\b|abnehm|gewicht verlieren|"
                                                r"flugangst|reizdarm")),
  # C: the first group (program/prescription identity) is COMPULSORY — condition
  # words alone are marketing ("hilft bei Depressionen" on a sounds app, a
  # publisher's boilerplate listing its other hypnosis titles) and must not fire.
  ("C: clinical therapy program", 2, G(r"therapieprogramm|online.?therapie|psychologische soforthilfe|"
                                       r"auf rezept|krankenkasse|diga\b",
                                       r"\bdepression",
                                       r"panikattack|angststörung|phobie",
                                       r"copd|chronische[nr]? (erkrankung|schmerz)")),
  ("Y: fitness/yoga workout", 2, G(r"workout|training(spl|s-)?plan", r"abnehm|gewichtsverlust|gewicht zu verlieren",
                                   r"muskel", r"fitness")),
  ("U: clock/timer utility", 1, G(r"(wecker|uhr|timer|stoppuhr)")),   # gated below on missing sleep-aid claim
]
SLEEP_AID = re.compile(r"einschlaf|schlafzyklus|schlafphase|schlaftrack|schlafanaly|schlafgeräusch|"
                       r"rauschen|white noise|meditation|entspannung|hypnose|beruhig|schlaflied|"
                       r"schlafgeschicht|besser (zu )?schlafen|schlaf verbessern|schlafqualität|"
                       r"schlafhilfe|schlafplan|schlafwissenschaft|achtsam|mindful|atemübung|atemtraining|"
                       r"pranayama|box.?breathing|naturgeräusch|klänge|lullab|power.?nap|nickerchen|"
                       r"fall(ing)? asleep|sleep (cycle|tracker|sounds?|score|aid)|bedtime|"
                       r"schlafstörung|insomni|schlaftraining", re.I)
# Per the frozen protocol, clinical sleep therapeutics (somnio, hiPanya) are IN
# scope: rule C is exempt when the text is dominated by sleep (>=8 schlaf-family
# hits — a general therapy platform mentions sleep once or twice in a program
# list, a sleep therapeutic says little else).
SCHLAF = re.compile(r"schlaf", re.I)
GENRE_V2 = {"Sports", "Navigation"}

def v2_excluded(rec):
    """Returns the fired rule as a short string, or None if the app survives."""
    name, desc, genre = rec.get("trackName") or "", rec.get("description") or "", rec.get("primaryGenreName")
    t = name + " " + desc
    if genre in GENRE_V2:
        return f"GE: genre {genre}"
    aid = len(SLEEP_AID.findall(t))
    for label, need, groups in RULES:
        # H matches against the title only; everything else against name+description
        hits = [g.pattern[:24] for g in groups
                if g.search(name if label.startswith("H:") else t)]
        if len(hits) < need:
            continue
        # BM and H are categorical: a babyphone is out however many lullabies it
        # ships, and a title stating a non-sleep purpose decides by itself.
        if label.startswith(("BM:", "H:")):
            return f"{label} ({', '.join(hits)})"
        # U fires only when the app makes no sleep-aid claim at all;
        # every other rule must out-signal the sleep-aid claim to fire.
        if label.startswith("U:"):
            if aid == 0: return f"{label} ({', '.join(hits)}; no sleep-aid claim)"
            continue
        # C is categorical (a therapy platform's wellness vocabulary would
        # otherwise outweigh it), needs its compulsory first group, and is
        # exempt for sleep-dominated therapeutics (in scope per protocol).
        if label.startswith("C:"):
            if not groups[0].search(t): continue
            if len(SCHLAF.findall(t)) >= 8: continue
            return f"{label} ({', '.join(hits[:3])})"
        raw = sum(len(g.findall(t)) for g in groups)
        if raw > aid:
            return f"{label} ({', '.join(hits[:3])}; signals {raw} > sleep-aid {aid})"
    return None

if __name__ == "__main__":
    S = json.load(open("data/sleep_slice.json", encoding="utf-8"))
    keep, drop = [], []
    for rec in sorted(S, key=lambda x: (x.get("trackName") or "").lower()):
        r = v2_excluded(rec)
        (drop if r else keep).append((rec, r))
    print(f"v1 slice: {len(S)} · survive v2: {len(keep)} · excluded: {len(drop)}\n")
    by = collections.Counter(r.split(":")[0] for _, r in drop)
    for k, n in by.most_common(): print(f"  {k:<4} {n}")
    print()
    for rec, r in drop:
        print(f"  OUT {(rec.get('trackName') or '')[:44]:<46} {r[:90]}")
    json.dump([r for r, _ in keep], open("data/sleep_slice_v2.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\nwrote data/sleep_slice_v2.json ({len(keep)} apps)")
