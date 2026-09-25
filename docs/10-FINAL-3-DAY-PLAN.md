# JanSetu — THE FINAL PLAN (3 days)

**Written: Wednesday 23 September 2026. Deadline: Saturday 26 September 2026.**

**You have 3 days.** This document is the single source of truth. Read it once,
end to end, then give each person their section. Nobody waits on anybody.

---

# PART 0 — The honest answer to "why did you send me an incomplete one?"

You deserve a straight answer, not an excuse.

**1. I built the hardest part first and the easiest part last. That was the wrong order.**
The engine — bias correction, ILP allocation, impact ledger — is the part that
wins competitions, and it is finished and working. But I left the *packaging*
(deployed link, demo video, slide deck, data provenance, tests) for the end.
Judges see the packaging first. Sequencing it last was my mistake.

**2. I wrote too many documents and not enough code.**
You got nine `.md` files. You needed working software and three short messages.
That is why you felt you had nothing to execute.

**3. Some things genuinely cannot be finished by me — they need your hands.**
API keys, a recorded voice, a deployed server, a video of your face. I cannot
sign up for Sarvam, I cannot record your voice, I cannot click "Deploy". These
are the remaining tasks, and they are all in PART 3.

**4. The good news, and it is genuinely good.**
I spent today verifying the code instead of describing it. Everything below I
ran myself, and it works:

```
27 projects · ₹39.98 Cr · 553,365 citizens · 15 of 15 blocks · solved in 45 ms
```

That is a real optimiser producing a real, costed, auditable portfolio. Most
teams at this hackathon will show a mockup. You have a working engine.

**What we are deliberately NOT building:** the React frontend. A separate
`frontend/` folder would take two days and add zero rubric points — the
dashboard you already have is a single self-contained HTML file that works
offline and never breaks. Spending Day 7 and Day 8 on React would cost you the
video and the deck, which are *mandatory* submissions. **Skip it.** This is a
deliberate decision, not a shortcut.

---

# PART 1 — What you have RIGHT NOW (I verified every line of this today)

## 1.1 Working and proven

| Piece | Proof | Status |
|---|---|---|
| Backend API | 20 endpoints, all returning 200 | ✅ |
| Dashboard | 5 tabs, one self-contained HTML file, no CDN | ✅ |
| **Bias correction** | Nandurbar 13 complaints → rank **4**. Haveli (Pune) 51 complaints → rank **228** | ✅ |
| **ILP allocator** | ₹40 Cr → 27 projects, ₹39.98 Cr, 553,365 citizens, 15/15 blocks, **45 ms**, provably optimal | ✅ |
| Constraint honesty | ₹12 Cr correctly *refuses* and explains: "covering every block needs at least ₹26.30 Cr" | ✅ |
| Impact ledger | Social audit with payment hold / partial / certified thresholds | ✅ |
| Routing table | 9 sectors → real schemes (PMGSY, JJM, NHA, SBM-G, RDSS, PMGDISHA…) | ✅ |
| BRICS adapters | 5 nations, config-only onboarding (Rule 04 satisfied) | ✅ |
| Privacy | Phone numbers SHA-256 hashed with salt before storage (DPDP 2023) | ✅ |
| Deterministic data | seed `20260917` → identical numbers on every machine | ✅ |

## 1.2 Fixed TODAY (these were real bugs)

| # | Bug | File · line | Fix |
|---|---|---|---|
| 1 | **Every Marathi complaint was labelled Hindi.** Devanagari is one script shared by two languages, so the old code always answered `hi` — meaning Marathi citizens got Hindi SMS replies | `backend/services/telephony/base.py` · `detect_language()` line ~79 | Now scores Marathi markers (`ळ, आहे, नाही, म्ह…`) against Hindi markers (`है, में, और, नहीं…`). **10/10 test cases pass** |
| 2 | **A bad API request crashed with 500** instead of a clean error — looks broken to anyone clicking `/docs` | `backend/app/main.py` · `intake_simulate()` line ~243 | Now returns a helpful **400** with a worked example |
| 3 | `.env` was never loaded at all, silently disabling Gemini | `backend/env_boot.py` (new) | Loads `.env` on import; `/api/v1/status` reports it |
| 4 | Gemini status said "no key" even when a key was set | `backend/services/gemini/client.py` | Note is now truthful |

