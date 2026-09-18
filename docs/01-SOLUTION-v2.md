# JanSetu — Solution Architecture v2
### The three new features, and how they change the build

**v2 changelog:** Added ① Single Helpline (one number, all departments), ② Feature-phone access (missed call · SMS · IVR · USSD · kiosk), ③ Citizen photo/comment verification feeding the Impact Ledger. Pipeline restructured 7 → 8 layers. Demo script and team split updated.

---

## 1. Why these three are not feature creep

Every one of your three ideas maps to an **exact clause** of the official problem statement. That is the whole argument for building them.

| The brief says… | Your idea | What it becomes |
|---|---|---|
| *"Development requests live in **fragmented systems**"* | **Single helpline number** | One front door + an AI routing brain. The citizen never has to know which department owns their problem. |
| *"aggregates citizen development requests via **voice, text, and messaging apps** across diverse linguistic regions"* | **SMS + missed call for non-smartphone users** | Feature-phone-first access. ~40% of rural India is not on a smartphone — right now every competing entry is invisible to them. |
| *"**no way to measure the impact** of large-scale digital public infrastructure initiatives"* | **Photo / comment feedback from the public** | Citizen-verified completion → the ground truth that drives the Impact Ledger. Solves the "ghost asset" problem. |

Read together: **you just closed all four clauses of the problem statement.** Nobody else in this track closes more than one.

### The bigger framing this unlocks

> **JanSetu is the missing coordination layer on India's DPI stack.**

India already has the bricks. Nobody has assembled them for this job:

| India DPI brick | What JanSetu takes from it |
|---|---|
| **Aadhaar** | De-duplicated identity (optional, consented) — one citizen, one vote |
| **LGD** (Local Government Directory) | Canonical location codes — every complaint resolves to a real administrative unit |
| **Bhashini** (National Language Translation Mission) | Free Indic ASR / MT / TTS — the multilingual layer, built on India's own language DPI |
| **DigiLocker** | Verified supporting documents from citizens |
| **CPGRAMS** | The existing grievance backend — **we route into it, we don't replace it** |
| **BharatNet** | The connectivity reality map → feeds our reporting-bias model |
| **UPI / DBT** | Payment rails for any citizen incentive or compensation |

**We are not building another complaint portal. We are the intelligence layer that sits in front of the ones that already exist.** That single sentence is worth more with a government evaluator than any feature list.

---

## 2. Feature ① — The Single Helpline

### The principle: **One number. Zero menu. No app. No English. No literacy required.**

Today a citizen in Dhule with a water problem must know that JJM ≠ PWD ≠ Zilla Parishad ≠ the local MLA's office. That's the fragmentation. So:

> **Dial 155XXX (toll-free). Speak. Hang up. The system figures out the rest.**

No `Press 1 for roads, Press 2 for water`. IVR menu trees *are* the fragmentation — we replace the tree with understanding.

### Call flow

```
   Citizen dials 155XXX  ·  or gives a MISSED CALL  ·  or sends SMS to 56767
                                  │
                                  ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  CHANNEL ADAPTER LAYER  →  normalises every channel to ONE   │
   │  CitizenReport schema. Downstream never knows the channel.   │
   └──────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
   "नमस्ते। कृपया आप अपनी समस्या बताइए।"        ← 8 sec open-speech capture
                                  │
                                  ▼
   STT (Bhashini → Sarvam → Google Chirp)  +  language ID
                                  │
                                  ▼
   Gemini structured extraction → sector · severity · LGD code · affected pop.
                                  │
                                  ▼
   TTS readback in the SAME language:
   "आपकी समस्या — धुले ब्लॉक में सड़क खराब। सही है?  1 हाँ ·  2 नहीं"
                                  │
                                  ▼
   DTMF / speech confirm  →  ticket JS-2026-MH-DHU-000123 created
                                  │
              ┌───────────────────┴───────────────────┐
              ▼                                       ▼
   AUTO-ROUTED by sector + LGD:               SMS/voice ACK to citizen
   PMGSY · PWD · JJM · DISCOM · DHS            in their own language
   BDO · Education · BharatNet                 + ticket ID + expected SLA
              │                                       │
              ▼                                       ▼
        SLA clock starts                  Call the SAME number anytime →
                                          TTS status in their language
```

