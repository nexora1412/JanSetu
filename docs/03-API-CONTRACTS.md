# LokNivesh — API Contracts v1.0
### **LOCKED ON DAY 1.** Changes require a message in the group chat.

These five objects are the entire interface between workstreams. If your code produces these and consumes these, it will integrate. Every workstream tests against `backend/fixtures/*.json` — **never wait for another person's code.**

```
A (Access) ──CitizenReport──▶ B (Intelligence) ──Hotspot──▶ C (Engine) ──Portfolio──▶ D (Console)
                    └──────────── VerificationEvent ─────────────▶ C
```

---

## 1. `CitizenReport` — produced by **A**, consumed by **B**

One normalised citizen complaint. The channel it arrived on is metadata, never a branch in downstream logic.

```json
{
  "report_id": "LN-2026-MH-DHU-000123",
  "created_at": "2026-09-17T10:22:31+05:30",

  "channel": "missed_call",
  "channel_meta": {
    "msisdn_hash": "sha256:9f2c...",
    "duration_s": 42,
    "audio_uri": "gs://loknivesh-audio/2026/09/abc.wav",
    "provider": "simulator",
    "handset_class": "feature_phone"
  },

  "raw_text": "धुले तालुक्यात सडक खराब झाली आहे पाऊस पडला की जाता येत नाही",
  "raw_language": "mr",
  "normalized_text_en": "The approach road in Dhule taluka is badly damaged; impassable in rain",

  "structured": {
    "sector": "roads",
    "subsector": "rural_approach_road",
    "asset": "road_surface",
    "issue": "damaged_impassable",
    "severity_1_5": 4,
    "affected_population_est": 2500,
    "geo": {
      "state": "Maharashtra",
      "district": "Dhule",
      "block": "Dhule",
      "village": "Kusumba",
      "lgd_code": "271234",
      "lat": 20.9012,
      "lon": 74.7749,
      "geohash": "teq7z"
    },
    "confidence": 0.86,
    "extractor": "gemini"
  },

  "evidence": [
    {
      "type": "photo",
      "uri": "gs://loknivesh-evidence/abc.jpg",
      "vision_verdict": "plausible",
      "vision_score": 0.72,
      "vision_note": "Image shows a damaged rural road consistent with the report"
    }
  ],

  "me_too": 0,
  "dedupe_key": "emb:9f2c81d4",
  "is_duplicate": false,
  "duplicate_of": null,

  "routing": {
    "department": "PMGSY / Zilla Parishad",
    "scheme": "PMGSY-III",
    "officer_ref": "Dhule-ZP-EE-04",
    "sla_days": 30,
    "routed_at": "2026-09-17T10:22:35+05:30",
    "ack_sent": true
  },

  "consent": { "given": true, "pii_minimized": true, "retention_days": 730 },
  "status": "received"
}
```

**Rules for A:**
- `structured.sector` ∈ `roads | water | power | health | education | sanitation | digital | other`
- `severity_1_5` is an integer 1–5. No halves.
- `lgd_code` must be a real LGD code (use `data/lgd_districts.csv`); if unresolvable, send `null` and B will geocode-fallback — **never invent one.**
- `raw_language` is BCP-47 (`mr`, `hi`, `bn`, `ta`, `te`, `en`). For code-mixed Hinglish use `hi-Latn`.
- If `extractor` is `"fallback"` (Gemini unavailable), set `confidence` ≤ 0.5 so B weights it down.

**Fixtures A must ship on Day 1:** `fixtures/reports_8lang.json` — 8 reports covering hi, mr, bn, ta, te, en, hi-Latn (Hinglish), and one unresolvable-location case.

---

## 2. `Hotspot` — produced by **B**, consumed by **C**, **D**

A clustered, bias-corrected, scored demand hotspot. **Every number here must be reproducible from stored inputs** — that's what the auditor view drills into.

```json
{
  "hotspot_id": "HS-MH-DHU-0042",
  "created_at": "2026-09-17T11:02:00+05:30",

  "lgd_block_code": "2712",
  "sector": "water",
  "centroid": { "lat": 20.9012, "lon": 74.7749 },
  "radius_m": 800,

  "report_count": 47,
  "me_too_total": 210,
  "report_ids": ["LN-2026-MH-DHU-000123"],

  "demand": {
    "raw": 0.82,
    "expected_reports": 91.4,
    "observed_reports": 47,
    "bias_factor": 1.94,
    "adjusted": 0.91,
    "model": "poisson_glm_v1"
  },

  "components": {
    "demand":    0.91,
    "deficit":   0.74,
    "reach":     0.61,
    "equity":    0.88,
    "feasibility": 0.55,
    "saturation": 0.10
  },
  "weights": {
    "demand": 0.30, "deficit": 0.25, "reach": 0.20,
    "equity": 0.15, "feasibility": 0.10
  },

  "priority_score": 76.4,
  "rank": 3,

  "lineage": {
    "census_row": "data/census_2011_mh.csv#2712",
    "nidi_row": "data/nidi_index.csv#2712:water",
    "model_version": "score_v1.2",
    "computed_at": "2026-09-17T11:02:00+05:30"
  }
}
```

