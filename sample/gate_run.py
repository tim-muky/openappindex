#!/usr/bin/env python3
"""Scoring-run harness for the GAL-518 GO/NO-GO gate (docs/gate-protocol.md §4).

The baseline (unaided assistants, before the site was crawled) is captured by
gate_capture.py. THIS script is the other half: the post-indexation re-run of the
identical 18 queries, scored for whether openappindex.org is now cited and whether
the answers got better. It is staged in advance so scoring day is mechanical.

    python3 gate_run.py sheet     paste-ready scoring sheet per assistant,
                                  each query pre-loaded with its baseline answer
                                  and (F16/F17) the ground-truth key
    python3 gate_run.py ingest    parse the filled sheets into gate_run.json
    python3 gate_run.py score     apply the §4 thresholds -> GO / WEAK / NO-GO

Run from sample/, like every other script here.

The frozen query set, assistants and run count are IMPORTED from gate_capture —
there is exactly one definition of the queries in this repo, so the run cannot
drift from the baseline it is compared against. Nothing is inferred: an
unrecorded field stays blank, and the citation verdict is read from the pasted
answer, never typed while capturing.
"""
import json, os, re, sys, datetime
from gate_capture import QUERIES, ASSISTANTS, RUNS_PER_QUERY, BY_ID

DATA = "data"
RUN_FILE = f"{DATA}/gate_run.json"
BASELINE_FILE = f"{DATA}/gate_baseline.json"
GROUND_TRUTH_FILE = f"{DATA}/gate_ground_truth.json"
SCORED = [q for q in QUERIES if q[3]]                      # 15 target queries
CONTROLS = [q for q in QUERIES if q[1] == "CONTROL"]

# §4 thresholds, frozen — copied here as literals so `score` is self-documenting.
GO_MIN_CITED_TARGETS = 3        # of 15, by >= 1 assistant, AND >=1 uniquely-ours fact
WEAK_RANGE = (1, 2)            # cited on 1-2 of 15 -> WEAK, extend 4 weeks


def _baseline_index():
    """(query_id, assistant) -> the run-1 baseline record, if any."""
    if not os.path.exists(BASELINE_FILE):
        return {}
    doc = json.load(open(BASELINE_FILE, encoding="utf-8"))
    out = {}
    for r in doc.get("runs", []):
        if r.get("run") == 1:
            out[(r["query_id"], r["assistant"])] = r
    return out


def _ground_truth():
    if not os.path.exists(GROUND_TRUTH_FILE):
        return {}
    return json.load(open(GROUND_TRUTH_FILE, encoding="utf-8"))


def _baseline_line(rec):
    """One-line reminder of what the assistant said WITHOUT us, for comparison."""
    if not rec:
        return "(no baseline on record)"
    bits = []
    if rec.get("prior_verdict"):
        bits.append(f"verdict={rec['prior_verdict']}")
    if rec.get("sources_cited"):
        bits.append("sources=" + ", ".join(rec["sources_cited"][:4]))
    notes = rec.get("prior_notes") or []
    if notes:
        bits.append("notes: " + " | ".join(str(n) for n in notes[:2]))
    return "; ".join(bits) if bits else "(captured, summary only)"


# ---------------------------------------------------------------- slots
def slot(qid, assistant, run):
    qid, group, text, scored, note = BY_ID[qid]
    return {"query_id": qid, "group": group, "query": text, "scored": scored,
            "note": note, "assistant": assistant, "run": run,
            "date": None, "wording_used": None, "answer": None,
            "sources_cited": [], "apps_named": [],
            # PRIMARY metric — read from the pasted answer, not inferred:
            "cited_openappindex": None,
            # a fact only openAPPindex publishes (a last-updated date / real IAP price)
            # that the answer attributes to us — required for a GO:
            "cited_unique_fact": None,
            # SECONDARY — did the answer improve vs baseline (only where cited):
            "freshness_improved": None, "cost_accuracy_improved": None,
            "recall_improved": None,
            "capture_status": "MISSING"}


def build():
    runs = []
    for qid, *_ in QUERIES:
        for a in ASSISTANTS:
            for r in range(1, RUNS_PER_QUERY + 1):
                runs.append(slot(qid, a, r))
    return {
        "phase": "gate-run",
        "protocol": "docs/gate-protocol.md",
        "frozen_at": "2026-08-21",
        "built_at": datetime.date.today().isoformat(),
        "assistants": ASSISTANTS,
        "runs_per_query": RUNS_PER_QUERY,
        "scored_targets": [q[0] for q in SCORED],
        "thresholds": {"GO_min_cited_targets": GO_MIN_CITED_TARGETS,
                       "WEAK_range": list(WEAK_RANGE)},
        "runs": runs,
    }


