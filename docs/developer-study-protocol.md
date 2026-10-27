# The cost of being found: a study of new, small app publishers

**Study protocol — v1.0 · Frozen 2026-10-22 by the public commit tagged `study-freeze-2026-10-22`**

*Decisions recorded in this version:*
- *2026-10-08 (Tim): headline **discovery**; target group: our two measured categories; method
  **survey only**, with an optional free-text statement, no interviews; no academic partner for
  now, reconsider for the paper or a follow-up.*
- *2026-10-20 (Tim): freeze and survey opening on 22 October 2026; one reminder email; AI-assisted
  analysis disclosed; a pre-registered bot-check rule; pre-registered channel codes; a legal check
  is advisable but does not gate the send.*

*Frozen by public commit on 2026-10-22, before the first invitation goes out. After that, changes
are dated amendments made before the data they affect — the same rule as the GO/NO-GO gate and
experiment 2.*

---

## 1. Why this study

openAPPindex measures the supply side of two App Store categories from the outside: what exists,
what search shows, what "free" costs. Three claims sit next to that measurement and have not been
measured from the publishers' side:

- that the share of revenue spent on user acquisition has risen steeply since about 2019 (the
  maintainer's own experience as COO of Bonial.com, publisher of kaufDA — an anecdote, not data);
- that a new app can barely reach a significant user base, even with considerable ad spend;
- that AI coding tools have multiplied new apps without multiplying usage (Demirer, Musolff and
  Yang, NBER Working Paper 35275, 2026 — measured across four software marketplaces, not from
  publishers' accounts).

This study asks the people those claims are about. Its focus is **newer and smaller publishers**,
the ones for whom discovery decides whether an app survives. Its headline is **discovery**.

## 2. Research questions

The headline question is discovery: **how do new, small apps get found, and does the store's
own search find them?** Acquisition cost and pricing are asked as context, because paying for
installs is what publishers do when search does not find them.

- **RQ1 (headline): Where do installs come from?** What share of a new, small publisher's
  installs comes from App Store search, from browse or featuring, from paid placement, and from
  outside the store? Do publishers know?
- **RQ2: Measured vs. experienced invisibility.** Do publishers whose apps our measurement found
  absent from the obvious query, or reachable only through the "similar apps" graph, report a
  lower search share and fewer installs than those it found visible? *This is what no other
  survey can do: it sets what publishers report against what was measured, app by app.*
- **RQ3: What they do about it.** ASO effort; whether they know which search terms they rank for;
  whether they turned to paid acquisition, and whether that paid for itself.
- **RQ4: AI assistants.** Any measurable traffic from AI assistants so far, and what publishers
  expect.

## 3. Predictions, stated before the data

Each is reported whether it holds or not, with its count, denominator and interval. Question IDs
are those in `study/survey.py` (§6.1). Option texts are quoted exactly as respondents see them.

| # | Prediction | Counts as holding if |
|---|---|---|
| P1 | Most target publishers report that App Store search brought a minority of their installs | > 50% of those who answered D2 choose a band below 50% ("0–9%", "10–24%" or "25–49%"). "Don't know" is excluded from the denominator; its count is reported beside the share. |
| P2 | Publishers whose app was measured absent from the obvious query report a lower search share than those measured present | The median D2 band is lower for "absent" than for "present". D2 "Don't know" excluded. Linked answers only (L2 = "Yes" and a usable L1); each arm needs n ≥ 30. |
| P3 | Apps reachable only through the "similar apps" graph report fewer installs than apps found by the query sweep | The median O1 band is lower for graph-only apps than for query-found apps. O1 "Don't know" excluded. Linked answers only; each arm needs n ≥ 30. |
| P4 | Most target publishers do not know which search terms their app ranks for | > 50% of those who answered D4 choose "No" or "Not sure what that means". "Yes, I check regularly" and "Roughly" count as knowing. |
| P5 | Among target publishers who ran paid acquisition, most report that it did not pay for itself | Among those who chose any paid channel in M1 and answered M4: > 50% choose "No, they cost more than they earned". "Too early to say" and "Don't know" are excluded from the denominator; their counts are reported beside the share. |
| P6 | Few publishers see measurable AI-assistant traffic | < 10% of those who answered AI1 report any: "Yes, noticeably" or "A few". "I couldn't tell" is excluded from the denominator; its count is reported beside the share. |

**Benchmark for P1.** Apple's own sales material states that almost 65% of downloads follow a
search (Apple Ads, "Ads on the App Store"). If P1 holds for new, small apps, the finding is
that the store's headline figure does not describe them.

**Which answers count, fixed now.**
- The headline target group is **new-small, pooled across both categories** (cooking and sleep).
- Only answers whose group comes from a valid email token count toward the per-group tests of
  P1–P6 (§5). Open-channel answers are reported beside them as a separate stream.
- A prediction is evaluated only where its denominator is **n ≥ 30**. Per-category and
  per-size-group figures are shown only where that cell has n ≥ 30. For P2 and P3, each compared
  arm needs n ≥ 30. Below that, the count is reported as "insufficient to evaluate".
- **Expect the established group to be too small.** Only about 100 established developers publish
  a contact address. At any plausible response rate, comparisons with the established group will
  most likely read "insufficient to evaluate". That is stated now, so it is not a surprise later.

These are directional, descriptive predictions, not significance tests; with the sample sizes
expected here, intervals will be wide and are reported as such. P2 and P3 rest on the subset
that consents to linkage; its size is reported next to every linked figure.

## 4. Population and sampling frame

The frame is the measured category, not whoever answers. That is what makes non-response
visible: every respondent can be compared with every non-respondent on facts we already hold.

| | Cooking (DE) | Sleep & meditation (DE) |
|---|---|---|
| Apps in the measured category | 941 | 3,578 |
| Distinct developers | 839 | 3,047 |
| **Target group:** apps first released since 2023-10-01, < 1,000 ratings, developer with ≤ 3 apps in the category | **584 apps / 578 developers** | **1,951 apps / 1,850 developers** |
| …of those, apps with zero ratings | 307 | 1,372 |
| Comparison group: released before 2023-10-01 and ≥ 1,000 ratings | 61 apps | 101 apps |

*(Counts from the index data as of 2026-10-08; the frame is re-drawn from the latest weekly read
on the freeze date.)*

**Who is invited (changed 2026-10-09, Tim): every developer in both measured categories**,
about 3,900 in total, not only the target group. Only developers who publish a contact address
can be emailed (§5).
- The distribution is so top-heavy (median 0 ratings in the target group) that the full
  population is dominated by new, small apps anyway.
- Restricting invitations to our own cut-off would invite the objection "you only asked the
  ones that failed".
- Asking everyone gives the comparison that carries the finding.

**What is analysed as the headline, fixed now:**
- **Target group:** new and small, as defined in the table above. P1–P6 are evaluated on it.
- **Comparison group:** established apps, released before 2023-10-01 with ≥ 1,000 ratings. P1, P2
  and P4 are also reported for it, side by side, where n allows (§3).
- **Everyone in between** is reported as its own band, never pooled into either group after the
  fact.
- The group is assigned from **measured** facts (release date, ratings, apps per developer in the
  index), never from self-description.
- **Excluded:** galleybook (the maintainer's own app), and any app by a developer who is a funder
  of openAPPindex at the time of invitation.

Developers outside the two categories who answer through open channels are kept as a separate,
labelled stream and never pooled with the frame sample.

## 5. Recruitment

**Not combined with any request for support.** No invitation, reminder or survey page asks for
funding, donations or sponsorship, and no such request will be sent to participants until the
paper is published. Participation never affects how an app appears in the index, and the
invitation says so.

Channels, each response tagged with the channel it came from:

1. **Direct invitation to the frame** — by email, to the address the developer publishes on their
   own website, support or privacy page. The risk decision is in §8.
2. **Open call:** a study page on openappindex.org; developer communities (e.g. Indie Hackers,
   r/iOSProgramming, German iOS/Flutter meetups, F-Droid forum for the comparison of open stores);
   the press wave planned from 2026-10-20 (it carries the survey link once the survey opens on
   2026-10-22).
3. **The developer questionnaire page (GAL-579)**, if it is live by then — as a link, not a merge:
   that questionnaire publishes per-app answers, this study never does.

**Staging, decided 2026-10-08.**
- Open channels (2) and direct email (1) start **in parallel at the freeze**.
- Contact addresses are those the developer publishes on their own website, support or privacy
  page; the App Store shows none. The address list is refreshed before the first batch, and each
  address is re-checked on its source page on the day it is written to.
- **Risk accepted by Tim on 2026-10-08:** the email is an invitation to take part in research,
  not advertising for a product. A legal check remains advisable but does not gate the send (§8).
- One invitation email and one reminder email, nothing more. Both say that nothing is asked for or
  sold, carry the privacy notice (GDPR Art. 14), and offer an opt-out.

**Reminder (decided 2026-10-20, Tim): one email, about 14 days after the invitation.**
- It goes to every address that was written to, except opt-outs and bounces.
- Answers are anonymous by design, so we cannot tell who has answered. The reminder says so and
  thanks those who already did.
- Reminder links carry `channel=email-reminder` and a fresh random token, recorded as
  token → group in the same way as the invitation's.

**Invitation links (decided 2026-10-10, Tim): anonymous by group.**
- Each email link carries three hidden fields:
  - `group`: category/size group, e.g. `cooking/new-small`, `sleep/established`,
    `sleep/in-between`;
  - `channel`: one of the codes below;
  - `token`: a random one-time number.
- The sending script records only token → group. **It never stores which address received which
  token.** No answer can be traced to an app or a person through the link.
- A token used twice marks a duplicate; the first answer is kept. Invitation and reminder tokens
  are separate, so a person could in principle answer twice, once through each. This cannot be
  detected by design (§12).
- Individual linkage to measured data happens only through the optional consent and App Store
  link (L2, then L1).

**Channel codes (pre-registered 2026-10-20).**

| `channel` | Where the answer came from |
|---|---|
| `email` | the invitation email |
| `email-reminder` | the reminder email |
| `study-page` | the study page on openappindex.org |
| `community` | a post in a developer community |
| `press` | press coverage |
| `pretest` | the pretest (§6.3); excluded from all results |

**Two streams, never pooled.**
- **Email stream:** answers whose token is in the sender's token list. For these, the group is
  taken from the token list (token → group), not from the URL, which a respondent could edit.
  Only these answers count toward the per-group tests of P1–P6.
- **Open stream:** answers with no token, or with a token not found in the token list. They are
  reported beside the email stream, with their channel, and never enter the per-group tests.
- The `channel` value of an email answer only separates invitation from reminder answers; no
  test depends on it.

**What participants get:** the finished paper before public release, and the aggregated results
for their category. No individual analyses: the index treats every app the same, so a
participant learns nothing about their own app that a non-participant cannot.

## 6. Instruments

### 6.1 Survey (English, ~12 minutes, anonymous by default)

The instrument is defined once, in `study/survey.py` (the `SURVEY` list); the full wording and
options are there. In order:

- **Hidden fields:** `token`, `channel`, `group` (§5).
- **Introduction and consent [C1]:** what the study is, what happens with the answers (including
  AI-assisted analysis, §7), who runs it, the right to withdraw consent, and links to the frozen
  protocol and the privacy notice. One required consent box.
- **Screening:**
  - has published at least one app on the App Store [S1]; "No" ends the survey;
  - role: solo, small team, company or studio, agency, other; and which app to answer about —
    ideally the most recent, or the one named in the email [S2].
- **Your app (A):** year of first release [A1]; App Store category [A2]; how it earns money,
  several allowed [A3]; platforms, several allowed [A4]; number of apps published in total [A5];
  whether it is still on the App Store [A6].
- **D — Being found (headline block):**
  - how the app got its first 100 users, several allowed [D1];
  - share of first-time downloads from App Store search in the last 90 days, pointing to App Store
    Connect's Source Type report: 0–9%, 10–24%, 25–49%, 50–74%, 75–100%, or "Don't know" [D2];
  - where that figure comes from: App Store Connect, another analytics tool, or own estimate
    [D2a; hidden if D2 = "Don't know"];
  - how many of the search downloads come from people searching for the app's name: "Almost all",
    "More than half", "About half", "Less than half", "Almost none", "Don't know"
    [D2b; hidden if D2 = "Don't know"];
  - where the rest noticeably come from, several allowed [D3];
  - whether they know which search terms the app appears for [D4];
  - hours per month on App Store optimisation [D5];
  - whether they ever searched for the obvious words and did not find the app [D6].
- **M — Paying to be found (context):**
  - paid channels used, or "No, never" [M1]; M2–M5 are hidden after "No, never";
  - spend in a typical month with ads running, in bands [M2];
  - change in the cost of one new user through ads since they started [M3];
  - whether paid ads paid for themselves [M4];
  - whether they stopped paid ads, and why (optional free text) [M5].
- **O — Where the app stands:** total installs band [O1]; monthly users band [O2]; whether the app
  covers its costs [O3]; whether paid tiers were introduced or raised in the last 24 months [O4];
  the main reason (optional free text) [O4a; shown only after "Introduced", "Raised prices" or
  "Both"].
- **AI — Assistants:** installs or visitors traceable to AI assistants [AI1]; whether AI assistants
  will matter for discovery in the next two years [AI2].
- **Statement (optional):** "Is there anything you'd like to tell us about getting your app found:
  your experience, your background, what you would change?" Up to ~300 words [F1]. Permission to
  quote: no, anonymously, or by name [F2]; the name or studio name [F2a; shown only if quoted by
  name].
- **Linking to measured data (optional):** consent to compare the answers with the public data the
  index measured for the app [L2]; the App Store link [L1; shown only if L2 = "Yes"]. Without both,
  the answer is used unlinked.
- **Results:** a link to a separate form (`RESULTS_FORM` in the same file: email address and app
  category) for receiving the paper. It is not connected to the survey answers.

Bands, not exact figures, to lower the cost of answering honestly.

### 6.2 Free-text statements

- Statements are analysed thematically against RQ1–RQ4.
- They are quoted only with a separate, explicit permission given in the survey: anonymous by
  default, or named if the respondent asks to be named.
- Unquoted statements count only in theme counts.

### 6.3 Pretest

Three to five people (Tim's contacts, including former industry colleagues) take the survey on
20–21 October 2026, before the freeze, and say where a question was unclear. Their links carry
`channel=pretest`; their answers are not part of the results. Changes made after the pretest are
part of the frozen instrument. If the pretest cannot be done in time, the line below says so and
§12 names it as a limitation.

Done 20 October 2026, n = 1 (the study lead), about 10 minutes; all skip rules worked. Changed afterwards: the App Store link field now says the link starts with https://apps.apple.com/ (it had accepted an email address), and the completion-time part of the bot check was dropped because the survey tool records no start time (§7). See §12 for the limitation.

### 6.4 Frozen instrument

At the freeze, three values fix the instrument that is fielded:
- the public commit that freezes this protocol and `study/survey.py`, tagged
  `study-freeze-2026-10-22` in the openAPPindex repository
  (github.com/tim-muky/openappindex). A commit cannot name its own hash, so the tag does;
- the SHA-256 of `study/survey.py` in that commit: `2a0c086fd88b6a5585d854152efbc0fb686f7570b051530f71349be479508230`;
- the SHA-256 of the canonical form: `2405be6de88c6f0ee0a52e7816d88710e9ac1cd7811a065be516f51c2b8af17e`. The canonical
  form is every block of the survey in order, with its type and content, and with the random
  block identifiers (UUIDs) left out. It is the same whether it is built from `study/survey.py`
  or exported from the live Tally form, so anyone can check it: `python3 study/survey.py
  --canonical` prints it without network access. At the freeze it was confirmed identical for
  the live form, and the export is committed as `study/instrument-canonical.json`.

The address list and sending records (`study/frame/`) and `study/records/` are never published.

## 7. Analysis

**Reporting rules, fixed now.**
- The n ≥ 30 rule and which answers count are fixed in §3. (At n = 30 a share of 50% carries a
  95% interval of about ±17 points; at n = 100 about ±10.)
- Every share comes with its Wilson interval, count and denominator. Answers excluded from a
  denominator ("Don't know", "Too early to say", "I couldn't tell") are counted and reported
  beside it.
- The email stream and the open stream are reported side by side, never pooled (§5).
- No weighting in the headline. If the non-response check shows a skew, weighted figures are
  added beside the unweighted ones, never instead of them.
- Results describe **respondents**, and every headline says so ("among N new, small publishers
  who answered…"). Generalising to the category is limited to what the non-response check
  supports.

**P1 is reported three ways**, because "search" hides two different things. Each uses the P1
rule (§3): the share of respondents below 50%.
1. total search share (D2);
2. the same restricted to answers taken from App Store Connect (D2a = "App Store Connect
   analytics"), not estimates;
3. **generic search**: search share minus the part that is people typing the app's own name. A
   user who already knows the name was not found by search, they looked it up. This is the figure
   that speaks to discovery. The combination rule, per respondent:
   - generic share = midpoint of the D2 band × (1 − midpoint of the D2b band);
   - D2 midpoints: 0–9% → 5%; 10–24% → 17.5%; 25–49% → 37.5%; 50–74% → 62.5%; 75–100% → 87.5%;
   - D2b midpoints (share of search downloads that are name searches, read as five equal bands):
     "Almost all" → 90%; "More than half" → 70%; "About half" → 50%; "Less than half" → 30%;
     "Almost none" → 10%;
   - "Don't know" or no answer on either question: excluded, and counted.

**P2 and P3 (measured vs. reported)**
- Only for respondents who consented to linkage (L2) and gave a usable App Store link (L1). The
  linked n is reported every time.
- Measured visibility is **re-read during the field period**: the obvious query and the 25-query
  sweep are re-run for every linked app before the survey closes. A November answer is not
  compared with an August search.
- The comparison is **stratified** by release year and ratings band, because small, new apps are
  both less visible and less installed. Stratification separates "invisible" from "just new".
  The result is stated as an association, never as cause.

**Data quality**
- Installs below monthly users: an answer is flagged only when the lowest value of its O2 band is
  at or above the highest value of its O1 band (the two questions use different band scales). For
  example, O1 "100–999" with O2 "5,000–9,999" is flagged; O1 "100–999" with O2 "500–4,999" is
  not, since both can be true. "Don't know" on either: not flagged. Flagged answers are reported
  separately.
- Duplicate tokens: the first answer is kept. Invitation and reminder tokens are separate, so a
  person who answers through both cannot be detected (§5, §12).
- **Bot check (pre-registered 2026-10-20; amended 2026-10-20 before the freeze).** Answers
  without a valid email token (open-channel answers, or tokens not found in the sender's token
  list) are flagged if they chose the option in the same position (for example, always the
  first) on every single-choice question they answered. A completion-time rule ("under 3
  minutes") was planned but dropped after the pretest: the survey tool records only the time of
  submission, not when a respondent started.

  Flagged answers are reported separately, with their count. They are never silently dropped.
- Answers with `channel=pretest` are excluded from all results.

**Non-response check — at group level** (links are anonymous by group, see §5):
- Response rate per category × size group in the email stream, against the number written to in
  that group.
- Respondents who gave their App Store link and consented to linkage are compared with the frame
  on measured facts: first release date, ratings, in-app purchases, measured search visibility,
  days since last update.
- Non-respondents cannot be identified individually, by design.

**Free text.** Statements are coded against RQ1–RQ4. Where they contradict the survey figures,
the contradiction is reported, not smoothed over.

**AI-assisted analysis (decided 2026-10-20).**
- The analysis and the coding of free text are done with Claude (Anthropic), used as a service
  provider.
- Before any answers are shared with it, the name or studio name (F2a) and the App Store link (L1)
  are removed. For linked answers, the link is first replaced by the measured facts the analysis
  needs.
- Addresses from the results form are never shared with it.
- Tim reviews every figure and every code before publication. Anthropic's data-processing terms
  are part of the legal check (§8).

Every figure in the paper states its denominator and source (survey, free-text statement, or
measurement).

## 8. Law, ethics, data protection

- [x] **Unsolicited email (UWG §7, GDPR) — risk decision.**
  - Cold email can be unlawful advertising in Germany even between businesses, a public address
    is not consent, and the BGH has treated survey emails as advertising.
  - The open question: is a non-commercial research invitation "advertising", given the
    project's commercial links (galleybook, funding, paid reports allowed by the funding policy)?
  - Many indie developers are natural persons, so GDPR applies (Art. 6(1)(f); Art. 14 notice in
    the email).
  - **Decided 2026-10-08: Tim accepts the risk; emails go out in parallel with the open channels.**
    A legal check is advisable but does not gate the send.
  - One invitation and one reminder (§5), each saying that nothing is asked for or sold, with an
    opt-out and the privacy notice.
- [ ] **Legal check (advisable, does not gate the send).** Three questions:
  - (a) UWG §7: is the research invitation, with its one reminder, "advertising"?
  - (b) GDPR Art. 14(3): is the notice given in time for addresses collected from public pages?
    Mitigation: the list is refreshed before the first batch, and each address is re-checked on
    its source page on the day it is written to.
  - (c) Anthropic's data-processing terms for the AI-assisted analysis (§7).
- [ ] **Survey tool:** Tally, form data stored in the EU, no tracking. The study does not use IP
      addresses; Tally processes them technically to operate the form (privacy notice §4).
- [ ] **AI service for analysis (decided 2026-10-20):** Claude (Anthropic) as a service provider;
      it receives answers only without names (F2a) and App Store links (L1), and never the
      results-form addresses (§7). Named in the survey introduction and the privacy notice.
- [ ] **Consent text and privacy notice** (purpose, retention, deletion on request, withdrawal of
      consent, who sees raw data — Tim only; the AI service sees answers without names or App
      Store links).
- [ ] **Ethics review — deferred (decided 2026-10-08).** No partner for now. openAPPindex has no
      institution, so the protocol states that plainly. Reconsider a partner (e.g. DSA40
      Collaboratory, Weizenbaum Institute) for the paper or a follow-up.
- [ ] Data retention: the address list is deleted when the survey closes (31 January 2027); raw
      answers are deleted 12 months after publication; aggregated data is published.

## 9. Publication

A working paper, "The cost of being found" (working title), with: the protocol as frozen, every
amendment, the instrument (§6.4), aggregated data (CC BY 4.0), the non-response comparison, and a
list of what did not hold. Published whatever the result.

## 10. Timeline and the maintainer's time

| When | What | Tim's hours |
|---|---|---|
| Oct 2026 | Protocol and survey build (Claude); legal check on invitations (advisable, not gating) | ~1 |
| 2026-10-20 – 2026-10-21 | Pretest with 3–5 people | ~1 |
| 2026-10-22 | Freeze by public commit; survey opens; invitations start | — |
| about 14 days after each invitation | One reminder email | — |
| 22 Oct 2026 – 31 Jan 2027 | Survey open, ~14 weeks | ~1 (sharing in communities) |
| 2027-01-31 | Survey closes; address list deleted | — |
| Feb 2027 | Analysis (Claude, on answers without names or App Store links); Tim reviews | ~2 |
| Spring 2027 | Paper: "The cost of being found" (working title) | ~2 |

The Prototype Fund decision is expected in Feb/Mar 2027. The study can be named in the
application as outreach work (question 9a), which the Resilience track asks to be about half of
funded time.

## 11. Anticipated critique, and the answer built into the design

| Objection | Answer in the design |
|---|---|
| "Only frustrated developers answer." | The whole category is invited, not just the small apps. Respondents are compared with non-respondents on measured facts (§7). Headlines say "among respondents". |
| "Developers don't know where installs come from." | D2 points to the exact App Store Connect report; D2a records whether the figure was looked up or estimated; P1 is also reported on looked-up figures only. "Don't know" is reported as a finding. |
| "Search share includes people searching your name after an ad." | D2b separates name searches from generic searches; P1 is reported for generic search, by a rule fixed in advance (§7). |
| "Small apps get few installs because they're new or bad, not because they're invisible." | P2/P3 are stratified by release year and ratings, and stated as association, not cause. |
| "Your visibility data is from August." | Visibility of linked apps is re-measured during the field period. |
| "n is tiny." | n ≥ 30 rule per group and per compared arm; intervals on every share; groups below the threshold are reported as insufficient. |
| "Anyone could fill in the open link." | Only answers with a valid email token count toward P1–P6; their group comes from the token list, not the URL. Open-channel answers are a separate stream, with a pre-registered bot check. |
| "You primed respondents with your thesis." | The invitation and introduction state no finding. The predictions are published before the survey opens, but not on the survey page itself. |
| "Apps that failed and were removed can't answer." | A6 asks it; developers of removed apps are explicitly invited. The 36 apps no longer found on 2026-10-06 are in the frame. |
| "Conflict of interest: you sell a recipe app." | galleybook is excluded; the protocol is frozen and public before the data exists; the raw-data handling and funding policy are public. |
| "Survey bands are arbitrary." | Bands are fixed in the frozen instrument; results are reported per band, not interpolated. The one exception, the generic-search figure, uses midpoints fixed in advance (§7). |

## 12. Limitations, known in advance

- Self-reported figures, banded; publishers may not know their install sources.
- Response will skew toward the motivated, plausibly the frustrated; the non-response check
  measures how much, it does not remove it.
- Two categories, one storefront.
- The established group is small (about 100 developers with an address), so comparisons with it
  will most likely be insufficient to evaluate.
- Because answers are anonymous, a person who answers through both the invitation and the
  reminder link counts twice. This cannot be detected by design.
- Open-channel answers cannot be verified; they are a separate stream and are not used for the
  predictions.
- The pretest was smaller than planned: one person, the study lead, instead of three to five
  outside testers (§6.3). Questions that others find unclear may only show up in the field; any
  correction then follows as a dated amendment.
- The maintainer publishes an app in one of the categories; galleybook is excluded from the sample,
  and his own experience is cited as his, never pooled.

## Amendments

### Amendment 1 (2026-10-27, before the invitations of 2026-10-28): a second invitation text, assigned at random

- **Why.** The first 340 invitations (22–27 October, all with the original text) brought one survey
  answer.
- **What.** From 2026-10-28, each invitation gets the original text (A) or a second text (B) at
  random, half and half within each day's batch. B leaves out the maintainer's background and
  states the aim of the study: open numbers that let everyone see the barriers to entry for new
  apps and lower them. Like A, it states no finding about how apps get found. It says that nothing
  is asked for or sold and that taking part doesn't affect the index, and it carries the privacy
  notice and the opt-out. Both texts are in `study/send.py`. The reminder is the same for both.
- **What is recorded.** The sending script adds the text version to the token list
  (token → group, version). It still never stores which address received which token.
- **Analysis.**
  - The response rate per text (answers with a valid email token ÷ invitations) is reported with
    its interval.
  - Answers through both texts count toward P1–P6, because the text is assigned at random.
  - B states an aim, so it may attract or prime publishers who share that aim. P1–P3 are therefore
    also reported per text where n allows. A difference is reported, not corrected.
