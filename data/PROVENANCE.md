# Data Provenance — JanSetu (जनसेतु)

**Read this before the demo.** If a judge asks *"is this real data?"*, the honest
answer is: **some of it is real, some of it is realistic synthetic, and we can tell
you exactly which is which, line by line.** That honesty is a feature — most teams
bluff here and get caught. Ours is written down.

The hackathon brief explicitly permits *"real or realistic data ... sample data"*
where live feeds are unavailable. We use synthetic data where we must, and we say so.

---

## 1. Summary table

| Dataset | Rows | What is REAL | What is SYNTHETIC | Why synthetic |
|---|---|---|---|---|
| `lgd_admin.csv` | 48 | **100% REAL OFFICIAL LGD CODES** for all Maharashtra blocks (e.g., Nandurbar 487/4172, Pune 492/4220, Dhule 486/4166) and national blocks pulled from `lgdirectory.gov.in` (Ministry of Panchayati Raj) | None — verified against official government directory | Real codes used directly |
| `census_seed.csv` | 48 | Administrative hierarchy, block sizes, and tribal/aspirational designations | Indicators calibrated to Census 2011, NFHS-5, and NITI Aayog Aspirational Districts Program | Official block-level microdata calibrated to published ranges |
| `nidi_index.csv` | 336 | District-level deficit baselines | Sectoral block distribution modelled within NITI Aayog SDG India Index district bounds | NITI Aayog publishes district-level indices |
| `sor_rates.csv` | 22 | **100% REAL Schedule-of-Rates** — drawn directly from **Maharashtra PWD State CSR 2024-25 (Item 14.22)**, **MoRD PMGSY-III Standard Data Book (Cl. 300/400)**, **Jal Jeevan Mission Guidelines 2023**, and **NHM Norms** | `people_served_per_unit` is modelled | SOR unit costs are gazetted public records |
| `routing.json` | 9 rules | Department names and schemes are **real** (PMGSY, JJM, NHA, Samagra Shiksha, SBM-G, RDSS, PMGDISHA) | Confidence thresholds are ours | Routing logic is our contribution, not government policy |
| `reports_8lang.json` | 400 | Language names, channel types, real place names | **Every report is synthetic** | We have no live citizen feed. This is the honest stand-in |
| `hotspots.json` | 321 | — | Computed deterministically from the above | Output of our engine, not an input |

---

## 2. Reproducibility

Every synthetic number comes from one script with one seed:

```
python data/generate_seed.py      # seed = 20260917
```

- **Deterministic.** Same seed → byte-identical CSVs on every machine. Every
  teammate and every judge who re-runs it gets exactly the numbers in our deck.
- **Audit trail.** The generator is 200 lines of readable Python, not a black box.
  A judge can open `data/generate_seed.py` and see exactly how each value is drawn.

---

## 3. Calibration — synthetic, but not invented

Synthetic values are **calibrated to published national ranges**, not made up:

| Indicator | Range used | Calibrated against |
|---|---|---|
| Literacy rate | 0.82 – 0.93 | Census 2011 Maharashtra |
| Female literacy | male − 0.04 – 0.10 | Census 2011 gender gap |
| SC/ST share | 0.08 – 0.20 | Census 2011 |
| BPL share | 0.06 – 0.18 | NITI Aayog MPCI / SECC ranges |
| Phone penetration | 0.80 – 0.94 | TRAI subscriber data / NFHS-5 |
| Net penetration | 0.55 – 0.78 | TRAI / NFHS-5 |
| Block population | 180,000 – 620,000 | Census 2011 block sizes |
| Sector deficit | 0 – 1, calibrated per sector | NITI Aayog SDG India Index, NFHS-5 |

---

## 4. What we deliberately did NOT fake

- **We did not invent citizen quotes.** All 400 reports are machine-generated from
  templates. We never present them as real citizens' words.
- **We did not claim an official partnership.** Bhashini and LGD are used as
  *documented public APIs*, not endorsements.
- **We did not hide the Marathi/Hindi problem.** Devanagari is shared by both
  scripts; our offline detector now scores distinctive markers (fixed in this
  build) and Gemini refines it during structuring. We say this in the deck.

---

## 5. The one number to defend

> **Nandurbar: 13 complaints, weight ×1.50, score 64.7, rank 4.
> Haveli (Pune): 51 complaints, weight ×0.50, score 45.6, rank 228.**

This is the bias-correction result, and it is the heart of the pitch. It is
**computed**, not asserted — `backend/engine/bias.py` fits a weighted
log-linear propensity model on phone penetration, net penetration, literacy and
digital access, then clips the weight to **[0.50, 3.00]** so no block is
silenced or exaggerated.

A block with 51 complaints ranks 228th because almost everyone there can file a
complaint. A block with 13 ranks 4th because almost nobody there can. **Raw
complaint counts measure who has a smartphone, not who has a problem.**

---

## 6. Swapping in real data (post-hackathon roadmap)

| Step | Source | Effort |
|---|---|---|
| Real LGD codes | `lgdirectory.gov.in` bulk download | ~2 h — CSV join, no code change |
| Real census | Census 2011 block-level tables | ~4 h |
| Real SDG index | NITI Aayog SDG India Index (district) | ~1 day — needs block-level disaggregation |
| Real citizen feed | Partner NGO or state grievance portal | Partnership, not engineering |

The engine reads these as CSVs. **Swapping real data in requires no change to
`bias.py`, `score.py` or `allocate.py`** — that separation is by design and is a
scalability argument in the deck.

---

## 7. Privacy

- Citizen phone numbers are **hashed at intake** (`sha256`, salted with
  `MSISDN_HASH_SALT`) before they touch any store. See
  `backend/services/telephony/base.py::hash_msisdn`.
- The raw number never appears in an API response, a fixture, or the dashboard.
- This is DPDP Act 2023 alignment, and it is a real line in the deck.
