#!/usr/bin/env python3
"""
"The cost of being found" — sending the invitations (protocol §5).

    python3 study/send.py --plan              # who would get which email; counts only, nothing sent
    python3 study/send.py --check             # does each address's domain accept mail? (DNS only, nothing sent)
    python3 study/send.py --preview 5         # write 5 rendered emails to study/frame/preview/, nothing sent
    python3 study/send.py --test ADDRESS      # send ONE rendered sample to ADDRESS (Tim's own), no token logged
    python3 study/send.py --bounces           # read delivery-failure reports (IMAP, read-only); never retry those
    python3 study/send.py --optout ADDRESS    # a "no" reply: never write again, delete the address now
    python3 study/send.py --inbox             # read replies (IMAP, read-only): apply clear "no"s, count the rest
    python3 study/send.py --erase             # 31 January 2027: move the address list and sending records to the Trash
    python3 study/send.py --send [--resume]   # today's invitations (20 → 40 → 60 → 80 → 100 per sending day),
                                              # each address re-checked on its page first, plus the
                                              # reminders due (14 days after each batch)

Spam thresholds (decided with Tim, 2026-10-20: "we don't want to burn the address"):
- invitations ramp 20 → 40 → 60 → 80 → 100 a day, and ALL emails of a day (invitations and reminders)
  stay under a total that rises slowly: 100 in weeks 1–2, then 130, 160, 200. Reminders go first,
  so each comes 14 days after its invitation; invitations fill what is left;
- seed copies to Tim's own mailboxes (~/.config/study_seeds) go out inside every day's run, so a
  move to the spam folder is seen the same day (mailbox.org reports no spam complaints);
- the day stops at the first rejection that reads like a block (spam, policy, reputation, rate
  limit) and at any server error; --send refuses when more than 5% of the previous batch bounced
  (hard bounces read from the mailbox first). Weekends: SEND_WEEKENDS (on since 2026-10-22).

What is stored, and what is not (privacy notice §3.1–3.2):
- tokens.json: token → group, nothing else. The order is shuffled per batch and there are no times,
  so a token cannot be matched to an address by position or timestamp.
- sent.json: keyed HMAC of each address that was written to, so nobody is written twice. It does
  not record which token went to which address.
- optout.json: keyed HMAC of addresses that replied "no", kept after the list is deleted so they are
  never contacted again. The HMAC key lives outside the repo (~/.config/study_hmac_key); without
  it the fingerprints cannot be checked against any list of addresses.
- bounced.json: keyed HMAC of addresses whose mail server rejected the invitation, so they are not
  tried again. domains.json: whether each recipient domain accepts mail (domain names only).

SMTP: mailbox.org, From tim@study.openappindex.org. The login is read from ~/.config/mailbox_user
and the password from ~/.config/mailbox_app_password (an app password Tim creates; never printed).
"""
import json, os, re, sys, hmac, hashlib, random, secrets, smtplib, ssl, time, urllib.parse, urllib.request, email.utils
from email.message import EmailMessage
from email.utils import formataddr, make_msgid, formatdate
from datetime import date

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FR = os.path.join(ROOT, "study", "frame")
FRAME, EMAILS = os.path.join(FR, "frame.json"), os.path.join(FR, "emails.json")
TOKENS, SENT, OPTOUT, STATE = (os.path.join(FR, f) for f in ("tokens.json", "sent.json", "optout.json", "send_state.json"))
BOUNCED, DOMAINS, STALE = (os.path.join(FR, f) for f in ("bounced.json", "domains.json", "stale.json"))
PREVIEW = os.path.join(FR, "preview")
NO_ROUTE = ("none", "nxdomain", "null-mx")   # domain results that mean "cannot receive mail"
MAX_BOUNCE = 0.05                            # stop the ramp above this hard-bounce rate
REMIND_AFTER = 14                            # days from invitation to the one reminder
SEND_WEEKENDS = True                         # Tim, 2026-10-22: send on Saturdays and Sundays too
DAILY_TOTAL = [100, 100, 130, 160, 200]      # all emails per day, by week since the first batch
REMINDED = os.path.join(FR, "reminded.json")
BLOCK_WORDS = re.compile(r"spam|block|blacklist|blocklist|reputation|policy|denied|abuse|rate.?limit|too many", re.I)
ADDR_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")