### The routing brain

A **Department Routing Table** keyed on `(sector, subsector, admin_level, lgd_code)`:

| Sector | Primary authority | Scheme | Typical SLA |
|---|---|---|---|
| Rural roads | PMGSY / Zilla Parishad | PMGSY-III, MGNREGA | 30 d |
| State roads | PWD (state) | State plan / CRIF | 45 d |
| Drinking water | JJM → PHED / ZP Water & Sanitation | Jal Jeevan Mission | 21 d |
| Power | DISCOM | RDSS | 14 d |
| Health | District Health Society | NHM | 15 d |
| Education | Education Dept | Samagra Shiksha | 30 d |
| Sanitation | Block Development Officer | SBM-G 2.0 | 30 d |
| Digital access | BharatNet / CSC SPV | BharatNet | 60 d |

Routing is **data, not code** — one YAML per state. Adding a department or reassigning an SLA never touches the engine. That is a DPI property, and judges testing for *deployability* will look for exactly that.

### The honest integration story

We don't replace CPGRAMS — we hand it a **structured, de-duplicated, geo-coded, severity-scored ticket** instead of the free-text pile it gets today. Fallback chain if no API exists: API → email to the nodal officer → **SMS to the designated field officer** (works everywhere, always).

---

## 3. Feature ② — Feature-phone access (the reach argument)

Roughly **4 in 10 rural Indians are not on a smartphone**, and female smartphone ownership lags male ownership sharply. A voice-only, app-free entry is not a nice-to-have — it's the difference between a tool for Bharat and a tool for people who already have a voice.

| Channel | Handset | Cost to citizen | How it works |
|---|---|---|---|
| **Missed call** | Any keypad phone | **₹0** | Citizen gives a missed call → we call back within 60 s → same open-speech flow. The single most important channel for the poorest user. |
| **Toll-free voice** | Any phone | ₹0 | Dial 155XXX, speak, hang up. |
| **SMS** | Any phone (2G, Unicode) | ~₹0 with toll-free short code | Free-text regional-language SMS → same pipeline. Ambiguous? System asks one clarifying question. `STATUS <id>` → instant stage reply. |
| **IVR / DTMF** | Any keypad phone | ₹0 | For outbound verification bursts: *"काम पूरा हुआ? 1 हाँ · 2 नहीं"* |
| **USSD** | Any phone | ₹0 | `*99*1#` — works with zero data. Best for status checks in low-signal areas. |
| **WhatsApp** | Smartphone | Free | Rich: text, voice note, photo, location. |
| **Web / kiosk** | CSC / Gram Panchayat | — | **Offline-first sync**: kiosk operator batches reports without connectivity; syncs when a signal appears. |

### Why this wins "Depth & Reach Across India" (20%)

The criterion asks: *can this realistically scale from one state to communities across India?* A WhatsApp-and-web product cannot. **A toll-free number plus a missed call plus SMS works on a ₹1,200 handset with no data plan.** Say that out loud in the demo and it reframes the entire product.

### Build strategy: simulator-first, provider-agnostic

You will not get an Indian toll-free number provisioned in 13 days. So:

```
services/telephony/
├── base.py           # TelephonyProvider ABC: parse_inbound(), send_sms(), make_call(), send_tts()
├── simulator.py      # ← DEFAULT. A web UI that PRETENDS to be a phone. Judges "call" in-browser.
├── exotel.py         # Indian CPaaS — best real-world story for gov deployment
├── twilio.py         # Fastest to provision, good for the video
└── bhashini.py       # Govt of India language DPI: Indic ASR / MT / TTS
```

`TELEPHONY_PROVIDER=simulator` is the default. Swapping to a real provider is **one env var**. The simulator is not a cop-out — it's what lets four people build in parallel without blocking on a telecom KYC process, and it demos perfectly.

