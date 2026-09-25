# Day 1 — Every Step Explained (no guessing)

**Goal for today:** the AI correctly understands complaints in Indian languages, voice becomes text, and we have a list of everything that needs fixing on screen.

Each task below has: **What to do → Exactly how → How to test it → If it fails.**

---

# 👤 PERSON 1 — Turn voice into text

## What you're building
Right now our system only accepts typed complaints. You're making it accept **spoken** ones. Someone speaks Marathi into a phone → we get Marathi text out.

**Good news: I already wrote the code.** It's in `backend/services/stt/`. Your job today is to get a key, put it in `.env`, and test it.

---

## Step 1 — Understand what's already there (5 min)

Open these two files and read them:
- `backend/services/stt/providers.py` — three providers: Sarvam, Bhashini, Google
- `backend/services/stt/__init__.py` — one function: `transcribe(audio_bytes, language)`

You call it like this:

```python
from services.stt import transcribe
result = transcribe(audio_bytes, language="mr")
# result = {"text": "धुळे तालुक्यात रस्ता खराब आहे", "language": "mr", "provider": "sarvam"}
# result = None   ← if nothing worked (this is fine, nothing crashes)
```

The order is controlled by `STT_CHAIN=sarvam,bhashini,google` in `.env`. If Sarvam fails, it tries Bhashini. If that fails, Google. If all fail → `None`. **It never crashes.** That's deliberate.

---

## Step 2 — Run the self-test BEFORE you get any key (2 min)

```bash
cd jansetu/backend
source ../.venv/bin/activate
python -m services.stt
```

You should see:

```
chain: ['sarvam', 'bhashini', 'google_chirp']
  sarvam         not configured (skipped)
  bhashini       not configured (skipped)
  google_chirp   not configured (skipped)
  any_configured = False

transcribe() with 0.4s silence -> None (correct: degraded safely, nothing crashed)

Self-test passed.
```

✅ **This is the correct result right now.** It proves the safety net works: with no keys, nothing crashes. Now let's add a key so it actually transcribes.

---

## Step 3 — Get a Sarvam AI key (15 min) — START HERE, it's the easiest

### 3a. Sign up
1. Go to **https://dashboard.sarvam.ai**
2. Sign up with your email
3. Verify your email
4. Log in

### 3b. Get your API key
1. Look for **"API Keys"** in the dashboard (usually left menu or under your profile)
2. Click **Create new key** / **Generate key**
3. Copy it. It looks like a long random string.

> ⚠️ Copy it immediately and paste it somewhere safe. Some dashboards only show it once.

### 3c. Put it in your `.env`
Open the `.env` file in your project folder and find this line:

```
SARVAM_API_KEY=
```

Paste your key directly after the `=`, with **no space**:

```
SARVAM_API_KEY=abc123your-actual-key-here
```