SURVEY = "https://tally.so/r/obr9AP"
STUDY_PAGE = "https://openappindex.org/study/"
PRIVACY = "https://openappindex.org/study/privacy.html"
FROM_NAME, FROM_ADDR = "Tim Meyerdierks (openAPPindex)", "tim@study.openappindex.org"
SMTP_HOST, SMTP_PORT = "smtp.mailbox.org", 465
SMTP_USER_FILE = "mailbox_user"              # the mailbox login, kept out of the public repo
IMAP_HOST = "imap.mailbox.org"
RAMP = [20, 40, 60, 80, 100]                 # per sending day; stays at 100 afterwards
GAP = (25, 70)                               # seconds between two emails
CATEGORY = {"cooking": "941 cooking", "sleep": "3,578 sleep and meditation"}
PAGE_WORDS = {"support": "your app's support page", "privacy": "your app's privacy page",
              "website": "your website", "contact": "your website's contact page"}

SUBJECT = "Research survey for app publishers: how do new apps get found?"
BODY = """Hello,

I'm Tim. I run openAPPindex (openappindex.org), an independent, open index that measures whole App Store categories from public data. Your app {app} is one of the {category} apps we measured in the German App Store.

I'm running a short survey of app publishers, above all new and small ones: how do your users actually find your app, and what does it cost you to be found? It takes about 12 minutes, it doesn't ask who you are, and the results will be published as an open research paper.

Survey: {link}

To be clear about what this is not: nothing is for sale, and nothing is asked of you beyond the answers. Taking part (or not) changes nothing about how your app appears in the index. Everyone who takes part can receive the paper before it is published, plus the results for their category.

Before openAPPindex I was COO of a mid-sized marketing company in Berlin, Bonial.com (kaufDA in Germany), for ten years, and spent millions of euros on app installs every year. I also publish small apps myself (e.g. galleybook.com); they are excluded from this study.

I won't spam you: I'll send one short reminder in about two weeks, and nothing after that. If you'd rather not hear from me again, reply "no" and I'll delete your address.

Thank you,
Tim

Tim Meyerdierks
openappindex.org · {study_page}

{footer}
"""

REMINDER_SUBJECT = "Reminder: research survey for app publishers (open until 31 January)"
REMINDER_BODY = """Hello,

About two weeks ago I invited you to a short survey of app publishers: how do your users actually find your app, and what does it cost you to be found? Your app {app} is one of the {category} apps we measured in the German App Store.

If you have already taken part: thank you, and please ignore this email. The survey doesn't ask who you are, so I can't tell who has answered.

If you haven't yet, it takes about 12 minutes and is open until 31 January 2027:
{link}

Nothing is for sale, and nothing is asked of you beyond the answers. This is the last email you'll get from me about the study.

Thank you,
Tim

Tim Meyerdierks
openappindex.org · {study_page}

{footer}
"""

FOOTER = """--
Why you're receiving this, and your data: I found this address on {page_words} ({source}), where you publish it as a contact for your app, and checked that it was still there on the day of the invitation. I use it only for the invitation and one reminder, on the basis of a legitimate interest in independent research, published openly (GDPR Art. 6(1)(f)). Only my email provider (mailbox.org) processes it for me. It is deleted when the survey closes (31 January 2027), or straight away if you reply "no". Controller: Tim Meyerdierks, Sonnenburger Straße 54, 10437 Berlin, Germany; {from_addr}. You have the right to access, rectification, erasure, restriction and objection, and to complain to a data protection authority. Full notice: {privacy}"""

def load(p, default):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default

def save(p, obj):
    tmp = p + ".tmp"
    json.dump(obj, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, p)