**For the video:** the simulator screen *looks* like a phone. A judge cannot tell. Say "provider is configonly" once in the deck and move on.

---

## 4. Feature ③ — Citizen photo / comment verification

This is the one that closes the impact loop — and it's the most underrated of your three ideas.

### The problem it attacks

Indian public works has a **ghost asset** problem: roads and toilets that exist on paper and in the payment record but not on the ground. Departments self-certify completion. Nobody independent checks.

### The loop

```
Project marked complete by department
              │
              ▼
JanSetu pushes a VERIFICATION REQUEST to citizens in that geohash
   (SMS / WhatsApp / IVR voice blast — in their language):
   "धुले ब्लॉक में सड़क का काम पूरा हुआ? फोटो भेजें या 1/2 दबाएं"
              │
              ▼
Citizen replies with  📷 photo  ·  💬 comment  ·  👍/👎 verdict
              │
              ▼
GEMINI MULTIMODAL CHECK
   · Does the photo show the asset that was scoped?      (scope match)
   · Does it look complete, partial, or absent?          (completion 0–1)
   · Does it match the ORIGINAL complaint location?      (geohash / EXIF plausibility)
   · Is this a duplicate or brigaded submission?         (trust weight)
              │
              ▼
SOCIAL AUDIT SCORE per project = Σ(trust-weighted verdicts) / Σ(verdicts)
              │
              ├──→ < 0.5  ⟶  ⚠️ FLAGGED: payment hold, field inspection triggered
              ├──→ 0.5–0.8 ⟶  PARTIAL: punch-list issued
              └──→ > 0.8  ⟶  ✅ CERTIFIED: release final payment, close the ledger entry
              │
              ▼
IMPACT LEDGER gets REAL outcome data from citizens, not from the contractor
```

### Why this is the strongest thing in the whole build

1. **It's the honest answer to "no way to measure impact."** Not a survey. Not a consultant's report. Ground truth from the people who use the asset, timestamped and photo-evidenced.
2. **It's real anti-corruption infrastructure.** "Payment follows verified completion" is a sentence that lands hard with a policymaker.
3. **It makes the system learn.** Realization Ratios computed from citizen verification feed back into the sector weights (§4.5 of the master plan). Sectors that consistently under-deliver get repriced.
4. **It's symmetric and elegant to present:** *citizens report the problem, then citizens certify the fix.* Two-sided participation, one loop.

### Guardrails (put these on the deck — judges will probe)

- **Trust weighting**, not one-person-one-vote: repeat verified reporters, photo evidence, and geohash proximity raise weight; new/unverified/duplicate submissions lower it.
- **Brigading resistance**: log-capped counts, per-hash rate limits, dispersion checks.
- **No punitive use**: verification grades the *asset*, never the citizen. Consent + DPDP Act 2023 compliance; PII minimised at ingestion.
- **Grievance escape**: a citizen who says "not done" can escalate to the same helpline.

---

## 5. Updated pipeline — 8 layers

```
CITIZEN          📞 155XXX single helpline · missed call · SMS · USSD · WhatsApp · web · kiosk
                 hi · bn · ta · te · mr · en  +  code-mixed Hinglish  +  zero-menu voice
   ▼
⓪ ACCESS        Channel Adapter → one CitizenReport schema · Bhashini STT/TTS · language ID
   ▼
① UNDERSTAND    Gemini structured extraction → sector · severity · LGD · affected population
   ▼
② TRUST         Dedup fingerprint · corroboration ("मैं भी") · multimodal verification
   ▼
③ ROUTE  ★NEW   Department Routing Table → CPGRAMS / nodal officer · SLA clock starts · citizen ACK
   ▼
④ FUSE          Census · SECC · NFHS · PMGSY · JJM · SDG Index · Aspirational Districts → NIDI
   ▼
⑤ CLUSTER       Spatial + semantic hotspots  →  ⚖️ COVERAGE-BIAS CORRECTION
   ▼
⑥ SCORE         Deterministic 0–100 · auditable lineage · live weight sliders
   ▼
⑦ ALLOCATE  ★   ILP: maximise beneficiaries s.t. budget · scheme eligibility · sector caps
   │             · geographic spread · equity floor · SOR unit costs + efficiency–equity frontier
   ▼
⑧ MEASURE  ★↑   Pre-registered baseline → CITIZEN PHOTO/COMMENT VERIFICATION → social audit score
   │             → propensity-matched counterfactual → Realization Ratio → weight feedback
   ▼
OUTPUTS         🏛️ Policymaker console · 📱 Citizen tracking · 🔍 Auditor lineage · 🌍 BRICS console
```

