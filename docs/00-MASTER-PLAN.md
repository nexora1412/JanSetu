# LokNivesh (लोकनिवेश) — Master Plan
### *Track 01 · AI for Digital Public Infrastructure & Governance · BRICS Theme: Innovation*
**Build with AI: Code for Communities — Second Edition** (Google Cloud × Hack2Skill)

> ## 📌 v2 — read these first
> This document is the **concept + strategy**. Three features were added in v2 and the pipeline grew from 7 → 8 layers:
> ① **Single helpline number** (one number, all departments, zero IVR menu) · ② **Feature-phone access** (missed call · SMS · IVR · USSD · kiosk) · ③ **Citizen photo/comment verification** feeding the Impact Ledger.
>
> | Go to | For |
> |---|---|
> | **`docs/01-SOLUTION-v2.md`** | The three new features, the updated 8-layer pipeline, telephony strategy |
> | **`docs/02-TEAM-EXECUTION-PLAN.md`** | Workstreams, the parallel 13-day schedule, git, Definition of Done |
> | **`docs/03-API-CONTRACTS.md`** | The JSON schemas that let the team build without blocking each other |
>
> §§ 5–7 and 9 below remain authoritative. §3 (pipeline) and §11 (demo) are superseded by `01-SOLUTION-v2.md`.

> **One-line positioning:**
> Every other entry in this track **ranks complaints**. LokNivesh **allocates the budget**.
> *From citizen voice → verified demand → a costed, scheme-compliant, equity-constrained project portfolio → a measured outcome.*

- **Deadline:** 30 Sep 2026 (prototype submission) · 13 days from today
- **Top 20 shortlist:** 16 Oct 2026 · **Virtual Demo Day:** 23 Oct 2026
- **Stack:** Python (FastAPI) + React/Vite/TS · Gemini API (key already in hand)
- **Track page:** https://hack2skill.com/event/codeforcommunities2

---

## 1. What actually won last year — and why

Last year's edition pulled **7,000+ developers → 1,000+ projects**; 12 teams pitched at the Parliamentary Showcase in New Delhi (22 Jul 2026). Winners move into **real constituency pilots** — that's the prize that matters more than the ₹10L.

### Track 01 (our track) — the two that placed

| | **Praja Svaram** — Team Tech Jays (WINNER) | **Civic Pulse** (RUNNER-UP) |
|---|---|---|
| Core move | Voice-first grievance intake: WhatsApp + phone call | Text + voice + photo in Indic languages |
| AI | Classification, verification, language handling | Classification → demand hotspot clustering |
| Output | Analytics dashboard **for the MP** | Ranked demand hotspots |

### Also ran (public repos, useful intel — we can see their whole playbook)

| Project | Stack | Their angle |
|---|---|---|
| **CommonGround** (CivicPulse repo) | FastAPI + React 19 + MapLibre + PostGIS | Sarvam STT → Gemini verification gate → spatial clustering → **deterministic 0–100 score** → Gemini policy briefs |
| **NirmanVaani** | Vite/React + Gemini | Gemini structuring pipeline → grounded in data.gov.in → **explainable priority scoring** + weight sliders + ticket tracking |
| **NagarVaani** | Next.js + Firestore + deck.gl | Google Maps heatmap + BRICS comparison table + AI priority rankings |

### The five patterns every winner shares (steal all of them)

1. **Voice-first, not form-first.** Bharat speaks; it doesn't fill forms. Praja Svaram won on this alone.
2. **Structured extraction, not free chat.** Gemini emits strict JSON (language, sector, urgency, geo-entity).
3. **Deterministic scoring + Gemini reasoning.** Winners' own repos say it: *"mathematical formula that eliminates LLM numerical hallucinations."* Never let the LLM compute the score — let it explain a score.
4. **Cluster into hotspots.** Individual complaints are noise; hotspots are policy.
5. **One clear primary user.** Praja Svaram picked the **MP** and built everything for them.

---

## 2. The gap: what nobody built

Five openings, ranked by how much they'd move a judge.

