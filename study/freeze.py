#!/usr/bin/env python3
"""
"The cost of being found" — the freeze (protocol §6.4): one public commit, tagged
study-freeze-2026-10-22, that publishes the protocol, the instrument and the study pages.

    python3 study/freeze.py --check  --pretest "TEXT"   # dry run: writes nothing outside study/frame/,
                                                        # prints what the commit would contain
    python3 study/freeze.py --commit --pretest "TEXT"   # writes, stages, commits and tags — no push

--pretest fills the protocol's pretest line (§6.3), e.g. "20–21 October 2026, n = 4; changed: …".

Push and deploy are separate, deliberate steps after --commit:
    git push origin main && git push origin study-freeze-2026-10-22
    worker/night_deploy.sh          # rebuild (now with /study/) and deploy, with automatic rollback

Why a script: the working folder is shared with other sessions that commit and push main, so
nothing can be committed early; and docs/developer-study-protocol.md switches the study pages
on in every build, so it may only appear in the freeze commit itself.
"""
import hashlib, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TAG = "study-freeze-2026-10-22"
FORM = "obr9AP"
DRAFT = os.path.join(ROOT, "developer-study-protocol-draft.md")
PROTOCOL = os.path.join(ROOT, "docs", "developer-study-protocol.md")
PREVIEW = os.path.join(ROOT, "study", "frame", "freeze-preview")      # private, never published
PUBLISH = ["docs/developer-study-protocol.md", "study/index.md", "study/privacy.md",
           "study/questionnaire.md", "study/instrument-canonical.json", "study/survey.py",
           "study/send.py", "study/contacts.py", "study/freeze.py", "sample/build_site.py", ".gitignore",
           ".zenodo.json", "publish/release-notes-study-freeze-2026-10-22.md"]
NOTES = "publish/release-notes-study-freeze-2026-10-22.md"
RELEASE_TITLE = "Developer study pre-registration: The cost of being found (2026-10-22)"
NEVER = ("study/frame/", "study/records/", "developer-study-protocol-draft.md",
         "developer-study-survey-draft.md", "study/tally_blocks.json")
ALLOWED_ADDRESSES = {"tim@study.openappindex.org", "hallo@openappindex.org", "korrektur@openappindex.org",
                     "noreply@anthropic.com"}      # the commit's co-author line
SECRETS = ("tally_api_key", "mailbox_app_password", "study_hmac_key", "cloudflare_dns_token")
GITIGNORE_OLD = "# Developer study instrument -- public only at the freeze (2026-12-01)\nstudy/\n"
GITIGNORE_NEW = ("# Developer study: public since the freeze (2026-10-22, tag study-freeze-2026-10-22).\n"
                 "# The Tally dump gets new random IDs on every build; the canonical form is committed instead.\n"
                 "study/tally_blocks.json\n")

def sh(*cmd, check=True):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"failed: {' '.join(cmd)}\n{r.stderr}")
    return r.stdout.strip()

def stop(msg):
    sys.exit(f"STOP: {msg}")

def zenodo_json():
    """The archive's metadata, extended so that the study-freeze versions explain themselves.
    Both additions stay true for every later version of the record."""
    z = json.load(open(os.path.join(ROOT, ".zenodo.json"), encoding="utf-8"))
    z["notes"] = ("Versions tagged study-freeze-* archive pre-registrations. study-freeze-2026-10-22 froze the "
                  "developer study \"The cost of being found\": its protocol (docs/developer-study-protocol.md), "
                  "questionnaire (study/survey.py, study/questionnaire.md) and study pages, before the first answer.")
    rel = {"identifier": "https://openappindex.org/study/protocol.html", "relation": "isDocumentedBy"}
    if rel not in z.setdefault("related_identifiers", []):
        z["related_identifiers"].append(rel)
    for k in ("pre-registration", "survey"):
        if k not in z.setdefault("keywords", []):
            z["keywords"].append(k)
    return json.dumps(z, ensure_ascii=False, indent=2) + "\n"