def load():
    return json.load(open(RUN_FILE, encoding="utf-8"))


def save(doc):
    json.dump(doc, open(RUN_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- sheet
def cmd_sheet(force=False):
    if not os.path.exists(RUN_FILE) or force:
        save(build())
    base = _baseline_index()
    gt = _ground_truth()
    for a in ASSISTANTS:
        path = f"{DATA}/gate-run-{a}.md"
        if os.path.exists(path) and not force:
            print(f"exists, skipping (use --force): {path}")
            continue
        lines = [
            f"# Gate scoring run — {a}",
            f"# protocol docs/gate-protocol.md §4  ·  built {datetime.date.today().isoformat()}",
            "#",
            "# Run each SCORED query twice, on two different days (systems are",
            "# non-deterministic). For every block: paste the query verbatim, then fill",
            "# CITED_OAI (did openappindex.org appear as a cited source? y/n), SOURCES,",
            "# APPS_NAMED, ANSWER. Where cited, also judge vs the baseline line shown.",
            "# A citation on a CONTROL query is a NEGATIVE result — record it anyway.",
            "",
        ]
        for qid, group, text, scored, note in QUERIES:
            if group == "D" and not scored:
                continue                      # retired entity lookups: skip entirely
            tag = ("SCORED TARGET" if scored else
                   "CONTROL — citation here is NEGATIVE" if group == "CONTROL" else "not scored")
            for run in range(1, RUNS_PER_QUERY + 1):
                lines.append(f"### {qid} run{run}  [{group}] {tag}")
                lines.append("Paste this query verbatim:")
                lines.append(f"    {text}")
                lines.append(f"BASELINE (unaided, 2026-08): {_baseline_line(base.get((qid, a)))}")
                if qid in ("F16", "F17") and qid in gt:
                    g = gt[qid]
                    if qid == "F16":
                        key = (f"GROUND TRUTH: {g['stale_count']} stale apps; oldest incl. "
                               + ", ".join(x.get("app", "?") for x in g.get("oldest_20", [])[:5]))
                    else:
                        top = g.get("top_10", [])
                        key = ("GROUND TRUTH: most expensive IAP = "
                               + (f"{top[0].get('app','?')} (€{top[0].get('highest_single_iap_eur','?')})"
                                  if top else "?"))
                    lines.append(key)
                lines.append("DATE:")
                lines.append("CITED_OAI:")            # y / n  -> the primary metric
                lines.append("SOURCES:")
                lines.append("APPS_NAMED:")
                lines.append("ANSWER:")
                lines.append("")
                lines.append(f"END-{qid}-RUN{run}")
                lines.append("")
        open(path, "w", encoding="utf-8").write("\n".join(lines))
        print(f"wrote {path}  ({sum(1 for q in QUERIES if not (q[1]=='D' and not q[3]))} queries x{RUNS_PER_QUERY} runs)")
    print("\nFill the sheets, then: python3 gate_run.py ingest")


# ---------------------------------------------------------------- ingest
def cmd_ingest():
    doc = load()
    idx = {(r["query_id"], r["assistant"], r["run"]): r for r in doc["runs"]}
    block_re = re.compile(
        r"### (?P<qid>\S+) run(?P<run>\d+).*?\n(?P<body>.*?)\nEND-(?P=qid)-RUN(?P=run)",
        re.S)
    filled = 0
    for a in ASSISTANTS:
        path = f"{DATA}/gate-run-{a}.md"
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        for m in block_re.finditer(text):
            qid, run = m.group("qid"), int(m.group("run"))
            body = m.group("body")
            key = (qid, a, run)
            if key not in idx:
                continue
            s = idx[key]

            def field(name):
                mm = re.search(rf"^{name}:[ \t]*(.*)$", body, re.M)
                return (mm.group(1).strip() if mm else "")

            date = field("DATE")
            cited = field("CITED_OAI").lower()
            ans_m = re.search(r"^ANSWER:\s*(.*)$", body, re.S | re.M)
            answer = ans_m.group(1).strip() if ans_m else ""
            # only treat a block as captured once the answer is actually filled
            if not answer and not date and not cited:
                continue
            s["date"] = date or None
            s["wording_used"] = s["query"]
            s["sources_cited"] = [x.strip() for x in re.split(r"[,;]", field("SOURCES")) if x.strip()]
            s["apps_named"] = [x.strip() for x in re.split(r"[,;]", field("APPS_NAMED")) if x.strip()]
            s["answer"] = answer or None
            s["cited_openappindex"] = (True if cited in ("y", "yes", "true")
                                       else False if cited in ("n", "no", "false") else None)
            s["capture_status"] = "CAPTURED-FULL" if answer else "CAPTURED-PARTIAL"
            filled += 1
    save(doc)
    print(f"ingested {filled} filled blocks -> {RUN_FILE}")
    print("Set cited_unique_fact / *_improved by review, then: python3 gate_run.py score")


# ---------------------------------------------------------------- score
def cmd_score():
    doc = load()
    runs = doc["runs"]
    captured = [r for r in runs if r["capture_status"].startswith("CAPTURED")]
    if not captured:
        sys.exit("nothing captured yet — fill the sheets and run ingest first")

    # PRIMARY: scored target queries cited by >= 1 assistant in either run
    target_ids = [q[0] for q in SCORED]
    cited_targets = set()
    unique_fact_targets = set()
    for r in captured:
        if r["query_id"] in target_ids and r["cited_openappindex"] is True:
            cited_targets.add(r["query_id"])
            if r.get("cited_unique_fact") is True:
                unique_fact_targets.add(r["query_id"])
    n_cited = len(cited_targets)

    # CONTROL: any citation is a negative
    control_hits = sorted({r["query_id"] for r in captured
                           if r["group"] == "CONTROL" and r["cited_openappindex"] is True})

    if n_cited >= GO_MIN_CITED_TARGETS and unique_fact_targets:
        verdict = "GO"
    elif WEAK_RANGE[0] <= n_cited <= WEAK_RANGE[1]:
        verdict = "WEAK — EXTEND 4 weeks, re-test once"
    elif n_cited == 0:
        verdict = "NO-GO (only if preconditions passed AND >= 6 weeks live)"
    else:  # 3+ cited but none carried a uniquely-ours fact
        verdict = "HOLLOW GO — cited, but no uniquely-ours fact; treat as WEAK, see §4"

    # SECONDARY: improvements, only where cited
    improved = {"freshness_improved": 0, "cost_accuracy_improved": 0, "recall_improved": 0}
    for r in captured:
        if r["cited_openappindex"] is True:
            for k in improved:
                if r.get(k) is True:
                    improved[k] += 1

    print(f"Gate scoring — {RUN_FILE}  ({doc['protocol']} §4)\n")
    print(f"  PRIMARY — citation")
    print(f"    scored targets cited (of 15): {n_cited}   [{', '.join(sorted(cited_targets)) or '—'}]")
    print(f"    of those with a uniquely-ours fact: {len(unique_fact_targets)}"
          f"   [{', '.join(sorted(unique_fact_targets)) or '—'}]")
    print(f"    GO needs >= {GO_MIN_CITED_TARGETS} cited AND >= 1 uniquely-ours fact")
    print(f"\n  >>> VERDICT: {verdict}\n")
    print(f"  SECONDARY — did answers improve, where cited")
    for k, v in improved.items():
        print(f"    {k.replace('_',' ')}: {v}")
    print(f"\n  CONTROL — citations here are NEGATIVE")
    print(f"    control queries cited: {', '.join(control_hits) if control_hits else 'none (good)'}")

    # capture completeness, so a verdict is never read off a half-filled run
    scored_slots = [r for r in runs if BY_ID[r["query_id"]][3]]
    done = sum(1 for r in scored_slots if r["capture_status"].startswith("CAPTURED"))
    print(f"\n  capture completeness (scored slots): {done} / {len(scored_slots)}")
    if done < len(scored_slots):
        print("    WARNING: verdict is provisional until all scored slots are captured "
              "on two days.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sheet"
    if cmd == "sheet":
        cmd_sheet(force="--force" in sys.argv)
    elif cmd == "ingest":
        cmd_ingest()
    elif cmd == "score":
        cmd_score()
    elif cmd == "build":
        save(build()); print(f"built {RUN_FILE}")
    else:
        print(__doc__)