| # | Gap | Why it's the winning hole |
|---|---|---|
| **1** | **No one touches the money.** Every project ends at "here are the top 10 problems." Not one takes a budget envelope and returns an optimal, scheme-eligible **portfolio of funded projects**. | The problem statement's first sentence is *"misaligned public spending."* That's the actual ask. Ranking is half an answer. |
| **2** | **No impact measurement.** Zero entries answer the brief's *"no way to measure the impact of large-scale DPI initiatives."* | It's an explicit clause of the problem statement — free marks, untouched. |
| **3** | **No bias correction.** Digital intake systematically over-samples the literate, male, urban, connected. Every existing tool therefore tells ministries to pave the wards that already tweet. | Turns the obvious critique of our own category into our flagship feature. Judges *will* ask "how do you handle reporting bias?" |
| **4** | **BRICS is a static table.** NagarVaani's is a comparison view; everyone else says "it could scale." | Rule 04 of the hackathon: *designed with cross-border applicability.* Make portability **architectural and demonstrable**, not a claim. |
| **5** | **No government-system grounding.** No LGD codes, no scheme eligibility rules, no Schedule of Rates unit costs. | This is the whole of **Deployability (20%)** — the difference between "cool dashboard" and "ministry pilot." |

---

## 3. The concept

# LokNivesh — लोकनिवेश
**"The public investment intelligence layer."**
A Digital Public Good that turns fragmented citizen voice into a **costed, auditable, budget-optimal public investment portfolio** — and then measures whether it worked.

### The hero moment for the demo
> A policymaker drags the budget slider from ₹40 Cr to ₹12 Cr.
> The map re-solves live. Three road projects drop out, two water schemes are protected by the equity floor, one block would be left empty — so the solver swaps in a cheaper sanitation package to keep the geographic-spread constraint satisfied.
> Total expected beneficiaries: **1,84,000**. Cost per beneficiary: **₹6,521**.
> Click **"Generate Note for Standing Committee"** → Gemini drafts the two-page justification with scheme citations.

**No other team can show that. It is the "so what?" of the entire track.**

### Name options
1. **LokNivesh (लोकनिवेश)** — *public investment* ← recommended; names the actual object
2. **NirmanSetu (निर्माणसेतु)** — bridge from voice to construction
3. **JanNivesh / NyayaNivesh** — *just investment*

### The pipeline

```
CITIZEN          WhatsApp · SMS · Voice call · Web · Field kiosk (offline sync)
   │              hi · bn · ta · te · mr · en + code-mixed Hinglish
   ▼
① UNDERSTAND     STT (Chirp/Sarvam) → Gemini structured extraction → LGD geo-resolution
   ▼
② TRUST          Dedup fingerprint (embedding + geohash) · corroboration · multimodal verification
   ▼
③ FUSE           Census · SECC · NFHS · PMGSY · JJM · SDG Index · Aspirational Districts · MPLADS
   ▼              → National Infrastructure Deficit Index (NIDI) per admin unit × sector
   ▼
④ CLUSTER        Spatial + semantic hotspots   →   ⚖️ COVERAGE-BIAS CORRECTION
   ▼
⑤ SCORE          Deterministic 0–100 (transparent, slidable weights — no LLM math)
   ▼
⑥ ALLOCATE  ★    ILP: maximise beneficiaries subject to budget · scheme eligibility
   │              · sector caps · geographic spread · equity floor · SOR unit costs
   ▼
⑦ MEASURE        Pre-registered baseline → counterfactual match → Realization Ratio → weight feedback
   ▼
OUTPUTS          MP/DM console · Citizen tracking portal · Auditor lineage view · BRICS adapter console
```

---

## 4. The intelligence layer — the actual math

### 4.1 Demand signal (per hotspot *h*, sector *s*)

```
R_h = Σ_i  exp(−Δt_i / 180d) · v_i            # recency-weighted verified reports
M_h = min(1, log(1 + me_too_h) / log(1 + 200)) # corroboration, log-capped vs brigading
Demand_h = 0.75·norm(R_h) + 0.25·M_h
```

### 4.2 ⚖️ Coverage-bias correction — *the novel bit*

Digital intake is not a random sample of need. We model **reporting propensity** from census
features (literacy, female literacy, SC/ST share, urban/rural, phone/Net penetration) and reweight:

```
Ē_h  = expected report volume from a fitted reporting-rate model (Poisson / GLM on census covariates)
O_h  = observed report volume
c_h  = clip( Ē_h / max(O_h, ε), 0.50, 3.00 )     # under-reporting units get boosted, capped
AdjustedDemand_h = Demand_h · c_h
```

A silent, low-literacy, poorly-connected block with 12 complaints can outrank a connected
ward with 300. **This is the slide that wins the Impact and Reach criteria** — and it's the
honest answer to "your data is biased."

### 4.3 Priority score (deterministic, 0–100)

