# JanSetu — Team Execution Plan
### How you and your friends actually reach the goal by 30 Sep 2026

**The single biggest risk to a student team is not difficulty. It's integration hell on day 12** — four people with four working modules that have never met. This plan is built to make that impossible.

---

## 1. The one rule that makes a 4-person team work

> **Day 1: lock the API contracts. Then everyone codes against fake data (fixtures) and never waits for anyone.**

If you take one thing from this document, take that. Every workstream below is defined by (a) the files it owns, (b) the JSON it emits, and (c) the fixtures it tests against. Nothing else. Once the contracts are in `docs/03-API-CONTRACTS.md` and committed, four people can build for four days without a single conversation about interfaces.

**Corollary:** the frontend person builds against `fixtures/*.json` from hour one, so the UI exists *before* the backend does. This is why your demo will look finished on day 10 instead of day 13.

---

## 2. The four workstreams

Pick by strength, not by friendship. One owner each — ownership means the buck stops there, not that they code alone.

| # | Workstream | Owns | Best for someone strong in | Hardness |
|---|---|---|---|---|
| **A** | **ACCESS** — channels, telephony, voice | `services/telephony/`, `services/stt/`, `routers/intake.py`, citizen portal | Backend, integrations, curious about telecom APIs | Medium |
| **B** | **INTELLIGENCE** — AI + data + scoring | `services/gemini/`, `engine/bias.py`, `engine/score.py`, `data/` fusion | Python, pandas, ML, prompt engineering | Medium-Hard |
| **C** | **ENGINE** — allocator + ledger + routing ★ | `engine/allocate.py`, `engine/impact.py`, `data/routing.yaml`, `data/schemes.yaml` | Algorithms, OR, the person who likes hard problems | **Hardest — and it's the hero** |
| **D** | **CONSOLE + STORY** — UI, deck, video, deploy | `frontend/`, `adapters/`, pitch deck, demo video, README | React, design, and whoever can talk | Medium but relentless |

### ⚠️ Two warnings

1. **Give workstream C to your strongest builder.** It's the only thing in this project nobody else in the competition has. Everything else is table stakes. If C fails, you have a nice dashboard that ranks complaints — which is what everyone else built.
2. **D is not "the presentation person who starts on day 11."** D builds against fixtures from day 1 and owns the demo path. In a hackathon, a working demo that runs is worth more than a working feature nobody sees.

---

## 3. Team-size fallbacks

### 👥 4 people — ideal
One owner per workstream: **A · B · C · D**.

