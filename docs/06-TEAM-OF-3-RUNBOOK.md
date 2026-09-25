# JanSetu — The 3-Person Runbook
## You + 2 friends · Do this step by step, starting right now

> **Read this first, all three of you, out loud, together. It takes 10 minutes.**
> Every step below tells you: **what to do**, **exactly what to type**, and **how to know it worked**.
> If a step doesn't work, stop and message the group. Don't struggle alone.

---

# STEP 0 — Check where you are (5 minutes)

I couldn't see your screenshot, so let's confirm you're in the right place. Answer these three:

### ❓ Check 1 — Is your code on GitHub?
Go to `https://github.com/<your-username>/jansetu` in a browser.
- ✅ **You see files like `README.md`, `backend/`, `data/`, `docs/`** → good, continue.
- ❌ **You see "404" or an empty repo** → you haven't pushed yet. Go to the section "If you haven't pushed yet" at the bottom of this file.

### ❓ Check 2 — Does the code run on your computer?
Open a terminal in the `jansetu` folder and type:

```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8000
```

Then open **http://localhost:8000** in your browser.
- ✅ **You see the JanSetu dashboard with 5 tabs** → good, continue.
- ❌ **Error** → go to "If something breaks" at the bottom.

### ❓ Check 3 — Do you have an AI key?
Open the `.env` file in your project folder.
- ✅ There's a key next to `GEMINI_API_KEY=` → good.
- ❌ It's empty → get a free key from https://aistudio.google.com/apikey and paste it in.

**All three checked? Great. Now pick your jobs.**

---

# STEP 1 — Who does what (3 people)

With 3 people we combine the two "brain" jobs into one. Here's the split:

| | **Person 1** | **Person 2** | **Person 3** |
|---|---|---|---|
| **Job name** | **PHONE & VOICE** | **THE BRAIN** ⭐ | **SCREENS & STORY** |
| **What you own** | How citizens contact us | The AI, the maths, the data | What people see + the presentation |
| **In simple words** | Missed calls, SMS, voice, WhatsApp, village kiosk, photo upload | Language understanding, the fairness fix, scoring, the money allocator, measuring results | The dashboard website, other-countries screen, deploying it, pitch deck, demo video |
| **Folders you touch** | `backend/services/telephony/`<br>`backend/app/main.py` (intake parts) | `backend/engine/`<br>`backend/services/gemini/`<br>`data/` | `backend/static/`<br>`adapters/`<br>`docs/` |
| **Who should take it** | Good with backend / APIs | ⭐ **Your strongest coder.** Likes logic and hard problems | Good at design, or the best communicator |

### ⚠️ Two rules about picking jobs

**1. Person 2 (The Brain) must be your best coder.**
This job contains the two things no other team in the competition has: the **fairness fix** and the **money allocator**. If this job fails, you've built a nice complaint list — which is what everyone else built.

**2. Person 3 is NOT "the person who makes slides at the end."**
Person 3 starts building screens **today**. In a competition, a demo that actually runs beats a clever feature nobody can see.

### If someone finishes early
They help Person 2. **Never** let anyone sit idle — and everyone must commit code to GitHub every single day. That's your proof that you built this during the competition.

---

# STEP 2 — Everyone does this today (20 minutes)

### 2.1 — Set up your computer (once)

```bash
cd jansetu
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

> **Windows users:** use `.venv\Scripts\activate` instead of the `source` line.

**How you know it worked:** you see `(.venv)` at the start of your terminal line.

### 2.2 — Create the data

```bash
python3 data/generate_seed.py
cd backend
python3 generate_fixtures.py
```

**How you know it worked:** you see a line like this —

```
SILENT Nandurbar (tribal, aspirational): 13 reports · bias x1.50 · top score 64.7 · rank 4
→ 13 complaints from Nandurbar outrank 51 from Haveli: YES ✅
```

That's the fairness fix working. Remember it — it's your best demo moment.

### 2.3 — Start the website

```bash
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000**