## 1.3 Created TODAY (these did not exist before)

| File | What it does |
|---|---|
| `data/PROVENANCE.md` | **Judges WILL ask "is this real data?"** Honest line-by-line answer: what's real, what's synthetic, and why. Being straight about this scores points — bluffing loses them |
| `backend/test_languages.py` | Proves Marathi ≠ Hindi. 2 seconds to run |
| `backend/test_my_audio.py` | Tests STT with **your own recorded voice** |
| `render.yaml` | One-click deploy blueprint → gets you the mandatory deployed link |
| `Procfile`, `runtime.txt` | Fallback for Railway / Heroku |

## 1.4 Still missing — and WHO owns it

| Gap | Owner | Time |
|---|---|---|
| Gemini actually live (needs your key + correct model name) | Person 2 | 30 min |
| Sarvam API key (voice input) | Person 1 | 20 min |
| Deployed public URL (**mandatory**) | Person 3 | 45 min |
| Demo video 3–5 min (**mandatory**) | Person 3 | 3 h |
| Slide deck 10–12 slides (**mandatory**) | Person 3 | 3 h |
| Tests folder | Person 2 | 1 h |
| README live-demo link | Person 3 | 2 min |

---

# PART 2 — What to do with the code already on GitHub (read this before anything)

## 2.1 DO NOT delete your repository. Ever.

Your commit history **is the evidence** that you built this during the
competition window. Rule 02 of the brief. If you delete it, you cannot prove
you made it. **Deleting the repo would be the single worst thing you could do.**

## 2.2 `git pull` will NOT get you my changes

I cannot push to your GitHub. `git pull` only downloads commits **you** made.
My work lives in my sandbox, not in your repo.

## 2.3 The one thing that works: download the package

I built you a complete zip:

> ### `jansetu-package.zip` — 66 files, 237 KB (in the workspace)

It contains **everything**, including all of today's fixes.

**What to do — 5 minutes, exact steps:**

1. **Download `jansetu-package.zip`** from this workspace.
2. **Extract it** to a NEW folder, e.g. `C:\Users\prana\Downloads\jansetu-NEW`.
   Do **not** extract on top of your existing folder — a new folder means you
   can always go back.
3. **Copy your `.env` across** — this is the only file the zip cannot contain
   (it holds your secret keys, and `jansetu-package.zip` deliberately has none):

   ```
   copy C:\Users\prana\Downloads\Downloads\jansetu\backend\.env C:\Users\prana\Downloads\jansetu-NEW\backend\
   ```

   Check it arrived:

   ```
   dir C:\Users\prana\Downloads\jansetu-NEW\backend\.env*
   ```

   You must see **`.env`** — if you see **`.env.txt`**, rename it (Notepad
   silently adds `.txt`). The server only reads `.env`.

4. **Recreate the virtual environment** (one-time, ~2 min):

   ```
   cd C:\Users\prana\Downloads\jansetu-NEW\backend
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   > If activation is blocked by a security error, run this **once**, then retry:
   > `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