def secret(name):
    p = os.path.expanduser(f"~/.config/{name}")
    return open(p).read().strip() if os.path.exists(p) else None

def fingerprint(addr, key):
    return hmac.new(key.encode(), addr.strip().lower().encode(), hashlib.sha256).hexdigest()

def hmac_key():
    k = secret("study_hmac_key")
    if not k:
        k = secrets.token_hex(32)
        p = os.path.expanduser("~/.config/study_hmac_key")
        open(p, "w").write(k)
        os.chmod(p, 0o600)
    return k

def domain_of(addr):
    return addr.rpartition("@")[2].lower()

def queue(check_domains=True):
    """One entry per address: the first developer record that published it (frame order is
    stable), minus opt-outs, bounces, addresses already written to, and (after --check)
    addresses whose domain cannot receive mail."""
    frame = load(FRAME, None)["developers"]
    emails = load(EMAILS, {})
    key = hmac_key()
    skip = set(load(SENT, [])) | set(load(OPTOUT, [])) | set(load(BOUNCED, [])) | set(load(STALE, []))
    dead = {d for d, r in load(DOMAINS, {}).items() if r in NO_ROUTE} if check_domains else set()
    seen, q, shared, no_route = set(), [], 0, 0
    for d in frame:
        e = emails.get(d["key"], {})
        addr = (e.get("email") or "").strip().lower()      # one spelling per address, so no one is written twice
        if not addr:
            continue
        if addr in seen:
            shared += 1
            continue
        seen.add(addr)
        if fingerprint(addr, key) in skip:
            continue
        if domain_of(addr) in dead:
            no_route += 1
            continue
        q.append({**d, "email": addr, "source": e["source"], "page": e["page"]})
    queue.no_route = no_route
    return q, shared

def mail_route(dom):
    """Does the domain accept mail: MX, else an address record (RFC 5321 implicit MX)?
    Asked over DNS-over-HTTPS because the VPN's resolver answers NXDOMAIN to every MX query,
    which would wrongly drop every address. None = could not tell (kept, asked again later)."""
    for t, want in (("MX", 15), ("A", 1), ("AAAA", 28)):
        try:
            req = urllib.request.Request(f"https://dns.google/resolve?name={dom}&type={t}",
                                         headers={"User-Agent": "openAPPindex-study/1.0"})
            d = json.load(urllib.request.urlopen(req, timeout=15))
        except Exception:
            return None
        if d.get("Status") == 3:
            return "nxdomain"
        if d.get("Status") != 0:
            return None
        ans = [a["data"] for a in d.get("Answer", []) if a.get("type") == want]
        if want == 15 and ans:
            return "null-mx" if all(a.split()[-1] == "." for a in ans) else "mx"   # RFC 7505
        if ans:
            return t.lower()
    return "none"

def check():
    q, _ = queue(check_domains=False)
    cache = load(DOMAINS, {})
    todo = sorted({domain_of(d["email"]) for d in q} - {k for k, v in cache.items() if v})
    print(f"domains: {len(cache)} known, {len(todo)} to look up")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(8) as ex:
        for dom, r in zip(todo, ex.map(mail_route, todo)):
            cache[dom] = r
    save(DOMAINS, cache)
    from collections import Counter
    by_addr = Counter(cache.get(domain_of(d["email"])) for d in q)
    print("addresses by domain result:", dict(by_addr))
    print(f"dropped as undeliverable: {sum(n for r, n in by_addr.items() if r in NO_ROUTE)}; "
          f"unknown (kept, re-checked next run): {by_addr.get(None, 0)}")

