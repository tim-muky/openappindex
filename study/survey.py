#!/usr/bin/env python3
"""
"The cost of being found" — the questionnaire as code.

One definition (SURVEY below) is the instrument. This script turns it into Tally
blocks and, with --create, posts it to the Tally API as a new draft form. At the
freeze, this file is committed and its hash recorded in the protocol, so the
published instrument is exactly the one that was fielded.

    python3 study/survey.py --dump            # write study/tally_blocks.json, no network
    python3 study/survey.py --create          # create a DRAFT form in Tally

The API key is read from ~/.config/tally_api_key (created by Tim; never printed).
Question IDs (D2, M4, AI1, ...) are the ones the protocol cites in its predictions (§3) and
instrument list (§6.1).
"""
import json, sys, uuid, os, urllib.request

DK = "Don't know"

# (kind, id, text, options/extra). kinds: page, h3, text, single, multi, long, link, email, hidden
SURVEY = [
    ("hidden", None, None, ["token", "channel", "group"]),
    ("text", None, "A short survey of app publishers, above all new and small ones. About 12 minutes.", None),
    ("text", None, "This survey asks app publishers how people actually find their apps, and what it "
                   "costs to be found. There are no right answers, and \"don't know\" is a useful one: "
                   "how much publishers know about their own install sources is part of what we want to learn.", None),
    ("h3", None, "What happens with your answers", None),
    ("text", None, "• Results are published in aggregate in an open research paper (spring 2027). The aggregated "
                   "results are also released as open data under the Creative Commons Attribution licence "
                   "(CC BY 4.0): anyone may reuse them, as long as they name the source. Individual answers are "
                   "never released.", None),
    ("text", None, "• Your answers are anonymous unless you choose otherwise. The survey does not ask for your "
                   "email address, and a name is asked only if you want to be quoted by name. At the end you "
                   "can allow us to compare your answers with the public data we measured for your app; only "
                   "then do we ask for its App Store link. Quotes from your free-text answer are used only if "
                   "you explicitly allow it.", None),
    ("text", None, "• Raw answers are seen only by the study lead and are deleted 12 months after the paper "
                   "is published. The answers are analysed with the help of an AI service (Claude, by "
                   "Anthropic), which receives them only after the name and App Store link fields have been "
                   "removed. Please don't write personal details into free-text answers. Details are in "
                   "the privacy notice.", None),
    ("text", None, "• Nothing is for sale and nothing is asked of you beyond the answers. Taking part changes "
                   "nothing about how your app appears in openAPPindex.", None),
    ("text", None, "• You can skip any question. \"Don't know\" is always a valid answer.", None),
    ("text", None, "• You can withdraw your consent at any time, with effect for the future (GDPR Art. 7(3)), "
                   "by emailing tim@study.openappindex.org. Because answers are anonymous, we can find yours "
                   "only if you tell us your App Store link or roughly when you answered.", None),
    ("text", None, "Everyone who takes part and leaves an email address at the end receives the paper before "
                   "it is published, and the results for their app category.", None),
    ("h3", None, "Who runs this", None),
    ("text", None, "Tim Meyerdierks, openAPPindex (openappindex.org), Berlin. Before this, ten years as COO of "
                   "a mid-sized marketing company in Berlin, Bonial.com (kaufDA in Germany), spending millions of "
                   "euros on app installs every year. He also publishes small apps himself (e.g. galleybook.com); "
                   "they are excluded from the study. The study protocol was fixed and published before the survey opened: "
                   "https://openappindex.org/study/protocol.html", None),
    ("text", None, "Privacy notice: https://openappindex.org/study/privacy.html", None),
    ("consent", "C1", "Consent", ["I have read this and agree to take part."]),

    ("page", None, None, None),
    ("h3", None, "Screening", None),
    ("single", "S1", "Have you published (or helped publish) at least one app on Apple's App Store?", ["Yes", "No"]),
    ("text_hidden", "S1_end", "Thank you — this survey is only for people who have published an app on the App Store. "
                              "You can close this page.", None),
    ("single", "S2", "Which best describes you? Please answer the rest of the survey about one app, ideally your most recent one. "
                     "If you were invited by email, please answer about the app named in the email.",
        ["Solo developer", "Small team (2–10)", "Company or studio (11+)", "Agency publishing for clients", "Other"]),

    ("page", None, None, None),
    ("h3", None, "Your app", None),
    ("single", "A1", "In which year was this app first released?", ["2026", "2025", "2024", "2023", "2022 or earlier", DK]),
    ("single", "A2", "What category is it in on the App Store?",
        ["Food & Drink", "Health & Fitness", "Lifestyle", "Productivity", "Education", "Games", "Other"]),
    ("multi", "A3", "How does it earn money? (choose all that apply)",
        ["Paid download", "Subscription", "One-time in-app purchase", "Ads", "Free, no revenue", "Other"]),
    ("multi", "A4", "On which platforms is it available? (choose all that apply)",
        ["iOS", "Android (Google Play)", "Android (other stores, e.g. F-Droid)", "Web", "Other"]),
    ("single", "A5", "How many apps have you published in total, including this one?", ["1", "2–3", "4–10", "More than 10"]),
    ("single", "A6", "Is the app still available on the App Store?",
        ["Yes", "No, I removed it", "No, Apple removed it", "Not sure"]),
    ("text", None, "If the app is no longer available, you are just as welcome: please answer about it as it was.", None),

    ("page", None, None, None),
    ("h3", None, "Being found", None),
    ("multi", "D1", "How did your app get its first 100 users? (choose all that apply)",
        ["App Store search", "Featured or browsed in the App Store", "Paid ads", "Social media (organic)",
         "My own website, blog or newsletter", "Friends, family, colleagues", "A community or forum",
         "Press or reviews", "It never reached 100 users", DK, "Other"]),
    ("single", "D2", "Roughly what share of your app's first-time downloads comes from App Store search? "
                     "If you can, look it up: in App Store Connect Analytics, the Source Type breakdown shows "
                     "\"App Store Search\". Use the last 90 days.",
        ["0–9%", "10–24%", "25–49%", "50–74%", "75–100%", DK]),
    ("single", "D2a", "Where does that figure come from?",
        ["App Store Connect analytics", "Another analytics tool", "My own estimate"]),
    ("single", "D2b", "Of your App Store search downloads, roughly how many come from people searching for your "
                      "app's name rather than for a general term (like \"recipe app\")?",
        ["Almost all", "More than half", "About half", "Less than half", "Almost none", DK]),
    ("multi", "D3", "And where do the rest noticeably come from? (choose all that apply; \"App Store Browse\", "
                    "\"App Referrer\" and \"Web Referrer\" are App Store Connect source types)",
        ["App Store Browse (featuring, charts, categories)", "Apple Ads", "App Referrer (links in other apps, incl. social apps)",
         "Web Referrer (links on websites)", "Paid ads outside Apple (Meta, TikTok, Google…)", "Word of mouth", DK]),
    ("single", "D4", "Do you know which App Store search terms your app currently appears for?",
        ["Yes, I check regularly", "Roughly", "No", "Not sure what that means"]),
    ("single", "D5", "How many hours per month do you spend on App Store optimisation (title, subtitle, keywords, screenshots)?",
        ["None", "Under 2", "2–10", "More than 10", DK]),
    ("single", "D6", "Have you ever searched the App Store for the obvious words for your app and not found it?",
        ["Yes, and it still isn't there", "Yes, but it is now", "No, it shows up", "Never checked"]),

    ("page", None, None, None),
    ("h3", None, "Paying to be found", None),
    ("multi", "M1", "Have you paid for ads to get installs? (choose all that apply)",
        ["No, never", "Apple Ads (App Store search ads)", "Meta (Instagram, Facebook)", "TikTok", "Google",
         "Influencers or creators", "Other"]),
    ("single", "M2", "In a typical month with ads running, how much did you spend? (or the equivalent in your currency)",
        ["Under €100", "€100–499", "€500–1,999", "€2,000–9,999", "€10,000–49,999", "€50,000 or more", "Prefer not to say"]),
    ("single", "M3", "Since you started, has the cost of getting one new user through ads…",
        ["Risen a lot", "Risen somewhat", "Stayed about the same", "Fallen", DK]),
    ("single", "M4", "Did paid ads pay for themselves (did the users they brought in earn back what they cost)?",
        ["Yes", "Roughly", "No, they cost more than they earned", "Too early to say", DK]),
    ("long", "M5", "Have you stopped paid ads, and if so, why? (optional)", None),

    ("page", None, None, None),
    ("h3", None, "Where the app stands", None),
    ("single", "O1", "How many total installs (downloads) has the app had, roughly?",
        ["Under 100", "100–999", "1,000–9,999", "10,000–99,999", "100,000–999,999", "1–10 million", "More than 10 million", DK]),
    ("single", "O2", "How many people use it in a typical month?",
        ["Under 50", "50–499", "500–4,999", "5,000–9,999", "10,000–49,999", "50,000–99,999",
         "100,000–249,999", "250,000–499,999", "500,000 or more", DK]),
    ("single", "O3", "Does the app cover its own costs (including your time, if you count it)?",
        ["Yes, it makes a profit", "It covers its costs", "No", "It isn't meant to earn money", "Prefer not to say"]),
    ("single", "O4", "In the last 24 months, have you introduced or raised paid tiers (subscriptions, in-app purchases)?",
        ["Introduced", "Raised prices", "Both", "Neither", DK]),
    ("long", "O4a", "If you introduced or raised them: what was the main reason? (optional)", None),

    ("page", None, None, None),
    ("h3", None, "AI assistants", None),
    ("single", "AI1", "Have you seen any installs or visitors that you can trace to AI assistants (ChatGPT, Perplexity, "
                      "Claude, Gemini, etc.)? In App Store Connect Analytics, they can appear as web referrers such as "
                      "chatgpt.com or perplexity.ai.",
        ["Yes, noticeably", "A few", "None", "I couldn't tell"]),
    ("single", "AI2", "Do you expect AI assistants to matter for how people find apps in the next two years?",
        ["A lot", "Somewhat", "Not really", DK]),

    ("page", None, None, None),
    ("h3", None, "Your statement (optional)", None),
    ("long", "F1", "Is there anything you'd like to tell us about getting your app found: your experience, your "
                   "background, what you would change? (up to ~300 words)", None),
    ("single", "F2", "May we quote from your answer above?",
        ["No", "Yes, anonymously", "Yes, with my name or studio name"]),
    ("short", "F2a", "If you'd like to be named: name or studio name", None),

    ("page", None, None, None),
    ("h3", None, "Linking to measured data (optional)", None),
    ("single", "L2", "May we compare your answers with the public data openAPPindex measured for your app (for example, "
                     "whether it appeared for the obvious search)? Your app will not be named in any result.",
        ["Yes", "No"]),
    ("link", "L1", "Thank you. Please paste your app's App Store link, so we can find it in our data. It starts with "
                     "https://apps.apple.com/", None),
    ("h3", None, "Results", None),
    ("text", None, "Would you like the paper before it is published, and the results for your app category? "
                   "Leave your email address in a separate short form — it is not connected to your answers in "
                   "any way: https://tally.so/r/Mekb9Y", None),
]

