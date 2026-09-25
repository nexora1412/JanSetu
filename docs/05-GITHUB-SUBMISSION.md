# JanSetu — GitHub & Submission Fields
## Copy-paste everything in the boxes below

---

## 1 · Create the repository

| Field | Value |
|---|---|
| **Owner** | your GitHub account (or a team org) |
| **Repository name** | `jansetu` |
| **Visibility** | ✅ **Public** |
| **Initialize with README** | ❌ **No** — you already have one; adding one causes a merge conflict |
| **Add .gitignore** | ❌ **No** — already in the repo |
| **Choose a license** | ❌ **No** — `LICENSE` (MIT) already in the repo |

Then push the code you already have:

```bash
cd jansetu
git init
git add -A
git -c user.name="Your Name" -c user.email="you@example.com" \
    commit -m "JanSetu: bias-corrected citizen demand → budget-optimal public investment"

git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/jansetu.git
git push -u origin main
```

> ⚠️ **Never commit `.env`.** It is already in `.gitignore`. If you ever do commit a key,
> revoke it in AI Studio immediately — GitHub scrapes exposed keys within minutes.

---

## 2 · The "About" box (top-right of your repo page)

Click the ⚙️ gear next to **About** and fill in:

**Description** *(short — shows in search results, keep under ~160 chars)*
```
JanSetu (जनसेतु) — AI that turns citizen voice into a costed, auditable public investment portfolio.
```

**Website**
```
(leave blank for now — see §5, Day 8)
```

**Topics** *(add all 20 — this is how judges and recruiters find you)*
```
hackathon
google-cloud
gemini
digital-public-good
dpi
india
civic-tech
artificial-intelligence
public-policy
social-impact
multilingual
nlp
fastapi
python
optimization
brics
government
infrastructure
speech-to-text
open-source
```

**Include in the home page:** ✅ Releases ✅ Packages (optional)

---

## 3 · Hackathon submission — "Brief description (2–3 lines)"

> **JanSetu (जनसेतु)** turns fragmented citizen voice — via a single toll-free number, missed
> call, or SMS on any handset, in any Indian language — into a costed, scheme-compliant public
> investment portfolio. A Gemini-powered routing brain sends each complaint to the right
> department, a bias-correction model stops under-connected communities being drowned out, and
> an optimiser allocates a fixed budget to maximise citizens reached per rupee under equity and
> geographic-spread constraints. Citizens then photograph and certify the finished work, giving
> government an audited impact ledger instead of self-reported completion.

---

## 4 · Hackathon submission checklist

| # | Required | Status |
|---|---|---|
| 1 | **Source code** — public GitHub repo | `github.com/<you>/jansetu` |
| 2 | **Demo video (3–5 min)** — end-to-end walkthrough | ⬜ Day 8 |
| 3 | **Pitch deck (10–12 slides)** | ⬜ Day 7–8 (outline in `00-MASTER-PLAN.md` §12) |
| 4 | **Brief description (2–3 lines)** | ✅ §3 above |
| 5 | **Deployed link** — live prototype | ⬜ Day 8 → paste into §2 Website |
| 6 | **Google AI integration** | ✅ Gemini ×4 surfaces (`01-SOLUTION-v2.md` §6) |

**Also required by rule 04:** cross-border applicability — ✅ 5 BRICS adapters, config-only.

If the repo must stay private, grant access to:
`build-with-ai-india@googlegroups.com`

---

## 5 · Day 8 — after you deploy

1. Deploy (Cloud Run or Render), get the live URL.
2. Paste it into the **Website** field in §2.
3. Put it at the **very top of `README.md`**:
   ```markdown
   **🔗 Live demo: https://your-app.run.app**
   ```
4. Add it to the submission form's "Deployed link".

---

## 6 · Repo settings checklist

- [ ] Public
- [ ] Description + 20 topics + website filled in
- [ ] `README.md` renders correctly (check the tables and mermaid-free ASCII diagram)
- [ ] `LICENSE` detected by GitHub (should show "MIT license" in the header)
- [ ] `.env` is **not** in the repo — run `git ls-files | grep env` → should print only `.env.example`
- [ ] Every team member has push access (Settings → Collaborators)
- [ ] Branch protection on `main` (optional but stops 2 a.m. disasters)

---

## 7 · What the judges will actually look at

In rough order of how much it moves the score:

1. **`backend/engine/allocate.py`** — the thing nobody else in the track has
2. **`backend/engine/bias.py`** — the novel bit, with fitted coefficients
3. **Commit history** — daily commits from every member is your evidence against the
   "pre-existing project" rule (hackathon rule 02)
4. **`README.md`** — if the quickstart doesn't work in 60 seconds, you lose them
5. **`data/PROVENANCE.md`** — honesty about synthetic vs real data (Day 4/8)

---

*JanSetu (जनसेतु) — "the people's bridge." From citizen voice to a bridge that actually gets built.*
