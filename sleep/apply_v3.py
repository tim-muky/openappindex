#!/usr/bin/env python3
"""
Apply precision v3 uniformly across every hop's kept set and write the final
category files:

  data/sleep_slice_v3.json      sweep-visible apps, v3
  data/hop{1,2,3}_sleep_v3.json closure finds per hop, v3

Prints every MH exclusion by name so the decision is auditable, then the
consolidated category count. Run only after all hops' finishing passes are
complete, so every hop is filtered under identical rules.
"""
import json, os
from precision_v3 import v3_excluded

SETS=[("data/sleep_slice_v2.json","data/sleep_slice_v3.json","sweep"),
      ("data/new_apps_sleep.json","data/hop1_sleep_v3.json","hop-1"),
      ("data/hop2_sleep.json","data/hop2_sleep_v3.json","hop-2"),
      ("data/hop3_sleep.json","data/hop3_sleep_v3.json","hop-3"),
      ("data/hop4_sleep.json","data/hop4_sleep_v3.json","hop-4")]

total=0; out_total=0
for src,dst,label in SETS:
    if not os.path.exists(src):
        print(f"{label}: {src} missing — skipped"); continue
    d=json.load(open(src,encoding="utf-8"))
    apps=d if isinstance(d,list) else list(d.values())
    kept,dropped=[],[]
    for a in apps:
        r=v3_excluded(a)
        (dropped if r else kept).append((a,r))
    mh=[(a,r) for a,r in dropped if r and r.startswith("MH:")]
    print(f"{label}: {len(apps)} → {len(kept)} (MH excludes {len(mh)})")
    for a,r in mh:
        print(f"    OUT {(a.get('trackName') or '')[:46]:<48} {r}")
    json.dump([a for a,_ in kept] if isinstance(d,list) else {str(a['trackId']):a for a,_ in kept},
              open(dst,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    total+=len(kept); out_total+=len(mh)
print(f"\nfinal consolidated category (v3): {total} apps · MH excluded in total: {out_total}")
