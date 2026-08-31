#!/usr/bin/env python3
"""Capture harness for the GAL-518 GO/NO-GO baseline (docs/gate-protocol.md).

The baseline is the one part of the gate that cannot be reconstructed: once
openappindex.org is crawled, what the assistants said without it is gone. This
script exists to make capture cheap enough to finish before that happens.

    python3 gate_capture.py status    what is captured, what is missing
    python3 gate_capture.py sheet     write paste-ready sheets, one per assistant
    python3 gate_capture.py ingest    parse the sheets back into gate_baseline.json

Run it from sample/, like every other script here.

Two things it deliberately enforces:

1. Query wording is frozen. The 2026-08-23 amendment kept the wording of every
   retained query precisely so baseline and post-launch runs stay comparable, but
   the already-captured runs drifted anyway ("Ist Mein Rezeptebuch noch aktuell?"
   was asked as "Ist die App Mein Rezeptebuch noch aktuell und wird sie
   gepflegt?"). The sheet carries the verbatim string to copy, and ingest records
   what was actually pasted, so drift is visible in the data instead of silent.

2. Nothing is inferred. An unanswered field stays null. Verdicts and citation
   counts are scored later, from the recorded text, not typed in while capturing.
"""
import json, os, re, sys, datetime

DATA = "data"
CANON = f"{DATA}/gate_baseline.json"
ASSISTANTS = ["perplexity", "chatgpt-search", "claude-websearch"]
RUNS_PER_QUERY = 2          # protocol asks for two, on different days

# The frozen set, as amended 2026-08-23. Order is the protocol's order.
QUERIES = [
    ("A1",  "A", "Welche Rezept-App wird noch aktiv gepflegt?", True, None),
    ("A2",  "A", "Rezept-App die noch Updates bekommt", True, None),
    ("A3",  "A", "Ist Mein Rezeptebuch noch aktuell?", True, None),
    ("A4",  "A", "Welche Koch-Apps wurden seit Jahren nicht aktualisiert?", True, None),
    ("B5",  "B", "Rezept-App ohne Abo", True, None),
    ("B6",  "B", "Rezepte-App einmalig bezahlen statt Abo", True, None),
    ("B7",  "B", "Was kostet Chefkoch wirklich?", True, None),
    ("B8",  "B", "Kostenlose Rezept-App ohne versteckte Kosten", True, None),
    ("B9",  "B", "Welche Rezept-Apps haben teure In-App-Käufe?", True, None),
    ("C10", "C", "App zum Speichern von Rezepten von Webseiten", True, None),
    ("C11", "C", "Beste App um eigene Rezepte zu verwalten", True, None),
    ("C12", "C", "Rezepte sammeln App Deutschland", True, None),
    ("D13", "D", "KptnCook Kosten In-App-Käufe", True, None),
    ("D14", "D", "Kitchen Stories Abo Preis", False,
     "retired 2026-08-23 — ChatGPT answered exactly correctly at baseline"),
    ("D15", "D", "galleybook App", False,
     "retired 2026-08-23 — contaminated by that app's own listing change (GAL-534)"),
    ("F16", "F", "Liste von Rezept-Apps die seit über zwei Jahren kein Update bekommen haben", True, None),
    ("F17", "F", "Welche Rezept-App im deutschen App Store hat den teuersten In-App-Kauf?", True, None),
    ("X1",  "CONTROL", "Rezept für Lasagne", False,
     "control — a citation here is a NEGATIVE result"),
    ("X2",  "CONTROL", "Wie lange muss ein Ei kochen?", False,
     "control — a citation here is a NEGATIVE result"),
    ("X3",  "CONTROL", "Chefkoch Rezept Käsekuchen", False,
     "control — a citation here is a NEGATIVE result"),
]
BY_ID = {q[0]: q for q in QUERIES}

# Runs already captured on 2026-08-23, mapped to frozen ids. Where the wording
# drifted from the frozen string, the drift is recorded rather than corrected.
PRIOR = {
    "perplexity": {1: "A1", 2: "B5", 3: "B7", 4: "B9", 5: "C10", 6: "D13",
                   7: "D14", 8: "A3", 9: "A2", 10: "A4", 11: "B8", 12: "B6", 13: "X1"},
    "chatgpt-search": {1: "A1", 2: "B9", 3: "A3", 4: "A4"},
}
PRIOR_FILE = {"perplexity": f"{DATA}/gate_baseline_perplexity.json",
              "chatgpt-search": f"{DATA}/gate_baseline_chatgpt.json"}