def release_notes(survey_sha, canon_sha, pretest):
    return f"""Pre-registration of the developer study **"The cost of being found"**: how new and small apps get found, and what it costs their publishers. This release archives the study's protocol, questionnaire and study pages as they stood before the first answer. Zenodo mints a DOI for it.

**What is frozen**
- **Protocol:** `docs/developer-study-protocol.md`, with the research questions, six predictions and the rule for when each counts as holding, the sample, and the analysis and reporting rules. Online: https://openappindex.org/study/protocol.html
- **Questionnaire:** `study/survey.py` builds the survey form; `study/questionnaire.md` is the readable version (https://openappindex.org/study/questionnaire.html).
  - SHA-256 of `study/survey.py`: `{survey_sha}`
  - SHA-256 of the canonical form: `{canon_sha}`. It was confirmed identical to the live form before this release. Anyone can recompute it offline with `python3 study/survey.py --canonical`.
- **Study page and privacy notice:** https://openappindex.org/study/
- **Pretest:** {pretest}

**What is not in it.** The address list and sending records (`study/frame/`) hold personal data. They are never published and are deleted when the survey closes on 31 January 2027.

Any change after this release is a dated amendment, made before the data it affects.

The survey is open from 22 October 2026 to 31 January 2027. Results will be published openly in spring 2027.
"""