5. **Start it and confirm:**

   ```
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

   Open **http://localhost:8000** — you should see the JanSetu dashboard.

6. **Only when it works**, commit the new files to your existing repo:

   ```
   cd C:\Users\prana\Downloads\jansetu-NEW
   git init
   git remote add origin https://github.com/YOUR-USERNAME/jansetu.git
   git add .
   git commit -m "JanSetu: engine + bias correction + allocator + BRICS adapters"
   git push -u origin main --force
   ```

   > ⚠️ `--force` overwrites the remote with this version. **That is what you
   > want here** — but it means anything in the old repo that is not in this
   > folder is gone forever. Check first that your `.env` is NOT in the folder
   > (`git status` must never show `.env`). The `.gitignore` already protects it.

## 2.4 The `.env` trap — read this twice

**The server reads `.env` only when it starts.** Every time you edit `.env`,
you must **stop the server (Ctrl+C) and start it again**. Editing it while the
server runs does nothing. This single fact causes most "the key isn't working"
panics.

Your `.env` must contain **15 settings**. If you copied it from an older
`.env.example`, it is missing the entire STT block. Check with:

```
type backend\.env
```

It must include: `GEMINI_API_KEY`, `GEMINI_MODEL`, `STT_CHAIN`, `SARVAM_API_KEY`,
`SARVAM_MODEL`, `SARVAM_MODE`, `BHASHINI_USER_ID`, `BHASHINI_ULCA_API_KEY`,
`BHASHINI_PIPELINE_ID`, `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_STT_MODEL`,
`TELEPHONY_PROVIDER`, `MSISDN_HASH_SALT`, `PORT`, and `JANSETU_ENV_FILE`.
If any are missing, rebuild it: `copy .env.example .env` then fill it in again.

**Verify it is actually loaded** — open **http://localhost:8000/api/v1/status**
in your browser and look for:

```json
"env": { "env_file_found": true, "keys": { "GEMINI_API_KEY": "set", ... } }
```

- `env_file_found: true` and `GEMINI_API_KEY: "set"` → correct.
- `env_file_found: false` or any key `"EMPTY"` → the file is missing, is named
  `.env.txt`, or the server was started before you saved it.

---

# PART 3 — The 3-day plan (all three people work at the same time)

```
Today  Wed 23 Sep  ▸ Day 6 evening — set up + unblock keys
       Thu 24 Sep  ▸ Day 7 — make it real (Gemini live, voice live, deploy live)
       Fri 25 Sep  ▸ Day 8 — video + deck + freeze at 18:00
       Sat 26 Sep  ▸ Day 9 — SUBMIT
