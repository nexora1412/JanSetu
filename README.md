# JanSetu (जनसेतु) — Public Investment Intelligence

**🔗 Live demo:** _add your Cloud Run / Render URL here on Day 8_ — the citizen
app lives at **`<your-url>/app`** (installable PWA), the policymaker dashboard at **`/`**.

**Track 01 · AI for Digital Public Infrastructure & Governance · BRICS Theme: Innovation**
Build with AI: Code for Communities — Second Edition (Google Cloud × Hack2Skill)

> Every other entry in this track **ranks complaints**. JanSetu **allocates the budget**.
> *From citizen voice → verified demand → a costed, scheme-compliant, equity-constrained project portfolio → a measured outcome.*

---

## 60-second quickstart

```bash
cd jansetu
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

python3 data/generate_seed.py        # deterministic seed data (48 blocks, 5 states)
cd backend && python3 generate_fixtures.py   # fixtures so every workstream can start

cp .env.example .env                 # add your GEMINI_API_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** → dashboard · **http://localhost:8000/app** → citizen
mobile app · **http://localhost:8000/docs** → interactive API.

**It runs with no API key.** Every Gemini call degrades to a deterministic fallback, so the
demo survives a dead network on judging day.

### Citizen mobile app (PWA)

The citizen experience is a React + Vite **progressive web app** in `frontend/`:
report by voice or text in मराठी / हिंदी / English, track the ticket, photograph and
certify completed work, and trigger the missed-call callback. It installs to the
home screen, works offline (reports queue on-device and sync when connectivity
returns), and is served by the same FastAPI process at `/app` — one deploy, no
app store.

```bash
cd frontend
npm ci
npm run dev        # http://localhost:5173/app  (proxies /api to :8000)
npm run build      # outputs frontend/dist, served by FastAPI at /app
```

`frontend/dist` is committed so a fresh clone serves the app with zero Node setup.

---

## The one-paragraph pitch

A citizen gives a missed call from a ₹1,200 keypad phone. No app, no data, no English, no
IVR menu. The system rings back in Marathi, she speaks, and Gemini structures the complaint
into sector, severity and an LGD location code — then routes it to PMGSY instead of making
her guess which of forty departments owns her road. Thousands of such reports cluster into
demand hotspots, and a **coverage-bias model** corrects for the fact that connected wards
file 50× more than silent tribal blocks. A deterministic 0–100 score ranks every hotspot.
Then the **Allocator** takes a budget envelope and solves an integer programme for the
portfolio that maximises citizens reached per rupee, subject to scheme eligibility, sector
caps, geographic spread and an equity floor. When the project completes, citizens photograph
and certify it — and the **Impact Ledger** measures what actually happened against a
propensity-matched counterfactual.

---

## What's working today (Day 0)

| Module | Status | Where |
|---|---|---|
| Deterministic seed data | ✅ 48 blocks · 5 states · 336 NIDI cells · 22 SOR rates | `data/generate_seed.py` |
| ⚖️ Coverage-bias correction | ✅ fitted log-linear model, coefficients learned | `backend/engine/bias.py` |
| Deterministic scoring + lineage | ✅ auditable, `recomputed_score_check` self-verifies | `backend/engine/score.py` |
| ★ **Allocator (ILP)** | ✅ PuLP/CBC + relaxation ladder + frontier, ~15 ms | `backend/engine/allocate.py` |
| Impact ledger + counterfactual | ✅ propensity matching, realization ratio ρ | `backend/engine/impact.py` |
| Gemini client + offline fallback | ✅ 4 surfaces, degrades safely | `backend/services/gemini/client.py` |
| Single-helpline telephony layer | ✅ simulator, 6 channels, provider = 1 env var | `backend/services/telephony/` |
| FastAPI (20+ endpoints) | ✅ DB-backed, all contracts live | `backend/app/main.py` |
| 💾 SQLite persistence | ✅ citizen submissions survive restarts, seed vs live origin | `backend/db.py` |
| Dashboard | ✅ 6 views incl. live intake feed + charts + AI briefing, no external CDN | `backend/static/index.html` |
| 📱 Citizen mobile app (PWA) | ✅ voice+text intake, track, verify, missed call · 3 languages · offline queue | `frontend/` |
| Voice intake endpoint | ✅ recorded audio → STT chain → same pipeline | `POST /api/v1/intake/voice` |
| 🇿🇦 Second-nation demo | ✅ India ⇄ South Africa toggle — same engine, adapter + dataset only | `?nation=za` on every endpoint |
| 🧑‍⚖️ Human escalation queue | ✅ low-confidence / unresolved-location reports wait for an officer, resolutions become labelled corrections | `GET/POST /api/v1/escalations/` |
| ⚠️ Early-warning alerts | ✅ deterministic surge detection per block+sector (30-day window vs historical rate) | `GET /api/v1/alerts/` |
| 🎧 Helpline live explorer | ✅ judges simulate a missed call → voice/text complaint → real pipeline, no handset needed | dashboard "Try the helpline" tab |
| 🔒 Proof-of-life evidence | ✅ live photo + GPS fix + device timestamp bound at shutter; server re-checks freshness/accuracy, recycled photos flagged not trusted | `POST /api/v1/intake/` `evidence`, `GET /api/v1/evidence/{ticket}` |
| 🏛 Government resolution timeline | ✅ citizen-visible 7-stage promise (received → assigned officer → field inspection → work start → SLA → resolved); officers advance stages, citizen sees who + when | `GET /api/v1/track/{id}`, `POST /api/v1/timeline/{id}/advance` |
| BRICS adapters | ✅ 5 nations, config-only | `adapters/*.yaml` |

**Proven on the seeded data:** Nandurbar files **13** complaints and ranks **#4**; Haveli
(Pune) files **51** and ranks **#228** — the bias correction flipping the ranking is the demo.
At ₹40 Cr the allocator funds **27 projects reaching 553,365 citizens at ₹722 each**,
satisfying every constraint in 13 ms. Squeeze to ₹12 Cr and it reports honestly:
*"covering every block needs ₹26.30 Cr; envelope is ₹12.00 Cr."*

**The loop is live, not staged:** file a complaint in the citizen PWA (`/app`) and it is
written to SQLite, re-scores the hotspots, and appears on the officer dashboard's
**📡 Live intake & AI** tab within 5 seconds — with sector/time charts and a Gemini
operations briefing computed over the same database counters. Flip the header toggle to
🇿🇦 South Africa (531 reports, Eastern Cape + Gauteng) to show the whole engine is
country-agnostic: one adapter, one dataset, zero code change.

**Human-in-the-loop where it matters:** if Gemini's confidence is low or the location
cannot be resolved to a real administrative code, the complaint is NOT auto-routed —
it lands in the officer **escalation queue**, and every correction is stored as labelled
training data. Surge alerts (a block filing 3× its historical rate) are computed
deterministically, no LLM in the loop. Unit economics: **₹1.57 per complaint** vs
~₹45 at a staffed call centre — the 28× gap is the scaling argument. Judges can try the
whole helpline from their laptop: the **🎧 Try the helpline** tab simulates a missed
call, takes voice (browser mic) or typed complaint, and runs the real pipeline.

**Nothing is fake — proof-of-life on every photo.** A complaint or verification photo is
only trusted when it was taken *live*: the PWA binds the shutter to a GPS fix and the
device clock, and the server re-checks all three (magic-byte image validation, timestamp
freshness ≤ 10 min, GPS accuracy). A recycled gallery photo or a denied location is
downgraded to `partially_verified` / `unverified` and the flags are stored with the
report so an auditor sees *why*. And the citizen is never left guessing: every ticket
carries a **government resolution timeline** — which department and named officer owns
it, when the field inspection and work order fall due, and the SLA completion date.
Officers advance stages from the dashboard; the citizen's Track screen updates with the
real actor and timestamp, plus a progress bar. *Accountability in both directions.*

---

## Architecture

```
📞 155XXX single helpline · missed call · SMS · IVR · WhatsApp · web · kiosk
   │        hi · mr · bn · ta · te · en · hi-Latn · zero-menu voice
   ▼
⓪ ACCESS     Channel Adapter → one CitizenReport · Bhashini STT/TTS · language ID
① UNDERSTAND Gemini structured extraction → sector · severity · LGD · affected population
② TRUST      Dedup fingerprint · corroboration · multimodal verification
③ ROUTE      Department Routing Table (data, not code) → CPGRAMS · SLA clock · citizen ACK
④ FUSE       Census · SECC · NFHS · PMGSY · JJM · SDG Index → NIDI deficit index
⑤ CLUSTER    Block × sector hotspots  →  ⚖️ COVERAGE-BIAS CORRECTION
⑥ SCORE      Deterministic 0–100 · auditable lineage · live weight sliders
⑦ ALLOCATE ★ ILP: maximise citizens per rupee s.t. budget · eligibility · caps
   │          · geographic spread · equity floor · Schedule-of-Rates unit costs
⑧ MEASURE ★  Pre-registered baseline → CITIZEN PHOTO/COMMENT VERIFICATION → social audit
   │          → propensity-matched counterfactual → Realization Ratio → weight feedback
   ▼
🏛️ Policymaker console · 📱 Citizen tracking · 🔍 Auditor lineage · 🌍 BRICS console
```

### The rule we never break
> **Gemini explains and structures. It never computes a score.**

Every number is reproducible from stored inputs. Ask an LLM for "a number 1–100" and you get
a plausible fiction; we get audited lineage. `/api/v1/hotspots/{id}/lineage` recomputes the
score from components and asserts it equals the stored value — that assertion *is* the audit.

---

## Repository layout

```
jansetu/
├── backend/
│   ├── app/main.py               FastAPI — 16 endpoints, serves the dashboard
│   ├── models/schemas.py         ★ THE CONTRACTS (Pydantic). Change = team-wide event.
│   ├── engine/
│   │   ├── bias.py               ⚖️ coverage-bias correction          [B]
│   │   ├── score.py              deterministic 0–100 + lineage        [B]
│   │   ├── allocate.py           ★ ILP + relaxation ladder + frontier [C]
│   │   └── impact.py             impact ledger + counterfactual       [C]
│   ├── services/
│   │   ├── gemini/client.py      Gemini ×4 surfaces + fallbacks       [B]
│   │   └── telephony/            ABC + simulator (single helpline)    [A]
│   ├── fixtures/                 JSON every workstream builds against
│   ├── static/index.html         dashboard
│   └── tests/                    ⬅️ workstreams B and C
├── frontend/                     📱 citizen PWA (React + Vite + Workbox)
│   ├── src/pages/                Home · Report · Track · Verify · MissedCall
│   ├── src/i18n.ts               mr / hi / en strings
│   └── dist/                     committed build, served at /app
├── data/                         seed CSVs · routing.json · PROVENANCE (Day 8)
├── adapters/                     india · brazil · russia · china · south_africa
└── docs/
    ├── 00-MASTER-PLAN.md         concept + strategy
    ├── 01-SOLUTION-v2.md         the three new features
    ├── 02-TEAM-EXECUTION-PLAN.md workstreams, git, Definition of Done
    ├── 03-API-CONTRACTS.md       the five shared objects
    └── 04-DAY-BY-DAY-GUIDE.md    ⬅️ START HERE
```

---

## Google AI surface map

| Capability | Job | Fallback |
|---|---|---|
| Gemini structured JSON | language, sector, severity, LGD extraction | keyword classifier, confidence capped 0.35 |
| Gemini multimodal | is this asset really complete? | skip, lower evidence weight |
| Gemini generation | policy briefs, committee notes, citizen replies | data-true template |
| Cloud Speech-to-Text / Bhashini | Indic voice intake | text intake |
| BigQuery / BQ ML | national-scale fusion, propensity GLM | SQLite + numpy (dev parity) |

---

## Data honesty

District and block **names** and the administrative structure are real. **LGD codes are
synthetic placeholders** with the correct shape — swap in real ones from
[lgdirectory.gov.in](https://lgdirectory.gov.in) (Day 6 task). **Indicators are realistic
synthetic values** calibrated to published national ranges (Census 2011, NFHS-5, NITI Aayog
SDG Index) — they are not official figures. `data/PROVENANCE.md` states this per dataset.

The brief permits realistic sample data where live data is unavailable. We are explicit
about which is which — that honesty is part of the submission, not a caveat to hide.

---

## Licence

MIT — built as a Digital Public Good.