```
P = 100 · ( 0.30·Demand* + 0.25·Deficit + 0.20·Reach + 0.15·Equity + 0.10·Feasibility ) · (1 − Saturation)
                                                                        *Demand* = bias-corrected
```
- **Deficit** — NIDI(z) per sector, normalised within state
- **Reach** — population served, log-scaled, weighted for vulnerable groups
- **Equity** — deprivation (SECC/NFHS), Aspirational-District flag, gender-access gap
- **Feasibility** — land availability, implementing agency capacity, scheme readiness, lead time
- **Saturation** — spend already committed here (prevents double-funding winners)

Every component is stored and displayed. **Auditable lineage** = any score can be drilled to source rows.

### 4.4 ★ The Allocator — constrained portfolio optimisation

```
maximise   Σ_j  x_j · B_j                where  B_j = P_j · beneficiaries_j · cost_efficiency_j
subject to
   Σ_j x_j · cost_j                ≤  Budget                                    # envelope
   Σ_{j∈s} x_j · cost_j            ≤  cap_s · Budget          ∀ sector s        # no monoculture
   Σ_{j∈b} x_j                     ≥  1                       ∀ block b         # geographic spread
   Σ_{j∈E} x_j · cost_j            ≥  equity_floor · Budget                     # E = high-deprivation
   x_j ∈ {0,1}                                                                  # indivisible projects
   mutually-exclusive groups:  Σ_{j∈G} x_j ≤ 1
```
Solver: **PuLP + CBC** (exact at district scale). Greedy + 2-opt local search as the
`--fast` path for national scale. **Infeasibility is surfaced, never hidden** — if the equity
floor and the spread constraint can't both hold, the UI says so and shows the trade-off curve
(**efficiency–equity frontier**: an entire extra slide of insight for free).

### 4.5 Impact ledger — measuring the DPI itself

```
per approved project j:
  pre-register   baseline KPI + predicted outcome Ô_j  (sector-specific: travel minutes,
                 households with tap connection, outpatients served, classrooms, Mbps)
  at completion  Δ = observed − baseline
  counterfactual match untreated geohashes on census covariates (propensity score) → Δ_control
  Realization Ratio  ρ_j = (Δ_treated − Δ_control) / Ô_j

feedback loop:  w_s ← w_s · (1 + η · (mean ρ_s − 1))     # sectors that over/under-deliver self-correct
```

This closes the loop the problem statement says is missing, and gives us a **genuinely
learning system** rather than a static ranker.

---

## 5. Data sources — real, free, citable

| Layer | Source | Use |
|---|---|---|
| Demography | **Census 2011** (data.gov.in), **SECC 2011** | Population, literacy, deprivation, SC/ST |
| Health / education | **NFHS-5**, **NAS**, UDISE+ | Vulnerability, school infra deficit |
| Roads | **PMGSY** e-Marg / OMMAS | Road connectivity deficit |
| Water | **Jal Jeevan Mission** dashboard | FHTC coverage gap |
| Sanitation / urban | **SBM-G**, **AMRUT 2.0**, **SBM-U 2.0** | Toilets, urban infra |
| Admin boundaries | **LGD (Local Government Directory)** ⭐, Survey of India | Canonical state→district→block→GP codes |
| Planning | **NITI Aayog SDG India Index**, **Aspirational Districts**, **15th FC grants**, **MPLADS** | Equity weights, budget envelopes |
| Digital divide | **BharatNet**, TRAI subscriber data | Reporting-rate model features |
| Unit costs | **CPWD/State Schedule of Rates**, PMGSY & JJM unit costs | Real ₹ per project |
| BRICS | **World Bank WDI**, **UN SDG**, **WHO**, **ITU** | The 5-nation adapter demo |

Everything lands in a `data/` snapshot with a `PROVENANCE.md` — dated, licensed, and honest
about being cached where a live API isn't available (the brief explicitly permits this).

---

## 6. Google AI surface map (mandatory, and genuinely load-bearing)

| Google AI capability | Job | Fallback if it fails |
|---|---|---|
| **Gemini — structured JSON output** | Normalise code-mixed text; extract sector, asset, severity, geo-entity, affected population | Keyword + transliteration heuristic |
| **Gemini multimodal** | Photo verification (is this really a broken culvert?), damage severity | Skip; lower evidence weight |
| **Gemini embeddings** | Dedup fingerprinting + semantic clustering | TF-IDF + cosine |
| **Gemini generation** | Policy briefs, citizen replies in their own language, standing-committee notes | Templated text |
| **Cloud Speech-to-Text (Chirp)** | Indic voice intake | Web Speech API / Sarvam |
| **Cloud Translation** | Bulk translation; Gemini handles semantic normalisation | Indic-transliteration map |
| **BigQuery / BQ ML** | National-scale fusion, reporting-rate GLM, propensity matching | SQLite + scikit-learn (dev parity) |
| **Vertex AI** | Model serving for the scoring/deficit models | In-process Python |

