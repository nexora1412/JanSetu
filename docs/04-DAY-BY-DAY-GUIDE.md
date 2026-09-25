# JanSetu — Simple Day-by-Day Guide
## For a team of 4 · 9 working days · Goal: submit by Saturday 26 September 2026

---

# How to use this guide

- You are **4 people**: you + 3 friends. Each of you takes **one job** (called a "workstream").
- Every day has a **goal**, a list of **tasks per person**, and a **"How do we know we're done?"** check.
- If your day's check passes, you're on track. **If it doesn't, say it in the group chat immediately** — don't struggle alone till midnight.
- Technical words are explained the first time they appear. There's a **glossary at the end** if you forget what something means.
- **If you start late, just shift the dates.** The *order* matters, not the calendar. But keep the two "Integration Days" (Day 3 and Day 6) — those are the days that stop everything falling apart.

---

# Part 1 — What are we actually building? (plain English)

Read this together before you touch any code. Everyone should be able to explain it.

### The problem
In India, if your village road is broken, you have to figure out *which* government department is responsible — roads? rural development? the local council? Most people can't. So they give up, or complain to the wrong place.

Meanwhile, the government has a fixed budget and no reliable way to know **where the need is greatest**. So money often goes to whoever complains loudest — usually the areas with better schools, better phones, and better internet. The poorest areas complain least, and get least.

### What JanSetu does — the 6 steps

1. **A citizen reports a problem by just giving a missed call.**
   No app. No internet. No English. Any old ₹1,200 keypad phone works. Our system calls them back automatically and asks, in their own language, *"please tell us your problem."*

2. **AI listens and understands it.**
   The person speaks Marathi, Hindi, Bengali, Tamil, Telugu, or Hinglish. Our system turns the speech into text, figures out **what the problem is**, **how serious it is**, **where it is**, and **how many people it affects**.

3. **The system sends it to the right department automatically.**
   The citizen never needs to know which department exists. We work it out and send it there. They get an SMS back in their own language with a complaint number.

4. **Thousands of complaints become "hotspots".**
   One complaint is noise. Fifty complaints about water in one area is a pattern. We group them into hotspots and give each one a **score from 0 to 100**.

5. **★ We fix the unfairness (this is our special trick).**
   A rich, well-connected area might send 500 complaints. A poor tribal area might send 12 — not because it has fewer problems, but because complaining is harder there. **Every other team in this competition ranks the 500 above the 12.** We correct for that. We calculate *"how many complaints would this area have sent if it had normal phone and internet?"* and adjust. This is the heart of our project.

6. **★ We decide how to spend the money (this is our other special trick).**
   Everyone else stops at "here are the top 10 problems." We go further. You give us a budget — say ₹40 crore — and our system picks the **best combination of projects** to fund, so that the maximum number of people get helped per rupee, while following rules like:
   - you can't spend everything on roads
   - at least 40% must go to the poorest areas
   - no area should be left out completely
   - every project must be eligible under a real government scheme

7. **Citizens check the finished work.**
   When a project is marked "complete", we message the people there. They send a photo. AI checks it. If people say it's not done, **the payment gets held**. This catches "ghost projects" — roads that exist on paper but not in real life.

### Why we'll win
Most teams will build a nice dashboard that lists complaints. We're building the thing that **decides how the money gets spent** — and then **proves whether it worked**. That's the difference.

### The three numbers to remember (these win the demo)
1. **Nandurbar sends 13 complaints → ranks #4. Pune sends 51 complaints → ranks #228.** (Our fairness fix in action.)
2. **₹40 crore → 27 projects → 553,365 people helped → ₹722 per person.**
3. **Drop the budget to ₹12 crore → the system honestly says:** *"covering every area needs ₹26.30 crore, you only have ₹12 crore."*

---

# Part 2 — What is ALREADY built (don't rebuild this!)

I built the foundation. It's done and working. Your job is to improve and finish it, not start over.

