# Second category: sleep & meditation — measurement protocol

**Status: seed queries and classification v1 frozen 2026-09-01, before any counting.**
This document exists for the same reason as `openappindex-gate-protocol.md`: so that no
rule can be written after seeing the data it filters. Every later change to these rules
must be a dated amendment with its reason, recorded before the amended rule is used
for any published figure.

## Why a second category

The working paper's own limitation paragraph: one category, one storefront, one platform.
The cooking-category findings (discovery failure, price opacity) are a case study until a
second, structurally different category is measured with the same method. Sleep/meditation
was chosen because it is consumer-relevant, notoriously IAP/subscription-heavy, has a
natural German query vocabulary, and — unlike the fragmented recipe field — contains a few
dominant subscription players (concentration is the structural contrast).

**Publication constraint:** nothing from this measurement reaches openappindex.org before
the GO/NO-GO gate closes on 2026-09-15. The served index is under a content freeze; this
work is measurement only. Publication after the gate is a separate, dated decision.

## Category definition

An app belongs to the category when **its own store description identifies it as helping
the user sleep, relax, meditate, or practice mindfulness**. Same principle as cooking:
the app's self-description, not our judgment of its quality or its genre label alone.

In scope by this definition: sleep trackers, sleep-sound/white-noise apps (including
those aimed at babies), meditation and mindfulness apps, breathing/relaxation apps,
sleep-hypnosis apps, sleep-cycle alarm clocks, snoring-recording apps, prescription
digital sleep therapeutics sold through the consumer store (e.g. insomnia DiGAs — they
self-describe as sleep improvement and compete in the same search results).

Out of scope: apps that merely *mention* sleep or relaxation while being something else.
The anticipated error classes are listed below and must be checked against real data
before any count is published.

## Seed query set (25 queries, frozen)

Mirrors the cooking sweep's structure: head nouns, verb phrases, feature phrases, intent
phrases. German storefront (`country=de`), `entity=software`, `limit=200`, iTunes Search
API — identical mechanics to `sample/build_corpus.py`.

```
schlaf                     schlafen                  besser schlafen
einschlafen                einschlafhilfe            schlaf app
schlaftracker              schlafanalyse             schlafzyklus wecker
schlafgeschichten          einschlafgeräusche        weisses rauschen
naturgeräusche schlafen    entspannungsmusik         meditation
meditieren lernen          meditation deutsch        meditation gegen stress
geführte meditation        achtsamkeit               entspannung
atemübungen                stress abbauen            innere ruhe
hypnose schlafen
```

## Classification v1 (frozen; precision pass comes later, dated)

v1 deliberately mirrors cooking's v3 shape — core keyword, genre excludes, one
disambiguation counter, context threshold — because that shape survived contact with
data. The category-specific precision rules (the analogue of cooking's v4) will be
written **only after** inspecting the actual corpus, each rule dated with the error
class that motivated it.

- **Core:** description or name matches
  `schlaf|einschlaf|meditat|entspann|achtsam|beruhig` (case-insensitive).
- **Genre excludes:** Games, Finance, Business, Travel, Shopping, News,
  Magazines & Newspapers, Food & Drink, Photo & Video.
  Deliberately **not** excluded: Medical (sleep therapeutics), Music (soundscapes),
  Health & Fitness, Lifestyle, Education.
- **Disambiguation counter (the PHARMA analogue):** a record with ≥3 hits on
  `babyphone|babyfon|überwach|kamera|apnoe|cpap|diagnose|praxis|termin|arzt|ärzt`
  that outnumber its sleep-context hits is not a sleep app (it is a baby monitor,
  an apnea-device companion, or a medical-practice app).
- **Context threshold:** ≥2 hits on
  `schlaf|ruhe|stress|atem|meditation|traum|geräusch|klang|sound|musik|hypnose|`
  `erhol|müde|entspann|achtsam|mindful|gedanken|beruhig`.

## Anticipated trap classes (the Rezept lesson, applied prospectively)

The cooking run's costliest error was counting before classifying (*Rezept* = recipe
**and** prescription). The equivalent traps here, to be verified against real data:

1. **Baby monitors.** Babyphone/camera apps mention *schlafen* constantly but are
   surveillance tools. Baby *white-noise and lullaby* apps are genuine sleep apps.
   The line is monitoring vs. aiding.
2. **Medical adjacency.** Apnea/CPAP device companions and doctor-appointment apps are
   out; prescription insomnia therapeutics that self-describe as sleep training are in.
   Note `rezept` may appear here in its *prescription* sense — the homonym returns
   from the other side.