**Rule we never break:** the LLM explains and structures; it **never** computes a score.
Every number on screen is reproducible from stored inputs. This is exactly what the winners
did right, and it makes the auditor view honest.

---

## 7. Scoring against the official rubric

| Criterion | Weight | How LokNivesh scores |
|---|---|---|
| **AI / Technical Execution** | **25%** | Gemini does real work across 5 surfaces, *and* we add genuine OR (ILP), a bias-correction GLM, and counterfactual evaluation. Structured output + fallbacks everywhere; it demos even with the network down. |
| **Problem–Solution Fit** | **20%** | Directly answers all four clauses: consolidate feedback ✔, align with national priorities ✔, *misaligned spending* → the Allocator ✔, *measure DPI impact* → the Impact Ledger ✔. |
| **Depth & Reach Across India** | **20%** | LGD-coded so it drops into any state. Offline field-kiosk sync + voice + missed-call for low-connectivity Bharat. Bias correction means it works *for* the unconnected, not just the online. |
| **Deployability & Scalability** | **20%** | Ships as a **DPI**: modular, open APIs, registry-based (LGD), DPDP-Act-2023 privacy design, MIT-licensed, one-command Docker/Cloud Run. Outputs land in formats ministries already use. |
| **Impact Potential** | **15%** | Optimises *beneficiaries per rupee*, not complaint volume. Equity floor + frontier curve make the distributional consequence explicit rather than accidental. |

---

## 8. Interfaces (three users, one system)

**🏛️ Policymaker console** (primary — the Praja Svaram lesson: pick one user)
- India drill-down map: nation → state → district → block, MapLibre + deck.gl heatmap
- Hotspot table with score breakdown + **live weight sliders**
- **★ Budget Allocator workbench** — envelope, sector caps, equity floor, spread constraint → live re-solve → portfolio + ₹ + beneficiaries + cost/beneficiary
- Efficiency–equity frontier curve; "why was this dropped?" explainer
- Gemini: policy brief, standing-committee note, citizen reply — one click
- **BRICS portability console**: switch nation → entire pipeline runs on that nation's adapter

**📱 Citizen portal**
- Voice/text/photo filing in their language; WhatsApp fallback
- Token-based status tracking (4-stage lifecycle); **"मैं भी" (Me Too)** corroboration

**🔍 Auditor / transparency view**
- Full lineage: every score → inputs, weights, data provenance, model version
- Public aggregate API → civic-tech reuse (the DPI promise made real)

---

## 9. The BRICS story — make it architectural, not aspirational

Not a comparison table. A **portability proof**.

```
adapters/
  india.yaml          # LGD hierarchy, 22 langs, schemes: PMGSY/JJM/AMRUT..., SOR costs
  brazil.yaml         # IBGE codes, pt-BR, PAC/PPA programmes
  russia.yaml         # OKTMO codes, ru, national projects
  china.yaml          # GB/T codes, zh, five-year plan categories
  south_africa.yaml   # Stats SA / municipal codes, en/zu/af, MIG/USDG grants
```

**Onboarding a new nation = 1 adapter YAML + 1 index CSV. Zero code change.**
The demo shows the *same* pipeline running on India (real data) and Brazil (seeded) with the
same allocator, then adds a 6th nation live in ~30 seconds. That's the Digital-Public-Good
claim, demonstrated rather than asserted — and Rule 04 asks for exactly this.

---

## 10. 13-day build plan (17 → 30 Sep 2026)

| Day | Deliverable | Exit test |
|---|---|---|
| **0 · today** | Approve concept. Repo + `.env` w/ Gemini key. Pin model IDs (verify current Flash ID in AI Studio — recent teams referenced `gemini-3.x-flash`). | `curl /health` green |
| **1–2** | FastAPI skeleton, LGD district seed, Gemini client + offline fallback, pytest harness | 8-language structuring test passes offline |
| **3–4** | Intake API (text + voice upload), structuring pipeline, dedup, verification gate | Marathi/Hindi/Bengali voice → correct LGD code |
| **5** | Hotspot clustering + **coverage-bias correction** | Silent block outranks noisy ward |
| **6–7** | Data fusion CSVs → **NIDI** deficit index → scoring engine | Score lineage reproducible from inputs |
| **8–9** | ★ **Allocator**: PuLP/CBC ILP, scheme rules, sector caps, spread, equity floor | Slider re-solve < 400 ms |
| **10** | React dashboard: map, hotspot table, allocator workbench, BRICS view | Full demo path works end-to-end |
| **11** | Impact ledger + citizen tracking portal + Gemini briefs | Realization ratio computes on seeded data |
| **12** | Seed 100 multilingual complaints (5 states + 5 BRICS). Deploy Cloud Run/Render. Record 3–5 min video. | Live URL in README |
| **13** | Pitch deck (10–12), README, PROVENANCE.md, buffer | Submission package zipped |