### 3d. Restart the server
The `.env` file is only read when the program starts. So:
1. Stop the server (`Ctrl+C` in the terminal where it's running)
2. Start it again: `uvicorn app.main:app --reload --port 8000`

### ✅ How to test it
```bash
cd jansetu/backend
python -m services.stt
```

You should now see:

```
  sarvam         configured     ← ✅ this changed!
```

**If it still says "not configured":** your key isn't being read. Check: no spaces around `=`, no quotes around the key, and you restarted the server.

---

## Step 4 — Test with real audio (20 min)

### 4a. Record a test clip
- Use your phone's voice recorder, or an online voice recorder
- Record yourself saying something in Marathi or Hindi, e.g. *"धुळे तालुक्यात रस्ता खराब आहे"*
- Save it as a **WAV** file (if it's m4a/mp3, convert it — search "mp3 to wav converter" online)
- Put it in your project folder, e.g. `jansetu/test-audio.wav`

> Keep it **under 30 seconds** — Sarvam's REST endpoint caps at 30s.

### 4b. Run this test script

Create a file `backend/test_my_audio.py` and paste this in:

```python
from services.stt import transcribe, status

print("Provider status:", status())

with open("../test-audio.wav", "rb") as f:
    audio = f.read()

print(f"\nAudio loaded: {len(audio)} bytes")

result = transcribe(audio, language="mr")   # change to "hi" for Hindi

print("\n--- RESULT ---")
if result:
    print("Text     :", result["text"])
    print("Language :", result["language"])
    print("Provider :", result["provider"])
else:
    print("No transcription. Check your key and that the file is a valid WAV.")
```

Run it:

```bash
cd jansetu/backend
python test_my_audio.py
```

### ✅ How you know it worked
You see the Marathi/Hindi words you actually spoke, printed on screen.

**If the text is wrong or empty:**
- Is the file really a WAV? Run `file ../test-audio.wav` — it should say "WAV audio". If it says MP3, convert it.
- Is it under 30 seconds?
- Is the language right? Try `language="hi"` instead of `"mr"`, or `"en"`.
- Speak more clearly and re-record. Background noise hurts a lot.

---

## Step 5 — (Optional, do this if you have time) Add Bhashini

**Why bother?** Bhashini is free and built by the Government of India. Saying *"we use India's national language AI"* in your presentation is a big credibility win. But it's fiddlier — do Sarvam **first**, and only come back here if you have time.

### 5a. Register
1. Go to **https://meity-auth.ulca.ai**
2. Register for an account
3. Log in
4. Create an "application" (this is how ULCA issues you credentials)

### 5b. Copy THREE values
- **User ID** — your ULCA user id
- **ULCA API Key** — the key for the config call
- **Pipeline ID** — the id issued to your app

### 5c. Put all three in `.env`
```
BHASHINI_USER_ID=your-user-id
BHASHINI_ULCA_API_KEY=your-ulca-key
BHASHINI_PIPELINE_ID=your-pipeline-id
```

### 5d. Understand the two-step dance (this is what confuses everyone)
Bhashini needs **two** calls:

1. **Config call** — you ask *"which model should I use for Marathi speech-to-text?"* Bhashini replies with a model ID (`serviceId`) **and a temporary inference key**.
2. **Inference call** — you send your audio with that model ID and that key.

I've already written both steps in `providers.py` (look for `_get_config` and `transcribe`). It also **caches** the config per language so it doesn't re-ask every time.

### 5e. Test just Bhashini
Change the chain to Bhashini only, then run the test:

```bash
cd jansetu/backend
export STT_CHAIN=bhashini
python test_my_audio.py
```

### If it fails
- **"not configured"** → one of the three values is missing or has a space
- **Config call fails** → your pipeline ID is probably wrong, or your app isn't approved yet. ULCA sometimes takes time. **Don't block on this** — Sarvam is enough for the demo.
- **Inference fails** → the temporary key expired; it's cached, so restart the server to force a fresh config call.

---

## Step 6 — Connect it to the intake (30 min, end of day)

Now make the real system use it. Open `backend/app/main.py` and find the **intake** endpoint. Add this where the report is built:

```python
from services.stt import transcribe

# If the channel is voice and we have audio, transcribe it first
if body.channel in ("voice_call", "missed_call", "ivr") and body.audio_uri:
    with open(body.audio_uri, "rb") as f:
        audio = f.read()
    stt = transcribe(audio, language=body.language_hint or "hi")
    if stt:
        body.text = stt["text"]           # use the transcript as the complaint
        body.language_hint = stt["language"]
```

### ✅ How to test it
Use the **Single helpline** tab on the dashboard:
1. Choose channel = "Toll-free voice call"
2. Choose a Marathi sample
3. Click **File report**
4. The structured result should show the transcription

### ✅ Day 1 is done for you when:
You record yourself speaking Marathi, run it through the system, and see the correct Marathi text come out the other side.

---

# 👤 PERSON 2 — Make the AI understand all languages

## Step 1 — Confirm the AI is actually on (5 min)

```bash
curl http://localhost:8000/api/v1/status
```

Look for `"gemini"`. You want:
```json
"gemini": {"configured": true, "model": "gemini-2.5-flash"}
```

**If `"configured": false`:** your key isn't in `.env`. Fix that first.

**If it says `true` but you're not sure it's really working**, run this:

```bash
cd jansetu/backend
python -c "
from services.gemini.client import structure_report
r = structure_report('धुळे तालुक्यात कुसुंबा गावाकडे जाणारा रस्ता पूर्णपणे खराब झाला आहे')
print('sector   :', r.get('sector'))
print('language :', r.get('language'))
print('extractor:', r.get('extractor'))
print('text_en  :', (r.get('normalized_text_en') or '')[:100])
"
```

✅ **If `extractor` says `gemini`** → the real AI is working.
❌ **If it says `fallback`** → the AI is NOT being reached. Your model name is wrong. Go to https://aistudio.google.com, run one message, see which model responds, and put that exact name in `.env` as `GEMINI_MODEL=`.

---

## Step 2 — Test all 8 languages (20 min)

Create `backend/test_languages.py`:

```python
from services.gemini.client import structure_report

SAMPLES = [
    ("mr", "धुळे तालुक्यात रस्ता खराब झाला आहे"),
    ("hi", "गया जिले में पानी की बहुत समस्या है"),
    ("bn", "মুর্শিদাবাদে বিশুদ্ধ পানির সমস্যা"),
    ("ta", "கடலூரில் சாலை மிகவும் மோசமாக உள்ளது"),
    ("te", "కడప జిల్లాలో విద్యుత్ సమస్య"),
    ("en", "The primary health centre has no doctor"),
    ("hi-Latn", "Bahraich mein bijli ki bahut problem hai"),
]

print(f"{'expected':<10} {'detected':<10} {'sector':<12} {'extractor':<10} ok?")
print("-" * 58)
for expected, text in SAMPLES:
    r = structure_report(text)
    detected = r.get("language", "?")
    sector = r.get("sector", "?")
    extractor = r.get("extractor", "?")
    # Language detection is hard; sector correctness is what really matters.
    ok = "✅" if sector not in ("other", "?") else "❌"
    print(f"{expected:<10} {detected:<10} {sector:<12} {extractor:<10} {ok}")
```

Run it:

```bash
python test_languages.py
```

### ✅ How you know it worked
At least **6 out of 7** rows show a sensible sector (roads / water / power / health) and `extractor = gemini`.

### If a row shows ❌
The AI misread the complaint. Open `backend/services/gemini/client.py`, find `STRUCTURE_PROMPT`, and make the instruction clearer. For example add:

```
- If the complaint mentions road, rasta, sadak, pul, bridge → sector is "roads"
- If it mentions paani, pani, water, handpump, nal → sector is "water"
```

Small prompt tweaks fix most of these. Change, re-run, repeat.

---

## Step 3 — 🐛 Fix the Marathi/Hindi bug (30 min) — IMPORTANT

### What's broken
Our fallback language detector works by looking at the **script** (the alphabet). Marathi and Hindi both use Devanagari script. So:

```
"धुळे तालुक्यात रस्ता खराब आहे"   →  detected as "hi"   ❌ WRONG, it's Marathi
```

The citizen then gets a reply SMS in Hindi instead of Marathi. It looks careless.

### Where the bug is
`backend/services/telephony/base.py` → the `detect_language` function. It has this rule:

```python
if re.search(r"[ऀ-ॿ]", text):
    return "hi"          # Devanagari covers hi + mr   ← the bug
```

### How to fix it
Two options:

**Option A (quick, do this first):** let the AI decide. In `detect_language`, if the script is Devanagari, ask Gemini:

```python
from services.gemini.client import _call

DEVANAGARI_HINT = """Which language is this: Hindi or Marathi?
Reply with JSON only: {"language": "hi"} or {"language": "mr"}
TEXT: \"\"\"{text}\"\"\""""

def detect_language(text):
    if not text:
        return "en"
    if re.search(r"[ऀ-ॿ]", text):
        # Devanagari is shared by Hindi and Marathi — ask the AI to tell them apart.
        raw = _call(DEVANAGARI_HINT.format(text=text[:300]))
        try:
            import json, re as _re
            m = _re.sub(r"^```(?:json)?|```$", "", (raw or "").strip(), flags=_re.M)
            lang = json.loads(m).get("language")
            if lang in ("hi", "mr"):
                return lang
        except Exception:
            pass
        return "hi"     # safe default when the AI is unavailable
    ...rest unchanged...
```

**Option B (no AI needed):** look for Marathi-specific characters. Marathi uses `ळ` (retroflex L) and `र्‍` much more than Hindi:

```python
if re.search(r"ळ|र्ह|न्ह|म्ह", text):
    return "mr"
return "hi"
```

**Do Option A first. Add Option B as the fallback when the AI is offline.**

### ✅ How to test it
```bash
python -c "
from services.telephony.base import TelephonyProvider as T
print('Marathi ->', T.detect_language('धुळे तालुक्यात रस्ता खराब आहे'))
print('Hindi   ->', T.detect_language('गया जिले में पानी की समस्या है'))
"
```

✅ **Done when:** the first line prints `mr` and the second prints `hi`.

---

## Step 4 — Show everyone a "before and after" (10 min)

Save the output of `test_languages.py` from **before** your fixes and **after**. You'll need the "after" for the deck.

### ✅ Day 1 is done for you when:
All (or nearly all) languages return the right sector, and Marathi is detected as `mr`.

---

# 👤 PERSON 3 — Find everything that's broken

## Step 1 — Click through everything (30 min)

With the server running, open **http://localhost:8000** and go through all 5 tabs:

1. **★ Allocator** — drag the budget slider. Does it update? Does the graph redraw?
2. **Bias correction** — do you see the loud-vs-silent comparison?
3. **Demand hotspots** — change the sector filter. Does the table change?
4. **Impact ledger** — are there rows? Do the numbers make sense?
5. **📞 Single helpline** — file a report. Does the acknowledgment appear?

## Step 2 — Write the list

Open a file `docs/UI-PUNCH-LIST.md` and write:

```markdown
# UI punch list — Day 1

| # | Severity | Tab | What's wrong | Who fixes |
|---|----------|-----|--------------|-----------|
| 1 | 🔴 blocker | Allocator | Frontier graph disappears at low budgets | Person 3 |
| 2 | 🟡 ugly    | Hotspots  | Numbers not aligned right             | Person 3 |
| 3 | 🟢 nice    | All       | Add a JanSetu logo in the header      | Person 3 |
```

Severity guide:
- 🔴 **blocker** — breaks the demo, fix first
- 🟡 **ugly** — works but looks bad
- 🟢 **nice** — polish, only if time

## Step 3 — Share it

Post the list in the group chat. Agree with Person 2 which blockers you're allowed to fix today.

### ✅ Day 1 is done for you when:
You have a written list of at least 10 items, shared with the team.

---

# 🌙 End of Day 1 — everyone does this

```bash
cd jansetu
git add .
git commit -m "Day 1: <what you did>"
git push
```

Then answer together in the group chat:
1. Did each person's "done when" check pass?
2. What's blocking anyone?
3. What's the plan for tomorrow?

---

# 🆘 If you're stuck

| Problem | Fix |
|---|---|
| `No module named 'services'` | You're in the wrong folder. `cd jansetu/backend` first. |
| `No module named 'pulp'` | Run `source ../.venv/bin/activate` |
| Key in `.env` but "not configured" | No spaces around `=`, no quotes, and **restart the server** |
| `extractor` always says `fallback` | Your `GEMINI_MODEL` name is wrong. Test it in AI Studio. |
| WAV file rejected | `file test-audio.wav` — if it says MP3, convert it |
| Audio over 30 seconds | Sarvam REST caps at 30s. Record shorter, or use the batch API. |
| Bhashini config call fails | Pipeline ID wrong or app not approved. Don't block — use Sarvam. |
