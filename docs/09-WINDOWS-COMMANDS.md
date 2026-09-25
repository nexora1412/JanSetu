# JanSetu — Windows Command Reference

> Every command in the other guides was written for Mac/Linux (bash).
> **You're on Windows PowerShell**, so some commands behave differently.
> This page gives you the Windows version of everything.

---

## ⭐ The easy fix: use Git Bash, and every command in the guides just works

**Strongly recommended.** One install, and then `source`, `curl`, `grep`, `export` all work exactly as written in the guides.

1. Download **Git for Windows**: https://git-scm.com/download/win
2. Install it (accept all defaults)
3. Open **Git Bash** from the Start menu
4. `cd` into your project and use every command from the guides **unchanged**

If you do this, you can ignore the rest of this page.

---

## If you stay in PowerShell

### The `curl` problem you just hit

In PowerShell, `curl` is an **alias** for `Invoke-WebRequest`, which tries to parse web pages and shows security warnings.

**Fix 1 — use `curl.exe` instead** (the real curl, built into Windows 10+):
```powershell
curl.exe http://localhost:8000/api/v1/status
```
Add the `.exe` and **every curl command in the guides works as written.**

**Fix 2 — PowerShell's own way:**
```powershell
(Invoke-WebRequest -Uri http://localhost:8000/api/v1/status -UseBasicParsing).Content
```

**Fix 3 — easiest of all: just open it in your browser.**
Paste `http://localhost:8000/api/v1/status` into Chrome. Done. No command needed.

---

## Side-by-side: bash vs PowerShell

| What you want | Mac/Linux (in the guides) | Windows PowerShell |
|---|---|---|
| Activate environment | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |
| Install packages | `pip install -r backend/requirements.txt` | *same* |
| Run python | `python3` | `python` |
| Set an env var (temporary) | `export STT_CHAIN=bhashini` | `$env:STT_CHAIN="bhashini"` |
| Make env var permanent | (in `.env` file) | (in `.env` file) — same |
| Fetch a URL | `curl -s URL` | `curl.exe -s URL` |
| Pretty-print JSON | `curl -s URL \| python -m json.tool` | `curl.exe -s URL \| python -m json.tool` |
| Search text | `grep "word" file` | `Select-String "word" file` |
| First 10 lines | `head -10 file` | `Get-Content file -TotalCount 10` |
| List files | `ls` | `dir` (or `ls`, works too) |
| Find a running process | `pgrep -f uvicorn` | `Get-Process python` |
| Kill the server | `Ctrl+C` | `Ctrl+C` |
| Force-kill the server | `pkill -f uvicorn` | `taskkill /F /IM python.exe` |

---

## Your exact startup sequence on Windows

```powershell
cd C:\Users\prana\Downloads\Downloads\jansetu

# Activate the virtual environment
.venv\Scripts\Activate.ps1

# You should now see (.venv) at the start of the line

# Install packages (only needed once, and again after I add any)
pip install -r backend/requirements.txt

# Start the server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000** in your browser.

---

## ⚠️ If `.venv\Scripts\Activate.ps1` gives a security error

You'll see something about "running scripts is disabled on this system". Fix it once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Type `Y` and press Enter. Then try the activate command again.

---

## Checking your setup (the command you were trying)

Pick whichever you prefer:

**Option A — browser (simplest):**
Open http://localhost:8000/api/v1/status

**Option B — real curl:**
```powershell
curl.exe -s http://localhost:8000/api/v1/status
```

**Option C — PowerShell native:**
```powershell
(Invoke-WebRequest -Uri http://localhost:8000/api/v1/status -UseBasicParsing).Content
```

You want to see:
```json
"env_file_found": true
"gemini": { "configured": true, ... }
```

If `"env_file_found": false` → your `.env` file isn't in the project root folder, or it's named wrong (must be exactly `.env`, not `.env.txt`).

---

## ⚠️ "The file is named .env.txt" — a common Windows trap

Windows Notepad loves to add `.txt`. Check with:
```powershell
dir .env*
```

If you see `.env.txt`, rename it:
```powershell
Move-Item .env.txt .env
```

Or create it from the command line to avoid the problem entirely:
```powershell
Copy-Item .env.example .env
notepad .env
```

---

## Testing the speech-to-text setup (Person 1)

```powershell
cd backend
python -m services.stt
```

Expected (before any keys):
```
sarvam        not configured (skipped)
bhashini      not configured (skipped)
google_chirp  not configured (skipped)
any_configured = False
Self-test passed.
```

After you add a Sarvam key to `.env` **and restart the server**, it should say:
```
sarvam        configured
```

---

## Copy-paste: replacing your `.env` on Windows

```powershell
Copy-Item .env.example .env
notepad .env
```

Paste your keys in, **save**, close Notepad, then **restart the server** (Ctrl+C, then run uvicorn again).

> The server only reads `.env` when it starts. Changing the file does nothing until you restart.