### 👥 3 people
Merge **B + C → "ENGINE"** (Gemini, scoring, allocator, ledger all live in one head — they're tightly coupled anyway). Keep A and D separate.
> Engine (hardest, ~55% of the technical risk) · Access · Console+Story

### 👥 2 people
Split **vertical**, not horizontal:
- **P1 — Engine:** B + C (Gemini, data fusion, scoring, allocator, ledger, routing) → FastAPI
- **P2 — Access + Console:** A + D (channels, simulator, citizen portal, dashboard, deck, video)

P2 is deceptively large. If you're two people, cut to: **missed-call + SMS + web only** (drop USSD and kiosk), and one map view instead of four.

### 👤 Solo
Build the vertical slice only: `intake (simulated SMS + voice) → Gemini structure → score → ★ allocate → dashboard`. Then the deck. Accept that impact ledger and BRICS get seeded/faked with pre-computed results. Still beats most entries, because the allocator alone is the differentiator.

---

## 4. The shared contracts — commit these on Day 1

Full schemas live in `docs/03-API-CONTRACTS.md`. The five objects that matter:

| Object | Produced by | Consumed by | One-line meaning |
|---|---|---|---|
| `CitizenReport` | **A** | B, C | One normalised citizen complaint, whatever channel it arrived on |
| `Hotspot` | **B** | C, D | A clustered, scored, bias-corrected demand hotspot |
| `ProjectCandidate` | **C** | C, D | A costed, scheme-eligible intervention that could be funded |
| `Portfolio` | **C** | D | The chosen set + totals + why everything else was dropped |
| `VerificationEvent` | **A** | B, C | A citizen's photo/comment verdict on a completed project |

**A → B → C → D is a straight line. Nobody has a circular dependency. That's deliberate.** The only back-edge is `VerificationEvent` (A → C) at layer ⑧, and it arrives late by design — C must work before the verification flow exists.

### Endpoint contract (FastAPI, `backend/app/main.py`)

| Method | Path | Owner | Notes |
|---|---|---|---|
| `GET` | `/health` | any | Day-0 exit test |
| `POST` | `/api/v1/intake/` | A | Accepts any channel payload → `CitizenReport` |
| `POST` | `/api/v1/intake/simulate` | A | Simulator: fake a missed call / SMS / voice in-browser |
| `GET` | `/api/v1/reports/` | A | List + filter |
| `GET` | `/api/v1/track/{ticket_id}` | A | Citizen status lookup |
| `POST` | `/api/v1/verify/` | A | Citizen photo/comment verification |
| `GET` | `/api/v1/hotspots/` | B | Geo + filters → scored hotspots |
| `GET` | `/api/v1/hotspots/{id}/lineage` | B | Auditor view: full score provenance |
| `POST` | `/api/v1/score/recompute` | B | Live weight sliders |
| `POST` | `/api/v1/allocate/` | C | **The hero endpoint.** Budget + constraints → `Portfolio` |
| `GET` | `/api/v1/frontier/` | C | Efficiency–equity frontier points |
| `GET` | `/api/v1/impact/` | C | Impact ledger + Realization Ratios |
| `GET` | `/api/v1/routing/table` | C | Department routing table |
| `GET` | `/api/v1/adapters/` | D | List nation adapters |
| `POST` | `/api/v1/brief/` | B | Gemini policy brief / committee note |

---

## 5. The 13-day parallel schedule

Two **hard integration windows** — everyone stops, merges to `main`, and runs the end-to-end together. Non-negotiable.

| Day | 🎯 **A · Access** | 🎯 **B · Intelligence** | 🎯 **C · Engine** | 🎯 **D · Console + Story** | ✅ Team exit test |
|---|---|---|---|---|---|
| **0 · 17 Sep** | Repo, venv, `.env`, FastAPI skeleton | Repo, Gemini client + offline fallback | Repo, PuLP installed, toy knapsack solves | Vite + React + TS scaffold, MapLibre hello-world | `curl /health` green · contracts committed |
| **1** | `TelephonyProvider` ABC + simulator shell | Gemini structured output + JSON schema + 8-lang fixtures | `ProjectCandidate` + `SOR` cost model + `schemes.yaml` | Dashboard shell + layout, reads `fixtures/hotspots.json` | **🔒 CONTRACTS LOCKED** |
| **2** | Missed-call + SMS adapters | Language detect + normalisation + translation | Greedy allocator baseline (before ILP) | Hotspot table + score-breakdown component | B structures a Marathi SMS correctly |
| **3** | Voice/IVR adapter + STT wiring (Bhashini→Sarvam→Google) | Dedup fingerprint + embedding fallback | **ILP: budget + sector caps** (PuLP/CBC) | Map: heatmap + drill-down | Voice → correct LGD code |
| **4** | TTS readback + DTMF confirm flow | Hotspot clustering (spatial + semantic) | + geographic spread + equity floor constraints | Allocator workbench UI + budget slider | **🔗 INTEGRATION WINDOW 1** — intake → structure → hotspot → score → allocate, end to end |
| **5** | Citizen tracking portal + SMS ack | **⚖️ Coverage-bias correction** (reporting-rate model) | Infeasibility handling + `--fast` greedy/2-opt path | Portfolio view + "why was this dropped?" | ⚖️ **Silent block outranks noisy ward** |
| **6** | Verification intake (photo upload) | Data fusion: census/SECC/NFHS CSVs | **Department Routing Table** + SLA engine + CPGRAMS mock | BRICS adapter console + `india.yaml` | A complaint routes to the right dept |
| **7** | WhatsApp adapter (simulated) + `STATUS <id>` SMS | **NIDI** deficit index | Scheme eligibility rules engine | Efficiency–equity frontier chart | NIDI reproducible from source rows |
| **8** | USSD + kiosk offline sync (stretch) | Scoring engine v1 + lineage store | **Impact ledger**: baselines + Realization Ratio | Auditor lineage view | **🔗 INTEGRATION WINDOW 2** — full loop incl. routing + ledger |
| **9** | All 6 channels demoable in simulator | Gemini multimodal verification of photos | Propensity matching for counterfactuals | Gemini brief UI + standing-committee note export | Photo verification returns a verdict |
| **10** | Polish citizen portal | Gemini policy brief generation | Weight feedback loop (learned sector weights) | 🎬 **Full demo path works end to end** | 3 dry runs of the demo, under 5 min |
| **11** | Seed data: 100 multilingual reports, 5 states | Seed data: BRICS indices for 4 nations | Seed: 12 completed projects w/ verification histories | 🎥 **Record the 3–5 min demo video** | ⛔ **FEATURE FREEZE** |
| **12** | Deploy: Docker + Cloud Run/Render | `PROVENANCE.md` + data licences | Performance: slider re-solve budget < 400 ms | 🖼️ Pitch deck 10–12 slides | **Live URL in README** |
| **13 · 30 Sep** | Bugfix only | Bugfix only | Bugfix only | README, submission form, zip | 📦 **SUBMIT** |

### Cadence
- **10-min standup, same time daily:** what I finished · what I'm blocked on · what I'll ship today. Blocks get raised immediately, not at day's end.
- **Merge to `main` every evening.** If it breaks `main`, you fix it before you sleep. No long-lived branches.
- **Days 12–13 are deck, video, and bugs. No new features.** Write this on the wall.

---

## 6. Git workflow

```
main          ← always demoable. Protected. Never broken overnight.
feature/A-*   ← workstream branches
feature/B-*
feature/C-*
feature/D-*
```

- Branch off `main` each morning, rebase each evening, merge before you sleep.
- **Conflicts are almost impossible if workstreams respect their file ownership.** The only shared file is `docs/03-API-CONTRACTS.md` — changes to it require a message in the group chat.
- Commit messages: `feat(C): equity floor constraint`, `fix(B): marathi transliteration`.
- **Commit history is your proof against the "pre-existing project" rule.** Commit from day 0, every day, from every member. Screenshots of early commits are legitimate evidence if questioned.

### File ownership — stay in your lane
| Path | Owner | Touch only with permission |
|---|---|---|
| `backend/services/telephony/`, `services/stt/`, `routers/intake.py` | **A** | — |
| `backend/services/gemini/`, `engine/bias.py`, `engine/score.py`, `data/` | **B** | — |
| `backend/engine/allocate.py`, `engine/impact.py`, `data/routing.yaml`, `data/schemes.yaml` | **C** | — |
| `frontend/`, `adapters/`, `docs/pitch/` | **D** | — |
| `docs/03-API-CONTRACTS.md` | **everyone** | ⚠️ announce changes |

---

## 7. Definition of Done — per workstream

Not "I wrote the code." **"It works and someone else can run it."**

**A · Access**
- [ ] All 6 channels (missed call, voice, SMS, IVR, WhatsApp, kiosk) demoable in the simulator
- [ ] Regional-language TTS readback + DTMF confirmation works
- [ ] `TELEPHONY_PROVIDER=simulator` is the default; swapping providers is one env var
- [ ] Photo upload + comment submission works
- [ ] Ticket ID issued; `STATUS <id>` returns the right stage

**B · Intelligence**
- [ ] Structured JSON extraction works for hi · mr · bn · ta · te · en **and offline (fallback) mode**
- [ ] 8-language test suite passes with no API key present
- [ ] Bias correction demonstrably flips a silent block above a noisy ward
- [ ] Every score has retrievable lineage to source rows
- [ ] Gemini never computes a number — verify by code review

**C · Engine ★**
- [ ] ILP solves with budget + sector caps + spread + equity floor
- [ ] Re-solve on slider drag < 400 ms
- [ ] Infeasible cases are surfaced with a reason, never silently dropped
- [ ] Efficiency–equity frontier returns real points
- [ ] Routing table is YAML, not code; adding a department needs no code change
- [ ] Impact ledger computes a Realization Ratio on seeded data

**D · Console + Story**
- [ ] Dashboard: map, hotspot table, allocator workbench, BRICS switch — all fed by real API
- [ ] Demo runs end-to-end, 3 dry runs, under 5 min, no crashes
- [ ] Video recorded, audio clean, screen readable on a phone
- [ ] Deck 10–12 slides; README has the live URL and a 60-second quickstart
- [ ] Deployed and reachable from a fresh browser

---

## 8. Risk register — with owners

| Risk | Likelihood | Impact | Owner | Mitigation |
|---|---|---|---|---|
| **Integration hell on day 12** | **High** | **Fatal** | All | Contracts day 1 · fixtures · 2 integration windows · merge daily |
| Gemini rate limits mid-demo | High | High | **B** | Deterministic fallback + response cache; run the demo on cached fixtures |
| Allocator ILP too slow | Medium | High | **C** | Greedy/2-opt `--fast` path; solve per-district then aggregate |
| No toll-free number / CPaaS KYC | **Certain** | Medium | **A** | Simulator is default; provider is config-only. Already designed for this. |
| No live government APIs | Certain | Medium | **B** | Cached snapshots + `PROVENANCE.md` — the brief explicitly permits realistic data |
| Someone disappears for 3 days | Medium | High | All | Every workstream has a **minimum viable version** defined by day 8. If C stalls, a greedy allocator still ships. |
| Demo machine / network dies | Medium | Fatal | **D** | Recorded video as backup · Docker image · seeded local DB · `main` always demoable |
| Scope creep from good ideas | **High** | High | All | The kill list in `docs/01-SOLUTION-v2.md` §8 is binding. New ideas go in a `PARKING.md`, not the build. |
| Judges challenge the bias model | Medium | Medium | **B** | Show the model, the coefficients, and the before/after. Honesty about limitations beats false confidence. |

---

## 9. Submission checklist — 30 Sep 2026

Official requirements from the hackathon page:

- [ ] **1 · Source code** — public GitHub repo (or access granted to `build-with-ai-india@googlegroups.com`)
- [ ] **2 · Demo video (3–5 min)** — working end-to-end walkthrough
- [ ] **3 · Pitch deck (10–12 slides)** — problem, solution, AI approach, who it serves, why deployable, how it scales
- [ ] **4 · Brief description** — 2–3 lines
- [ ] **5 · Deployed link** — live prototype URL
- [ ] **6 · Google AI integration** — mandatory, and visibly load-bearing (our §6 surface map)
- [ ] `PROVENANCE.md` — every dataset, its licence, its snapshot date
- [ ] `README.md` — 60-second quickstart, architecture diagram, live URL
- [ ] `LICENSE` — MIT (Digital Public Good)

### The 2–3 line description (draft, ready to paste)

> **JanSetu (जनसेतु)** turns fragmented citizen voice — via a single toll-free number, missed call, or SMS on any handset, in any Indian language — into a costed, scheme-compliant public investment portfolio. A Gemini-powered routing brain sends each complaint to the right department, a bias-correction model ensures under-connected communities aren't drowned out, and an optimiser allocates a fixed budget to maximise beneficiaries per rupee under equity and geographic-spread constraints. Citizens then photograph and certify the finished work, giving government an audited impact ledger instead of self-reported completion.

---

## 10. What to do in the next 60 minutes

1. **Count your team.** Assign A/B/C/D using §2. Give C to your strongest builder.
2. **One person creates the GitHub repo** and invites the others. Add the group as collaborators — you want commit history from every member from day 0.
3. **Everyone clones and runs `curl localhost:8000/health`** before the session ends.
4. **Read `docs/03-API-CONTRACTS.md` together** and argue about it *now*, not on day 9.
5. **Set the daily standup time** and put the integration windows (Day 4, Day 8) and the freeze (Day 11) in a shared calendar.
6. **Start a `PARKING.md`.** Every new idea goes there. It's the highest-value file in the repo — it stops good ideas from killing the build.

---
*Next: `docs/03-API-CONTRACTS.md` — the JSON schemas that let four people build without talking.*