def U(): return str(uuid.uuid4())

def esc(t): return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

HIDDEN_BY_DEFAULT = {"F2a", "O4a", "L1"}

# (trigger question, operator, option texts, action, target ids)
LOGIC = [
    ("S1", "IS", ["No"], "SHOW_STOP", ["S1_end"]),
    ("D2", "IS", [DK], "HIDE_BLOCKS", ["D2a", "D2b"]),
    ("M1", "CONTAINS", ["No, never"], "HIDE_BLOCKS", ["M2", "M3", "M4", "M5"]),
    ("O4", "IS", ["Introduced", "Raised prices", "Both"], "SHOW_BLOCKS", ["O4a"]),
    ("F2", "IS", ["Yes, with my name or studio name"], "SHOW_BLOCKS", ["F2a"]),
    ("L2", "IS", ["Yes"], "SHOW_BLOCKS", ["L1"]),
]

def blocks():
    out = []
    reg = {}      # qid -> {"group": options group uuid, "opts": {text: uuid}, "blocks": [uuids], "gtype": ...}
    def add(type_, payload, group=None, gtype=None):
        u = U()
        out.append({"uuid": u, "type": type_, "groupUuid": group or u, "groupType": gtype or type_, "payload": payload})
        return u
    ids = {x[1] for x in SURVEY}
    pending = [r for r in LOGIC if r[0] in ids]
    def emit_logic(done_qid):
        # place each rule as soon as its trigger and all its targets exist
        for rule in list(pending):
            trig, op, vals, action, targets = rule
            if trig not in reg or any(t not in reg for t in targets):
                continue
            r = reg[trig]
            conds = [{"uuid": U(), "type": "SINGLE", "payload": {
                        "field": {"uuid": r["group"], "type": "INPUT_FIELD", "questionType": r["gtype"],
                                  "blockGroupUuid": r["group"], "title": trig},
                        "comparison": op, "value": r["opts"][v]}} for v in vals]
            tb = [b for t in targets for b in reg[t]["blocks"]]
            if action == "SHOW_STOP":
                acts = [{"uuid": U(), "type": "SHOW_BLOCKS", "payload": {"showBlocks": tb}},
                        {"uuid": U(), "type": "HIDE_BUTTON_TO_DISABLE_COMPLETION"}]
            else:
                key = "showBlocks" if action == "SHOW_BLOCKS" else "hideBlocks"
                acts = [{"uuid": U(), "type": action, "payload": {key: tb}}]
            add("CONDITIONAL_LOGIC", {"updateUuid": None, "logicalOperator": "OR" if len(conds) > 1 else "AND",
                                      "conditionals": conds, "actions": acts})
            pending.remove(rule)
    page_idx = 0
    add("FORM_TITLE", {"title": "The cost of being found", "safeHTMLSchema": [["The cost of being found"]]}, gtype="TEXT")
    for kind, qid, text, extra in SURVEY:
        if kind == "hidden":
            add("HIDDEN_FIELDS", {"hiddenFields": [{"uuid": U(), "name": n} for n in extra]})
        elif kind == "text":
            add("TEXT", {"safeHTMLSchema": [[text]]})
        elif kind == "text_hidden":
            u = add("TEXT", {"safeHTMLSchema": [[text]], "isHidden": True})
            reg[qid] = {"blocks": [u]}
        elif kind == "h3":
            add("HEADING_3", {"safeHTMLSchema": [[text]]})
        elif kind == "page":
            page_idx += 1
            add("PAGE_BREAK", {"index": page_idx, "isFirst": False, "isLast": False})
        elif kind in ("single", "multi", "consent"):
            q = U(); tu = U()
            out.append({"uuid": tu, "type": "TITLE", "groupUuid": q, "groupType": "QUESTION",
                        "payload": {"safeHTMLSchema": [[text]], "isHidden": qid in HIDDEN_BY_DEFAULT}})
            otype, gtype = (("MULTIPLE_CHOICE_OPTION", "MULTIPLE_CHOICE") if kind == "single"
                            else ("CHECKBOX", "CHECKBOXES"))
            og = U()
            has_other = "Other" in extra
            for i, opt in enumerate(extra):
                p = {"index": i, "isFirst": i == 0, "isLast": i == len(extra) - 1, "text": opt,
                     "isRequired": kind == "consent", "hasOtherOption": has_other,
                     "isOtherOption": opt == "Other"}
                if qid: p["name"] = qid
                if qid in HIDDEN_BY_DEFAULT: p["isHidden"] = True
                ou = U()
                out.append({"uuid": ou, "type": otype, "groupUuid": og, "groupType": gtype, "payload": p})
                r = reg.setdefault(qid, {"group": og, "gtype": gtype, "opts": {}, "blocks": [tu]})
                r["opts"][opt] = ou; r["blocks"].append(ou)
            emit_logic(qid)
        elif kind in ("long", "short", "link", "email"):
            q = U(); tu = U(); hid = qid in HIDDEN_BY_DEFAULT
            out.append({"uuid": tu, "type": "TITLE", "groupUuid": q, "groupType": "QUESTION",
                        "payload": {"safeHTMLSchema": [[text]], "isHidden": hid}})
            t = {"long": "TEXTAREA", "short": "INPUT_TEXT", "link": "INPUT_LINK", "email": "INPUT_EMAIL"}[kind]
            iu = add(t, {"isRequired": False, "name": qid, "isHidden": hid})
            reg[qid] = {"blocks": [tu, iu]}
            emit_logic(qid)
    assert not pending, f"unplaced logic rules: {pending}"
    return out