**Three starred layers (③ ⑦ ⑧) are the ones no competitor has.** Lead with them.

---

## 6. Updated rubric position

| Criterion | Weight | Before | After v2 |
|---|---|---|---|
| AI / Technical Execution | 25% | Strong | **Stronger** — + multimodal completion verification, + Bhashini language DPI, + routing classifier |
| Problem–Solution Fit | 20% | Strong | **All four clauses of the brief now closed, verbatim.** |
| Depth & Reach Across India | 20% | Good | **Best-in-track** — works on a ₹1,200 keypad phone with no data plan |
| Deployability & Scalability | 20% | Strong | **Strongest** — sits on India's existing DPI bricks, routes into CPGRAMS, routing is config not code |
| Impact Potential | 15% | Good | **Transformed** — anti-ghost-asset verification + payment-linked certification |

---

## 7. Updated demo script (3–5 min)

| Time | Beat | Screen |
|---|---|---|
| **0:00–0:40** | **The missed call.** A keypad phone. No app, no data, no English. A farmer gives a missed call. 60 s later the system calls back in Marathi: *"कृपया आप अपनी समस्या बताइए."* He speaks. Transcript appears. | Simulator phone UI |
| **0:40–1:15** | **One number, zero menu.** Gemini structures it, TTS reads it back, he presses 1. Ticket created → **auto-routed to PMGSY Dhule** → Marathi SMS ack with SLA. Three more languages fire in behind it. | Routing animation |
| **1:15–1:50** | **⚖️ The bias reveal.** A noisy ward has 340 complaints; a tribal block has 14 — and higher modelled need. Correction flips the ranking live. | Before/after map |
| **1:50–2:45** | **★ The Allocator.** ₹40 Cr → portfolio. Drag to ₹12 Cr → live re-solve, equity floor protects two water schemes, solver repairs an empty block. **1,84,000 beneficiaries · ₹6,521 per beneficiary.** | Live re-solve |
| **2:45–3:25** | **★ The people audit the fix.** A completed project. Citizens get an IVR/SMS ping. Photos arrive. Gemini says *partial — 40% complete*. Social audit score 0.38 → ⚠️ payment hold. Compare with a certified one at 0.91. | Verification console |
| **3:25–3:55** | **Impact + BRICS.** Realization Ratios across sectors. Then switch nation → Brazil adapter → same pipeline, zero code change. | Ledger + nation switch |
| **3:55–4:30** | **It's a DPI.** Stack diagram on India's DPI bricks. MIT, DPDP-compliant, one-command deploy. Export the standing-committee note. | PDF note |

**Closer:** *"One number instead of forty departments. A missed call instead of a smartphone. And the people who reported the problem are the ones who certify the fix — because no one else is standing on that road."*

---

## 8. Revised scope discipline

### Build
Simulated telephony (all 6 channel types) · single-number routing brain + routing YAML · Gemini structuring + verification · missed-call/SMS/IVR adapters · citizen verification console · allocator · impact ledger · dashboard · BRICS adapters · deck + video.

### Still don't build 🚫
Real toll-free number provisioning · WhatsApp Business API approval · real CPGRAMS integration (mock the webhook, document the contract) · Aadhaar auth (design it, don't wire it) · USSD carrier gateway (simulate) · native mobile apps · custom model training · payments · i18n beyond 6 languages.

**Rule for the team: every "real integration" becomes a config flag + a documented contract + a simulator. Zero exceptions.**

---
*Next: `docs/02-TEAM-EXECUTION-PLAN.md` — who builds what, in what order, without colliding.*