def render(d, token, reminder=False, channel=None):
    params = {"token": token, "channel": channel or ("email-reminder" if reminder else "email"), "group": d["group"]}
    link = SURVEY + "?" + urllib.parse.urlencode(params)
    footer = FOOTER.format(page_words=PAGE_WORDS.get(d["page"], "your website"), source=d["source"],
                           from_addr=FROM_ADDR, privacy=PRIVACY)
    body = (REMINDER_BODY if reminder else BODY).format(app=d["app"], category=CATEGORY[d["cat"]], link=link,
                                                        study_page=STUDY_PAGE, footer=footer)
    m = EmailMessage()
    m["From"] = formataddr((FROM_NAME, FROM_ADDR))
    m["To"] = d["email"]
    m["Subject"] = REMINDER_SUBJECT if reminder else SUBJECT
    m["Date"] = formatdate(localtime=True)
    m["Message-ID"] = make_msgid(domain="study.openappindex.org")
    m["List-Unsubscribe"] = f"<mailto:{FROM_ADDR}?subject=no>"
    m.set_content(body)
    return m

def smtp():
    pw = secret("mailbox_app_password")
    if not pw:
        sys.exit("No app password at ~/.config/mailbox_app_password — Tim creates one in mailbox.org first.")
    s = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl.create_default_context(), timeout=60)
    s.login(secret(SMTP_USER_FILE) or sys.exit("No login at ~/.config/mailbox_user."), pw)
    return s