# A separate form for the results email, so the address is never stored with any answer.
RESULTS_FORM = [
    ("text", None, "Leave your email address to receive the paper \"The cost of being found\" before it is "
                   "published (spring 2027), and the aggregated results for your app category.", None),
    ("text", None, "This form is separate from the survey: your address is not connected to your answers. It is "
                   "used only to send you the paper and the results, and deleted afterwards (by 31 January 2028 "
                   "at the latest). Privacy notice: https://openappindex.org/study/privacy.html", None),
    ("email", "R1", "Email address", None),
    ("single", "R2", "Which app category is your app in?", ["Food & Drink / cooking", "Sleep, meditation, wellbeing", "Other"]),
]

SETTINGS = {"language": "en", "hasProgressBar": True, "hasPartialSubmissions": False, "saveForLater": False,
            # Closes with the field period (protocol §10); answers are deleted by Tally after 14 months
            # at the latest, a backstop inside "12 months after the paper" (privacy notice 3.2).
            "closeDate": "2027-01-31", "closeTime": "23:59", "closeTimezone": "Europe/Berlin",
            "closeMessageTitle": "This survey has closed",
            "closeMessageDescription": "Thank you for your interest. The results will be published in spring 2027: "
                                       "https://openappindex.org/study/",
            "submissionsDataRetentionDuration": 14, "submissionsDataRetentionUnit": "MONTHS",
            "metaTitle": "The cost of being found: a survey of app publishers",
            "metaDescription": "How do new apps get found, and what does it cost? About 12 minutes. "
                               "By openAPPindex; results published openly."}