| Already working | What it means |
|---|---|
| Sample data | 48 areas across 5 states, with population, literacy, poverty, phone/internet levels |
| The fairness fix | Already built and tested — the Nandurbar vs Pune example really works |
| Scoring (0–100) | Every hotspot gets a score, and we can show exactly how it was calculated |
| ★ The money allocator | Give it a budget, it picks the best projects. Works in 13 milliseconds |
| Impact measuring | Compares what was promised vs what actually happened |
| The phone system | Handles missed calls, SMS, voice, WhatsApp etc. (simulated — no real phone number needed) |
| The brain (AI) | Connects to Google Gemini. **Runs even with no internet** — it falls back to a simpler method |
| The website | A working dashboard with 5 screens. No login, no setup |
| Other countries | 5 config files (India, Brazil, Russia, China, South Africa) |

**You can run the whole thing right now** (see Part 3) and it works, even before you add anything.

---

# Part 3 — Setup (do this together, first, 30 minutes)

### Step 1 — Everyone installs the project

Open a terminal and type these lines one at a time. Press Enter after each.

```bash
cd jansetu
python3 -m venv .venv
source .venv/bin/activate
```

> **Windows users:** the last line is different. Use `.venv\Scripts\activate` instead.

You'll know it worked when you see `(.venv)` at the start of your terminal line.

```bash
pip install -r backend/requirements.txt
```

This installs the tools we need. It takes a minute or two.

### Step 2 — Create the sample data

```bash
python3 data/generate_seed.py
cd backend
python3 generate_fixtures.py
```

You should see messages like "48 blocks", "321 hotspots", and the Nandurbar vs Pune comparison.

### Step 3 — Add your AI key

```bash
cd ..
cp .env.example .env
```

Now open the `.env` file in any text editor and put your Gemini key next to `GEMINI_API_KEY=`.

**Get a free key here:** https://aistudio.google.com/apikey

> ⚠️ **NEVER send the `.env` file to anyone, and never commit it to GitHub.** It contains your secret key. It's already protected, but be careful.

### Step 4 — Start the website

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser and go to: **http://localhost:8000**

### ✅ How do we know we're done?

All four of you should see:
- The dashboard loads with **5 tabs** at the top
- The **Allocator** tab shows **27 projects** and about **553,365 people**
- The **Single helpline** tab lets you file a Marathi complaint, and it gets sent to the roads department

**Do not write any code until all 4 of you have seen this working.**

### Step 5 — IMPORTANT: check the AI model name

This is the #1 thing that can break your demo.

1. Open https://aistudio.google.com
2. Send one test message and see which model name actually responds
3. Open your `.env` file and set `GEMINI_MODEL=` to that exact name

Don't trust a model name you read in a blog post or another team's code. **Test it yourself.** If the model name is wrong, every AI feature silently falls back to the simple method and your demo looks dumb.

---

# Part 4 — Who does what? (4 people)

Pick jobs by **strength**, not by who's your best friend.

| Person | Job name | What they own | Good for someone who is... |
|---|---|---|---|
| **Person A** | **Phone & Voice** | How citizens contact us: missed calls, SMS, voice, WhatsApp, village kiosk | Good at backend, APIs, curious about how phone systems work |
| **Person B** | **AI & Data** | Talking to Gemini, understanding languages, the fairness fix, scoring | Good at Python, data, maths, likes experimenting with AI prompts |
| **Person C** | **The Money Brain** ★ | The allocator that decides which projects get funded, and measuring results | Your **strongest** coder. Likes hard problems and logic. |
| **Person D** | **Screens & Story** | The dashboard/website, the pitch deck, the demo video, deploying it | Good at design/frontend, or the best communicator |

### ⚠️ Two warnings about picking jobs

**1. Give the Money Brain (Person C) to your best builder.**
This is the only part of the project that no other team in the competition has. If it fails, you've built a nice complaint-list — which is what *everyone else* built.

**2. Person D is NOT "the person who makes slides at the end."**
Person D starts on Day 1, building the screens using the sample data that already exists. In a competition, a demo that actually runs beats a clever feature nobody sees.

