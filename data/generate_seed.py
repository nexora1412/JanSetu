"""
JanSetu — Seed data generator
===============================
Deterministic (seeded) generator for the demo dataset.

⚠️  HONESTY NOTE (also in PROVENANCE.md):
District / block NAMES and the ADMINISTRATIVE STRUCTURE are real.
LGD CODES are SYNTHETIC PLACEHOLDERS with the correct shape — real codes must be
pulled from https://lgdirectory.gov.in and swapped in (see Day 6 task for workstream B).
All INDICATORS are realistic synthetic values calibrated to published national ranges
(Census 2011 literacy, NFHS-5, NITI Aayog SDG India Index). They are NOT official figures.

The hackathon brief explicitly permits "real or realistic data ... sample data" where
live data is unavailable. We are explicit about which is which — that honesty is part
of the submission, not a caveat to hide.

Run:  python data/generate_seed.py
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

OUT = Path(__file__).parent
random.seed(20260917)  # deterministic — same data on every machine, every time

SECTORS = ["roads", "water", "power", "health", "education", "sanitation", "digital"]

# (state, district, block, aspirational?, tribal?, urban?)
# Real districts. Nandurbar ↔ Pune is our canonical BIAS-FLIP demo pair.
ADMIN = [
    # Maharashtra — home state. Nandurbar (tribal, aspirational) vs Pune (connected).
    ("Maharashtra", "Dhule",      "Dhule",       False, False, False),
    ("Maharashtra", "Dhule",      "Sakri",       False, True,  False),
    ("Maharashtra", "Nandurbar",  "Nandurbar",   True,  True,  False),   # ⚖️ silent block
    ("Maharashtra", "Nandurbar",  "Shahada",     True,  True,  False),
    ("Maharashtra", "Nandurbar",  "Taloda",      True,  True,  False),
    ("Maharashtra", "Nandurbar",  "Navapur",     True,  True,  False),
    ("Maharashtra", "Nandurbar",  "Akkalkuwa",   True,  True,  False),
    ("Maharashtra", "Nandurbar",  "Akrani",      True,  True,  False),
    ("Maharashtra", "Pune",       "Haveli",      False, False, False),
    ("Maharashtra", "Pune",       "Khed",        False, False, False),
    ("Maharashtra", "Pune",       "Mulshi",      False, False, False),
    ("Maharashtra", "Pune",       "Bhor",        False, False, False),
    ("Maharashtra", "Jalgaon",    "Jalgaon",     False, False, False),
    ("Maharashtra", "Jalgaon",    "Bhusawal",    False, False, False),
    ("Maharashtra", "Nashik",     "Nashik",      False, False, False),
    ("Maharashtra", "Nashik",     "Malegaon",    False, False, False),
    ("Maharashtra", "Gadchiroli", "Gadchiroli",  True,  True,  False),
    ("Maharashtra", "Washim",     "Washim",      True,  False, False),
    ("Maharashtra", "Osmanabad",  "Osmanabad",   True,  False, False),
    # Bihar
    ("Bihar", "Gaya",        "Gaya Town",   True,  False, False),
    ("Bihar", "Gaya",        "Bodh Gaya",   True,  False, False),
    ("Bihar", "Muzaffarpur", "Muzaffarpur", True,  False, False),
    ("Bihar", "Sitamarhi",   "Sitamarhi",   True,  False, False),
    ("Bihar", "Purnia",      "Purnia East", True,  False, False),
    ("Bihar", "Katihar",     "Katihar",     True,  False, False),
    ("Bihar", "Patna",       "Patna Sadar", False, False, True),
    ("Bihar", "Patna",       "Danapur",     False, False, True),
    # Uttar Pradesh
    ("Uttar Pradesh", "Bahraich",      "Bahraich",     True,  False, False),
    ("Uttar Pradesh", "Balrampur",     "Balrampur",    True,  False, False),
    ("Uttar Pradesh", "Shravasti",     "Bhinga",       True,  False, False),
    ("Uttar Pradesh", "Siddharthnagar","Naugarh",      True,  False, False),
    ("Uttar Pradesh", "Sonbhadra",     "Robertsganj",  True,  True,  False),
    ("Uttar Pradesh", "Lucknow",       "Lucknow",      False, False, True),
    ("Uttar Pradesh", "Lucknow",       "Mohanlalganj", False, False, True),
    # West Bengal
    ("West Bengal", "Murshidabad",    "Berhampore",   True,  False, False),
    ("West Bengal", "Maldah",         "Old Malda",    True,  False, False),
    ("West Bengal", "Purulia",        "Purulia II",   True,  True,  False),
    ("West Bengal", "Uttar Dinajpur", "Raiganj",      True,  False, False),
    ("West Bengal", "Birbhum",        "Suri I",       False, False, False),
    ("West Bengal", "Kolkata",        "Borough V",    False, False, True),
    ("West Bengal", "Kolkata",        "Borough VII",  False, False, True),
    # Tamil Nadu
    ("Tamil Nadu", "Cuddalore",     "Cuddalore",     False, False, False),
    ("Tamil Nadu", "Perambalur",    "Perambalur",    False, False, False),
    ("Tamil Nadu", "Ariyalur",      "Ariyalur",      False, False, False),
    ("Tamil Nadu", "Namakkal",      "Namakkal",      False, False, False),
    ("Tamil Nadu", "Ramanathapuram","Ramanathapuram", True, False, False),
    ("Tamil Nadu", "Chennai",       "Alandur",       False, False, True),
    ("Tamil Nadu", "Chennai",       "Madhavaram",    False, False, True),
]

# ---------------------------------------------------------------------------
# 1. Admin units (LGD-shaped)
# ---------------------------------------------------------------------------
def build_admin() -> list[dict]:
    rows = []
    for i, (state, district, block, aspirational, tribal, urban) in enumerate(ADMIN):
        rows.append({
            # SYNTHETIC but correctly-shaped. Replace from lgdirectory.gov.in on Day 6.
            "lgd_state_code": f"{27 if state == 'Maharashtra' else 10 if state == 'Bihar' else 9 if state == 'Uttar Pradesh' else 19 if state == 'West Bengal' else 33:02d}",
            "lgd_district_code": f"{27 if state == 'Maharashtra' else 10 if state == 'Bihar' else 9 if state == 'Uttar Pradesh' else 19 if state == 'West Bengal' else 33:02d}{(i // 8) + 1:03d}",
            "lgd_block_code": f"{27 if state == 'Maharashtra' else 10 if state == 'Bihar' else 9 if state == 'Uttar Pradesh' else 19 if state == 'West Bengal' else 33:02d}{(i // 8) + 1:03d}{i % 8:03d}",
            "state": state,
            "district": district,
            "block": block,
            "aspirational": aspirational,
            "tribal": tribal,
            "urban": urban,
        })
    return rows


# ---------------------------------------------------------------------------
# 2. Demographics (calibrated to published national ranges)
# ---------------------------------------------------------------------------
def build_census(admin: list[dict]) -> list[dict]:
    rows = []
    for a in admin:
        if a["urban"]:
            pop = random.randint(180_000, 620_000)
            literacy = round(random.uniform(0.82, 0.93), 3)
            female_literacy = round(literacy - random.uniform(0.04, 0.10), 3)
            sc_st_share = round(random.uniform(0.08, 0.20), 3)
            phone_pen = round(random.uniform(0.80, 0.94), 3)
            net_pen = round(random.uniform(0.55, 0.78), 3)
            bpl_share = round(random.uniform(0.06, 0.18), 3)
        elif a["tribal"]:
            pop = random.randint(60_000, 190_000)
            literacy = round(random.uniform(0.45, 0.63), 3)   # tribal belts lag badly
            female_literacy = round(literacy - random.uniform(0.10, 0.18), 3)
            sc_st_share = round(random.uniform(0.55, 0.88), 3)
            phone_pen = round(random.uniform(0.42, 0.62), 3)  # ← drives the bias model
            net_pen = round(random.uniform(0.14, 0.30), 3)
            bpl_share = round(random.uniform(0.38, 0.62), 3)
        elif a["aspirational"]:
            pop = random.randint(120_000, 340_000)
            literacy = round(random.uniform(0.55, 0.72), 3)
            female_literacy = round(literacy - random.uniform(0.09, 0.16), 3)
            sc_st_share = round(random.uniform(0.22, 0.42), 3)
            phone_pen = round(random.uniform(0.58, 0.75), 3)
            net_pen = round(random.uniform(0.24, 0.42), 3)
            bpl_share = round(random.uniform(0.28, 0.48), 3)
        else:
            pop = random.randint(140_000, 380_000)
            literacy = round(random.uniform(0.68, 0.84), 3)
            female_literacy = round(literacy - random.uniform(0.07, 0.14), 3)
            sc_st_share = round(random.uniform(0.14, 0.32), 3)
            phone_pen = round(random.uniform(0.70, 0.86), 3)
            net_pen = round(random.uniform(0.36, 0.58), 3)
            bpl_share = round(random.uniform(0.16, 0.32), 3)

        rows.append({
            "lgd_block_code": a["lgd_block_code"],
            "state": a["state"], "district": a["district"], "block": a["block"],
            "population": pop,
            "literacy_rate": literacy,
            "female_literacy_rate": female_literacy,
            "sc_st_share": sc_st_share,
            "bpl_share": bpl_share,
            "phone_penetration": phone_pen,
            "net_penetration": net_pen,
            "urban": a["urban"], "tribal": a["tribal"], "aspirational": a["aspirational"],
            # Reporting-rate feature: how likely a need here becomes a digital complaint.
            # Deliberately correlated with connectivity + literacy — this is what the
            # coverage-bias model corrects for.
            "digital_access_index": round(0.45 * phone_pen + 0.35 * net_pen + 0.20 * literacy, 4),
        })
    return rows


# ---------------------------------------------------------------------------
# 3. NIDI — National Infrastructure Deficit Index (block × sector)
# ---------------------------------------------------------------------------
def build_nidi(census: list[dict]) -> list[dict]:
    rows = []
    for c in census:
        # Deprived blocks have structurally higher deficit across every sector.
        base = 0.32 + 0.42 * (1 - c["digital_access_index"]) + 0.18 * c["bpl_share"]
        base += 0.10 if c["aspirational"] else 0.0
        base += 0.06 if c["tribal"] else 0.0
        base -= 0.14 if c["urban"] else 0.0
        for sector in SECTORS:
            deficit = base + random.uniform(-0.11, 0.11)
            rows.append({
                "lgd_block_code": c["lgd_block_code"],
                "state": c["state"], "district": c["district"], "block": c["block"],
                "sector": sector,
                "deficit_0_1": round(max(0.05, min(0.98, deficit)), 4),
                "coverage_pct": round(max(2.0, min(99.0, (1 - deficit) * 100 + random.uniform(-8, 8))), 2),
            })
    return rows


# ---------------------------------------------------------------------------
# 4. Schedule of Rates — unit costs (cost_basis strings trace back here)
# ---------------------------------------------------------------------------
SOR = [
    # code, sector, description, unit_rate, unit, source, PEOPLE_SERVED_PER_UNIT
    ("PMGSY-ROAD-NEW",   "roads",      "New rural road construction (PMGSY)",            6_200_000, "per km",   "PMGSY-III unit cost", 3000),
    ("PMGSY-ROAD-UPG",   "roads",      "Upgradation of existing rural road",            4_100_000, "per km",   "PMGSY-III unit cost", 4000),
    ("CULVERT-REPAIR",   "roads",      "Culvert / cross-drainage repair",                 850_000, "per unit", "Maharashtra PWD SOR 2025", 3000),
    ("JJM-HH-CONN",      "water",      "Household tap connection (FHTC)",                   6_900, "per HH",   "JJM unit cost", 4.5),
    ("JJM-OHT",          "water",      "Overhead storage tank (100 KL)",                1_800_000, "per unit", "JJM / state SOR 2025", 2500),
    ("JJM-PIPE-MAIN",    "water",      "Distribution main pipeline",                       2_400, "per m",    "JJM / state SOR 2025", 2),
    ("BORE-REPAIR",      "water",      "Handpump / borewell repair",                        55_000, "per unit", "State SOR 2025", 250),
    ("RDSS-FEEDER",      "power",      "11 kV feeder upgrade",                          3_100_000, "per km",   "RDSS unit cost", 1200),
    ("RDSS-TRANSFORMER", "power",      "Distribution transformer (100 kVA)",               420_000, "per unit", "RDSS unit cost", 1500),
    ("SOLAR-STREET",     "power",      "Solar street lighting cluster (50 poles)",          680_000, "per cluster", "State SOR 2025", 1200),
    ("PHC-UPGRADE",      "health",     "PHC upgrade to 24x7 (IPHS norms)",              9_500_000, "per unit", "NHM unit cost", 25000),
    ("PHC-EQUIP",        "health",     "PHC diagnostic equipment package",              2_200_000, "per unit", "NHM unit cost", 25000),
    ("AMBULANCE",        "health",     "108 ambulance + crew (annual)",                 1_600_000, "per unit", "NHM unit cost", 60000),
    ("SCHOOL-TOILET",    "education",  "School toilet block (separate G/B)",               480_000, "per unit", "Samagra Shiksha", 200),
    ("SCHOOL-CLASSROOM", "education",  "Additional classroom construction",              1_250_000, "per unit", "Samagra Shiksha", 60),
    ("SCHOOL-DIGITAL",   "education",  "Smart classroom / ICT lab",                        750_000, "per unit", "Samagra Shiksha", 400),
    ("SBM-IHHL",         "sanitation", "Individual household latrine",                      12_000, "per unit", "SBM-G 2.0", 4.5),
    ("SLWM-PLANT",       "sanitation", "Solid/liquid waste management plant",           6_800_000, "per unit", "SBM-G 2.0", 15000),
    ("DRAINAGE",         "sanitation", "Village drainage network",                        3_400_000, "per km",  "15th FC grant norms", 2500),
    ("BHARATNET",        "digital",    "BharatNet last-mile fibre to GP",                2_900_000, "per GP",   "BharatNet Phase-III", 4000),
    ("CSC-UPGRADE",      "digital",    "Common Service Centre upgrade",                     340_000, "per unit", "CSC SPV", 3000),
    ("TOWER-SITE",       "digital",    "Mobile tower site (gap-fill)",                   4_200_000, "per unit", "USOF / state SOR", 8000),
]


def build_sor() -> list[dict]:
    return [
        {"intervention_code": c, "sector": s_, "description": d,
         "unit_rate_inr": r, "unit": u, "source": src,
         "people_served_per_unit": ppl}
        for c, s_, d, r, u, src, ppl in SOR
    ]


# ---------------------------------------------------------------------------
# Write everything
# ---------------------------------------------------------------------------
def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  ✓ {path.relative_to(OUT.parent)}  ({len(rows)} rows)")


def main() -> None:
    print("Generating JanSetu seed data (deterministic)…")
    admin = build_admin()
    census = build_census(admin)
    nidi = build_nidi(census)
    write_csv(OUT / "lgd_admin.csv", admin)
    write_csv(OUT / "census_seed.csv", census)
    write_csv(OUT / "nidi_index.csv", nidi)
    write_csv(OUT / "sor_rates.csv", build_sor())
    print(f"\nDone. {len(admin)} blocks · {len(census)} demographic rows · {len(nidi)} NIDI cells · {len(SOR)} rates.")
    print("⚠️  LGD codes are SYNTHETIC placeholders. Swap in real codes from lgdirectory.gov.in (Day 6).")


if __name__ == "__main__":
    main()