```

**Rule for all three:** if you are stuck for more than **20 minutes**, stop,
screenshot the error, and post it in the group. Do not start rewriting code.
Nobody debugs alone.

---

## 👤 PERSON 1 — Phone & Voice
### Your job: prove a person with NO smartphone can be heard.

#### Day 6 (tonight, ~45 min) — Get the Sarvam key

**1. Sign up**
- Go to **https://dashboard.sarvam.ai**
- Sign up with any email. Verify it.
- Find **API Keys** in the left menu → **Create new key** → copy it.
  It looks like `sk_abc123...` or a long UUID.

**2. Put it in `.env`**

```
cd C:\Users\prana\Downloads\jansetu-NEW\backend
notepad .env
```

Find the line `SARVAM_API_KEY=` and paste your key directly after `=` with
**no space and no quotes**:

```
SARVAM_API_KEY=paste_your_key_here
```

Save. **Check it is not `.env.txt`**:

```
dir .env*
```

If you see `.env.txt`, run: `ren .env.txt .env`

**3. Test it — how, and how to know it worked**

```
cd backend
.venv\Scripts\Activate.ps1
python test_my_audio.py
```

- **PASS** → you see `READY  sarvam` and `>>> 1 provider(s) ready`
- **FAIL** → you see `no key  sarvam`:
  1. Re-open `.env`, confirm the key is there and there is no space after `=`
  2. Confirm the filename is exactly `.env`
  3. **Close the terminal and open a fresh one** — this is the step people skip
  4. Still failing? Screenshot the output into the group. Do **not** edit code.

#### Day 7 (~1.5 h) — Record your own voice and make it work

**1. Record.** Phone voice recorder. Say one sentence about a real local
problem, in **Marathi or Hindi**. Under 30 seconds.
Example: *"धुळे तालुक्यात रस्ता खराब आहे"*

**2. Copy the file** into `backend\` and run:

```
python test_my_audio.py myvoice.m4a mr
```

(use `hi` for Hindi)

- **PASS** → `provider: sarvam` and your sentence appears as text.
  **Screenshot this. It goes in the demo video.**
- **FAIL → `transcribe() returned None`** → the key was found but the call
  failed. Screenshot, post in group.
- **FAIL → `provider: bhashini` or `provider: google`** → that is still a pass.
  Sarvam failed, the chain fell through automatically. Tell the group which one.

**3. Then prove the language fix works** (2 seconds):

```
python test_languages.py
```

You must see **10/10 passed**. This is the bug where every Marathi complaint
was being answered in Hindi. It is fixed.

#### Day 8 (~1 h) — Be the villager in the video

You are on camera for roughly 60 seconds. Do this:

1. **Hold up a basic feature phone** (₹1,500, no internet) — borrow one.
2. Say: *"This phone cannot run any app. It cannot fill any form. But it can
   make a call. That is the only thing 400 million Indians can do."*
3. **Call your helpline number**, speak your complaint in Marathi.
4. **Show the reply SMS arriving** in the citizen's own language.
5. **Show the dashboard** — the complaint has appeared as a ticket and been
   routed to the correct department.

Also send me these, for the deck:
- A photo of the feature phone
- The one sentence you will say on camera

#### Day 9 — Help Person 3. Do not touch code.

---

## 👤 PERSON 2 — The Brain (strongest coder)
### Your job: make the AI genuinely live, and make the numbers defensible.

#### Day 6 (tonight, ~30 min) — Verify Gemini is really running

**1. Find your key.** **https://aistudio.google.com** → **Get API key**.
Starts with `AIza...`

**2. Confirm the model name — this is the step that breaks most often.**
A wrong `GEMINI_MODEL` does not show an error. It silently falls back, and you
think the AI is live when it is not.

In AI Studio, open a **new chat** (or a prompt) and send: `hello`
Look at the model dropdown / the response header — **copy the exact model name
it used**, e.g. `gemini-2.5-flash`.

Put it in `.env`:

```
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.5-flash
```

**3. Test it** (server must be running):

```
cd backend
.venv\Scripts\Activate.ps1
python -c "from services.gemini.client import structure_report; r=structure_report('धुळे तालुक्यात रस्ता खराब आहे'); print('extractor:', r['extractor'], '| sector:', r['sector'])"
```

- **`extractor: gemini`** → ✅ **AI is genuinely live.** Screenshot it.
- **`extractor: fallback`** → your `GEMINI_MODEL` name is wrong for your key.
  Go back to step 2, copy the exact name from AI Studio, update `.env`,
  **restart the server**, run again.

**4. Install the SDK** if you have not:

```
pip install google-genai
```

> **If Gemini genuinely will not work, that is survivable.** The fallbacks are
> deterministic and the whole demo still runs. Say so in the group; do not burn
> three hours on it. We present it honestly as "Gemini for explanation,
> deterministic engine for computation" — which is the correct architecture
> anyway (see PART 4).

#### Day 7 (~3 h) — Make the numbers bulletproof

**Task A — Write `tests/` (1 h).** Five small test files. Each is 10 lines.
This is 5–8 rubric points for almost no effort.

| File | What it proves |
|---|---|
| `tests/test_bias.py` | Nandurbar (13) outranks Haveli (51). The core claim |
| `tests/test_allocate.py` | ₹40 Cr → 27 projects; budget never exceeded |
| `tests/test_infeasible.py` | ₹12 Cr refuses politely with an explanation |
| `tests/test_languages.py` | Marathi ≠ Hindi (10/10) |
| `tests/test_privacy.py` | No raw phone number ever appears in any response |

Run them all with:

```
pip install pytest
cd backend && python -m pytest ../tests -q
```

**Task B — Learn the two numbers you must defend (20 min).**

> **Nandurbar: 13 complaints, weight ×1.50, score 64.7, rank 4.**
> **Haveli (Pune): 51 complaints, weight ×0.50, score 45.6, rank 228.**

Read `data/PROVENANCE.md` §5. Be able to explain it in one breath:
*"A block with 51 complaints ranks 228th because almost everyone there can file
one. A block with 13 ranks 4th because almost nobody there can. Raw complaint
counts measure who owns a smartphone, not who has a problem."*

**Task C — Verify the money story (30 min).**

```
curl.exe -X POST http://localhost:8000/api/v1/allocate/ -H "Content-Type: application/json" -d "{\"budget_inr\":400000000}"
```

Must give: **27 projects · ₹39.98 Cr · 553,365 citizens · 15/15 blocks**.
Note the field is `budget_inr`, **not** `budget` — using the wrong name silently
falls back to the ₹4 Cr default.

Then:

```
curl.exe -X POST http://localhost:8000/api/v1/allocate/ -H "Content-Type: application/json" -d "{\"budget_inr\":120000000}"
```

Must **refuse** and explain. **This refusal is a feature — put it in the demo.**
A system that says "impossible, here's why" is more trustworthy than one that
silently returns something wrong.

#### Day 8 (~2 h) — Freeze at 18:00

- Finish tests, make them all pass.
- Re-read `data/PROVENANCE.md`. Correct anything inaccurate.
- **After 18:00: no more code changes.** Only documentation and video.

#### Day 9 — On call for last-minute fixes only.

---

## 👤 PERSON 3 — Screens & Story
### Your job: the deployed link, the video, and the deck. **All three are mandatory.**

#### Day 6 (tonight, ~1 h) — Deploy

**1. Push `render.yaml` to GitHub** (it is in the new folder).

**2. Deploy:**
- Go to **https://dashboard.render.com** → **Sign up with GitHub**
- **New +** → **Blueprint** → select your `jansetu` repo
- Render reads `render.yaml` and asks for the secret values
- Paste `GEMINI_API_KEY` (get it from Person 2)
- Wait ~4 minutes → you get a URL like `https://jansetu.onrender.com`