**How you know it worked:** all 5 tabs load, and the Allocator tab shows **27 projects / 553,365 people**.

### 2.4 — 🔴 MOST IMPORTANT: check your AI model name

Do this **today**, all three of you. It's the #1 thing that silently ruins demos.

1. Go to https://aistudio.google.com
2. Send one test message
3. Note the **exact model name** that responds
4. Open `.env` and set `GEMINI_MODEL=` to that exact name

**Why this matters:** if the name is wrong, the AI quietly stops working and the system switches to a simple backup method. Your demo will still run — but it'll look dumb, and you won't know why.

### 2.5 — Create the "parking lot" file

Make a file called `PARKING.md` in the project folder. Write today's date in it.

**Why:** When someone gets a new idea at 11pm ("what if we add blockchain?!"), it goes in `PARKING.md`, not into the code. New ideas during the final week are how teams miss deadlines.

---

# STEP 3 — The nine days

Each day has: **a goal**, **what each person does**, and **how to know the day is done**.

Two days are marked 🔗 **INTEGRATION DAY**. On those days, everyone stops at 6pm and you test the whole thing together. **Do not skip these** — they're what stops everything breaking at the end.

---

## 📅 DAY 1 — Get the AI actually working

**Goal:** The AI correctly understands complaints in Indian languages.

### 👤 Person 1 (Phone & Voice)
**Task:** Add speech-to-text — turn spoken voice into written words.