# The results form keeps addresses only until the paper is sent: 12 months after the last
# possible entry is 31 January 2028 (privacy notice 3.3).
RESULTS_SETTINGS = {**SETTINGS, "submissionsDataRetentionDuration": 12,
                    "metaTitle": "The cost of being found: get the results",
                    "metaDescription": "Receive the paper before publication. Not connected to your survey answers."}

UUID_RE = __import__("re").compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

def canonical(blocks_):
    """The form without its random identifiers: every block in order, its type and its content,
    with UUID keys dropped and UUID values blanked. The same for a fresh build of SURVEY and for
    the live form, so its SHA-256 pins the fielded instrument (protocol §6.4)."""
    def clean(x):
        if isinstance(x, dict):
            return {k: clean(v) for k, v in sorted(x.items()) if "uuid" not in k.lower()}
        if isinstance(x, list):
            return [clean(v) for v in x]
        return "<id>" if isinstance(x, str) and UUID_RE.match(x) else x
    return [{"type": b["type"], "payload": clean(b.get("payload", {}))} for b in blocks_]

def sha256_of(obj):
    import hashlib
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()

def markdown():
    """The questionnaire as a readable page (/study/questionnaire.html), generated from SURVEY
    and LOGIC, so the published page and the fielded form cannot drift apart."""
    kinds = {"single": "one answer", "multi": "any number of answers", "long": "free text",
             "short": "short text", "link": "a link", "email": "an email address", "consent": "required box"}
    rule = {}
    for trig, op, vals, action, targets in LOGIC:
        said = " or ".join(f'"{v}"' for v in vals)
        for t in targets:
            rule[t] = (f"shown only if {trig} is {said}" if action == "SHOW_BLOCKS" else
                       f"skipped if {trig} {'includes' if op == 'CONTAINS' else 'is'} {said}" if action == "HIDE_BLOCKS" else
                       f"shown instead of the rest of the survey if {trig} is {said}")
    out = ["# The questionnaire as fielded", "",
           "### The cost of being found: every question, answer option and skip rule", "",
           "This page is generated from study/survey.py, the same definition that built the survey form, "
           "so it shows exactly what respondents see. Question IDs (S1, D2, M4…) are the ones the "
           "[study protocol](https://openappindex.org/study/protocol.html) refers to. "
           "Survey: [tally.so/r/obr9AP](https://tally.so/r/obr9AP?channel=study-page).", ""]
    page = 1
    out += [f"## Page {page}", ""]
    for kind, qid, text, extra in SURVEY:
        if kind == "hidden":
            out += [f"*Carried by the invitation link, not shown: {', '.join(extra)}.*", ""]
        elif kind == "page":
            page += 1
            out += [f"## Page {page}", ""]
        elif kind == "h3":
            out += [f"**{text}**", ""]
        elif kind == "text":
            out += [text, ""]
        elif kind == "text_hidden":
            out += [f"*{text}* ({rule.get(qid, 'conditional')})", ""]
        else:
            note = "; ".join([kinds.get(kind, kind)] + ([rule[qid]] if qid in rule else []))
            out += [f"**{qid}.** {text} *({note})*", ""]
            if extra:
                out += [f"- {o}" for o in extra] + [""]
    return "\n".join(out)