### Scope discipline — the kill list 🚫
Build none of this: real WhatsApp Business API (simulate the webhook — no number, no time),
auth/RBAC beyond a demo switch, native mobile apps, real-time streaming, custom model
training, payments, multi-tenancy, i18n beyond 6 languages, IVR telephony.
**Depth on the allocator beats breadth on channels. Every time.**

### Top risks
| Risk | Mitigation |
|---|---|
| Gemini rate limits mid-demo | Deterministic fallback + response cache; demo runs on cached fixtures |
| No live gov APIs / stale data | Cached snapshots + explicit `PROVENANCE.md` (the brief permits realistic data) |
| ILP too slow at national scale | Greedy + 2-opt `--fast` path; solve per-district and aggregate |
| Solo bandwidth | Ship the vertical slice: intake → score → **allocate** → dashboard. Everything else is polish. |
| "Pre-existing project" rule | Build entirely inside the window; commit history is the proof |

---

## 11. Demo script — 3–5 min (built for the 23 Oct virtual round)

| Time | Beat | What's on screen |
|---|---|---|
| 0:00–0:30 | **The problem, lived.** A farmer in Dhule speaks Marathi into a phone about a broken approach road. No form. No English. | Raw voice → live transcript |
| 0:30–1:10 | **Understanding.** Gemini structures it: sector, severity, LGD code, affected population, translation. Then 3 more languages fire in. | JSON structuring panel |
| 1:10–1:50 | **The bias reveal.** A dense noisy ward has 340 complaints; a scattered tribal block has 14 — and higher modelled need. Show the correction flip it. | Before/after map ⚖️ |
| 1:50–2:50 | **★ The Allocator.** ₹40 Cr → hotpots → portfolio. Drag to ₹12 Cr. Watch the solver re-optimise, protect the equity floor, repair a geographic gap. Portfolio: cost, beneficiaries, ₹/beneficiary. | Live re-solve |
| 2:50–3:40 | **Impact + BRICS.** Impact ledger: predicted vs realised, counterfactual lift. Then switch nation → same pipeline, Brazil adapter, zero code change. | Ledger + nation switch |
| 3:40–4:30 | **It's a DPI.** Architecture, LGD-native, DPDP-compliant, MIT, one-command deploy. Export standing-committee note with scheme citations. | PDF note |

**The one-line closer:** *"We're not building a better complaint box. We're building the layer
that decides what the complaint box was always trying to tell us — and then proves whether it worked."*

---

## 12. Pitch deck — 10–12 slides

1. Title — LokNivesh लोकनिवेश · Track 01
2. Problem — the four clauses; ₹ spent vs need unmet
3. Why current systems fail — the bias diagram (loud ≠ needy)
4. Solution — the 7-layer pipeline
5. **★ The Allocator** — the money slide (before/after portfolio)
6. ⚖️ Coverage-bias correction — the trust slide
7. Impact ledger — measuring the DPI itself
8. AI architecture + Google AI surface map
9. Depth & reach — LGD-native, voice-first, offline kiosk
10. BRICS portability — 1 YAML per nation
11. Deployability — DPI principles, DPDP, MIT, Cloud Run, pilot ready
12. Impact & ask — beneficiaries per rupee; the constituency pilot

---

## 13. Immediate next step (say the word)

I'll scaffold the repo and build **Day 0–2** now:

```
loknivesh/
├── backend/          FastAPI · app/, services/ (gemini, stt, geo), engine/ (score, allocate, bias)
├── frontend/         React + Vite + TS · MapLibre + deck.gl
├── data/             census, indices, seeds, PROVENANCE.md
├── adapters/         india.yaml, br.yaml, ru.yaml, cn.yaml, za.yaml
├── tests/            structuring, scoring, allocator (incl. ILP feasibility cases)
└── docs/             00-MASTER-PLAN.md (this file), ARCHITECTURE.md, DEMO-SCRIPT.md
```

Set up venv + FastAPI skeleton, LGD district seed, Gemini client with offline fallback, and
the 8-language structuring test suite. Then we build the allocator — the thing nobody else has.

---
*Licence: MIT · Built as a Digital Public Good · Data: public sources, `PROVENANCE.md`*
