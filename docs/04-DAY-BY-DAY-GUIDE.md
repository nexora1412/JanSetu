# LokNivesh — Day-by-Day Guide
## Submitting 26 Sep 2026 · 9 working days · Thu 17 → Sat 26 Sep

> **Read this first.** Day 0 is already done — the foundation is built and running.
> Your job is Days 1–9. This document tells each person exactly what to do, in order,
> with an acceptance test for every task. If your day's acceptance test passes, you are
> on schedule. If it doesn't, raise it in the group chat the same hour, not at midnight.

---

## 0 · What is already built (Day 0, done)

Do not rebuild any of this. Read it, run it, then extend it.

| Built | Acceptance proof |
|---|---|
| Seed data: 48 blocks, 5 states, 336 NIDI cells, 22 SOR rates | `python3 data/generate_seed.py` |
| ⚖️ Coverage-bias correction — **fitted**, coefficients learned from data | Nandurbar ×1.50, Haveli ×0.50 |
| Deterministic 0–100 scoring with full lineage | `/api/v1/hotspots/{id}/lineage` |
| ★ Allocator — PuLP/CBC ILP + relaxation ladder + frontier | ₹40 Cr → 27 projects, 553,365 citizens, ₹722 each, 13 ms |
| Impact ledger with propensity-matched counterfactual | `/api/v1/impact/` |
| Gemini client, 4 surfaces, **offline fallback** | runs with no API key |
| Single-helpline telephony layer + simulator, 6 channels | `/api/v1/intake/` |
| FastAPI, 16 endpoints, all contracts live | `/docs` |
| Dashboard, 5 views, no external CDN | http://localhost:8000 |
| BRICS adapters ×5 | `adapters/` |

### The three numbers that win the demo — memorise them
1. **Nandurbar files 13 complaints and ranks #4. Haveli (Pune) files 51 and ranks #228.**
2. **₹40 Cr → 27 projects, 553,365 citizens, ₹722 per citizen, every constraint satisfied.**
3. **Squeeze to ₹12 Cr → "covering every block needs ₹26.30 Cr; envelope is ₹12.00 Cr."**

---

## 1 · Setup — 30 minutes, whole team, do it together (TODAY)