3. **Religious meditation.** *Meditation*, *Andacht*, *innere Ruhe* in prayer/devotional
   apps (Gebet, Bibel, Rosenkranz). Religious contemplation apps are a different
   category unless they self-describe as sleep/relaxation aids.
4. **Hardware companions.** Apps unusable without a specific purchased device (smart
   mattress, wearable ring). The analogue of cooking's venue rule: they describe
   operating a product, not an offering in the app market.
5. **German ambush words.** `ruhe` catches *Ruhestand* (retirement/pension apps);
   `traum` catches *Traumdeutung* (esoteric dream interpretation) and marketing German
   (*Traumkörper*) — while *Traumreise* is simultaneously a genuine children's
   sleep-technique term. `entspann` appears in massage-device and physiotherapy apps.
   None of these words appear in the v1 core regex for exactly this reason; `traum`
   and `ruhe` sit only in the context list where a single hit decides nothing.
6. **Utility alarm clocks.** *Wecker* apps that mention sleep in passing; sleep-cycle
   alarms are in scope, plain clock utilities are not.

## AMENDED 2026-09-01 — classification v2, written after inspecting the v1 slice

The sweep ran 2026-09-01: **1,766 distinct apps** across the 25 queries; v1 kept
1,280. Descriptions of the borderline records were read, and a precision layer v2
(`sleep/precision_v2.py`) was written the same day — the analogue of cooking's v4:
each rule motivated by an observed error class, every exclusion printing the rule
that fired. **v2 keeps 1,167 apps** (113 excluded). Confirmed error classes:

- **T** baby-care logbooks (feeding/diaper/growth trackers logging sleep as one
  field) — 25. Baby sleep-aid apps (white noise, lullabies, Napper) survive.
- **U** clock/timer utilities with no sleep-aid claim (ClockZ, Timer+, Opal) — 23.
- **G** health-analytics coaches (heart rate/HRV/blood-pressure/longevity
  dashboards: Welltory, CardioBot, Bevel) — 19.
- **Y** fitness/yoga workout apps (Asana Rebel, Peloton) — 16.
- **H** purpose-specific hypnosis/cessation, decided by the *title* (weight loss,
  smoking, flight anxiety, IBS) — description boilerplate listing a publisher's
  other titles made description-matching unusable — 10.
- **D** hardware companions (Oura, WHOOP, Withings, CPAP/DreamMapper, wake-up
  lights, myHummy), incl. a dated device-brand list observed in this corpus — 9.
- **BM** baby monitors, categorical on the name — 4. **P** pregnancy/birth apps,
  incl. hypnobirthing — 4. **GE** genres Sports (freediving apnea trainers) and
  Navigation (anchor alarms) added — 3. **C** clinical therapy programs
  (HelloBetter, Kaia COPD, Stresscoach) — 3, with the program/prescription group
  compulsory and a sleep-dominance exemption so prescription sleep therapeutics
  (somnio, hiPanya) stay in scope as the frozen definition requires.

**Two new German substring traps found while writing v2** (the *Rezept* lesson,
new instances): plain `wickel` (diaper-changing) matches inside *entwickelt* /
*Entwicklung* and flagged meditation apps as baby logbooks; bare `slim` matches
inside *Slime* and *Muslim* and excluded a Muslim meditation app. Both fixed with
word boundaries the day they were found; both are recorded here because the trap
list is a credential, not an embarrassment.

**Known residual gray zone, accepted and documented:** mood/anxiety companions
without prescription language (MindDoc, 7 Cups, DARE) remain in the slice — they
sit on the same shelf as the kept anxiety-relief and breathing tail, and the
frozen self-description rule does not cleanly separate them. Revisiting them is
a future dated decision, before any publication.

## Pipeline & artifacts

Scripts live in `sleep/`, data in `sleep/data/` — the cooking scripts under `sample/`
are frozen evidence and are not modified. Order mirrors the cooking run:

1. `sleep/build_corpus.py` — 25-query sweep → `sleep/data/corpus_sleep_de.json`
2. `sleep/classify.py` — v1 classification report (counts + every exclusion with the
   rule that fired, so wrong exclusions are findable)
3. Manual precision inspection → dated v2 rules if error classes are confirmed
4. Price enrichment (product pages, `serialized-server-data`) — same reader as
   `sample/enrich_prices.py`
5. Closure crawl over `similarItems` from the classified seed set — same mechanics,
   same politeness (2.6 s between fetches, resumable checkpoints)

Every record carries its read date. Missing values are *not collected*, never zero.
