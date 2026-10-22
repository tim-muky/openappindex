Pre-registration of the developer study **"The cost of being found"**: how new and small apps get found, and what it costs their publishers. This release archives the study's protocol, questionnaire and study pages as they stood before the first answer. Zenodo mints a DOI for it.

**What is frozen**
- **Protocol:** `docs/developer-study-protocol.md`, with the research questions, six predictions and the rule for when each counts as holding, the sample, and the analysis and reporting rules. Online: https://openappindex.org/study/protocol.html
- **Questionnaire:** `study/survey.py` builds the survey form; `study/questionnaire.md` is the readable version (https://openappindex.org/study/questionnaire.html).
  - SHA-256 of `study/survey.py`: `2a0c086fd88b6a5585d854152efbc0fb686f7570b051530f71349be479508230`
  - SHA-256 of the canonical form: `2405be6de88c6f0ee0a52e7816d88710e9ac1cd7811a065be516f51c2b8af17e`. It was confirmed identical to the live form before this release. Anyone can recompute it offline with `python3 study/survey.py --canonical`.
- **Study page and privacy notice:** https://openappindex.org/study/
- **Pretest:** 20 October 2026, n = 1 (the study lead), about 10 minutes; all skip rules worked. Changed afterwards: the App Store link field now says the link starts with https://apps.apple.com/ (it had accepted an email address), and the completion-time part of the bot check was dropped because the survey tool records no start time (§7). See §12 for the limitation.

**What is not in it.** The address list and sending records (`study/frame/`) hold personal data. They are never published and are deleted when the survey closes on 31 January 2027.

Any change after this release is a dated amendment, made before the data it affects.

The survey is open from 22 October 2026 to 31 January 2027. Results will be published openly in spring 2027.