```bash
git clone <your-repo> && cd loknivesh
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
python3 data/generate_seed.py
cd backend && python3 generate_fixtures.py
cp ../.env.example ../.env                              # paste in YOUR GEMINI_API_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Acceptance:** http://localhost:8000 loads, the Allocator tab shows 27 projects, and the
Intake tab files a Marathi report that routes to PMGSY. Everyone sees this before anyone
writes a line of code.

**Then, in order:**
1. **Verify your Gemini model ID.** Open [AI Studio](https://aistudio.google.com), run one
   test call, and set `GEMINI_MODEL` in `.env` to the model that actually responds. Recent
   teams referenced `gemini-3.x-flash` — **confirm it yourself**, do not trust a blog post.
   This is the single highest-risk unknown in the project.
2. **Assign workstreams** (§2 of `02-TEAM-EXECUTION-PLAN.md`). Rule: **workstream C goes to
   your strongest builder.** If C fails you have a nice complaint-ranking dashboard — which
   is what everyone else built.
3. **Create `PARKING.md`.** Every new idea goes there, not into the build.

---

## 2 · The nine days

Two **hard integration windows** — everyone stops, merges to `main`, runs the whole thing
together. Non-negotiable. Integration hell on Day 8 is what kills student teams.

### **Day 1 · Fri 18 Sep** — Go live with Gemini

| Who | Task | Acceptance |
|---|---|---|
| **B** | Add the key, run `structure_report()` on all 8 fixture languages. Fix the prompt until JSON validates every time. | 8/8 languages → correct sector; `extractor=gemini` |
| **B** | ⚠️ **Fix hi vs mr.** Our script-based fallback maps all Devanagari → `hi`. Gemini must distinguish Marathi from Hindi. | Marathi text returns `mr`, not `hi` |
| **A** | Wire real STT: Bhashini (free, govt of India) → Sarvam → Google Chirp as fallback chain. | Marathi audio → correct transcript |
| **C** | Read `engine/allocate.py`. Add 3 unit tests your fixtures don't cover. | `pytest` green |
| **D** | Walk the whole dashboard end-to-end with the API live. List every broken/ugly thing. | Written punch list |

**Day 1 exit:** `curl -X POST /api/v1/intake/` with Marathi voice text returns sector, correct
LGD code, and routes to the right department — with Gemini, not the fallback.

---

### **Day 2 · Sat 19 Sep** — Channels and the bias story (weekend: go long)

| Who | Task | Acceptance |
|---|---|---|
| **A** | Missed-call + SMS + IVR working in the simulator, with TTS readback in mr/hi/bn and DTMF confirm. | Full call flow demoable in-browser |
| **B** | Make the bias correction **visible**: expose fitted coefficients, per-block propensity, and the counterfactual "would have filed N reports" through the API. | `/api/v1/hotspots/` shows `expected_reports` and `bias_factor` per hotspot |
| **C** | Department routing: load `data/routing.json`, handle the 8 sectors + rural/urban split, officer reference, SLA clock. | Every sample complaint routes correctly |
| **D** | Build the **Bias tab** properly — the loud-vs-silent flip must be the emotional centre of the demo. | Side-by-side: 51 reports/rank 228 vs 13 reports/rank 4 |

**Day 2 exit:** the missed-call flow works and the bias flip is on screen.

---

### **Day 3 · Sun 20 Sep** — 🔗 **INTEGRATION WINDOW 1**

**Everyone stops feature work at 18:00. Merge to `main`. Run the full loop together:**
intake → structure → route → cluster → bias-correct → score → allocate → render.

| Who | Task |
|---|---|
| **All** | Fix every break found. No new features until the loop is green. |
| **A** | Citizen tracking portal: `STATUS <ticket>` by SMS, 4-stage lifecycle. |
| **B** | Score lineage hardening — `/lineage` must recompute and assert equality for **every** hotspot. |
| **C** | Impact ledger: pre-registered baselines for all 44 projects. |
| **D** | Record a **rough 90-second walkthrough** on your phone. Not for submission — to find what's confusing. |

**Day 3 exit:** one person can file a complaint and watch it become a funded project, live.

---

### **Day 4 · Mon 21 Sep** — Data fusion and the deficit index

| Who | Task | Acceptance |
|---|---|---|
| **B** | Replace/extend `data/census_seed.csv` with **real** values from data.gov.in where you can get them. Where you can't, keep synthetic and record it in `PROVENANCE.md`. | `PROVENANCE.md` lists every dataset, source, licence, snapshot date |
| **B** | Build the NIDI properly: per-sector deficit from PMGSY / JJM / NFHS / UDISE / SDG Index. | Deficit reproducible from source rows |
| **C** | Scheme eligibility engine + funding splits (centre:state) from `adapters/india.yaml`. | An ineligible project is rejected with named failed conditions |
| **D** | Policymaker polish: drill-down state → district → block, sector filter, sortable tables. | Drill-down works |

---

### **Day 5 · Tue 22 Sep** — ★ Make the allocator undeniable

| Who | Task | Acceptance |
|---|---|---|
| **C** | Performance: slider drag must re-solve **< 400 ms**. Profile `solve_with_ladder`; cache the frontier; use `fast=True` on drag and exact on release. | Timing printed in the UI |
| **C** | **"Why was this dropped?"** for every rejected project, with the marginal rupee. | 100% of dropped projects have a reason |
| **C** | Push the equity floor high until it actually binds; verify the frontier curve bends. | Frontier visibly bends at high floors |
| **B** | Gemini policy brief + standing-committee note. | One click, exports cleanly |
| **D** | Allocator workbench: budget slider, equity slider, sector caps, live re-solve, frontier chart, constraint report. | **This tab is the demo.** Make it beautiful. |

**Day 5 exit:** dragging the budget from ₹40 Cr to ₹4 Cr is the single most impressive thing
in the build. If it isn't yet, spend Day 6 on it.

---

### **Day 6 · Wed 23 Sep** — 🔗 **INTEGRATION WINDOW 2** + measurement

| Who | Task |
|---|---|
| **All** | **Merge to `main` at 18:00. Full-loop run. Freeze the feature set after today.** |
| **B** | Swap synthetic LGD codes for **real** ones from [lgdirectory.gov.in](https://lgdirectory.gov.in). |
| **C** | Impact ledger: counterfactual matching across all delivered projects; ρ computed per sector. |
| **C** | Feedback loop: `update_sector_weights()` actually reweights from realised ρ. |
| **A** | Citizen verification intake: photo upload + comment → Gemini multimodal verdict → social audit score. |
| **D** | BRICS console: switch nation → same pipeline runs on that adapter. Add a 6th nation live. |

**Day 6 exit:** the citizen-verification loop works and BRICS switching is demoable.

---

### **Day 7 · Thu 24 Sep** — Real Gemini multimodal + the story

| Who | Task | Acceptance |
|---|---|---|
| **B** | `pip install google-genai`; wire real image parts into `verify_photo()`. | A photo gets a real `completion_est` |
| **B** | Swap the stub control-gain assumption in `impact.py` for a defensible estimate; document it. | `impact.py` has no magic 0.15 without a comment |
| **A** | WhatsApp adapter (simulated webhook) + `STATUS <id>` + kiosk offline sync. | All 6 channels demoable |
| **C** | Seed 12 completed projects with verification histories: some certified, some flagged. | Impact tab shows both a ✅ and a ⚠️ |
| **D** | **Draft the deck.** All 12 slides, real screenshots. | Deck draft shared |

---

### **Day 8 · Fri 25 Sep** — Deploy, seed, record ⛔ **FEATURE FREEZE 18:00**

| Who | Task |
|---|---|
| **A** | Dockerfile + deploy to Cloud Run or Render. **Deploy early — it always takes 3× longer than you think.** |
| **B** | `data/PROVENANCE.md` finished. Run the 8-language suite with the network **unplugged** — everything must degrade, nothing may crash. |
| **C** | Seed the demo dataset: 100+ multilingual reports, 5 states, 12 completed projects. |
| **D** | 🎥 **Record the 3–5 min demo video.** Three takes minimum. Audio clean, screen readable on a phone. |
| **All** | After 18:00: **bugs, deck, README, video only.** No new features. Write it on the wall. |

**Day 8 exit:** live URL works from a fresh browser with no login and no local setup.

---

### **Day 9 · Sat 26 Sep** — 📦 **SUBMIT**

- [ ] Full dry run of the demo, timed, three times, under 5 minutes
- [ ] Re-record any video segment that stumbles
- [ ] Deck final: 10–12 slides (outline in `00-MASTER-PLAN.md` §12)
- [ ] README: live URL at the top, 60-second quickstart, architecture diagram
- [ ] `PROVENANCE.md`, `LICENSE` (MIT), git history clean and pushed
- [ ] Repo public, or access granted to `build-with-ai-india@googlegroups.com`
- [ ] Submission form: **source code · video · deck · 2–3 line description · live URL**
- [ ] Submit with **hours to spare**, not minutes

---

## 3 · The 2–3 line description (paste-ready)

> **LokNivesh (लोकनिवेश)** turns fragmented citizen voice — via a single toll-free number,
> missed call, or SMS on any handset, in any Indian language — into a costed, scheme-compliant
> public investment portfolio. A Gemini-powered routing brain sends each complaint to the right
> department, a bias-correction model stops under-connected communities being drowned out, and
> an optimiser allocates a fixed budget to maximise citizens reached per rupee under equity and
> geographic-spread constraints. Citizens then photograph and certify the finished work, giving
> government an audited impact ledger instead of self-reported completion.

---

## 4 · The demo script (3–5 min — rehearse to 4:00)

| Time | Beat | Screen |
|---|---|---|
| **0:00–0:40** | **The missed call.** A keypad phone. No app, no data, no English. Farmer gives a missed call → we ring back in Marathi → he speaks → transcript appears. | Intake tab |
| **0:40–1:15** | **One number, zero menu.** Gemini structures it, TTS reads it back, he presses 1 → ticket → auto-routed to PMGSY Dhule → Marathi SMS ack with SLA. | Intake + outbox |
| **1:15–1:50** | **⚖️ The bias reveal.** Haveli: 51 reports, rank 228. Nandurbar: 13 reports, rank 4. Correction flips it. | Bias tab |
| **1:50–2:45** | **★ The Allocator.** ₹40 Cr → 27 projects, 553,365 citizens, ₹722 each. Drag to ₹12 Cr → live re-solve, and the tool reports that covering every block needs ₹26.30 Cr. | Allocator tab |
| **2:45–3:25** | **★ The people audit the fix.** Photo arrives. Gemini says *40% complete*. Social audit 0.38 → ⚠️ payment hold. Compare with a certified one at 0.91. | Impact tab |
| **3:25–3:55** | **Impact + BRICS.** Realization ratios per sector. Switch nation → Brazil adapter → same pipeline, zero code change. | Impact + adapters |
| **3:55–4:30** | **It's a DPI.** Stack diagram on India's DPI bricks. MIT, DPDP-compliant, one-command deploy. Export the committee note. | Documentation |

**Closer:** *"One number instead of forty departments. A missed call instead of a smartphone.
And the people who reported the problem are the ones who certify the fix — because no one
else is standing on that road."*

---

## 5 · Known gaps — the honest list

These are **not** done. They are assigned, not hidden.

| Gap | Owner | Day |
|---|---|---|
| Real STT (Bhashini/Sarvam/Chirp) — intake is text-only today | A | 1 |
| hi vs mr distinction (fallback maps all Devanagari → `hi`) | B | 1 |
| Real image parts in `verify_photo()` (needs `google-genai`) | B | 7 |
| Real LGD codes (currently synthetic placeholders) | B | 6 |
| Frontend is vanilla HTML, not React/Vite — **it works, and it's fast to change. Only rewrite if you have spare hands after Day 6.** | D | — |
| WhatsApp / USSD / kiosk adapters | A | 7 |
| Real CPGRAMS integration (mock the webhook, document the contract) | C | 6 |
| Control-gain assumption in `impact.py` is a documented stub (0.15) | C | 7 |

---

## 6 · Non-negotiables

1. **Gemini never computes a score.** It explains and structures only. Enforced in code.
2. **Infeasibility is surfaced, never hidden.** HTTP 200 with a reason and a suggested
   relaxation — never a 500, never a silent empty portfolio.
3. **The demo must run with no network.** Every AI call has a fallback. Test by unplugging.
4. **Commit every day from every member.** Commit history is your evidence against the
   "pre-existing project" rule.
5. **`main` is always demoable.** If you break it, you fix it before you sleep.
6. **State your limitations on the deck.** Judges respect a stated limitation and punish a
   hidden one. We have three: synthetic indicators, the control-gain assumption, and that
   bias correction reweights observed signal rather than recovering unspoken need.

---

*Built as a Digital Public Good · MIT · Good luck.*