def slot(qid, assistant, run):
    qid, group, text, scored, note = BY_ID[qid]
    return {"query_id": qid, "group": group, "query": text, "scored": scored,
            "note": note, "assistant": assistant, "run": run,
            "date": None, "wording_used": None, "answer": None,
            "sources_cited": [], "apps_named": [],
            "maintenance_claim": None, "cost_claim": None,
            "cited_openappindex": None, "capture_status": "MISSING"}


def build():
    """Rebuild the canonical file: amended query set, prior captures merged in."""
    runs = []
    for qid, *_ in QUERIES:
        for a in ASSISTANTS:
            for r in range(1, RUNS_PER_QUERY + 1):
                runs.append(slot(qid, a, r))
    index = {(s["query_id"], s["assistant"], s["run"]): s for s in runs}

    for assistant, mapping in PRIOR.items():
        path = PRIOR_FILE[assistant]
        if not os.path.exists(path):
            continue
        prior = {r["n"]: r for r in json.load(open(path, encoding="utf-8"))["runs"]}
        for n, qid in mapping.items():
            rec = prior.get(n)
            if rec is None:
                continue
            s = index[(qid, assistant, 1)]
            s["date"] = "2026-08-23"
            s["wording_used"] = rec["q"]
            s["answer"] = None          # only notes survive; full text was not kept
            s["sources_cited"] = rec.get("sources", [])
            s["prior_verdict"] = rec.get("verdict")
            s["prior_notes"] = rec.get("notes", [])
            if "response_1" in rec:
                s["prior_responses"] = [rec.get("response_1"), rec.get("response_2")]
            s["cited_openappindex"] = False   # site was not live on 2026-08-23
            # "CONTROL: " is a logging prefix from the 2026-08-23 sheet, not drift.
            asked = re.sub(r"^CONTROL:\s*", "", rec["q"])
            s["capture_status"] = ("CAPTURED-SUMMARY" if asked == BY_ID[qid][2]
                                   else "CAPTURED-SUMMARY-WORDING-DRIFT")
    return {
        "frozen_at": "2026-08-21",
        "amended_at": "2026-08-23",
        "protocol": "docs/gate-protocol.md",
        "phase": "baseline",
        "assistants": ASSISTANTS,
        "runs_per_query": RUNS_PER_QUERY,
        "scored_targets": [q[0] for q in QUERIES if q[3]],
        "not_scored": {q[0]: q[4] for q in QUERIES if not q[3]},
        "capture_status_values": {
            "MISSING": "not captured",
            "CAPTURED-FULL": "verbatim answer and sources recorded",
            "CAPTURED-SUMMARY": "2026-08-23 run; verdict and notes only, no verbatim answer",
            "CAPTURED-SUMMARY-WORDING-DRIFT": "as above, and the query asked was not the frozen string",
        },
        "ground_truth_for_scoring": json.load(open(CANON, encoding="utf-8"))
            ["ground_truth_for_scoring"] if os.path.exists(CANON) else {},
        "runs": runs,
    }


def load():
    return json.load(open(CANON, encoding="utf-8"))


