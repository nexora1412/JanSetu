"""
LokNivesh — Deterministic Priority Scoring  (workstream B)
==========================================================
⚠️ GOLDEN RULE, restated here because it is the single most important line in this repo:

    THE LLM EXPLAINS THE SCORE. IT NEVER COMPUTES THE SCORE.

Every number below is reproducible from stored inputs. That is what makes the
auditor view honest and what separates us from teams that ask Gemini for a number
between 1 and 100. (Their own repos call this "eliminating LLM numerical
hallucinations". We enforce it in code.)

    P = 100 x (0.30*Demand + 0.25*Deficit + 0.20*Reach + 0.15*Equity + 0.10*Feasibility)
            x (1 - Saturation)

Demand is the BIAS-CORRECTED demand (see bias.py). Weights are user-adjustable and
renormalise to 1.0 (see schemas.ScoreWeights.normalised).
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from engine.bias import BiasModel, load_census, load_nidi

RECENCY_TAU_DAYS = 180.0   # reports lose weight with a 180-day half-life-ish decay
ME_TOO_SATURATION = 200    # log-cap so a brigade can't outweigh a community


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------

def build_hotspots(reports: list[dict], radius_m: int = 500) -> list[dict]:
    """
    Group reports into (block x sector) demand hotspots.

    Production version uses HDBSCAN + semantic constraint. For the prototype,
    administrative-block x sector grouping is BOTH simpler and more useful —
    budgets are sanctioned at block level, so hotspots must align to blocks or
    the allocator can't spend against them. Documented trade-off, not an oversight.
    """
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in reports:
        st = r.get("structured", {}) or {}
        geo = st.get("geo", {}) or {}
        key = (geo.get("lgd_code") or "UNKNOWN", st.get("sector", "other"))  # NB: schema field is geo.lgd_code
        groups[key].append(r)

    hotspots = []
    for (block_code, sector), items in groups.items():
        lats = [(r["structured"]["geo"]["lat"]) for r in items
                if (r.get("structured", {}).get("geo", {}) or {}).get("lat") is not None]
        lons = [(r["structured"]["geo"]["lon"]) for r in items
                if (r.get("structured", {}).get("geo", {}) or {}).get("lon") is not None]
        centroid = {
            "lat": round(sum(lats) / len(lats), 6) if lats else 0.0,
            "lon": round(sum(lons) / len(lons), 6) if lons else 0.0,
        }
        hotspots.append({
            "hotspot_id": f"HS-{block_code}-{sector.upper()}",
            "lgd_block_code": block_code,
            "sector": sector,
            "centroid": centroid,
            "radius_m": radius_m,
            "report_count": len(items),
            "me_too_total": sum(int(r.get("me_too", 0)) for r in items),
            "report_ids": [r.get("report_id") for r in items],
            "_reports": items,
            "created_at": datetime.now(timezone.utc),
        })
    return hotspots


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

def _demand_raw(hotspot: dict, now: datetime | None = None) -> float:
    """Recency-weighted verified reports + log-capped corroboration."""
    now = now or datetime.now(timezone.utc)
    total_r, total_m = 0.0, hotspot.get("me_too_total", 0)

    for r in hotspot["_reports"]:
        st = r.get("structured", {}) or {}
        created = r.get("created_at")
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except ValueError:
                created = now
        if created is None:
            created = now
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        age_days = max(0.0, (now - created).total_seconds() / 86_400.0)
        decay = math.exp(-age_days / RECENCY_TAU_DAYS)

        confidence = float(st.get("confidence", 0.5))
        severity = float(st.get("severity_1_5", 3)) / 5.0
        total_r += decay * (0.4 + 0.6 * confidence) * (0.5 + 0.5 * severity)

    m = math.log1p(total_m) / math.log1p(ME_TOO_SATURATION)
    return float(min(1.0, 0.75 * _norm(total_r, scale=25.0) + 0.25 * min(1.0, m)))


def _norm(v: float, scale: float = 1.0) -> float:
    """Squash to [0,1]. Deterministic and monotonic."""
    if scale <= 0:
        return 0.0
    return float(1.0 - math.exp(-max(0.0, v) / scale))


def compute_components(
    hotspot: dict,
    census_row: dict | None,
    deficit: float,
    bias_model: BiasModel | None = None,
    saturation: float = 0.0,
) -> dict:
    """All five components + the bias correction. Fully explainable."""
    raw_demand = _demand_raw(hotspot)

    # --- ⚖️ COVERAGE-BIAS CORRECTION -------------------------------------
    if bias_model is not None and census_row is not None:
        observed = float(hotspot.get("report_count", 0))
        p = bias_model.propensity(census_row)
        p_ref = bias_model.reference_propensity
        bias_factor = float(max(0.50, min(3.00, p_ref / p if p > 0 else 3.00)))
        # Under average connectivity this block would have filed:
        expected = observed * bias_factor
    else:
        bias_factor = 1.0
        expected = float(hotspot.get("report_count", 0))

    adjusted_demand = float(min(1.0, raw_demand * bias_factor))

    # --- REACH: people served, log-scaled, boosted for vulnerable groups ---
    pop = float((census_row or {}).get("population", 100_000))
    sc_st = float((census_row or {}).get("sc_st_share", 0.2))
    reach = float(min(1.0, (math.log10(max(1.0, pop)) / 6.0) * 0.75 + sc_st * 0.25))

    # --- EQUITY: deprivation + aspirational + gender access gap -----------
    bpl = float((census_row or {}).get("bpl_share", 0.25))
    lit = float((census_row or {}).get("literacy_rate", 0.7))
    flit = float((census_row or {}).get("female_literacy_rate", 0.6))
    aspirational = str((census_row or {}).get("aspirational", "")).lower() in ("true", "1", "yes")
    tribal = str((census_row or {}).get("tribal", "")).lower() in ("true", "1", "yes")
    equity = float(min(1.0,
                       0.45 * (bpl / 0.55)
                       + 0.25 * (1.0 - lit)
                       + 0.20 * max(0.0, lit - flit) / 0.20
                       + (0.10 if aspirational else 0.0)
                       + (0.05 if tribal else 0.0)))

    # --- FEASIBILITY: placeholder until agency-capacity data lands (Day 7) -
    feasibility = 0.6 if not aspirational else 0.45  # harder terrain, thinner capacity

    return {
        "components": {
            "demand": round(adjusted_demand, 4),
            "deficit": round(float(deficit), 4),
            "reach": round(reach, 4),
            "equity": round(equity, 4),
            "feasibility": round(feasibility, 4),
            "saturation": round(float(saturation), 4),
        },
        "demand_detail": {
            "raw": round(raw_demand, 4),
            "expected_reports": round(expected, 2),
            "observed_reports": float(hotspot.get("report_count", 0)),
            "bias_factor": round(bias_factor, 4),
            "adjusted": round(adjusted_demand, 4),
            "model": bias_model.method if bias_model else "none",
        },
    }


def priority_score(components: dict, weights: dict) -> float:
    """P = 100 * (weighted sum) * (1 - saturation). Deterministic. Auditable."""
    total_w = sum(weights.get(k, 0.0) for k in ("demand", "deficit", "reach", "equity", "feasibility"))
    if total_w <= 0:
        return 0.0
    weighted = sum(
        (weights.get(k, 0.0) / total_w) * float(components.get(k, 0.0))
        for k in ("demand", "deficit", "reach", "equity", "feasibility")
    )
    sat = float(components.get("saturation", 0.0))
    return round(100.0 * weighted * (1.0 - sat), 2)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def score_all(
    reports: list[dict],
    weights: dict | None = None,
    sector: str = "all",
) -> list[dict]:
    """End-to-end: reports -> hotspots -> scored, ranked, lineage-tagged."""
    weights = weights or {"demand": 0.30, "deficit": 0.25, "reach": 0.20, "equity": 0.15, "feasibility": 0.10}
    census = {r["lgd_block_code"]: r for r in load_census()}
    nidi = load_nidi()

    hotspots = build_hotspots(reports)

    # Fit the bias model on what we actually observed, per block.
    observed_by_block: dict[str, int] = defaultdict(int)
    for h in hotspots:
        observed_by_block[h["lgd_block_code"]] += h["report_count"]

    from engine.bias import fit_bias_model
    bias_model = fit_bias_model(list(census.values()), dict(observed_by_block), nidi, sector=sector)

    out = []
    for h in hotspots:
        row = census.get(h["lgd_block_code"])
        deficit = nidi.get((h["lgd_block_code"], h["sector"]), 0.5)
        res = compute_components(h, row, deficit, bias_model)
        score = priority_score(res["components"], weights)
        h = {k: v for k, v in h.items() if not k.startswith("_")}
        h["demand"] = res["demand_detail"]
        h["components"] = res["components"]
        h["weights"] = weights
        h["priority_score"] = score
        h["lineage"] = {
            "census_row": f"data/census_seed.csv#{h['lgd_block_code']}",
            "nidi_row": f"data/nidi_index.csv#{h['lgd_block_code']}:{h['sector']}",
            "model_version": "score_v1.2",
            "bias_model": bias_model.method,
            "bias_coefficients": dict(bias_model.coefficients),
            "bias_reference_propensity": round(bias_model.reference_propensity, 5),
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
        out.append(h)

    out.sort(key=lambda x: x["priority_score"], reverse=True)
    for i, h in enumerate(out, start=1):
        h["rank"] = i
    return out
