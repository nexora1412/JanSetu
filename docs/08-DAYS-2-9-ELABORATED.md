# Days 2–9 — Every Step Explained

Same format as the Day 1 guide: **What → Exactly how → How to test → If it fails.**

---

# 📅 DAY 2 — The phone flow + the fairness story

---

## 👤 PERSON 1 — The missed-call flow

### What you're building
The moment that opens your demo: a farmer gives a **missed call** from a basic phone. We call back, ask in Marathi what's wrong, she speaks, we read it back, she presses 1. Done.

### Step 1 — Look at what exists (10 min)
Open `backend/services/telephony/simulator.py`. You already have:
- `simulate_missed_call()` — logs an incoming missed call
- `greeting(language)` — the greeting in 6 languages
- `make_call()` — "places" a call (adds to the outbox)
- `ack()` — the confirmation SMS template

**What's missing:** the middle of the flow — reading the problem back and getting a keypress.

### Step 2 — Add the read-back step
Add this method to `SimulatorProvider`:

```python
CONFIRM_TEMPLATES = {
    "hi": "आपकी समस्या — {summary}। क्या यह सही है? हाँ के लिए 1, नहीं के लिए 2 दबाएँ।",
    "mr": "आपली समस्या — {summary}। हे बरोबर आहे का? होय साठी 1, नाही साठी 2 दाबा.",
    "en": "Your problem — {summary}. Is this correct? Press 1 for yes, 2 for no.",
    "bn": "আপনার সমস্যা — {summary}। সঠিক? হ্যাঁর জন্য 1, না এর জন্য 2 চাপুন।",
    "ta": "உங்கள் பிரச்சனை — {summary}. சரியா? ஆம் என்றால் 1, இல்லை என்றால் 2.",
    "te": "మీ సమస్య — {summary}. ఇది సరైనదా? అవును అయితే 1, కాదు అయితే 2.",
}

def confirm_prompt(self, summary: str, language: str = "en") -> str:
    tmpl = self.CONFIRM_TEMPLATES.get(language, self.CONFIRM_TEMPLATES["en"])
    return tmpl.format(summary=summary)
```

### Step 3 — Handle the keypress
In `parse_inbound`, you already capture `payload.get("dtmf")`. Now use it:

```python
if channel == "ivr":
    dtmf = payload.get("dtmf")
    meta["dtmf"] = dtmf
    if dtmf == "1":
        report["status"] = "acknowledged"     # citizen confirmed
    elif dtmf == "2":
        report["status"] = "needs_retry"      # we got it wrong, ask again
```

### Step 4 — Wire the full sequence in the dashboard
Add a **"Simulate full call"** button to the Single helpline tab that does all of this in order and shows each step:

1. `simulate_missed_call()` → show "📞 Missed call received"
2. `make_call(..., greeting)` → show "📞 Calling back… 'कृपया आपली समस्या सांगा'"
3. `transcribe(audio)` → show "🎙️ She said: '<transcript>'"
4. `structure_report(transcript)` → show "🤖 Understood: roads, severity 4"
5. `confirm_prompt(summary)` → show "📞 Reading back… press 1"
6. On DTMF 1 → create ticket → show "✅ Ticket JS-2026-000401, SMS sent"

### ✅ How to test it
Click your new button. All 6 steps appear in order, with real content in the right language.