def main():
    a = sys.argv[1:]
    commit = "--commit" in a
    if not commit and "--check" not in a:
        sys.exit(__doc__)
    if "--pretest" not in a or a.index("--pretest") + 1 >= len(a):
        stop('--pretest "TEXT" is required (protocol §6.3)')
    pretest = a[a.index("--pretest") + 1].strip()

    # 1. The instrument: regenerate the readable page, and confirm the live form is the code.
    sys.path.insert(0, os.path.join(ROOT, "study"))
    import survey
    built = survey.canonical(survey.blocks())
    key = open(os.path.expanduser("~/.config/tally_api_key")).read().strip()
    import urllib.request
    live = json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.tally.so/forms/{FORM}",
           headers={"Authorization": f"Bearer {key}", "User-Agent": "Mozilla/5.0 (Macintosh) openAPPindex-study"})))
    live_c = survey.canonical(live["blocks"])
    if live_c != built:
        stop("the live Tally form differs from study/survey.py — run `survey.py --update obr9AP` first")
    if live.get("status") != "PUBLISHED":
        stop(f"the live form is {live.get('status')}, not PUBLISHED")
    canon_sha = survey.sha256_of(live_c)
    survey_sha = hashlib.sha256(open(os.path.join(ROOT, "study", "survey.py"), "rb").read()).hexdigest()

    # 2. The protocol with its freeze values filled.
    text = open(DRAFT, encoding="utf-8").read()
    text = (text.replace("⟦FREEZE: dates, n, changes made⟧", pretest)
                .replace("⟦FREEZE: SHA-256 of study/survey.py⟧", f"`{survey_sha}`")
                .replace("⟦FREEZE: SHA-256 of canonical export⟧", f"`{canon_sha}`"))
    left = re.findall(r"⟦FREEZE[^⟧]*⟧", text)
    if left:
        stop(f"unfilled freeze markers: {left}")

    # 3. Everything that will be public: no address but the study's own, no secret, no placeholder.
    gi = open(os.path.join(ROOT, ".gitignore"), encoding="utf-8").read()
    if GITIGNORE_OLD not in gi and GITIGNORE_NEW not in gi:
        stop(".gitignore no longer has the expected study/ block")
    staged = {"docs/developer-study-protocol.md": text,
              "study/questionnaire.md": survey.markdown(),
              "study/instrument-canonical.json": json.dumps(live_c, ensure_ascii=False, indent=1),
              ".gitignore": gi.replace(GITIGNORE_OLD, GITIGNORE_NEW),
              ".zenodo.json": zenodo_json(),
              NOTES: release_notes(survey_sha, canon_sha, pretest)}
    contents = {p: staged.get(p) or open(os.path.join(ROOT, p), encoding="utf-8").read() for p in PUBLISH}
    secrets = [open(os.path.expanduser(f"~/.config/{s}")).read().strip()
               for s in SECRETS if os.path.exists(os.path.expanduser(f"~/.config/{s}"))]
    problems = []
    for p, c in contents.items():
        for addr in set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}", c)):
            if addr.lower() not in ALLOWED_ADDRESSES and not addr.lower().endswith(("@example.org", "@example.com")):
                problems.append(f"{p}: address {addr}")
        if any(s and s in c for s in secrets):
            problems.append(f"{p}: contains a secret from ~/.config")
        for ph in ("SURVEY_LINK", "PROTOCOL_LINK", "INSTRUMENT_LINK", "[LINK TO", "TODO", "(draft)"):
            if ph in c and p not in ("study/freeze.py",):
                problems.append(f"{p}: placeholder {ph!r}")
    if problems:
        stop("not safe to publish:\n  " + "\n  ".join(problems))

    print(f"instrument: live form {FORM} PUBLISHED and identical to study/survey.py")
    print(f"  SHA-256 study/survey.py:   {survey_sha}")
    print(f"  SHA-256 canonical form:    {canon_sha}")
    print(f"pretest line: {pretest}")
    print("files in the freeze commit:")
    for p in PUBLISH:
        print(f"  {p:38} {len(contents[p]):7} bytes{'  (written by the freeze)' if p in staged else ''}")
    print("never published:", ", ".join(NEVER))

    if not commit:
        os.makedirs(PREVIEW, exist_ok=True)
        for p, c in staged.items():
            open(os.path.join(PREVIEW, p.replace("/", "__")), "w", encoding="utf-8").write(c)
        print(f"\nDRY RUN: nothing written outside {os.path.relpath(PREVIEW, ROOT)}/, nothing staged.")
        return

    # 4. The commit: only these files, on main, with nothing else staged, then the tag. No push.
    if sh("git", "branch", "--show-current") != "main":
        stop("not on main")
    if sh("git", "diff", "--cached", "--name-only"):
        stop("something else is already staged; unstage it first")
    if sh("git", "tag", "-l", TAG):
        stop(f"tag {TAG} already exists")
    for p, c in staged.items():
        os.makedirs(os.path.dirname(os.path.join(ROOT, p)) or ROOT, exist_ok=True)
        open(os.path.join(ROOT, p), "w", encoding="utf-8").write(c)
    sh("git", "add", "--", *PUBLISH)
    names = sh("git", "diff", "--cached", "--name-only").splitlines()
    bad = [n for n in names if n.startswith(NEVER) or n not in PUBLISH]
    if bad:
        sh("git", "reset", "-q")
        stop(f"refusing: would publish {bad}")
    msg = ("Developer study frozen: protocol, instrument and study pages\n\n"
           "\"The cost of being found\" is pre-registered by this commit (tag " + TAG + ").\n"
           f"SHA-256 study/survey.py: {survey_sha}\nSHA-256 canonical form:  {canon_sha}\n"
           "The live Tally form was confirmed identical to study/survey.py before committing.\n"
           "The address list and sending records (study/frame/, study/records/) are never published.\n\n"
           "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    sh("git", "commit", "-q", "-m", msg)
    sh("git", "tag", "-a", TAG, "-m", "Developer study \"The cost of being found\": pre-registration freeze")
    print(f"\ncommitted {sh('git', 'rev-parse', '--short', 'HEAD')} and tagged {TAG}. Not pushed.")
    print(f"Next, with Tim's go: git push origin main && git push origin {TAG}; then worker/night_deploy.sh")
    print(f'Then the Zenodo release: gh release create {TAG} -R tim-muky/openappindex '
          f'--title "{RELEASE_TITLE}" --notes-file {NOTES} --verify-tag')

if __name__ == "__main__":
    main()