**Rules for B:**
- `priority_score` = `100 × Σ(weightᵢ × componentᵢ) × (1 − saturation)`, rounded to 1 dp. **No LLM ever produces this number.**
- `bias_factor` is clipped to `[0.50, 3.00]`. Always.
- `components.*` ∈ [0, 1]. `weights` must sum to 1.0 (the UI sliders renormalise).
- `lineage` must point at real source rows — if you can't cite it, D can't show it and the auditor view dies.

**Fixtures B must ship on Day 1:** `fixtures/hotspots.json` — ≥12 hotspots across ≥3 states, including **the canonical bias case**: a high-complaint urban ward and a low-complaint tribal block where correction flips the ranking. D builds the whole UI against this before B finishes.

---

## 3. `ProjectCandidate` — produced by **C**, consumed by **C**, **D**

A costed, scheme-eligible intervention that the optimiser may fund.

```json
{
  "project_id": "P-MH-DHU-0042-W1",
  "hotspot_id": "HS-MH-DHU-0042",
  "lgd_block_code": "2712",
  "sector": "water",

  "intervention": "Extend piped water supply to 4 habitations (2,100 HH) + 2 overhead tanks",
  "intervention_code": "JJM-HH-CONN",

  "cost_inr": 14500000,
  "cost_basis": "JJM unit cost ₹6,900/HH + OHT ₹18L × 2 (Maharashtra SOR 2025)",
  "beneficiaries": 8200,
  "cost_per_beneficiary_inr": 1768,

  "scheme": "Jal Jeevan Mission",
  "eligibility": {
    "eligible": true,
    "conditions_met": ["rural", "fhtc_coverage_lt_95pct", "gp_resolution_attached"],
    "conditions_failed": [],
    "funding_split": { "centre": 0.50, "state": 0.50 }
  },

  "constraint_tags": {
    "deprivation_flag": true,
    "aspirational_district": false,
    "block": "2712",
    "exclusive_group": null
  },

  "predicted_outcome": {
    "kpi": "households_with_tap_connection",
    "baseline_value": 310,
    "predicted_value": 2410,
    "confidence": 0.7
  },

  "feasibility": {
    "land_available": true,
    "agency_capacity": 0.7,
    "lead_time_days": 240
  }
}
```

**Rules for C:**
- `cost_inr` must trace to a named rate in `data/sor_rates.csv`. **`cost_basis` is a required string, always.** A project without a cost basis doesn't ship — that provenance is 20% of the deployability score.
- `exclusive_group` — if two candidates are alternatives for the same asset, give them the same non-null group; the ILP enforces `Σ ≤ 1`.
- `beneficiaries` is people, not households.

---

## 4. `Portfolio` ★ — produced by **C**, consumed by **D**

**This is the hero object.** The demo is this JSON being recomputed live as the budget slider moves.

```json
{
  "portfolio_id": "PF-2026-09-17-001",
  "computed_at": "2026-09-17T11:04:12+05:30",
  "solver": { "engine": "pulp_cbc", "status": "optimal", "solve_ms": 212 },

  "request": {
    "budget_inr": 120000000,
    "sector_caps": { "roads": 0.35, "water": 0.30, "sanitation": 0.20, "power": 0.15 },
    "equity_floor_pct": 0.40,
    "geographic_spread": "min_one_per_block",
    "state_filter": "Maharashtra"
  },

  "selected": ["P-MH-DHU-0042-W1", "P-MH-DHU-0007-R2"],
  "totals": {
    "projects": 2,
    "cost_inr": 118400000,
    "budget_utilisation": 0.987,
    "beneficiaries": 184000,
    "cost_per_beneficiary_inr": 6521,
    "equity_share": 0.44,
    "blocks_covered": 9,
    "sector_breakdown": { "water": 0.31, "roads": 0.34, "sanitation": 0.20, "power": 0.15 }
  },

  "dropped": [
    {
      "project_id": "P-MH-NSK-0011-R1",
      "reason": "budget_exhausted",
      "detail": "Rank 3 by benefit; ₹3.2 Cr needed, ₹16 L available",
      "would_need_inr": 32000000
    },
    {
      "project_id": "P-MH-JLG-0003-R5",
      "reason": "sector_cap_binding",
      "detail": "Roads cap 35% reached (34.8%)"
    }
  ],

  "constraint_report": [
    { "constraint": "budget",            "binding": true,  "slack_inr": 1600000 },
    { "constraint": "sector_cap_roads",  "binding": true,  "slack_inr": 240000 },
    { "constraint": "equity_floor",      "binding": false, "slack_pct": 0.04 },
    { "constraint": "geographic_spread", "binding": false, "blocks_uncovered": 0 }
  ],

  "frontier": [
    { "equity_floor_pct": 0.20, "beneficiaries": 211000, "cost_per_beneficiary_inr": 5687 },
    { "equity_floor_pct": 0.30, "beneficiaries": 198000, "cost_per_beneficiary_inr": 6060 },
    { "equity_floor_pct": 0.40, "beneficiaries": 184000, "cost_per_beneficiary_inr": 6521 },
    { "equity_floor_pct": 0.50, "beneficiaries": 162000, "cost_per_beneficiary_inr": 7407 }
  ],

  "infeasible": null
}
```