**3. Test it:** open the URL. You must see the dashboard.

- **FAIL → build error** → screenshot, post in group. Most likely the Python
  version; `runtime.txt` says `3.11.9`.
- **FAIL → blank page** → wait 60 s and refresh (free tier cold start).

**4. ⚠️ CRITICAL — keep it awake.**
Render's free tier sleeps after 15 minutes idle and takes ~50 s to wake.
**A judge opening your link cold will think it is broken.**
Fix: **https://uptimerobot.com** (free) → ping `your-url/health` every 5 min.
Do this tonight, not on Day 9.

**5. Put the URL in the README** — `README.md` line 3:

```
**🔗 Live demo:** https://jansetu.onrender.com
```

#### Day 7 (~4 h) — Build the deck (10–12 slides, mandatory)

| # | Slide | Content |
|---|---|---|
| 1 | Title | **JanSetu (जनसेतु)** — *"People's Bridge"*. Team name, track |
| 2 | The problem | 400M Indians have a feature phone, no app, no English. Their complaints vanish |
| 3 | The real insight | **Complaint counts measure who owns a smartphone.** Nandurbar 13 → rank 4; Haveli 51 → rank 228 |
| 4 | Solution | One number. Any language. Voice, SMS, or missed call |
| 5 | How it works | Intake → Gemini structures → LGD resolve → bias-correct → score → optimise |
| 6 | The optimiser | ₹40 Cr → 27 projects, 553,365 citizens, 15/15 blocks, **45 ms**, provably optimal |
| 7 | Honesty | ₹12 Cr *refuses* and explains why. Systems that admit limits get trusted |
| 8 | AI role | **Gemini explains; deterministic engine computes.** Never the reverse |
| 9 | Reach | 8 languages, 5 BRICS nations, config-only onboarding |
| 10 | Data honesty | Real vs synthetic, line by line (`PROVENANCE.md`) |
| 11 | Privacy | SHA-256 phone hashing, DPDP 2023 |
| 12 | Ask | It should be a Digital Public Good |

**Design rules:** one idea per slide. Big numbers. No paragraphs. The bias flip
(slide 3) and the 45 ms (slide 6) are the two slides that win — make them loud.

#### Day 8 (~4 h) — Record the video (3–5 min, mandatory)

**Shoot in this order. Each shot is one take; do not edit heavily.**

| Time | Shot |
|---|---|
| 0:00–0:30 | **The hook.** Person 1 holds a ₹1,500 feature phone. *"This phone can't run an app. 400 million Indians own one. Today their complaints go nowhere."* |
| 0:30–1:15 | **The call.** Real call to the helpline, spoken in **Marathi**. Show the reply SMS arriving **in Marathi** |
| 1:15–2:00 | **The flip.** Dashboard → **Bias correction** tab. Nandurbar 13 → rank 4. Haveli 51 → rank 228. Say the one sentence from `PROVENANCE.md` §5 |
| 2:00–3:00 | **The money.** Move the budget slider to ₹40 Cr. Hit **Solve portfolio**. **27 projects, 553,365 citizens, 45 ms.** Then drop it to ₹12 Cr and show it **refuse with an explanation** |
| 3:00–3:45 | **The proof.** Show the impact ledger + a citizen photo verification |
| 3:45–4:30 | **Scale.** 8 languages → 5 BRICS nations, config-only |
| 4:30–5:00 | **Close.** *"JanSetu. From complaint to costed portfolio in 45 milliseconds."* |

**Rules:** screen-record at 1080p. Narrate live, do not dub. Show the **deployed
URL**, not localhost. Under 5 minutes — judges stop watching after that.

#### Day 9 (~1 h) — Submit

---

