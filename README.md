# LokNivesh (लोकनिवेश) — Public Investment Intelligence

**Track 01 · AI for Digital Public Infrastructure & Governance · BRICS Theme: Innovation**
Build with AI: Code for Communities — Second Edition (Google Cloud × Hack2Skill)

> Every other entry in this track **ranks complaints**. LokNivesh **allocates the budget**.
> *From citizen voice → verified demand → a costed, scheme-compliant, equity-constrained project portfolio → a measured outcome.*

---

## 60-second quickstart

```bash
cd loknivesh
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

python3 data/generate_seed.py        # deterministic seed data (48 blocks, 5 states)
cd backend && python3 generate_fixtures.py   # fixtures so every workstream can start

cp .env.example .env                 # add your GEMINI_API_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** → dashboard · **http://localhost:8000/docs** → interactive API.

**It runs with no API key.** Every Gemini call degrades to a deterministic fallback, so the
demo survives a dead network on judging day.

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
| FastAPI (16 endpoints) | ✅ fixture-backed, all contracts live | `backend/app/main.py` |
| Dashboard | ✅ 5 views, no external CDN | `backend/static/index.html` |
| BRICS adapters | ✅ 5 nations, config-only | `adapters/*.yaml` |

**Proven on the seeded data:** Nandurbar files **13** complaints and ranks **#4**; Haveli
(Pune) files **51** and ranks **#228** — the bias correction flipping the ranking is the demo.
At ₹40 Cr the allocator funds **27 projects reaching 553,365 citizens at ₹722 each**,
satisfying every constraint in 13 ms. Squeeze to ₹12 Cr and it reports honestly:
*"covering every block needs ₹26.30 Cr; envelope is ₹12.00 Cr."*

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
loknivesh/
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
