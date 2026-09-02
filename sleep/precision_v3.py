#!/usr/bin/env python3
"""
Precision layer v3 = v2 + rule MH. Decided and dated 2026-09-02.

Rule MH (condition-dominated mental-health companion): an app whose own
description is dominated by clinical-condition vocabulary is a mental-health
app, not a sleep/relaxation aid — the frozen category definition asks what the
description identifies the app as. Fires when condition words (depression,
Angststörung, Panikattacke, Phobie, Angst/Panik, mentale Gesundheit / mental
health, psychisch) appear >= 4 times AND outnumber sleep/relaxation vocabulary.

Sized before deciding, on the 2026-09-01 consolidated set (3,114 apps):
32 apps (1.0%) — MindDoc, Rootd, DARE, Quabble, Moodfit, Mindspa, Elomia,
Somaya and the rest of that shelf; no false positives observed in review.
No headline figure moves by more than rounding. Kept as a separate file so the
hop runs classified under v2 stay reproducible as they were run; final counts
are produced by apply_v3.py, uniformly across all hops.
"""
import re
from precision_v2 import v2_excluded

COND  = re.compile(r"\bdepression|panikattack|angststörung|phobie|angst|panik|"
                   r"mental health|mentale gesundheit|psychisch", re.I)
SLEEPY= re.compile(r"schlaf|sleep|einschlaf|meditation|entspann|achtsam|mindful|"
                   r"atemübung|hypnose|rauschen|white noise|klänge|geräusch", re.I)

def v3_excluded(rec):
    """Returns the fired rule as a short string, or None if the app survives."""
    r = v2_excluded(rec)
    if r: return r
    t = (rec.get("trackName") or "") + " " + (rec.get("description") or "")
    c, s = len(COND.findall(t)), len(SLEEPY.findall(t))
    if c >= 4 and c > s:
        return f"MH: condition-dominated ({c} condition vs {s} sleep/relax)"
    return None
