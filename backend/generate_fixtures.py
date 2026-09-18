"""
JanSetu — Fixture generator
=============================
Produces backend/fixtures/*.json so that EVERY workstream can start on Day 1
without waiting for anyone else's code. Workstream D builds the whole dashboard
against these files before the engine is finished.

Run:  cd backend && python generate_fixtures.py
"""
from __future__ import annotations

import csv
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from engine.allocate import DEFAULT_SECTOR_CAPS, allocate  # noqa: E402

DEFAULT_CAPS = DEFAULT_SECTOR_CAPS
from engine.score import score_all            # noqa: E402

BACKEND = Path(__file__).parent
DATA = BACKEND.parent / "data"
FIX = BACKEND / "fixtures"
FIX.mkdir(exist_ok=True)
random.seed(20260917)

NOW = datetime.now(timezone.utc)

# ---------------------------------------------------------------------------
# Hand-written, genuinely multilingual seeds (workstream B tests against these)
# ---------------------------------------------------------------------------
SEED_TEXTS = [
    # (lang, sector, text, translation) — real, natural phrasing, not machine glosses
    ("mr", "roads",
     "धुळे तालुक्यात कुसुंबा गावाकडे जाणारा रस्ता पूर्णपणे खराब झाला आहे. पाऊस पडला तर गाड्या जात नाहीत, शाळेत जाणारी मुलं अडकतात.",
     "The approach road to Kusumba village in Dhule taluka is completely damaged; vehicles cannot pass in rain and schoolchildren are stranded."),
    ("hi", "water",
     "गया जिले के बोध गया ब्लॉक में पानी की बहुत समस्या है। हैंडपंप छह महीने से खराब पड़ा है और महिलाओं को दो किलोमीटर दूर जाना पड़ता है।",
     "There is a severe water problem in Bodh Gaya block, Gaya district. The handpump has been broken for six months and women must walk two kilometres."),
    ("bn", "water",
     "মুর্শিদাবাদ জেলার বহরমপুর ব্লকে বিশুদ্ধ পানির সমস্যা খুব বেশি। নলকূপের পানি লালচে এবং পেটের অসুখ বাড়ছে।",
     "Berhampore block in Murshidabad district faces a severe drinking water problem; tubewell water is reddish and stomach illness is rising."),
    ("ta", "roads",
     "கடலூர் மாவட்டத்தில் எங்கள் ஊர் சாலை மிகவும் மோசமாக உள்ளது. மழை காலத்தில் ஆம்புலன்ஸ் வருவதில்லை.",
     "The road to our village in Cuddalore district is in very poor condition; ambulances cannot come during the monsoon."),
    ("te", "power",
     "కడప జిల్లాలో విద్యుత్ సమస్య చాలా ఎక్కువగా ఉంది. రోజుకు ఎనిమిది గంటలు కరెంట్ ఉండదు.",
     "The power problem in Kadapa district is severe; there is no electricity for eight hours a day."),
    ("en", "health",
     "The primary health centre in Raiganj has had no doctor posted for four months. Pregnant women are being sent 30 km away for checkups.",
     "The primary health centre in Raiganj has had no doctor posted for four months. Pregnant women are being sent 30 km away for checkups."),
    ("hi-Latn", "power",
     "Bahraich mein bijli ki bahut problem hai, transformer 6 mahine se kharab pada hai, kitni baar complaint kar chuke hain",
     "There is a serious electricity problem in Bahraich; the transformer has been broken for six months and we have complained many times."),
    ("mr", "education",
     "नंदुरबार तालुक्यातील शाळेत मुलींसाठी स्वतंत्र शौचालय नाही. आठवीच्या नंतर मुली शाळा सोडतात.",
     "The school in Nandurbar taluka has no separate toilet for girls; girls drop out after class eight."),
    ("hi", "sanitation",
     "श्रावस्ती जिले की भिंगा ब्लॉक में नाली नहीं है। बारिश में गाँव का पूरा पानी घरों में घुस जाता है और बच्चे बीमार पड़ते हैं।",
     "Bhinga block of Shravasti district has no drainage; during rain all the village water enters homes and children fall sick."),
    ("bn", "digital",
     "পুরুলিয়া জেলায় মোবাইল নেটওয়ার্ক নেই। অনলাইন সরকারি ফর্ম জমা দিতে পারি না, কাজের জন্য শহরে যেতে হয়।",
     "There is no mobile network in Purulia district; we cannot submit online government forms and must travel to town for work."),
    ("en", "roads",
     "The culvert near Sakri has collapsed. Two villages are completely cut off and the harvest cannot reach the mandi.",
     "The culvert near Sakri has collapsed. Two villages are completely cut off and the harvest cannot reach the mandi."),
    ("unknown-location", "water",
     "पानी की बहुत समस्या है, कोई सुनने वाला नहीं है",
     "There is a severe water problem and nobody listens.",
     ),  # ⚠️ deliberately unresolvable location — tests the null-LGD fallback path
]