- Open `backend/services/telephony/base.py`
- Add a function that takes an audio file and returns text
- Use **Bhashini** first (it's free and made by the Government of India — good for your story). If Bhashini fails, try Sarvam. If that fails, use Google.
- **Done when:** You play a Marathi voice clip and the correct Marathi text appears.

### 👤 Person 2 (The Brain) ⭐
**Task 1:** Turn the AI on and test it with all 8 sample languages.

- Open `backend/services/gemini/client.py`
- Your key is already wired. Test with the sample complaints in `backend/fixtures/reports_8lang.json`
- If the AI returns broken text, fix the prompt (the instruction text) until it returns clean, correct answers every time

**Task 2 — IMPORTANT BUG TO FIX:** ⚠️
Right now our simple backup method thinks **everything written in Devanagari script is Hindi**. But Marathi also uses Devanagari. So Marathi complaints are being labelled as Hindi, and people get reply SMS in the wrong language.

- Make the AI correctly tell **Marathi and Hindi apart**
- **Done when:** you send a Marathi complaint and it comes back labelled `mr`, not `hi`.

### 👤 Person 3 (Screens & Story)
**Task:** Click through every tab. Write down everything broken, ugly, missing, or confusing.

- Number your list by how much it hurts the demo
- Share it in the group chat
- **Done when:** you have a written list of at least 10 things.

### ✅ How do we know Day 1 is done?
Send a Marathi complaint through the system. It comes back with the right problem type, the right location, and goes to the right department — **using the real AI**, not the backup method.

---

## 📅 DAY 2 — The phone flow + the fairness story

**Goal:** The missed-call flow works start to finish, and the fairness fix is visible on screen.
*(It's the weekend — put in a long day.)*

### 👤 Person 1
Build the complete missed-call flow in the simulator:

1. Citizen gives a missed call
2. We call back and speak a greeting in their language
3. They speak their problem
4. We read the problem back and ask them to press 1 to confirm
5. They get an SMS with their complaint number

- Files: `backend/services/telephony/simulator.py`
- **Done when:** you can demonstrate the whole flow in the browser without touching the keyboard twice.

### 👤 Person 2
Make the fairness fix **visible**. It works already, but nobody can see *why*.

Show these three numbers for every hotspot on screen:
- how many complaints the area actually sent
- how many it **would have** sent with normal phone/internet
- the multiplier we applied (e.g. ×1.50)

- **Done when:** the website shows all three numbers for each hotspot.

### 👤 Person 3
Build the **"Bias correction" tab**. This is the emotional heart of your demo.

It must clearly show, side by side:
> **Pune (Haveli): 51 complaints → rank 228**
> **Nandurbar: 13 complaints → rank 4**

- **Done when:** someone who knows nothing about the project looks at it and says *"oh, that's unfair — and you fixed it."*

### ✅ How do we know Day 2 is done?
The missed-call flow works, and anyone can see the fairness comparison on screen.

---

## 📅 DAY 3 — 🔗 INTEGRATION DAY 1

**Goal: everything works together as ONE system.**

### ⛔ Everyone stops adding new features at 6pm.

At 6pm, all three of you:

1. **Save your work:**
   ```bash
   git add .
   git commit -m "Day 3: describe what you did"
   git push
   ```
2. **Get everyone else's work:** `git pull`
3. **Test the complete journey together:**
   > File a complaint → AI understands it → it gets routed to a department → it joins a hotspot → fairness is applied → it gets scored → the allocator funds it → it appears on screen
4. **Fix everything that breaks.** No new features until this journey works perfectly.

### If the journey works and you have time left
- **Person 1:** start the citizen tracking portal (someone sends `STATUS JS-2026-000401` by SMS and gets the status back)
- **Person 2:** make the "how this score was calculated" page work for every hotspot, not just some
- **Person 3:** 📱 **record a rough 90-second demo on your phone.** It's not for submission — it's to find what's confusing. Watch it together, cringe, then fix it.

### ✅ How do we know Day 3 is done?
One person can file a complaint and watch it become a funded project, live, in one go.

---

## 📅 DAY 4 — Real data + citizen tracking

**Goal:** Use real government data where we can, and be honest about what we couldn't get.

### 👤 Person 1
**Task:** Build the citizen tracking portal.
- A page where someone types their complaint number and sees the current stage
- The 4 stages: Received → Routed → In progress → Resolved
- Make `STATUS <number>` work by SMS too
- **Done when:** you can look up any complaint by its number and see where it is.

### 👤 Person 2 ⭐ (biggest day)
**Task:** Replace our made-up numbers with real ones.
1. Go to **data.gov.in** and download real data for our 48 areas: population, literacy, poverty (BPL), SC/ST population
2. Where you **can't** find real data, keep our sample numbers — but **write down that you did**
3. Build the "how badly is this area lacking?" score using real sources:
   - PMGSY → roads
   - Jal Jeevan Mission → water
   - NFHS → health
   - UDISE → schools
4. Give Person 3 a list of: which numbers are real, which are estimates, and where each came from

- **Done when:** Person 3 has that list and can write it up.

### 👤 Person 3
**Task 1:** Write `data/PROVENANCE.md` using Person 2's list. It's a simple table:

| Data | Source | Real or estimate? | Date downloaded | Licence |

**Task 2:** Add drill-down to the dashboard: click a state → see districts → click a district → see blocks.

- **Done when:** you can get from "all of India" down to one specific block just by clicking.

### 💡 Why today matters
Judges will ask *"is this real data?"* Answering honestly — *"these are real, these are estimates, here's the full list"* — is far more impressive than pretending everything is real.

---

## 📅 DAY 5 — ★ Make the money allocator amazing

**Goal:** Dragging the budget slider becomes the most impressive thing in your project.

### 👤 Person 1
**Task:** Let citizens send a **photo and a comment** about a finished project.
- Add an upload box
- Store the photo and comment
- Send it to Person 2's checking function
- **Done when:** you can upload a photo and see it saved with the right project.

### 👤 Person 2 ⭐ (main day)
**Task 1 — Speed.** When someone drags the budget slider, the answer must appear in **under 0.4 seconds**.
- If it's too slow, use the "fast" setting while dragging and the exact setting when they let go
- Show the time it took on screen (e.g. "solved in 18 ms") — it looks impressive and proves it's real

**Task 2 — "Why wasn't this funded?"**
- Every rejected project must show a plain-English reason and how much more money it needed
- **Done when:** 100% of rejected projects have a reason.

**Task 3 — Test the fairness rule actually works.**
- Push the "poorest areas" slider up to 60%, 70%
- The trade-off graph must visibly bend
- **Done when:** if the graph stays flat, you've found a bug — fix it.

### 👤 Person 3
**Task:** Build out the Allocator screen properly:
- budget slider
- poorest-areas slider
- live updating as you drag
- the trade-off graph
- the "which rules are blocking us" report

- **Done when:** this tab looks like a real product, not a school project. **This tab IS your demo.**

### ✅ How do we know Day 5 is done?
You show someone the budget slider and they say "wow."

---

## 📅 DAY 6 — 🔗 INTEGRATION DAY 2 + measuring results

### ⛔ Everyone stops and saves work at 6pm. After today, the feature list is FROZEN.

### 👤 Person 1
**Task:** Finish the WhatsApp channel and the offline village-kiosk channel.
- **Done when:** all 6 ways of contacting us are demoable.

### 👤 Person 2 ⭐
**Task 1:** Our area ID codes are currently fake placeholders. Replace them with **real codes** from https://lgdirectory.gov.in

**Task 2:** Finish measuring results.
- For each finished project, find a **similar area that did NOT get the project**
- Compare what happened to both — that's how you know the project actually caused the improvement

**Task 3:** The learning loop.
- If road projects keep delivering less than promised, the system should automatically lower roads' priority next time

- **Done when:** you can show a number like *"roads delivered 82% of what was promised."*

### 👤 Person 3
**Task:** The other-countries screen.
- Switch from India to Brazil → the same system runs on Brazil's settings
- Then add a 6th country **live**, in front of someone

- **Done when:** you switch country and everything still works.

---

## 📅 DAY 7 — Real photo checking + the story

| Person | Task |
|---|---|
| **1** | Polish the citizen portal. Make sure all 6 channels work and look decent. |
| **2** | Install `google-genai` (`pip install google-genai`) and make photo checking actually **look at the image**. Right now it only reads the text comment. Also: in `backend/engine/impact.py` there's a temporary guess number `0.15` — replace it with something defensible and **write a comment explaining your reasoning**. |
| **3** | **Draft the pitch deck.** All 12 slides, with real screenshots. Not pretty yet — just complete. Share it with the team. |

### ✅ How do we know Day 7 is done?
The photo check returns a real answer about an actual image, and the deck draft is shared.

---

## 📅 DAY 8 — 🚀 Deploy, record, ⛔ FREEZE AT 6PM

| Person | Task |
|---|---|
| **1** | Create a Dockerfile and deploy to **Google Cloud Run** or **Render**. **Start this in the morning** — deploying always takes 3× longer than you think. |
| **2** | Finish `PROVENANCE.md`. Then 🔌 **turn off your internet** and run everything. Nothing should crash — things should just get simpler. Create the final demo data: 100+ complaints in many languages, 12 completed projects. |
| **3** | 🎥 **Record the 3–5 minute demo video.** At least 3 takes. Check the audio is clear and the text is readable on a phone screen. |
| **Everyone** | ⛔ **After 6pm: only bug fixes, the deck, the README, and the video. NO new features.** |

### ✅ How do we know Day 8 is done?
The live website works when opened in a fresh browser, with no login and no setup.

---

## 📅 DAY 9 — 📦 SUBMIT

Tick these off together:

- [ ] Run the full demo 3 times, timed, under 5 minutes each
- [ ] Re-record any part of the video where you stumble
- [ ] Final deck: 10–12 slides
- [ ] README: live link at the top, setup steps, how it works
- [ ] `PROVENANCE.md` finished, `LICENSE` present, GitHub history clean and pushed
- [ ] Repo is public (or you've given access to `build-with-ai-india@googlegroups.com`)
- [ ] Submission form: **code · video · deck · 2–3 line description · live link**
- [ ] **Submit with hours to spare, not minutes**

---

# STEP 4 — Your daily routine

Every day, at the same time:

**1. 10-minute standup (standing up keeps it short).** Each person says:
- What I finished yesterday
- What I'm doing today
- **What's blocking me** ← most important. Say it early, not at midnight.

**2. Save your work every evening:**
```bash
git add .
git commit -m "Day 4: what you did"
git push
```
Everyone does this **every single day**, even if it feels small. It's your proof you built this during the competition.

**3. The main version must always work.** If you break it, fix it before you sleep.

---

# STEP 5 — If something breaks

| Problem | Fix |
|---|---|
| `No module named 'pulp'` | You forgot to activate the environment. Run `source .venv/bin/activate` again. |
| "Port already in use" | Another copy is running. Close it, or use `--port 8001`. |
| AI isn't responding / everything says "fallback" | Wrong key or wrong model name. Test the exact model name in AI Studio. |
| GitHub conflicts when pushing | Run `git pull` first. Fix the conflicting lines together. Don't edit the same file at the same time. |
| Allocator returns nothing | Your rules contradict each other (e.g. poorest-areas % too high). Lower the sliders and read the message it gives you. |
| Works on my machine, not theirs | Delete `.venv`, reinstall from `requirements.txt`, compare Python versions. |
| Everything is slow | Tick the "fast solver" box. Don't redraw the trade-off graph on every slider movement. |

---

# STEP 6 — If you haven't pushed to GitHub yet

Do this **once**, from the person whose computer has the working code:

```bash
cd jansetu
git init
git add -A
git -c user.name="Your Name" -c user.email="you@example.com" commit -m "JanSetu: first commit"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/jansetu.git
git push -u origin main
```

Then the other two run:
```bash
git clone https://github.com/<YOUR_USERNAME>/jansetu.git
```

⚠️ **Never commit the `.env` file.** It holds your secret key. It's already protected, but check before every push:
```bash
git status
```
If you see `.env` listed there, **stop** and tell the group.

---

# STEP 7 — Quick reference: who owns which file

| File | Owner |
|---|---|
| `backend/services/telephony/*` | Person 1 |
| `backend/app/main.py` (intake / tracking / verify parts) | Person 1 |
| `backend/engine/bias.py` | Person 2 |
| `backend/engine/score.py` | Person 2 |
| `backend/engine/allocate.py` ⭐ | Person 2 |
| `backend/engine/impact.py` | Person 2 |
| `backend/services/gemini/client.py` | Person 2 |
| `data/*` | Person 2 |
| `backend/static/index.html` | Person 3 |
| `adapters/*` | Person 3 |
| `docs/*`, deck, video, deployment | Person 3 |
| `README.md`, `PROVENANCE.md` | Person 3 (with facts from Person 2) |

**Stay in your own files.** If you need to change someone else's file, tell them first. This one rule prevents 90% of team disasters.

---

# STEP 8 — The three numbers that win the demo

Memorise these. All three of you.

1. **Nandurbar sends 13 complaints → ranks #4. Pune sends 51 → ranks #228.**
2. **₹40 crore → 27 projects → 553,365 people helped → ₹722 per person.**
3. **Drop the budget to ₹12 crore → the system honestly says:** *"covering every area needs ₹26.30 crore, you only have ₹12 crore."*

---

# STEP 9 — The 2–3 line description (for the submission form)

> **JanSetu (जनसेतु)** turns fragmented citizen voice — via a single toll-free number, missed call, or SMS on any handset, in any Indian language — into a costed, scheme-compliant public investment portfolio. A Gemini-powered routing brain sends each complaint to the right department, a bias-correction model stops under-connected communities being drowned out, and an optimiser allocates a fixed budget to maximise citizens reached per rupee under equity and geographic-spread constraints. Citizens then photograph and certify the finished work, giving government an audited impact ledger instead of self-reported completion.

---

*JanSetu (जनसेतु) — "the people's bridge." Three people, nine days. You've got this.*