### If it fails
- **No transcript** → your STT key isn't set (Person 1, Day 1 Step 3)
- **Wrong language greeting** → `detect_language` is returning the wrong code (Person 2's Day 1 bug)
- **Button does nothing** → open your browser's console (F12) to see the JavaScript error

---

## 👤 PERSON 2 — Make the fairness fix visible

### What you're doing
The fairness maths already works. But right now nobody can see **why** a hotspot got bumped up. You're exposing the working.

### Step 1 — See what's already there (5 min)
```bash
curl "http://localhost:8000/api/v1/hotspots/?limit=2" | python3 -m json.tool
```

Find the `demand` block. You already have:
```json
"demand": {
  "raw": 0.42, "expected_reports": 19.5, "observed_reports": 13,
  "bias_factor": 1.5, "adjusted": 0.63, "model": "wls_fitted"
}
```

`expected_reports` = how many this area *would* have sent at normal connectivity.
`observed_reports` = how many it actually sent.
`bias_factor` = the multiplier we applied.

### Step 2 — Add a plain-English explanation
Open `backend/engine/bias.py`. There's already an `explain()` method. Add this to the hotspot output in `backend/engine/score.py`:

```python
h["demand"]["explanation"] = (
    f"This area sent {h['demand']['observed_reports']:.0f} complaints, but with "
    f"average phone and internet it would have sent about "
    f"{h['demand']['expected_reports']:.0f}. We scaled its demand "
    f"{'UP' if h['demand']['bias_factor'] > 1 else 'DOWN'} by "
    f"{abs(h['demand']['bias_factor'] - 1) * 100:.0f}%."
)
```

### Step 3 — Show the model's coefficients
In `score_all()`, the lineage already includes `bias_coefficients`. Add a human-readable line to the API response so Person 3 can display it:

```python
h["lineage"]["bias_plain"] = (
    "We predicted how easily each area can complain using literacy, internet "
    "access, phone ownership and whether it's a city. Areas that complain less "
    "than predicted get their demand scaled up."
)
```

### ✅ How to test it
```bash
curl "http://localhost:8000/api/v1/hotspots/?limit=1" | python3 -c "
import json,sys
h = json.load(sys.stdin)['hotspots'][0]
print(h['demand'].get('explanation'))
print(h['lineage'].get('bias_plain'))
"
```

You should read a sentence that a non-technical person would understand.

---

## 👤 PERSON 3 — The Bias tab

### What you're building
The emotional centre of your demo. Someone who knows nothing about the project must look at it and say *"oh, that's unfair — and you fixed it."*

### Step 1 — The data is already there
```bash
curl "http://localhost:8000/api/v1/hotspots/?limit=400" > /tmp/hs.json
```

Each hotspot has `report_count`, `demand.bias_factor`, `priority_score`, `rank`.

### Step 2 — Build the side-by-side comparison
In `backend/static/index.html`, find the `loadHotspots()` function. Replace the `#flip` block with a clean two-card comparison:

```javascript
const loud = [...rows].sort((a,b)=>b.report_count-a.report_count)[0];
const silent = [...rows].filter(h=>h.demand.bias_factor>1.2)
                        .sort((a,b)=>b.priority_score-a.priority_score)[0];

$('#flip').innerHTML = `
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <div style="background:#331414;border:1px solid #ff6b6b;border-radius:8px;padding:12px">
      <div style="color:#ff6b6b;font-weight:800;font-size:12px">LOUD AREA — well connected</div>
      <div style="font-size:26px;font-weight:800;margin:6px 0">${loud.report_count} complaints</div>
      <div class="mono">rank #${loud.rank} · score ${loud.priority_score.toFixed(1)}</div>
      <div style="margin-top:8px;font-size:12px;color:#93a0c4">
        Scaled DOWN ×${loud.demand.bias_factor.toFixed(2)}
      </div>
    </div>
    <div style="background:#0f2a20;border:1px solid #3ddc97;border-radius:8px;padding:12px">
      <div style="color:#3ddc97;font-weight:800;font-size:12px">SILENT AREA — poorly connected</div>
      <div style="font-size:26px;font-weight:800;margin:6px 0">${silent.report_count} complaints</div>
      <div class="mono">rank #${silent.rank} · score ${silent.priority_score.toFixed(1)}</div>
      <div style="margin-top:8px;font-size:12px;color:#93a0c4">
        Scaled UP ×${silent.demand.bias_factor.toFixed(2)}
      </div>
    </div>
  </div>
  <div style="margin-top:12px;font-size:13px">
    <b>${silent.report_count} complaints beat ${loud.report_count}.</b>
    Without this correction, public money follows whoever has the best phone
    signal — not whoever has the worst road.
  </div>`;
```

### ✅ How to test it
Open the Bias tab. You should see two cards, red and green, and the sentence. Show it to someone who hasn't seen the project. If they "get it" in under 10 seconds, you're done.

---

# 📅 DAY 3 — 🔗 INTEGRATION DAY 1

## What integration day means
Everyone stops adding features at 6pm. You combine all three people's work and test the **whole journey**.

### Step 1 — Everyone saves their work (5 min)
```bash
git add .
git commit -m "Day 3: <what you did>"
git push
```

### Step 2 — Everyone pulls (5 min)
```bash
git pull
```

**If you get a conflict**, don't panic:
1. Open the file Git says is conflicted
2. Look for `<<<<<<< HEAD` … `=======` … `>>>>>>>`
3. Talk to the other person and decide which version to keep
4. Delete the marker lines, save, then `git add . && git commit`

### Step 3 — Restart and test the full journey (30 min, together)
```bash
uvicorn app.main:app --reload --port 8000
```

Then walk this path out loud, all three of you watching:

| # | Action | Where | Expected |
|---|---|---|---|
| 1 | File a Marathi complaint | Single helpline tab | Ticket `JS-2026-xxxxxx` created |
| 2 | Check it was understood | Same screen | sector = roads, LGD code present |
| 3 | Check routing | Same screen | "PMGSY / Zilla Parishad" |
| 4 | Check the SMS | Outbox section | Hindi/Marathi confirmation |
| 5 | Recompute hotspots | Run `curl -X POST localhost:8000/api/v1/score/recompute -H 'Content-Type: application/json' -d '{}'` | Your new complaint is in there |
| 6 | Allocate | Allocator tab → Solve | A portfolio appears |
| 7 | Check impact | Impact tab | Rows present |

**Write down every step that fails.** Fix them together, in priority order.

### Step 4 — Person 3 records a rough demo (20 min)
Phone camera. 90 seconds. Narrate as you go:
> *"A farmer gives a missed call… we call back… she speaks Marathi… the AI understands it's a road problem in Dhule… it goes to PMGSY… now watch the money allocator…"*

Watch it back together. Note every "wait, what's that?" moment. **Those are your demo's weak points.** Fix them on Days 4–5.

### ✅ Day 3 is done when
One person can do steps 1→7 without anyone touching the keyboard twice.

---

# 📅 DAY 4 — Real data + citizen tracking

---

## 👤 PERSON 1 — Citizen tracking portal

### Step 1 — The endpoint already exists
```bash
curl http://localhost:8000/api/v1/track/JS-2026-000001
```

Returns status, sector, department, SLA.

### Step 2 — Build the page
Add a section to the dashboard (or a new tab) with a ticket-number box:

```html
<div class="card">
  <h3>Track your complaint</h3>
  <div class="row">
    <input id="ticket" placeholder="JS-2026-000401" style="flex:1"/>
    <button onclick="track()">Track</button>
  </div>
  <pre id="track-out" class="mono"></pre>
</div>
```

```javascript
async function track(){
  const id = $('#ticket').value.trim();
  const r = await fetch('/api/v1/track/' + encodeURIComponent(id));
  const d = await r.json();
  $('#track-out').textContent = r.ok
    ? JSON.stringify(d, null, 2)
    : 'Not found: ' + id;
}
```

### Step 3 — Make `STATUS` work by SMS
Add to `app/main.py`:

```python
@app.post("/api/v1/telephony/inbound-sms")
def inbound_sms(body: dict):
    """Citizen texts e.g. 'STATUS JS-2026-000401' to our short code."""
    text = (body.get("text") or "").strip().upper()
    if text.startswith("STATUS"):
        ticket = text.split()[-1] if len(text.split()) > 1 else None
        if ticket:
            r = next((x for x in REPORTS if x.get("report_id") == ticket), None)
            if r:
                return {"reply": f"JanSetu: {ticket} is '{r.get('status')}' with "
                                 f"{(r.get('routing') or {}).get('department')}."}
    return {"reply": "Send STATUS followed by your complaint number."}
```

### ✅ Test
```bash
curl -X POST localhost:8000/api/v1/telephony/inbound-sms \
  -H 'Content-Type: application/json' \
  -d '{"text":"STATUS JS-2026-000401"}'
```

---

## 👤 PERSON 2 — Real data

### Step 1 — What to download
Go to **https://data.gov.in** and search for:
- "Census 2011 population district" → population
- "Census 2011 literacy rate" → literacy
- "SECC 2011" or "BPL households" → poverty
- "SC ST population census 2011" → social composition

Filter to our 5 states: Maharashtra, Bihar, Uttar Pradesh, West Bengal, Tamil Nadu.

### Step 2 — Match to our areas
Our file `data/lgd_admin.csv` has 48 blocks. Open `data/census_seed.csv` — same 48 rows, with columns `population`, `literacy_rate`, `female_literacy_rate`, `sc_st_share`, `bpl_share`, `phone_penetration`, `net_penetration`.

Replace the columns you found real data for. **Leave the rest as-is.**

> ⚠️ **Do not change `digital_access_index`.** It's derived from the other columns. If you change literacy/phone/net, recompute it:
> `DAI = 0.45*phone + 0.35*net + 0.20*literacy`

### Step 3 — Write down the truth
Create `data/PROVENANCE.md`:

```markdown
# Data provenance

| Column | Real or estimate? | Source | Downloaded | Licence |
|--------|-------------------|--------|------------|---------|
| population | REAL | Census 2011, data.gov.in | 22-Sep-2026 | Open Govt Data Licence |
| literacy_rate | REAL | Census 2011 | 22-Sep-2026 | Open Govt Data Licence |
| bpl_share | ESTIMATE | Calibrated to NFHS-5 ranges | — | — |
| phone_penetration | ESTIMATE | Calibrated to TRAI subscriber data | — | — |
| lgd_block_code | SYNTHETIC | Placeholder — real codes pending | — | — |
```

**Why this matters:** judges will ask "is this real data?" Answering honestly beats pretending.

### ✅ Test
Restart and re-run:
```bash
cd backend && python generate_fixtures.py
```
The Nandurbar-vs-Haveli flip should still work. If it broke, your new numbers removed the connectivity gap — check `digital_access_index` got recomputed.

---

# 📅 DAY 5 — ★ Make the allocator amazing

---

## 👤 PERSON 2 — Speed and explanations

### Step 1 — Measure the speed first
```bash
curl -s -X POST localhost:8000/api/v1/allocate/ \
 -H 'Content-Type: application/json' \
 -d '{"budget_inr":400000000,"equity_floor_pct":0.40,"geographic_spread":"min_one_per_block","weights":{"demand":0.30,"deficit":0.25,"reach":0.20,"equity":0.15,"feasibility":0.10}}' \
 | python3 -c "import json,sys; d=json.load(sys.stdin); print('solve_ms =', d['solver']['solve_ms'])"
```

**Under 400?** You're done, skip to Step 3.
**Over 400?** Continue.

### Step 2 — Make it faster
Two levers:
1. Use the fast solver while dragging: set `"fast": true` in the request
2. Don't recompute the frontier on every drag — the dashboard should call `/api/v1/frontier/` once, not inside `allocate()`

In `allocate.py`, `compute_frontier()` is already called on every allocate. Move it out:

```python
# In app/main.py — only compute the frontier when explicitly asked
@app.post("/api/v1/allocate/")
def allocate_endpoint(req: AllocationRequest, with_frontier: bool = False):
    ...
    result["frontier"] = compute_frontier(...) if with_frontier else []
    return result
```

### Step 3 — "Why wasn't this funded?"
Already implemented in `_dropped()` in `allocate.py`. Verify:

```bash
curl -s -X POST localhost:8000/api/v1/allocate/ \
 -H 'Content-Type: application/json' \
 -d '{"budget_inr":40000000,"equity_floor_pct":0.40,"geographic_spread":"none","weights":{"demand":0.30,"deficit":0.25,"reach":0.20,"equity":0.15,"feasibility":0.10}}' \
 | python3 -c "
import json,sys
d=json.load(sys.stdin)
for x in d['dropped'][:5]: print(f\"{x['reason']:<22} {x['detail']}\")"
```

Every row must have a reason. If any say "below_cutoff" with an unhelpful detail, improve the message.

### Step 4 — Prove the equity rule works
```bash
for F in 0 20 40 60 80; do
  curl -s -X POST localhost:8000/api/v1/allocate/ \
   -H 'Content-Type: application/json' \
   -d "{\"budget_inr\":400000000,\"equity_floor_pct\":0.$F,\"geographic_spread\":\"min_one_per_block\",\"fast\":true,\"weights\":{\"demand\":0.30,\"deficit\":0.25,\"reach\":0.20,\"equity\":0.15,\"feasibility\":0.10}}" \
   | python3 -c "
import json,sys; t=json.load(sys.stdin)['totals']
print(f'equity floor 0.$F → {t[\"beneficiaries\"]:>9,} people   equity share {t[\"equity_share\"]:.0%}')"
done
```

**✅ The number of people must go DOWN as the equity floor goes UP.** That's the trade-off. If it stays flat, the equity constraint isn't binding — check that not every project is flagged as deprived.

---

## 👤 PERSON 3 — The Allocator screen

This tab IS your demo. Requirements:
- Budget slider that re-solves as you drag (debounced — wait 200ms after they stop)
- Equity floor slider
- Big numbers: projects funded, citizens reached, ₹ per citizen
- The frontier graph
- The "which rules are blocking us" table
- The "why wasn't this funded" list

### Debounce the slider (important — don't hammer the server)
```javascript
let timer;
$('#budget').oninput = e => {
  $('#lbl-budget').textContent = CR(e.target.value * 1e7);
  clearTimeout(timer);
  timer = setTimeout(solve, 200);   // wait 200ms after they stop dragging
};
```

---

# 📅 DAY 6 — 🔗 INTEGRATION DAY 2

### 👤 PERSON 1 — WhatsApp + kiosk
Add two channels to `simulator.py`:
- `whatsapp` — same as SMS but with a photo field
- `kiosk` — add `sync_id` and `offline_created_at` to the metadata (proves it was captured without signal and synced later)

### 👤 PERSON 2 — Real LGD codes + measuring results
**Real codes:** https://lgdirectory.gov.in → download the block-level list → match by state/district/block name → replace `lgd_block_code` in `data/lgd_admin.csv` and `data/census_seed.csv`.

**Counterfactual:** `backend/engine/impact.py` already has `match_control()`. Verify:
```bash
curl -s localhost:8000/api/v1/impact/ | python3 -c "
import json,sys
d=json.load(sys.stdin)
for l in d['ledger']: print(f\"{l['project_id']:<26} ρ={l['realization_ratio']:<6} control={l.get('counterfactual_control_block')}\")"
```

**Learning loop:** `update_sector_weights()` exists. Call it and show the output on the dashboard.

### 👤 PERSON 3 — Other countries
```bash
curl localhost:8000/api/v1/adapters/
```
Build a dropdown that lists the 5 nations. Switching should change the currency symbol, language list, and scheme names shown — **using the same engine**.

---

# 📅 DAY 7 — Real photo checking + the deck

### 👤 PERSON 2 — Make photo checking actually look at the image
```bash
pip install google-genai
```
In `services/gemini/client.py`, `verify_photo()` already has the SDK path — it activates automatically once the SDK is installed and a key is set.

Test:
```bash
python -c "
from services.gemini.client import verify_photo
print(verify_photo('Village road, 2km', 'road is half finished', image_b64=None))"
```

**Also today:** find the `0.15` in `backend/engine/impact.py` (the "how much would this area have improved anyway" guess). Replace it with something you can defend, and **write a comment explaining your reasoning.** Leaving a mystery number in your code is exactly what a judge will probe.

### 👤 PERSON 3 — Draft the deck
12 slides. Don't make it pretty yet — make it **complete**. Screenshot the dashboard for each. Outline in `docs/00-MASTER-PLAN.md` §12.

---

# 📅 DAY 8 — Deploy + record + freeze

### 👤 PERSON 1 — Deploy
Create `Dockerfile` in the project root:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/backend
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Deploy to Cloud Run:
```bash
gcloud run deploy jansetu --source . --region asia-south1 --allow-unauthenticated
```
Or push to Render.com (simpler if you've never used gcloud).

**Start this in the morning.** Deploying always takes 3× longer than you think.

### 👤 PERSON 2 — The offline test
1. Turn off your wifi
2. Run everything
3. **Nothing should crash.** Things should get simpler (fallback classifier, no transcription), but the allocator, scoring, bias fix, and dashboard must all still work.

This is not paranoia — judges' wifi fails.

### 👤 PERSON 3 — Record the video
3–5 minutes. At least 3 takes. Check: audio clear, text readable on a phone screen.

### ⛔ 6pm: FREEZE. Only bugs, deck, README, video.

---

# 📅 DAY 9 — Submit

Run through the final checklist in `docs/06-TEAM-OF-3-RUNBOOK.md` → Day 9.

**Submit with hours to spare, not minutes.**

---

# 🆘 Stuck? Quick fixes

| Symptom | Fix |
|---|---|
| Slider is slow | `fast: true` + debounce 200ms + don't recompute the frontier on drag |
| Equity floor does nothing | Too many projects flagged deprived — lower the threshold in `generate_fixtures.py` |
| `git push` rejected | `git pull` first, then push |
| Works locally, fails deployed | Check env vars are set on the host, and that `PORT` is 8080 |
| Dashboard blank after deploy | Check `/health` on the live URL first |
| Everything `fallback` on the live site | `GEMINI_API_KEY` not set in the host's environment |