# Block-level reporting "loudness" — THIS IS THE BIAS DEMO.
# Connected blocks file many reports; silent blocks file few but need more.
# Format: (block_name, sector, n_reports)  — assembled below from census.


def load(name: str) -> list[dict]:
    with open(DATA / name, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # CSV is all strings — coerce the numeric columns we rely on.
    for r in rows:
        for k in ("unit_rate_inr", "population"):
            if k in r:
                r[k] = int(float(r[k]))
    return rows


def main() -> None:
    census = load("census_seed.csv")
    admin = load("lgd_admin.csv")
    sor = load("sor_rates.csv")
    by_block = {r["lgd_block_code"]: r for r in census}
    print(f"Loaded {len(census)} blocks · {len(sor)} rates")

    # ---------------------------------------------------------------
    # 1. Reports: hand-written seeds + generated volume
    # ---------------------------------------------------------------
    reports: list[dict] = []
    rid = 0

    def mk(lang: str, sector: str, text: str, en: str | None, block: dict,
           severity: int, channel: str, age_days: int, confidence: float = 0.85,
           extractor: str = "gemini", lgd: str | None = None) -> dict:
        nonlocal rid
        rid += 1
        lgd = block["lgd_block_code"] if lgd is None else lgd
        return {
            "report_id": f"JS-2026-{block['state'][:2].upper()}-{rid:05d}",
            "created_at": (NOW - timedelta(days=age_days)).isoformat(),
            "channel": channel,
            "channel_meta": {"msisdn_hash": f"sha256:{rid:064x}"[:74], "provider": "simulator",
                             "handset_class": "feature_phone" if channel in ("sms", "missed_call", "ivr") else "smartphone",
                             "duration_s": 38 if channel in ("voice_call", "missed_call") else None},
            "raw_text": text,
            "raw_language": lang,
            "normalized_text_en": en,
            "structured": {
                "sector": sector,
                "severity_1_5": severity,
                "affected_population_est": int(float(block["population"]) * random.uniform(0.08, 0.35)),
                "geo": {"state": block["state"], "district": block["district"], "block": block["block"],
                        "village": f"{block['block']} GP-{random.randint(1, 12)}",
                        "lgd_code": lgd,
                        "lat": round(random.uniform(18.5, 26.5), 5),
                        "lon": round(random.uniform(72.5, 88.5), 5),
                        "geohash": f"t{random.randint(1000, 9999)}"},
                "confidence": confidence,
                "extractor": extractor,
            },
            "me_too": random.randint(0, 60),
            "status": "received",
        }

    # (a) the 12 hand-written multilingual seeds, placed on their natural blocks
    placements = ["Dhule", "Bodh Gaya", "Berhampore", "Cuddalore", "Namakkal",
                  "Raiganj", "Bahraich", "Nandurbar", "Bhinga", "Purulia II",
                  "Sakri", None]
    for (lang, sector, text, en), block_name in zip(
            [s[:4] if len(s) >= 4 else (*s, None) for s in SEED_TEXTS], placements):
        blk = next((b for b in census if b["block"] == block_name), census[0]) if block_name else census[0]
        lgd = None if block_name is None else blk["lgd_block_code"]
        reports.append(mk(lang, sector, text, en, blk, random.randint(3, 5),
                          random.choice(["missed_call", "sms", "voice_call", "whatsapp"]),
                          random.randint(0, 90), lgd=lgd))

    # (b) generated volume — LOUD connected blocks vs SILENT deprived blocks
    for blk in census:
        dai = float(blk["digital_access_index"])
        # Reports filed scale with connectivity, NOT with need. That's the bias.
        n = int(60 * (dai ** 2.2) * random.uniform(0.7, 1.3))
        if blk["urban"]:
            n = int(n * 1.4)
        for _ in range(n):
            sector = random.choice(["roads", "water", "power", "health", "education", "sanitation", "digital"])
            lang = {"Maharashtra": "mr", "Bihar": "hi", "Uttar Pradesh": "hi",
                    "West Bengal": "bn", "Tamil Nadu": "ta"}[blk["state"]]
            channel = random.choice(["missed_call", "sms", "voice_call", "whatsapp", "web"])
            native = {
                "mr": "गावात {} ची खूप समस्या आहे, कृपया लवकर उपाय करा.",
                "hi": "गाँव में {} की बहुत समस्या है, कृपया जल्दी समाधान करें.",
                "bn": "গ্রামে {} এর খুব সমস্যা, দয়া করে দ্রুত সমাধান করুন.",
                "ta": "கிராமத்தில் {} பிரச்சனை மிக அதிகம், தயவுசெய்து விரைவில் தீர்க்கவும்.",
            }[lang]
            issue = {"roads": "रस्ता", "water": "पानी", "power": "बिजली", "health": "स्वास्थ्य",
                     "education": "शिक्षा", "sanitation": "स्वच्छता", "digital": "नेटवर्क"}
            reports.append(mk(lang, sector, native.format(issue[sector]),
                              f"Village faces a serious {sector} problem; urgent remedy requested.",
                              blk, random.randint(2, 5), channel, random.randint(0, 240),
                              confidence=round(random.uniform(0.55, 0.95), 2)))

    print(f"  ✓ {len(reports)} reports "
          f"({sum(1 for r in reports if r['channel'] in ('missed_call', 'sms', 'ivr'))} from feature phones)")

    # ---------------------------------------------------------------
    # 2. Score -> hotspots (this exercises bias.py + score.py for real)
    # ---------------------------------------------------------------
    hotspots = score_all(reports)
    print(f"  ✓ {len(hotspots)} hotspots scored")

    def block_summary(name: str):
        code = next((b["lgd_block_code"] for b in census if b["block"] == name), None)
        hs = [h for h in hotspots if h["lgd_block_code"] == code]
        if not hs:
            return None
        top = max(hs, key=lambda h: h["priority_score"])
        return {"name": name, "reports": sum(h["report_count"] for h in hs),
                "bias": top["demand"]["bias_factor"], "score": top["priority_score"],
                "rank": top["rank"], "deficit": top["components"]["deficit"]}

    loud, silent = block_summary("Haveli"), block_summary("Nandurbar")
    if loud and silent:
        print(f"\n  ⚖️  BIAS DEMO (the demo beat)")
        print(f"      LOUD   {loud['name']:10s} (Pune, connected): {loud['reports']:4d} reports · "
              f"bias x{loud['bias']:.2f} · top score {loud['score']:.1f} · rank {loud['rank']}")
        print(f"      SILENT {silent['name']:10s} (tribal, aspirational): {silent['reports']:4d} reports · "
              f"bias x{silent['bias']:.2f} · top score {silent['score']:.1f} · rank {silent['rank']}")
        print(f"      → {silent['reports']} complaints from {silent['name']} outrank "
              f"{loud['reports']} from {loud['name']}: "
              f"{'YES ✅' if silent['score'] > loud['score'] else 'no ❌'}")

    # ---------------------------------------------------------------
    # 3. Project candidates from the top hotspots, priced off real SOR rates
    # ---------------------------------------------------------------
    code_by_sector: dict[str, list[str]] = {}
    for r in sor:
        code_by_sector.setdefault(r["sector"], []).append(r["intervention_code"])
    rate_by_code = {r["intervention_code"]: r for r in sor}

    # Pick an absolute BPL threshold targeting ~60% of the top hotspots' blocks,
    # so the equity floor is a REAL constraint that can bind (and the frontier curves).
    _bpls = sorted(float(next(b for b in census if b["lgd_block_code"] == h["lgd_block_code"])["bpl_share"])
                   for h in hotspots[:44])
    _BPL_THRESHOLD = round(_bpls[int(len(_bpls) * 0.40)], 3)
    print(f"  · deprivation threshold: BPL share >= {_BPL_THRESHOLD:.3f}")

    projects: list[dict] = []
    for i, h in enumerate(hotspots[:44]):
        blk = by_block.get(h["lgd_block_code"], census[0])
        code = random.choice(code_by_sector.get(h["sector"], ["CULVERT-REPAIR"]))
        rate = rate_by_code[code]
        pop = float(blk["population"])
        # A single project serves a SHARE of a block, not the whole block, and
        # never an unbounded number of people. Without this cap, road projects
        # sized to "serve the block" cost Rs 100+ Cr and swamp the portfolio.
        beneficiaries = int(min(pop * random.uniform(0.06, 0.18), 25_000))
        # Quantity is DERIVED from the people it must serve — not a random number.
        # This is what makes cost_per_beneficiary a credible figure on stage.
        unit = rate["unit"]
        per_unit = float(rate["people_served_per_unit"])
        qty = max(1.0, beneficiaries / per_unit)
        if unit == "per HH":
            qty = max(50.0, round(qty))
        elif unit in ("per km", "per m"):
            qty = round(qty, 1)
        else:
            qty = float(max(1, round(qty)))
        cost = int(rate["unit_rate_inr"] * qty)

        projects.append({
            "project_id": f"P-{h['lgd_block_code']}-{h['sector'][:3].upper()}-{i:03d}",
            "hotspot_id": h["hotspot_id"],
            "lgd_block_code": h["lgd_block_code"],
            "sector": h["sector"],
            "district": blk["district"],
            "state": blk["state"],
            "intervention": f"{rate['description']} — {blk['block']}, {blk['district']}",
            "intervention_code": code,
            "cost_inr": cost,
            "cost_basis": f"{rate['description']}: {qty:,.0f} {unit} x ₹{rate['unit_rate_inr']:,} ({rate['source']})",
            "beneficiaries": beneficiaries,
            "cost_per_beneficiary_inr": int(cost / beneficiaries) if beneficiaries else 0,
            "scheme": {"roads": "PMGSY-III", "water": "Jal Jeevan Mission", "power": "RDSS",
                       "health": "NHM", "education": "Samagra Shiksha",
                       "sanitation": "SBM-G 2.0", "digital": "BharatNet Phase-III"}[h["sector"]],
            "eligibility": {"eligible": True,
                            "conditions_met": ["gp_resolution_attached", "no_pending_utilisation_certificate"],
                            "conditions_failed": [],
                            "funding_split": {"centre": 0.60, "state": 0.40}},
            "constraint_tags": {
                # Must DISCRIMINATE, or the equity floor can never bind and the
                # whole "equity_share" metric becomes meaningless (it was 100%).
                # Target: roughly a third to a half of the portfolio supply.
                "deprivation_flag": bool(float(blk["bpl_share"]) >= _BPL_THRESHOLD),
                "aspirational_district": blk["aspirational"].lower() == "true",
                "block": h["lgd_block_code"],
                "exclusive_group": None,
            },
            "predicted_outcome": {
                "kpi": {"roads": "avg_travel_time_min_to_pucca_road", "water": "households_with_tap_connection",
                        "power": "hours_of_supply_per_day", "health": "outpatients_per_month",
                        "education": "girls_enrolled_class_9", "sanitation": "households_with_toilet",
                        "digital": "villages_with_broadband"}[h["sector"]],
                "baseline_value": round(random.uniform(0.15, 0.45) * beneficiaries),
                "predicted_value": round(random.uniform(0.60, 0.95) * beneficiaries),
                "confidence": round(random.uniform(0.55, 0.85), 2),
            },
            "feasibility": {"land_available": True,
                            "agency_capacity": round(random.uniform(0.45, 0.9), 2),
                            "lead_time_days": random.randint(90, 400)},
            "priority_score": h["priority_score"],
        })

    dep = sum(1 for p in projects if p["constraint_tags"]["deprivation_flag"])
    dep_cost = sum(p["cost_inr"] for p in projects if p["constraint_tags"]["deprivation_flag"])
    print(f"  ✓ {len(projects)} project candidates "
          f"({dep} deprived = {dep/len(projects):.0%} of count, "
          f"Rs{dep_cost/1e7:.1f}Cr = {dep_cost/sum(p['cost_inr'] for p in projects):.0%} of supply)")

    # ---------------------------------------------------------------
    # 4. Portfolios at two budgets — the money-slide fixtures
    # ---------------------------------------------------------------
    score_by_hs = {h["hotspot_id"]: h["priority_score"] for h in hotspots}
    base_req = {
        "budget_inr": 400_000_000,   # Rs 40 Crore (1 Cr = 10,000,000)
        "sector_caps": DEFAULT_CAPS,
        "equity_floor_pct": 0.40,
        "geographic_spread": "min_one_per_block",
        "state_filter": None,
        "sector_filter": None,
        "weights": {"demand": 0.30, "deficit": 0.25, "reach": 0.20, "equity": 0.15, "feasibility": 0.10},
        "fast": False,
    }
    p40 = allocate(dict(base_req), projects, score_by_hs)
    p12 = allocate({**base_req, "budget_inr": 120_000_000}, projects, score_by_hs)  # Rs 12 Crore
    print(f"  ✓ ₹40Cr → {p40['totals']['projects']} projects · {p40['totals']['beneficiaries']:,} beneficiaries "
          f"(₹{p40['totals']['cost_per_beneficiary_inr']:,}/person) · {p40['solver']}")
    print(f"  ✓ ₹12Cr → {p12['totals']['projects']} projects · {p12['totals']['beneficiaries']:,} beneficiaries "
          f"(₹{p12['totals']['cost_per_beneficiary_inr']:,}/person)")

    # ---------------------------------------------------------------
    # 5. Verification events — the citizen-audit demo
    # ---------------------------------------------------------------
    verifications = []
    for i, pid in enumerate((p40["selected"] or [f"P-{census[0]['lgd_block_code']}-ROA-000"])[:2]):
        good = i == 0
        n = 63 if good else 58
        pos, par, neg = (48, 11, 4) if good else (9, 15, 34)
        score = round((pos * 1.0 + par * 0.5) / n, 3)
        verifications.append({
            "verification_id": f"V-2026-09-17-{i:05d}",
            "project_id": pid, "report_id": None,
            "created_at": NOW.isoformat(), "channel": "whatsapp" if good else "sms",
            "respondent": {"msisdn_hash": f"sha256:{i:064x}"[:74], "prior_verifications": 6,
                           "trust_weight": 0.8},
            "verdict": "completed" if good else "not_done",
            "raw_comment": ("रस्ता पूर्ण झाला आहे, आता गाड्या सहज जातात"
                            if good else "सडक अर्धीच राहिली आहे, पुलाचे काम बाकी आहे"),
            "comment_language": "mr",
            "comment_en": ("The road is complete, vehicles pass easily now"
                           if good else "The road is only half done; the culvert work is still pending"),
            "photo": {"uri": f"gs://jansetu-evidence/verify/{i:05d}.jpg",
                      "vision_check": {"matches_scope": True, "asset_visible": True,
                                       "completion_est": 0.95 if good else 0.40,
                                       "confidence": 0.82 if good else 0.71,
                                       "note": "Completed pucca surface, ~2.4 km"
                                               if good else "Surface present for ~400 m; culvert absent"}},
            "geo_check": {"geohash": "teq7z", "within_project_radius": True},
            "aggregates": {
                "project_verification_count": n, "positive": pos, "partial": par, "negative": neg,
                "social_audit_score": score,
                "recommended_action": ("certified_release_payment" if score > 0.8
                                       else "partial_punch_list" if score >= 0.5
                                       else "payment_hold_field_inspection"),
            },
        })
    print(f"  ✓ {len(verifications)} verification events")

    # ---------------------------------------------------------------
    # 6. Write
    # ---------------------------------------------------------------
    def w(name: str, obj) -> None:
        p = FIX / name
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False, default=str)
        print(f"  → fixtures/{name}")

    w("reports_8lang.json", reports[:400])
    w("hotspots.json", hotspots)
    w("projects.json", projects)
    w("portfolio_40cr.json", p40)
    w("portfolio_12cr.json", p12)
    w("verifications.json", verifications)
    print("\n✅ Fixtures ready. Every workstream can now build independently.")


if __name__ == "__main__":
    main()