### ⚠️ Infeasibility must be surfaced, never hidden
If the request cannot be satisfied, return HTTP 200 with a populated `infeasible` object — **never a 500, never an empty portfolio**:

```json
{
  "infeasible": {
    "reason": "equity_floor_infeasible",
    "detail": "Equity floor 60% requires ₹9.2 Cr in high-deprivation blocks, but only ₹7.1 Cr of eligible projects exist there",
    "relaxation_suggestion": { "equity_floor_pct": 0.42 },
    "nearest_feasible_beneficiaries": 171000
  }
}
```
D renders this as a visible banner. **"The tool tells you when your policy is impossible" is a feature, and it's a slide.**

**Rules for C:**
- `solve_ms` must be < 400 on slider drag. If not, use the `--fast` greedy/2-opt path and set `solver.engine: "greedy_2opt"`.
- `frontier` is computed by re-solving at ≥4 equity-floor values. Cache it; don't recompute per drag.
- `dropped[].reason` ∈ `budget_exhausted | sector_cap_binding | exclusive_group | ineligible | below_cutoff`. D renders each differently.

**Fixtures C must ship on Day 1:** `fixtures/portfolio.json` — two versions, ₹40 Cr and ₹12 Cr, so D can build the entire allocator workbench before the solver exists.

---

## 5. `VerificationEvent` — produced by **A**, consumed by **B**, **C**

A citizen's verdict on a completed project. **This is the ground truth that drives the impact ledger** and the anti-ghost-asset feature.

```json
{
  "verification_id": "V-2026-09-17-00871",
  "project_id": "P-MH-DHU-0007-R2",
  "report_id": null,
  "created_at": "2026-09-17T15:40:02+05:30",

  "channel": "whatsapp",
  "respondent": { "msisdn_hash": "sha256:1a4e...", "prior_verifications": 6, "trust_weight": 0.8 },

  "verdict": "partial",
  "raw_comment": "सडक अर्धी झाली आहे, पुलाचे काम बाकी आहे",
  "comment_language": "mr",
  "comment_en": "The road is half done; the culvert work is still pending",

  "photo": {
    "uri": "gs://loknivesh-evidence/verify/00871.jpg",
    "vision_check": {
      "matches_scope": true,
      "asset_visible": true,
      "completion_est": 0.40,
      "confidence": 0.71,
      "note": "Road surface present for ~400 m; culvert absent"
    }
  },

  "geo_check": { "geohash": "teq7z", "within_project_radius": true },

  "aggregates": {
    "project_verification_count": 63,
    "positive": 21, "partial": 27, "negative": 15,
    "social_audit_score": 0.38,
    "recommended_action": "payment_hold_field_inspection"
  }
}
```

**Rules for A:**
- `verdict` ∈ `completed | partial | not_done | spam`.
- `social_audit_score` = `Σ(trust_weight × verdict_value) / Σ(trust_weight)`, where `completed=1.0, partial=0.5, not_done=0.0`. Spam is excluded from the numerator.
- Thresholds — **these are policy, so they live in config, not code**: `<0.5 → payment_hold` · `0.5–0.8 → partial_punch_list` · `>0.8 → certified_release_payment`
- `trust_weight` ∈ [0, 1], default 0.5 for a new respondent, raised by prior verified activity and proximity.

---

## 6. Error envelope — everyone

```json
{
  "error": {
    "code": "UPSTREAM_AI_UNAVAILABLE",
    "message": "Gemini call failed; deterministic fallback applied",
    "degraded": true,
    "fallback_used": "keyword_classifier_v1",
    "confidence_penalty": 0.4
  }
}
```

`degraded: true` means **the request still succeeded, just with lower confidence.** The system never hard-fails in a demo. Every AI call site wraps in this envelope — that's the difference between a demo that survives a flaky network and one that dies in front of judges.

---

## 7. Change log

| Version | Date | Change | Agreed by |
|---|---|---|---|
| 1.0 | 2026-09-17 | Initial contracts: 5 objects + endpoint table | — |

*Add rows here. If a contract changes, the whole team is told in the group chat the same minute.*