if __name__ == "__main__":
    b = blocks()
    here = os.path.dirname(os.path.abspath(__file__))
    if "--dump" in sys.argv or len(sys.argv) == 1:
        json.dump({"status": "DRAFT", "blocks": b, "settings": SETTINGS},
                  open(os.path.join(here, "tally_blocks.json"), "w"), ensure_ascii=False, indent=1)
        qs = [x for x in SURVEY if x[1]]
        print(f"{len(b)} blocks · {len(qs)} questions · {sum(1 for x in SURVEY if x[0]=='page')} page breaks")
    if "--canonical" in sys.argv:              # offline: anyone can check the hash in protocol §6.4
        print(sha256_of(canonical(b)))
    if "--fingerprint" in sys.argv:
        fid = sys.argv[sys.argv.index("--fingerprint") + 1]
        key = open(os.path.expanduser("~/.config/tally_api_key")).read().strip()
        live = json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.tally.so/forms/{fid}",
               headers={"Authorization": f"Bearer {key}", "User-Agent": "Mozilla/5.0 (Macintosh) openAPPindex-study"})))
        here_c, live_c = canonical(b), canonical(live["blocks"])
        print("built from survey.py:", sha256_of(here_c))
        print(f"live form {fid}:       ", sha256_of(live_c), "| status", live.get("status"))
        print("identical:", here_c == live_c)
        if "--write" in sys.argv:
            json.dump(live_c, open(os.path.join(here, "instrument-canonical.json"), "w"), ensure_ascii=False, indent=1)
            print("wrote study/instrument-canonical.json")
    if "--markdown" in sys.argv:
        open(os.path.join(here, "questionnaire.md"), "w", encoding="utf-8").write(markdown())
        print("wrote study/questionnaire.md")
    if "--update" in sys.argv:
        fid = sys.argv[sys.argv.index("--update") + 1]
        key = open(os.path.expanduser("~/.config/tally_api_key")).read().strip()
        req = urllib.request.Request(f"https://api.tally.so/forms/{fid}", method="PATCH",
              data=json.dumps({"blocks": b, "settings": SETTINGS}).encode(),
              headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                       "User-Agent": "openappindex-survey/0.2 (+https://openappindex.org)"})
        try:
            r = json.load(urllib.request.urlopen(req)); print("updated form:", r.get("id"), r.get("status"))
        except urllib.error.HTTPError as e:
            print("HTTP", e.code, e.read().decode()[:1500])
    if "--update-results" in sys.argv:
        fid = sys.argv[sys.argv.index("--update-results") + 1]
        key = open(os.path.expanduser("~/.config/tally_api_key")).read().strip()
        SURVEY = RESULTS_FORM
        rb = blocks()
        for x in rb:
            if x["type"] == "FORM_TITLE":
                x["payload"] = {"title": "The cost of being found — get the results",
                                "safeHTMLSchema": [["The cost of being found — get the results"]]}
        req = urllib.request.Request(f"https://api.tally.so/forms/{fid}", method="PATCH",
              data=json.dumps({"blocks": rb, "settings": RESULTS_SETTINGS}).encode(),
              headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                       "User-Agent": "Mozilla/5.0 (Macintosh) openAPPindex-study"})
        r = json.load(urllib.request.urlopen(req)); print("updated results form:", r.get("id"), r.get("status"))
    if "--create-results" in sys.argv:
        SURVEY = RESULTS_FORM
        rb = blocks()
        for x in rb:
            if x["type"] == "FORM_TITLE":
                x["payload"] = {"title": "The cost of being found — get the results",
                                "safeHTMLSchema": [["The cost of being found — get the results"]]}
        key = open(os.path.expanduser("~/.config/tally_api_key")).read().strip()
        req = urllib.request.Request("https://api.tally.so/forms", method="POST",
              data=json.dumps({"status": "DRAFT", "blocks": rb, "settings": SETTINGS}).encode(),
              headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                       "User-Agent": "openappindex-survey/0.2 (+https://openappindex.org)"})
        r = json.load(urllib.request.urlopen(req)); print("results form:", r.get("id"), r.get("status"))
    if "--create" in sys.argv:
        key = open(os.path.expanduser("~/.config/tally_api_key")).read().strip()
        req = urllib.request.Request("https://api.tally.so/forms", method="POST",
              data=json.dumps({"status": "DRAFT", "blocks": b, "settings": SETTINGS}).encode(),
              headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "openappindex-survey/0.2 (+https://openappindex.org)"})
        try:
            r = json.load(urllib.request.urlopen(req))
            print("created form:", r.get("id"), r.get("status"))
        except urllib.error.HTTPError as e:
            print("HTTP", e.code, e.read().decode()[:1500])