### If someone is struggling
Swap *tasks*, not *workstreams*. Person A can help Person D. But don't let one person drift away — every person must commit code **every single day**. That's your proof you built this during the competition (it's one of the rules).

---

# Part 5 — The 9 days

---

## 📅 DAY 1 (Friday 18 Sep) — Make the AI actually work

**Today's goal:** The AI (Gemini) should correctly understand complaints in all Indian languages.

### Person A — Voice
- **Task:** Add speech-to-text. When someone speaks, turn it into written words.
- **Use:** Bhashini (free, made by the Government of India) first. If that fails, try Sarvam, then Google.
- **File:** `backend/services/telephony/base.py`
- ✅ **Done when:** You play a Marathi voice clip and the correct Marathi text appears on screen.

### Person B — AI
- **Task 1:** Put your API key in and test the AI with all 8 sample languages.
- **Task 2 (important):** ⚠️ Right now, our simple fallback treats **all Devanagari text as Hindi**. Marathi also uses Devanagari. So Marathi complaints are being labelled Hindi, and the reply SMS goes out in the wrong language. **Fix this** so the AI correctly tells Marathi and Hindi apart.
- ✅ **Done when:** You send a Marathi complaint and it comes back as `mr` (Marathi), not `hi` (Hindi).

### Person C — Money Brain
- **Task:** Read `backend/engine/allocate.py` carefully until you understand every line. Then write 3 tests that check it behaves correctly.
- ✅ **Done when:** Your tests pass and you can explain the file to the rest of the team in 5 minutes.

### Person D — Screens
- **Task:** Click through every single tab of the dashboard with the system running. Write down everything that's broken, ugly, missing, or confusing.
- ✅ **Done when:** You have a written list. Share it in the group chat.

### ✅ How do we know today is done?
You send a Marathi complaint through the system and it comes back with the right problem type, the right location, and gets sent to the right department — **using the real AI**, not the fallback.

---

## 📅 DAY 2 (Saturday 19 Sep) — Phone channels + the fairness story

**Today's goal:** The phone flow works end to end, and the fairness fix is visible on screen.
*(It's the weekend — put in a long day today.)*

### Person A
- **Task:** Make the missed-call flow work fully in the simulator:
  1. Citizen gives a missed call
  2. We call back and speak the greeting in their language
  3. They speak
  4. We read the problem back to them and ask them to press 1 to confirm
  5. They get an SMS with their complaint number
- ✅ **Done when:** You can demonstrate the whole flow in the browser, start to finish.

### Person B
- **Task:** Make the fairness fix *visible*. Right now it works, but nobody can see *why*.
  Show on screen:
  - How many complaints an area actually sent
  - How many it **would have** sent with normal connectivity
  - The multiplier we applied (like ×1.50)
- ✅ **Done when:** The website shows these three numbers for every hotspot.

### Person C
- **Task:** Department routing. Load `data/routing.json` and make sure every complaint goes to the right department — including the difference between **rural** roads (PMGSY) and **city** roads (State PWD).
- ✅ **Done when:** You test 10 sample complaints and all 10 go to the correct department.

### Person D
- **Task:** Build the **"Bias correction" tab** properly. This is the emotional centre of your demo.
  It must clearly show side by side:
  > **Pune: 51 complaints → rank 228**
  > **Nandurbar: 13 complaints → rank 4**
- ✅ **Done when:** Someone who knows nothing about the project looks at that tab and says "oh, that's unfair — and you fixed it."

### ✅ How do we know today is done?
The missed-call flow works, and the fairness comparison is clearly visible on screen.

---

## 📅 DAY 3 (Sunday 20 Sep) — 🔗 INTEGRATION DAY 1

**Today's goal: Everything works together as ONE system.**

### ⛔ Everyone stops adding new features at 6pm today.

From 6pm, the whole team does this together:

1. Everyone **saves their work to GitHub** (`git add .` → `git commit` → `git push`)
2. Pull everyone else's work (`git pull`)
3. Run the whole system and test the **complete journey**:
   > File a complaint → AI understands it → it gets routed → it joins a hotspot → fairness is applied → it gets scored → the allocator funds it → it appears on screen
4. **Fix every single thing that breaks.** No new features until this journey works perfectly.

### After the integration works, if you have time:
- **Person A:** Citizen tracking — someone sends `STATUS JS-2026-000401` by SMS and gets the current status back.
- **Person B:** Make the "how this score was calculated" page work for *every* hotspot, not just some.
- **Person C:** Add "expected result" data for all 44 projects (we need it for Day 6).
- **Person D:** 📱 **Record a rough 90-second video of the demo on your phone.** It's not for submission — it's to find out what's confusing. Watch it together and cringe. Then fix it.

### ✅ How do we know today is done?
One person can file a complaint and watch it become a funded project, live, without anyone touching the keyboard twice.

---

## 📅 DAY 4 (Monday 21 Sep) — Real data

**Today's goal:** Replace our made-up numbers with real government data where possible, and honestly label what we couldn't replace.

### Person B (main work today)
- **Task 1:** Go to **data.gov.in** and download real data for: population, literacy, poverty (BPL), and SC/ST population, for our 48 areas.
- **Task 2:** Where you **cannot** find real data, keep our sample numbers — but write it down honestly in a file called `data/PROVENANCE.md`.
- **Task 3:** Build the "how badly is this area lacking?" score properly using real sources: PMGSY (roads), Jal Jeevan Mission (water), NFHS (health), UDISE (schools).
- ✅ **Done when:** `PROVENANCE.md` lists every dataset, where it came from, its licence, and the date you downloaded it.

### Person C
- **Task:** Scheme eligibility. A project should only be funded if it's allowed under a real government scheme. Include the funding split (e.g. 60% central government, 40% state).
- ✅ **Done when:** You mark one project as ineligible, and the system rejects it and explains exactly which condition it failed.

### Person D
- **Task:** Add drill-down to the dashboard: click a state → see districts → click a district → see blocks. Plus filters by problem type.
- ✅ **Done when:** You can go from "all of India" down to one specific block by clicking.

### 💡 Why today matters
Judges will ask *"is this real data?"* Being honest — "these numbers are real, these are realistic estimates, here's the list" — is far more impressive than pretending everything is real.

---

## 📅 DAY 5 (Tuesday 22 Sep) — ★ Make the allocator amazing

**Today's goal:** The money allocator becomes the most impressive thing in your project.

### Person C (main work today)
- **Task 1:** Speed. When someone drags the budget slider, the answer must appear in **under 0.4 seconds**. If it's slower, use the "fast" setting while dragging and the exact setting when they let go.
- **Task 2:** "Why wasn't this funded?" Every rejected project must show a plain-English reason and how much more money it would have needed.
- **Task 3:** Push the "poorest areas" percentage up high (60%, 70%) and check the trade-off graph visibly bends. If it stays flat, the setting isn't actually doing anything.
- ✅ **Done when:** Dragging the budget from ₹40 crore down to ₹4 crore is genuinely impressive to watch.

### Person B
- **Task:** Use AI to write a **policy brief** — a short summary a government officer could actually read. Plus a "note for the committee" that can be downloaded.
- ✅ **Done when:** One button, one click, produces a clean readable document.

### Person D
- **Task:** Build out the Allocator screen properly: budget slider, poorest-areas slider, live updating, the trade-off graph, and the "which rules are blocking us" report.
- ✅ **Done when:** This tab looks like a product, not a school project. **This is the demo.**

### ✅ How do we know today is done?
You show someone the budget slider and they say "wow."

---

## 📅 DAY 6 (Wednesday 23 Sep) — 🔗 INTEGRATION DAY 2 + measuring results

### ⛔ Everyone stops and merges at 6pm. After today, the feature list is FROZEN.

### Person B
- **Task:** Our area ID codes are currently fake placeholders. Replace them with **real codes** from https://lgdirectory.gov.in
- ✅ **Done when:** Every complaint maps to a real, correct government area code.

### Person C
- **Task 1:** Finish the impact measurement. For each finished project, find a **similar area that did NOT get the project** and compare what happened to both. That's how you know if the project actually caused the improvement.
- **Task 2:** The learning loop. If road projects keep delivering less than promised, the system should automatically lower road projects' priority next time.
- ✅ **Done when:** You can show a number for "roads delivered 82% of what was promised."

### Person A
- **Task:** Citizen checking. After a project is "complete", let citizens send a **photo and a comment**. AI checks whether the work really looks finished.
- ✅ **Done when:** You upload a photo of an unfinished road and the system correctly says "not complete."

### Person D
- **Task:** The other-countries screen. Switch from India to Brazil and the **same system runs** on Brazil's settings. Then add a 6th country live, in front of people.
- ✅ **Done when:** You switch country and everything still works.

---

## 📅 DAY 7 (Thursday 24 Sep) — Real photo checking + the story

| Person | Task |
|---|---|
| **B** | Install `google-genai` and make photo checking actually look at the image (right now it only reads the text comment). |
| **B** | In `backend/engine/impact.py` there's a temporary guess number (0.15) for "how much would this area have improved anyway?" Replace it with something defensible, and **write a comment explaining it**. |
| **A** | Finish WhatsApp and the offline village-kiosk channel. All 6 ways to contact us should work. |
| **C** | Create sample data for 12 finished projects — some certified as good, some flagged as incomplete. |
| **D** | **Draft the pitch deck.** All 12 slides, with real screenshots. Not pretty yet — just complete. |

### ✅ How do we know today is done?
The photo check returns a real answer, and the deck draft is shared with the team.

---

## 📅 DAY 8 (Friday 25 Sep) — 🚀 Deploy, record, ⛔ FREEZE AT 6PM

| Person | Task |
|---|---|
| **A** | Create a Dockerfile and deploy to Google Cloud Run or Render. **Start this in the morning** — deploying always takes 3× longer than you think. |
| **B** | Finish `PROVENANCE.md`. Then **turn off your internet** and run everything. Nothing should crash — things should just get simpler. |
| **C** | Create the final demo data: 100+ complaints in many languages across 5 states, plus 12 completed projects. |
| **D** | 🎥 **Record the 3–5 minute demo video.** Do at least 3 takes. Check the audio is clear and the text is readable on a phone screen. |
| **Everyone** | ⛔ **After 6pm: only bug fixes, the deck, the README, and the video. NO new features.** |

### ✅ How do we know today is done?
The live website works when opened in a fresh browser with no login and no setup.

---

## 📅 DAY 9 (Saturday 26 Sep) — 📦 SUBMIT

Tick these off:

- [ ] Run the full demo 3 times, timed, under 5 minutes each
- [ ] Re-record any part of the video where you stumble
- [ ] Final deck: 10–12 slides
- [ ] README: live link at the top, setup instructions, how it works
- [ ] `PROVENANCE.md` finished, `LICENSE` present, GitHub history clean and pushed
- [ ] Repo is public (or you've given access to `build-with-ai-india@googlegroups.com`)
- [ ] Submission form filled: **code · video · deck · 2–3 line description · live link**
- [ ] **Submit with hours to spare, not minutes**

---

# Part 6 — The demo (3–5 minutes)

Practise this until it takes exactly 4 minutes.

| Time | What happens | What's on screen |
|---|---|---|
| **0:00–0:40** | **The missed call.** A farmer with a basic keypad phone gives a missed call. No app, no internet, no English. We call back in Marathi. She speaks. | The Single Helpline tab |
| **0:40–1:15** | **One number, no menu.** The AI understands it, reads it back, she presses 1. Complaint created, sent to the correct department, SMS reply in Marathi with a complaint number. | Complaint + SMS outbox |
| **1:15–1:50** | **The fairness moment.** Pune: 51 complaints → rank 228. Nandurbar: 13 complaints → rank 4. Show the fix flipping it. | Bias correction tab |
| **1:50–2:45** | **★ The money allocator.** ₹40 crore → 27 projects → 553,365 people → ₹722 each. Now drag the budget to ₹12 crore. It re-solves live, then honestly tells you covering every area needs ₹26.30 crore. | Allocator tab |
| **2:45–3:25** | **★ The people check the work.** A citizen photo arrives. AI says "only 40% complete." Score 0.38 → ⚠️ payment held. Compare with a properly finished one scoring 0.91. | Impact tab |
| **3:25–3:55** | **Results + other countries.** Show what was promised vs delivered. Then switch to Brazil — the same system, no code changes. | Impact + adapters |
| **3:55–4:30** | **It's built to be reused.** Show how it plugs into India's existing government systems. Open source, privacy-compliant, one-command setup. | Documentation |

**Closing line:**
> *"One number instead of forty departments. A missed call instead of a smartphone. And the people who reported the problem are the ones who certify the fix — because no one else is standing on that road."*

---

# Part 7 — Rules everyone must follow

1. **The AI never decides the score.** It only explains and sorts things. All numbers come from our own maths. (This matters — if you ask AI for "a score out of 100" it just makes something up.)
2. **When the rules can't all be met, say so.** Never show an empty result and never crash. Always explain which rule couldn't be kept and suggest a fix.
3. **The demo must work with no internet.** Every AI feature needs a simple backup. Test by turning off your wifi.
4. **Save your work to GitHub every single day.** Every person, every day. This is your proof you built it during the competition.
5. **The main version of the code must always work.** If you break it, fix it before you sleep.
6. **Admit your limitations in the presentation.** We have three: some numbers are estimates, one comparison number is a temporary guess, and the fairness fix adjusts what people *did* report rather than magically finding problems nobody mentioned.

---

# Part 8 — Simple glossary

| Word | What it actually means |
|---|---|
| **Hotspot** | A group of complaints about the same problem in the same area |
| **Bias correction** | Fixing the unfairness that rich/connected areas send more complaints |
| **Allocator** | The part that decides which projects get the money |
| **LGD code** | The government's official ID number for a village/block area |
| **Scheme** | A government programme with its own rules and budget (like PMGSY for roads) |
| **SOR** | The government's official price list for construction work |
| **NIDI** | Our "how badly is this area lacking?" score (0 to 1) |
| **Equity floor** | A rule that at least X% of money must reach the poorest areas |
| **Relaxation ladder** | If the rules contradict each other, we drop them one at a time and tell you which we dropped |
| **Frontier** | A graph showing the trade-off: helping the most people vs helping the poorest |
| **Social audit score** | What citizens say about whether the work was really finished |
| **Realization ratio** | Promised result vs actual result (1.0 = exactly as promised) |
| **Counterfactual** | Comparing with a similar area that did NOT get the project, to see if the project really caused the improvement |
| **Fixture** | A sample data file so you can build your part without waiting for someone else |
| **Endpoint** | A web address your program responds to (like `/api/v1/allocate/`) |
| **Commit / push** | Saving your work / sending it to GitHub |
| **Merge** | Combining everyone's work together |
| **Workstream** | One person's area of responsibility |
| **STT / TTS** | Speech-to-text (voice → words) / Text-to-speech (words → voice) |
| **Main branch** | The main, working version of the code |

---

# Part 9 — If something breaks

| Problem | What to do |
|---|---|
| `ModuleNotFoundError: No module named 'pulp'` | You forgot to activate the virtual environment. Run `source .venv/bin/activate` again. |
| The website won't start, "port already in use" | Another copy is running. Close it, or use `--port 8001`. |
| The AI isn't responding / everything says "fallback" | Your key is wrong or the model name is wrong. Test the exact model name in AI Studio. |
| Everyone's changes conflict on GitHub | Pull first (`git pull`), fix the conflicting lines together, then commit. Don't work on the same file at the same time. |
| The allocator returns nothing | You've set rules that contradict each other (e.g. too high a poorest-areas %). Lower the sliders and watch the message it gives you. |
| It works on my machine but not theirs | Delete `.venv` and reinstall from `requirements.txt`. Then compare Python versions. |
| Everything is slow | Use the "fast solver" checkbox, and don't recompute the trade-off graph on every slider movement. |

---

# Part 10 — The 2–3 line description (for the submission form)

> **JanSetu (जनसेतु)** turns fragmented citizen voice — via a single toll-free number, missed call, or SMS on any handset, in any Indian language — into a costed, scheme-compliant public investment portfolio. A Gemini-powered routing brain sends each complaint to the right department, a bias-correction model stops under-connected communities being drowned out, and an optimiser allocates a fixed budget to maximise citizens reached per rupee under equity and geographic-spread constraints. Citizens then photograph and certify the finished work, giving government an audited impact ledger instead of self-reported completion.

---

*JanSetu (जनसेतु) — "the people's bridge." Good luck, team of 4. Build it, then prove it worked.*