def save(doc):
    json.dump(doc, open(CANON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- status
def cmd_status(doc=None):
    doc = doc or load()
    runs = doc["runs"]
    print(f"Baseline capture — {CANON}")
    print(f"protocol {doc['protocol']}  ·  frozen {doc['frozen_at']}, amended {doc['amended_at']}\n")
    hdr = f"{'':6}" + "".join(f"{a:>18}" for a in ASSISTANTS)
    print(hdr); print("-" * len(hdr))
    for qid, group, text, scored, note in QUERIES:
        cells = ""
        for a in ASSISTANTS:
            marks = []
            for r in range(1, RUNS_PER_QUERY + 1):
                s = next(x for x in runs if x["query_id"] == qid
                         and x["assistant"] == a and x["run"] == r)
                marks.append({"MISSING": "·", "CAPTURED-FULL": "#",
                              "CAPTURED-SUMMARY": "~",
                              "CAPTURED-SUMMARY-WORDING-DRIFT": "!",
                              "WINDOW-CLOSED": "x"}[s["capture_status"]])
            cells += f"{''.join(marks):>18}"
        flag = " " if scored else "-"
        print(f"{flag}{qid:<5}{cells}   {text[:44]}")
    print("\n  # verbatim   ~ summary only   ! summary, wording drifted   · missing"
          "   x window closed")
    print("  - not scored (retired query or control)\n")

    tot = len(runs)
    done = sum(1 for r in runs if r["capture_status"] != "MISSING")
    full = sum(1 for r in runs if r["capture_status"] == "CAPTURED-FULL")
    scored_r1 = [r for r in runs if r["run"] == 1 and BY_ID[r["query_id"]][3]]
    scored_r1_missing = [r for r in scored_r1 if r["capture_status"] == "MISSING"]
    print(f"  slots filled          {done:>3} / {tot}   ({full} with a verbatim answer)")
    print(f"  scored targets, run 1 {len(scored_r1)-len(scored_r1_missing):>3} / {len(scored_r1)}"
          f"   <- the irrecoverable set")
    if scored_r1_missing:
        by_a = {}
        for r in scored_r1_missing:
            by_a.setdefault(r["assistant"], []).append(r["query_id"])
        print("\n  still missing (run 1, scored):")
        for a in ASSISTANTS:
            if a in by_a:
                print(f"    {a:<18} {len(by_a[a]):>2}  {' '.join(by_a[a])}")


# ---------------------------------------------------------------- sheet
BLOCK = """
### {qid} {tag}
Paste this query verbatim:

    {query}

DATE:
SOURCES:
ANSWER:

END-{qid}-RUN{run}

"""

def cmd_sheet(force=False):
    doc = load()
    runs = doc["runs"]
    today = datetime.date.today().isoformat()
    written = []
    for a in ASSISTANTS:
        missing = [r for r in runs if r["assistant"] == a and r["capture_status"] == "MISSING"]
        if not missing:
            continue
        tiers = [
            ("TIER 1 — scored targets, run 1. Irrecoverable once the site is crawled.",
             [r for r in missing if r["run"] == 1 and BY_ID[r["query_id"]][3]]),
            ("TIER 2 — controls, run 1. A citation here is a negative result, so the "
             "unaided answer has to be on record too.",
             [r for r in missing if r["run"] == 1 and r["group"] == "CONTROL"]),
            ("TIER 3 — second runs. The protocol asks for two runs on different days, "
             "because these systems are non-deterministic.",
             [r for r in missing if r["run"] == 2 and BY_ID[r["query_id"]][3]]),
            ("TIER 4 — retired queries and control second runs. Optional; recorded, not scored.",
             [r for r in missing if r["run"] == 2 and not BY_ID[r["query_id"]][3]
              or (r["run"] == 1 and not BY_ID[r["query_id"]][3] and r["group"] != "CONTROL")]),
        ]
        out = [f"# Baseline capture — {a}", "",
               f"Sheet generated {today}. Protocol: `docs/gate-protocol.md`.", "",
               "**Web search must be ON.** Paste each query *verbatim* — the wording is frozen,",
               "and two of the runs already captured drifted from it, which costs comparability",
               "against the post-launch run.", "",
               "Fill `DATE:`, `SOURCES:` (comma-separated URLs) and everything between `ANSWER:`",
               "and the `END-` line. Paste the whole answer, unedited — a wrong answer is the most",
               "valuable thing here. Leave a block untouched to skip it; nothing is inferred from",
               "a blank. Then run `python3 gate_capture.py ingest`.", ""]
        for title, group in tiers:
            group = [r for r in group if r in missing]
            if not group:
                continue
            out.append(f"\n## {title}\n")
            for r in group:
                qid = r["query_id"]
                _, _, text, scored, note = BY_ID[qid]
                tag = f"· run {r['run']}" + (f" · {note}" if note else "")
                out.append(BLOCK.format(qid=qid, tag=tag, query=text, run=r["run"]))
        path = f"{DATA}/capture-{a}.md"
        # Never overwrite a sheet that may hold answers not yet ingested. Losing a
        # captured answer is unrecoverable once the site is crawled.
        if os.path.exists(path) and not force:
            if any(r["answer"] for r in parse_sheet(path, a)):
                print(f"  ! {path} holds answers that are not ingested yet — "
                      f"run `ingest` first, or `sheet --force` to discard them")
                continue
        open(path, "w", encoding="utf-8").write("\n".join(out))
        written.append((path, len(missing)))
    for p, n in written:
        print(f"wrote {p}  ({n} blocks)")
    if not written:
        print("nothing missing — every slot is filled")


# ---------------------------------------------------------------- ingest
HEAD = re.compile(r"^### ([A-FX]\d+) .*?· run (\d+)", re.M)

def parse_sheet(path, assistant):
    text = open(path, encoding="utf-8").read()
    out = []
    heads = list(HEAD.finditer(text))
    for i, m in enumerate(heads):
        qid, run = m.group(1), int(m.group(2))
        body = text[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        end = body.find(f"END-{qid}-RUN{run}")
        if end != -1:
            body = body[:end]
        def field(name):
            fm = re.search(rf"^{name}:[ \t]*(.*)$", body, re.M)
            return (fm.group(1).strip() if fm else "")
        am = re.search(r"^ANSWER:[ \t]*\n?(.*)$", body, re.S | re.M)
        answer = (am.group(1).strip() if am else "")
        if not answer:
            continue                      # untouched block — skip, infer nothing
        srcs = [s.strip() for s in field("SOURCES").split(",") if s.strip()]
        out.append({"query_id": qid, "run": run, "assistant": assistant,
                    "date": field("DATE") or None, "answer": answer,
                    "sources_cited": srcs})
    return out


def cmd_ingest():
    doc = load()
    index = {(r["query_id"], r["assistant"], r["run"]): r for r in doc["runs"]}
    n = 0
    for a in ASSISTANTS:
        path = f"{DATA}/capture-{a}.md"
        if not os.path.exists(path):
            continue
        for rec in parse_sheet(path, a):
            s = index.get((rec["query_id"], a, rec["run"]))
            if s is None:
                print(f"  ! {path}: unknown slot {rec['query_id']} run {rec['run']} — skipped")
                continue
            s.update(date=rec["date"], answer=rec["answer"],
                     sources_cited=rec["sources_cited"], wording_used=BY_ID[rec["query_id"]][2],
                     capture_status="CAPTURED-FULL")
            s["cited_openappindex"] = any("openappindex" in u.lower()
                                          for u in rec["sources_cited"])
            n += 1
    save(doc)
    print(f"ingested {n} run(s) into {CANON}\n")
    cmd_status(doc)


def cmd_record(assistant, qid):
    """Fill one block in a sheet from stdin: 'SOURCES: ...', a '---' line, then the answer.

    Capturing by hand through the sheet is the documented path; this is the same
    write, for when the answer is already in hand and retyping it would only add a
    chance to mistype it.
    """
    raw = sys.stdin.read()
    head, _, ans = raw.partition("\n---\n")
    srcs = re.sub(r"^SOURCES:\s*", "", head.strip(), flags=re.I)
    ans = ans.strip()
    if not ans:
        sys.exit("no answer text after the --- line")
    path = f"{DATA}/capture-{assistant}.md"
    s = open(path, encoding="utf-8").read()
    for run in (1, 2):
        old = f"DATE:\nSOURCES:\nANSWER:\n\nEND-{qid}-RUN{run}"
        if old in s:
            new = (f"DATE: {datetime.date.today().isoformat()}\nSOURCES: {srcs}\n"
                   f"ANSWER:\n{ans}\n\nEND-{qid}-RUN{run}")
            open(path, "w", encoding="utf-8").write(s.replace(old, new, 1))
            print(f"recorded {qid} run {run} -> {path}")
            return
    sys.exit(f"no empty {qid} block in {path} (already filled, or not in this sheet)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "build":
        save(build()); print(f"rebuilt {CANON}"); cmd_status()
    elif cmd == "status":
        cmd_status()
    elif cmd == "sheet":
        cmd_sheet(force="--force" in sys.argv)
    elif cmd == "ingest":
        cmd_ingest()
    elif cmd == "record":
        cmd_record(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