# PART 4 — What to SAY (the 3 lines that win)

## The 2–3 line description (paste this exactly)

> JanSetu (जनसेतु) turns citizen complaints from any phone, in any Indian
> language, into a costed and auditable public investment portfolio. It
> corrects for the fact that complaint counts measure who owns a smartphone
> rather than who has a problem, then solves a real integer programme to
> allocate budget optimally — 553,365 citizens covered from ₹40 Cr in 45 ms.

## The one sentence to memorise (the bias flip)

> **"A block with 51 complaints ranks 228th, because almost everyone there can
> file one. A block with 13 complaints ranks 4th, because almost nobody there
> can. Raw complaint counts measure who has a smartphone — not who has a
> problem."**

## The answer when they ask "why doesn't AI just decide?"

> **"Gemini explains. A deterministic engine computes."**
> Every number in the portfolio comes from a Python solver we can show you.
> Gemini turns messy regional speech into structured JSON, and writes the
> explanation a policymaker reads. It never computes a score and never picks a
> project. That is deliberate: you can audit a solver, you cannot audit a
> language model. When the AI is unavailable the system still runs — it just
> gets less intelligent, never wrong.

**This is your strongest answer. It turns the "AI can't do maths" objection
into proof that you understand the domain.**

## The answer when they ask "is your data real?"

> *"Some is real, some is realistic synthetic, and it's all written down in
> `data/PROVENANCE.md`. Block and district names are real. LGD codes are
> placeholders, because the bulk pull takes two hours we spent elsewhere.
> Indicators are calibrated to Census 2011, NFHS-5 and the NITI Aayog SDG
> index, seeded so every number here reproduces exactly. Swapping in the real
> feeds is a CSV swap — no engine change."*

---

# PART 5 — Submission checklist (Day 9)

- [ ] **GitHub repo** `jansetu` — **Public**, contains all code
- [ ] **Deployed link** — live, and README line 3 filled in
- [ ] **UptimeRobot** pinging it so it never sleeps
- [ ] **Demo video** — 3–5 min, uploaded (YouTube unlisted), link in README
- [ ] **Slide deck** — 10–12 slides, PDF
- [ ] **2–3 line description** — from PART 4
- [ ] **README** — live demo link + video link + how to run locally
- [ ] **`data/PROVENANCE.md`** — in the repo root
- [ ] **`.env` is NOT committed** — run `git status`; `.env` must never appear
- [ ] **Tests pass** — `python -m pytest ../tests -q`
- [ ] **Marathi test passes** — `python test_languages.py` → 10/10
- [ ] **Last commit is before the deadline**

---

# PART 6 — Windows quick reference

| You want | Type this |
|---|---|
| Activate venv | `.venv\Scripts\Activate.ps1` (not `source`, not `/bin/`) |
| If activation blocked (once) | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Make `.env` | `copy .env.example .env` **then** `notepad .env` |
| Check `.env` name | `dir .env*` — must be `.env`, **not** `.env.txt` |
| Set an env var | `$env:GEMINI_API_KEY="AIza..."` |
| Call the API | `curl.exe ...` (**not** `curl` — PowerShell's `curl` is a different command that prompts) |
| Find a running server | `netstat -ano \| findstr :8000` |
| Kill it | `taskkill /PID <number> /F` |
| Start server | `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` |

**Golden rule: after editing `.env`, stop the server and start it again.**

---

# PART 7 — If something breaks

| Symptom | Cause | Fix |
|---|---|---|
| `env_file_found: false` | `.env` missing or named `.env.txt` | `dir .env*` → `ren .env.txt .env` → restart server |
| Key shows `EMPTY` but it's in the file | Server started before you saved | Stop server, start server |
| `extractor: fallback` | `GEMINI_MODEL` name wrong | Copy exact name from AI Studio, restart |
| `no key sarvam` | Same two causes as above | Same two fixes |
| Marathi replies come back in Hindi | Old code | You have the fix — run `python test_languages.py` |
| Allocate returns 7 projects not 27 | You sent `budget`, not `budget_inr` | Use `budget_inr` |
| Deployed site takes 50 s to load | Free tier asleep | UptimeRobot (PART 3, Person 3) |
| `curl` prints a security warning | PowerShell alias | Press **N**, use `curl.exe` |

---

**You have 3 days and a working engine. Go.**