def plan():
    q, shared = queue()
    from collections import Counter
    print(f"to write: {len(q)} addresses ({shared} developer records share an address already queued; "
          f"{queue.no_route} dropped because their domain cannot receive mail)")
    for g, n in sorted(Counter(d["group"] for d in q).items()):
        print(f"  {g:28} {n}")
    # The schedule as --send will run it: reminders first, invitations fill the day's total.
    from datetime import timedelta
    st = load(STATE, {"days": 0})
    day0 = date.fromisoformat(st["batches"][0]["date"]) if st.get("batches") else date.today()
    d, i, left, batches, queued, due, days, last_inv, last_rem = date.today(), st["days"], len(q), [], set(), [], 0, None, None
    while left > 0 or due or len(queued) < len(batches):
        if SEND_WEEKENDS or d.weekday() < 5:
            for b, n in batches:
                if b not in queued and (d - b).days >= REMIND_AFTER:
                    due.append([b, n]); queued.add(b)
            cap, r = DAILY_TOTAL[min((d - day0).days // 7, len(DAILY_TOTAL) - 1)], 0
            while due and r < cap:
                k = min(due[0][1], cap - r); r += k; due[0][1] -= k; last_rem = d
                if due[0][1] == 0: due.pop(0)
            inv = min(RAMP[min(i, len(RAMP) - 1)], cap - r, left)
            if inv > 0:
                batches.append((d, inv)); left -= inv; i += 1; last_inv = d
            days += 1
        d += timedelta(1)
    print(f"daily total by week {DAILY_TOTAL}, invitations ramp {RAMP}, reminders after {REMIND_AFTER} days")
    print(f"if sending started today: last invitations {last_inv}, last reminders {last_rem}, {days} sending days")

def preview(n):
    q, _ = queue()
    os.makedirs(PREVIEW, exist_ok=True)
    random.seed(1)
    for i, d in enumerate(random.sample(q, min(n, len(q))), 1):
        open(os.path.join(PREVIEW, f"{i:02}.eml"), "w", encoding="utf-8").write(render(d, "PREVIEW").as_string())
    print(f"{min(n, len(q))} previews in {PREVIEW} (token 'PREVIEW', nothing sent, nothing logged)")

def test(addr):
    """One rendered invitation to Tim's own address. Its link carries channel=pretest, so an
    answer given through it is excluded from the results like the pretest's."""
    q, _ = queue()
    d = {**q[0], "email": addr}
    with smtp() as s:
        s.send_message(render(d, "TEST", channel="pretest"))
    print(f"one sample sent to {addr} (token 'TEST', channel 'pretest', not logged)")

def failed_recipients(msg):
    """Hard-failed recipients in a delivery status notification (RFC 3464): Action failed, 5.x.x."""
    out = []
    for part in msg.walk():
        if part.get_content_type() != "message/delivery-status":
            continue
        for block in part.get_payload():
            action, status = (block.get("Action") or "").lower(), block.get("Status") or ""
            rcpt = (block.get("Final-Recipient") or block.get("Original-Recipient") or "").partition(";")[2]
            if rcpt.strip() and action.startswith("failed") and status.startswith("5"):
                out.append(rcpt.strip().strip("<>").lower())
    return out

def bounces(quiet=False):
    """Read delivery-failure reports from the mailbox, read-only (nothing is marked as read or
    moved), and record each hard-failed address as a fingerprint. Returns the hard-bounce rate
    of the last batch, or None if no batch was sent yet."""
    import imaplib, email
    st = load(STATE, {"days": 0})
    if not st.get("batches"):
        return None
    pw = secret("mailbox_app_password")
    if not pw:
        sys.exit("No app password at ~/.config/mailbox_app_password.")
    key = hmac_key()
    since = date.fromisoformat(st["batches"][0]["date"]).strftime("%d-%b-%Y")
    found = set()
    with imaplib.IMAP4_SSL(IMAP_HOST) as m:
        m.login(secret(SMTP_USER_FILE) or sys.exit("No login at ~/.config/mailbox_user."), pw)
        for box in ("INBOX", "Junk"):
            if m.select(box, readonly=True)[0] != "OK":
                continue
            _, ids = m.search(None, "SINCE", since, "OR", "FROM", "mailer-daemon", "FROM", "postmaster")
            for i in ids[0].split():
                _, data = m.fetch(i, "(BODY.PEEK[])")
                found.update(failed_recipients(email.message_from_bytes(data[0][1])))
    sent = load(SENT, [])
    fps = {fingerprint(a, key) for a in found} & set(sent)    # only addresses we actually wrote to
    bounced = sorted(set(load(BOUNCED, [])) | fps)
    save(BOUNCED, bounced)
    last = st["batches"][-1]
    batch = set(sent[last["start"]:last["end"]])
    rate = len(batch & set(bounced)) / len(batch) if batch else 0.0
    if not quiet:
        print(f"hard bounces recorded: {len(bounced)} of {len(sent)} sent; "
              f"last batch ({last['date']}): {len(batch & set(bounced))}/{len(batch)} = {rate:.1%}")
    return rate

def optout(addr):
    """A "no" reply: the address is never written to again, and is deleted from the address
    list now (privacy notice). Only its keyed fingerprint is kept."""
    addr = addr.strip().lower()
    fp = fingerprint(addr, hmac_key())
    oo = load(OPTOUT, [])
    if fp not in oo:
        save(OPTOUT, oo + [fp])
    emails, n = load(EMAILS, {}), 0
    for v in emails.values():
        if (v.get("email") or "").lower() == addr:
            v.update(email=None, removed="opt-out")
            v.pop("source", None)
            n += 1
        if v.get("alternates"):
            v["alternates"] = [a for a in v["alternates"] if a[0].lower() != addr]
    save(EMAILS, emails)
    print(f"opt-out recorded; the address was removed from {n} record(s) of the address list")

def still_published(d):
    """Re-collect the address on the day it is used (GDPR Art. 14(3)): fetch the page it was
    found on and confirm it is still published there. True / False, or None if the page could
    not be reached today (then the address simply waits for another day)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import contacts
    try:
        if not contacts.allowed(d["source"]):
            return False
        _, _, h = contacts.get(d["source"], ua=contacts.UA_STUDY, timeout=15)
    except Exception:
        return None
    return d["email"] in contacts.emails_in(h)

def daily_total(st):
    b = st.get("batches") or []
    week = (date.today() - date.fromisoformat(b[0]["date"])).days // 7 if b else 0
    return DAILY_TOTAL[min(week, len(DAILY_TOTAL) - 1)]

def due_reminders(st, key):
    """Addresses invited at least REMIND_AFTER days ago that have had no reminder yet, oldest
    batch first: everyone invited, minus opt-outs and bounces (answers are anonymous, so nobody
    can be left out for having answered)."""
    today, sent = date.today(), load(SENT, [])
    skip = set(load(OPTOUT, [])) | set(load(BOUNCED, [])) | set(load(REMINDED, []))
    order = {}
    for n_b, b in enumerate(st.get("batches", [])):
        if (today - date.fromisoformat(b["date"])).days >= REMIND_AFTER:
            for fp in sent[b["start"]:b["end"]]:
                if fp not in skip:
                    order.setdefault(fp, n_b)
    recs = [(order[f], d) for d in records() if (f := fingerprint(d["email"], key)) in order]
    return [d for _, d in sorted(recs, key=lambda x: x[0])]

def records():
    """Every address in the list once, with its first developer record (as in queue())."""
    frame, emails, seen, out = load(FRAME, None)["developers"], load(EMAILS, {}), set(), []
    for d in frame:
        e = emails.get(d["key"], {})
        addr = (e.get("email") or "").strip().lower()
        if addr and addr not in seen:
            seen.add(addr)
            out.append({**d, "email": addr, "source": e["source"], "page": e["page"]})
    return out

NO_WORDS = re.compile(r"^\s*(no|nein|no\.|nein\.|no thanks|no, thanks|nein danke|unsubscribe|remove me|stop)\s*[.!]?\s*$", re.I)
AUTO_SUBJECT = re.compile(r"^(auto:|automatic reply|automatische antwort|out of office|abwesenheit|autoreply|"
                          r"inquiry received|request received|we.ve received|we have received|ticket|"
                          r"\[?(case|ticket|request) ?#|anfrage erhalten|ihre anfrage|eingangsbest)", re.I)

def first_line(msg):
    """The first line the person wrote: plain text, above any quoted text."""
    part = msg.get_body(preferencelist=("plain",)) if hasattr(msg, "get_body") else None
    text = part.get_content() if part else ""
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith(">"):
            return line
    return ""

def inbox():
    """Replies to the invitations, read-only. A reply whose subject is "no" (the List-Unsubscribe
    mail) or whose first line is a plain "no" is applied as an opt-out at once, as the email
    promises. Everything else is only counted: the study lead reads it. No address is printed."""
    import imaplib, email
    from email import policy
    st = load(STATE, {})
    if not st.get("batches"):
        sys.exit("No batch sent yet.")
    pw = secret("mailbox_app_password") or sys.exit("No app password at ~/.config/mailbox_app_password.")
    seen = set(load(os.path.join(FR, "inbox_seen.json"), []))
    since = date.fromisoformat(st["batches"][0]["date"]).strftime("%d-%b-%Y")
    counts, new_seen = {"no (applied)": 0, "auto-reply": 0, "to read": 0}, set()
    with imaplib.IMAP4_SSL(IMAP_HOST) as m:
        m.login(secret(SMTP_USER_FILE) or sys.exit("No login at ~/.config/mailbox_user."), pw)
        m.select("INBOX", readonly=True)
        _, ids = m.search(None, "SINCE", since)
        for i in ids[0].split():
            _, data = m.fetch(i, "(BODY.PEEK[])")
            msg = email.message_from_bytes(data[0][1], policy=policy.default)
            mid = hashlib.sha256((msg.get("Message-ID") or i.decode()).encode()).hexdigest()
            sender = email.utils.parseaddr(msg.get("From", ""))[1].lower()
            if mid in seen or sender.startswith(("mailer-daemon", "postmaster")) or sender == FROM_ADDR:
                continue
            new_seen.add(mid)
            subject = (msg.get("Subject") or "").strip()
            if (msg.get("Auto-Submitted", "no").lower() != "no" or msg.get("X-Autoreply")
                    or (msg.get("Precedence") or "").lower() in ("auto_reply", "bulk", "junk")
                    or AUTO_SUBJECT.match(re.sub(r"^((re|aw|fwd?|wg):\s*)+", "", subject, flags=re.I))):
                counts["auto-reply"] += 1
            elif subject.lower() in ("no", "nein") or NO_WORDS.match(first_line(msg)):
                optout(sender)
                counts["no (applied)"] += 1
            else:
                counts["to read"] += 1
    save(os.path.join(FR, "inbox_seen.json"), sorted(seen | new_seen))
    print("new replies:", counts)
    if counts["no (applied)"]:
        print("Delete those \"no\" replies in the mailbox within 7 days (privacy notice 3.4).")
    if counts["to read"]:
        print("Replies to read in the mailbox; for any other \"no\": python3 study/send.py --optout ADDRESS")

def erase(force=False):
    """31 January 2027 (privacy notice 3.1): the address list, its backups, previews and the
    sending fingerprints go. Kept: optout.json until 31 January 2028, and tokens.json (token ->
    group, no address), which the analysis needs. Files are moved to the Trash, so the last,
    irreversible step (emptying it) is a deliberate one."""
    if date.today() < date(2027, 1, 31) and not force:
        sys.exit("The address list is kept until the survey closes on 31 January 2027. --force to override.")
    import shutil, glob
    keep = {"optout.json", "tokens.json"}
    trash = os.path.expanduser(f"~/.Trash/study-frame-{date.today().isoformat()}")
    os.makedirs(trash, exist_ok=True)
    moved = []
    for p in sorted(glob.glob(os.path.join(FR, "*"))):
        if os.path.basename(p) in keep:
            continue
        shutil.move(p, os.path.join(trash, os.path.basename(p)))
        moved.append(os.path.basename(p))
    print(f"moved {len(moved)} items to {trash}: {', '.join(moved)}")
    print("Now: empty the Trash; delete the sent invitations, reminders and replies in mailbox.org;\n"
          "the results form (Tally Mekb9Y) once the paper is sent, by 31 January 2028; optout.json on 31 January 2028.")

def send(force=False, resume=False):
    """resume: finish a day that a dropped connection cut off (the daily job always passes it).
    A day stopped by a rejection that reads like a block is never resumed without --force."""
    st = load(STATE, {"days": 0, "last": None})
    today = date.today().isoformat()
    sent_today = sum(b["end"] - b["start"] for b in st.get("batches", []) if b["date"] == today)
    stop = st.get("stopped") or {}
    if stop.get("kind") == "block" and not force:
        sys.exit(f"Stopped on {stop.get('date')} by a rejection that reads like a block ({stop.get('reason')}). "
                 "Look before sending more; --force to override.")
    if st.get("last") == today and not (resume and stop.get("date") == today):
        sys.exit("Already sent today.")
    if date.today().weekday() >= 5 and not (SEND_WEEKENDS or force):
        sys.exit("Weekend: no batch. --force to override.")
    rate = bounces(quiet=False)
    if rate is not None and rate > MAX_BOUNCE and not force:
        sys.exit(f"The last batch bounced at {rate:.1%} (limit {MAX_BOUNCE:.0%}). Stop and look at the "
                 "address list before sending more; --force to override.")
    key = hmac_key()
    resuming = resume and stop.get("date") == today
    total = daily_total(st) - (sent_today if resuming else 0)
    reminders = due_reminders(st, key)[:max(0, total)]
    ramp_day = st["days"] - 1 if (resuming and sent_today) else st["days"]
    n = max(0, min(RAMP[min(ramp_day, len(RAMP) - 1)] - (sent_today if resuming else 0), total - len(reminders)))
    q, _ = queue()
    random.shuffle(q)
    batch, stale = [], []
    for d in q[:3 * n]:                         # re-check on the source page, today
        if len(batch) == n:
            break
        ok = still_published(d)
        if ok:
            batch.append(d)
        elif ok is False:
            stale.append(fingerprint(d["email"], key))
    if stale:
        save(STALE, sorted(set(load(STALE, [])) | set(stale)))
    jobs = [(d, "invite") for d in batch] + [(d, "remind") for d in reminders]
    seeds = [l.strip() for l in (secret("study_seeds") or "").splitlines() if "@" in l]
    sample = (batch or reminders or q or [None])[0]
    if sample:
        for k, addr in enumerate(seeds):        # spread through the run, like any other recipient
            jobs.insert((k + 1) * len(jobs) // (len(seeds) + 1), ({**sample, "email": addr}, "seed"))
    print(f"today (daily total {total}): {len(batch)} invitations (re-checked; {len(stale)} no longer "
          f"published), {len(reminders)} reminders, {len(seeds)} seed copies", flush=True)
    sent, tokens, new_tokens = load(SENT, []), load(TOKENS, []), []
    reminded = load(REMINDED, [])
    start, n_rem, refused, stopped = len(sent), 0, [], None
    try:
        with smtp() as s:
            for i, (d, kind) in enumerate(jobs, 1):
                token = "SEED" if kind == "seed" else secrets.token_urlsafe(9)
                fp = fingerprint(d["email"], key)
                try:
                    s.send_message(render(d, token, reminder=(kind == "remind"),
                                          channel="pretest" if kind == "seed" else None))
                except smtplib.SMTPRecipientsRefused as e:
                    code, msg = next(iter(e.recipients.values()))
                    text = ADDR_RE.sub("<address>", msg.decode("utf-8", "replace") if isinstance(msg, bytes) else str(msg))
                    if BLOCK_WORDS.search(text):
                        stopped = ("block", f"{code} {text[:160]}")
                        break
                    if kind != "seed":
                        refused.append(fp)              # rejected at once: a bounce
                    continue
                except (smtplib.SMTPResponseException, smtplib.SMTPServerDisconnected) as e:
                    stopped = ("server", ADDR_RE.sub('<address>', str(e))[:160])
                    break
                if kind == "invite":
                    sent.append(fp)
                    save(SENT, sent)
                elif kind == "remind":
                    reminded.append(fp)
                    n_rem += 1
                    save(REMINDED, reminded)
                if kind != "seed":
                    new_tokens.append({"token": token, "group": d["group"],
                                       "channel": "email-reminder" if kind == "remind" else "email"})
                print(f"  {i}/{len(jobs)}", flush=True)
                if i < len(jobs):
                    time.sleep(random.uniform(*GAP))
    finally:                                    # a dropped connection still leaves a true record
        random.shuffle(new_tokens)              # no order to match against
        save(TOKENS, tokens + new_tokens)
        if refused:
            save(BOUNCED, sorted(set(load(BOUNCED, [])) | set(refused)))
        batches = st.get("batches", [])
        if len(sent) > start:
            batches = batches + [{"date": date.today().isoformat(), "start": start, "end": len(sent)}]
        new_day = len(sent) > start and not (resuming and sent_today)
        st_new = {**st, "days": st["days"] + new_day, "batches": batches}
        if len(sent) > start or n_rem or stopped:
            st_new["last"] = today
        if stopped:
            st_new["stopped"] = {"date": today, "kind": stopped[0], "reason": stopped[1]}
        else:
            st_new.pop("stopped", None)
        save(STATE, st_new)
        print(f"day {st['days'] + 1}: {len(sent) - start} invitations, {n_rem} reminders sent, "
              f"{len(refused)} refused at once, {len(q) - (len(sent) - start) - len(refused)} not yet invited")
    if stopped:
        sys.exit(f"STOPPED ({stopped[0]}): {stopped[1]}. " + ("Look before the next run." if stopped[0] == "block"
                 else "The next run of the job finishes the day (--resume)."))

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--plan"]: plan()
    elif a[:1] == ["--check"]: check()
    elif a[:1] == ["--preview"]: preview(int(a[1]) if len(a) > 1 else 5)
    elif a[:1] == ["--test"] and len(a) == 2: test(a[1])
    elif a[:1] == ["--bounces"]: bounces()
    elif a[:1] == ["--optout"] and len(a) == 2: optout(a[1])
    elif a[:1] == ["--inbox"]: inbox()
    elif a[:1] == ["--erase"]: erase(force="--force" in a)
    elif a[:1] == ["--send"]:
        import fcntl                              # one sending run at a time (hourly job + manual runs)
        lock = open(os.path.join(FR, ".send.lock"), "w")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            sys.exit("Another sending run is in progress.")
        send(force="--force" in a, resume="--resume" in a)
    else: sys.exit(__doc__)
