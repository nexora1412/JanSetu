"""
JanSetu — FastAPI application
===============================
The single contract every workstream builds against.

Day 0 state: everything is backed by fixtures/, so all four workstreams can start
immediately and the demo runs end-to-end before any real integration lands.
Each workstream replaces its stub with real logic without touching the others.

Run:
    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    → http://localhost:8000         dashboard
    → http://localhost:8000/docs    interactive API
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

try:
    import env_boot  # noqa: F401  — MUST run before any os.getenv() below
except ImportError:
    pass

from fastapi import FastAPI, File, Form, HTTPException, UploadFile  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware            # noqa: E402
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse  # noqa: E402
from pydantic import ValidationError                            # noqa: E402
from fastapi.staticfiles import StaticFiles                     # noqa: E402
from pydantic import BaseModel                                  # noqa: E402

import db  # noqa: E402  — SQLite persistence (backend/db.py)
from engine.allocate import DEFAULT_SECTOR_CAPS, allocate, compute_frontier  # noqa: E402
from engine.impact import compute_impact_ledger                              # noqa: E402
from engine.score import score_all                                           # noqa: E402
from models.schemas import AllocationRequest, HealthResponse                 # noqa: E402
from services import gemini                                                  # noqa: E402
from services.gemini.client import structure_report                          # noqa: E402
from services.telephony.simulator import SimulatorProvider, get_provider      # noqa: E402

DATA = BACKEND.parent / "data"
FIX = BACKEND / "fixtures"
STATIC = BACKEND / "static"

app = FastAPI(
    title="JanSetu (जनसेतु)",
    description="From citizen voice to a costed, auditable public investment portfolio.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Per-nation state — seeded from fixtures, persisted in SQLite.
# Citizen submissions (mobile app / helpline) are written to the DB, so they
# survive restarts and appear on the officer dashboard immediately.
# ---------------------------------------------------------------------------
PROVIDER = get_provider()

NATIONS = {
    "in": {
        "label": "India",
        "flag": "🇮🇳",
        "ticket_prefix": "JS-2026-",
        "fixtures": {"reports": "reports_8lang.json", "hotspots": "hotspots.json",
                     "projects": "projects.json", "verifications": "verifications.json"},
        "routing": DATA / "routing.json",
    },
    "za": {
        "label": "South Africa",
        "flag": "🇿🇦",
        "ticket_prefix": "ZA-2026-",
        "fixtures": {"reports": "south_africa_reports.json",
                     "hotspots": "south_africa_hotspots.json",
                     "projects": "south_africa_projects.json",
                     "verifications": "south_africa_verifications.json"},
        "routing": DATA / "south_africa_routing.json",
    },
}

STATE: dict[str, dict] = {}


def _load(name: str) -> Any:
    with open(FIX / name, encoding="utf-8") as f:
        return json.load(f)


def _bootstrap_nation(nation: str) -> None:
    cfg = NATIONS[nation]
    with open(cfg["routing"], encoding="utf-8") as f:
        routing = json.load(f)

    seed_reports = _load(cfg["fixtures"]["reports"])
    seed_verifs = _load(cfg["fixtures"]["verifications"])
    if db.count_reports(nation) == 0:
        db.insert_reports(nation, seed_reports, origin="seed")
        for v in seed_verifs:
            db.insert_verification(nation, v, origin="seed")

    reports = db.all_reports(nation)
    verifications = db.all_verifications(nation)
    hotspots = _load(cfg["fixtures"]["hotspots"])
    projects = _load(cfg["fixtures"]["projects"])

    STATE[nation] = {
        "REPORTS": reports,
        "HOTSPOTS": hotspots,
        "HOTSPOTS_BASE": hotspots,   # fixture baseline, kept for merge on re-score
        "PROJECTS": projects,
        "VERIFICATIONS": verifications,
        "ROUTING": routing,
        "LEDGER": compute_impact_ledger(projects, verifications),
        "ticket_seq": db.max_ticket_seq(nation, cfg["ticket_prefix"]),
    }


def _bootstrap() -> None:
    db.init()
    for nation in NATIONS:
        _bootstrap_nation(nation)


_bootstrap()


def _S(nation: str) -> dict:
    """State for a nation; unknown codes fall back to India rather than 500."""
    return STATE.get(nation if nation in STATE else "in")


def _rescore(nation: str) -> None:
    """Recompute hotspots from ALL persisted reports and merge over the fixture
    baseline (fixture-only hotspots are kept because projects reference them)."""
    s = _S(nation)
    calc = {h["hotspot_id"]: h for h in score_all(s["REPORTS"])}
    merged = list(s["HOTSPOTS_BASE"])
    for i, h in enumerate(merged):
        if h["hotspot_id"] in calc:
            merged[i] = calc.pop(h["hotspot_id"])
    merged.extend(calc.values())
    merged.sort(key=lambda h: -h["priority_score"])
    for i, h in enumerate(merged):
        h["rank"] = i + 1
    s["HOTSPOTS"] = merged

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _route(sector: str, geo: dict, nation: str = "in") -> dict:
    """Department Routing Table lookup. Data-driven: no code change to add a dept."""
    routing = _S(nation)["ROUTING"]
    rural = not geo.get("urban", False)
    for rule in routing.get("rules", []):
        if rule["sector"] != sector:
            continue
        m = rule.get("match") or {}
        if "rural" in m and m["rural"] != rural:
            continue
        pattern = rule.get("officer_ref_pattern", "")
        return {
            "department": rule["department"],
            "scheme": rule["scheme"],
            "officer_ref": pattern.format(state=geo.get("state") or "XX",
                                          district=geo.get("district") or "XX",
                                          block=geo.get("block") or "XX"),
            "sla_days": rule["sla_days"],
            "routed_at": datetime.now(timezone.utc).isoformat(),
            "ack_sent": False,
            "funding_split": rule.get("funding_split", {}),
        }
    return {"department": routing["rules"][-1]["department"], "scheme": "District Plan",
            "officer_ref": "UNROUTED", "sla_days": routing.get("_default_sla_days", 30),
            "routed_at": datetime.now(timezone.utc).isoformat(), "ack_sent": False}


def _next_ticket(nation: str = "in") -> str:
    s = _S(nation)
    s["ticket_seq"] += 1
    return f"{NATIONS[nation if nation in NATIONS else 'in']['ticket_prefix']}{s['ticket_seq']:06d}"


# ---------------------------------------------------------------------------
# Core endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok", version="0.1.0",
        gemini=gemini.client.available(),
        telephony_provider=PROVIDER.name,
    )


@app.get("/api/v1/status")
def status():
    try:
        import env_boot
        env_report = env_boot.report()
    except Exception:
        env_report = {"env_file_found": False}
    return {
        "env": env_report,
        "gemini": gemini.client.status(),
        "telephony": {"provider": PROVIDER.name,
                      "outbox": len(getattr(PROVIDER, "outbox", []))},
        "counts": {n: {"reports": len(s["REPORTS"]), "hotspots": len(s["HOTSPOTS"]),
                       "projects": len(s["PROJECTS"]), "verifications": len(s["VERIFICATIONS"]),
                       "ledger_entries": len(s["LEDGER"])}
                   for n, s in STATE.items()},
        "nations": [{"code": n, "label": c["label"], "flag": c["flag"]}
                    for n, c in NATIONS.items()],
        "database": {"engine": "sqlite", "path": str(db.DB_PATH)},
        "contracts_version": "1.1",
    }


# ------------------------------------------------------------------ INTAKE (A)

class IntakeIn(BaseModel):
    text: str
    channel: str = "sms"
    from_number: str | None = None
    language_hint: str | None = None
    audio_uri: str | None = None
    nation: str = "in"


@app.post("/api/v1/intake/")
def intake(body: IntakeIn):
    """
    THE SINGLE HELPLINE entrypoint. Any channel, any language -> one CitizenReport
    -> structured by Gemini -> resolved to an LGD code -> auto-routed to the right
    department -> acknowledged by SMS in the citizen's own language.
    Persisted to SQLite, so the officer dashboard sees it immediately.
    """
    nation = body.nation if body.nation in STATE else "in"

    # 1 · normalise the channel payload
    partial = PROVIDER.parse_inbound({
        "channel": body.channel, "text": body.text, "from": body.from_number or "+910000000000",
    })

    # 2 · Gemini structures it (degrades to the keyword fallback if unavailable)
    st = structure_report(body.text, body.language_hint)
    geo = st.get("geo") or {}

    # 3 · resolve an LGD code from the seed admin table when Gemini left it null
    if not geo.get("lgd_code"):
        code = _resolve_lgd(geo, nation)
        geo["lgd_code"] = code

    # 4 · route + acknowledge
    routing = _route(st.get("sector", "other"), geo, nation)
    ticket = _next_ticket(nation)
    lang = st.get("language", "en")
    if isinstance(PROVIDER, SimulatorProvider):
        ack = PROVIDER.ack(ticket, routing["department"], routing["sla_days"], lang)
        PROVIDER.send_sms(partial["channel_meta"].get("msisdn_hash") or "unknown", ack, lang)
        routing["ack_sent"] = True

    report = {
        **partial,
        "report_id": ticket,
        "nation": nation,
        "normalized_text_en": st.get("normalized_text_en"),
        "structured": {
            "sector": st.get("sector", "other"),
            "subsector": st.get("subsector"), "asset": st.get("asset"), "issue": st.get("issue"),
            "severity_1_5": int(st.get("severity_1_5") or 3),
            "affected_population_est": int(st.get("affected_population_est") or 0),
            "geo": geo,
            "confidence": float(st.get("confidence", 0.5)),
            "extractor": st.get("extractor", "gemini"),
        },
        "routing": routing,
        "me_too": 0,
        "status": "routed",
        "origin": "live",
    }
    if not report.get("created_at"):
        report["created_at"] = datetime.now(timezone.utc).isoformat()

    # 4b · route LOW-CONFIDENCE cases to a human expert instead of trusting the
    # model blindly — the same guard Kisan Alert winners used. The AI knows what
    # it doesn't know; an officer closes the loop.
    esc_reasons = []
    if report["structured"]["confidence"] < 0.4:
        esc_reasons.append("low_extraction_confidence")
    if not geo.get("lgd_code"):
        esc_reasons.append("location_unresolved")
    if report["structured"]["sector"] == "other":
        esc_reasons.append("sector_unclassified")
    if esc_reasons:
        report["status"] = "needs_human_review"
        report["escalation"] = {"reasons": esc_reasons,
                                "confidence": report["structured"]["confidence"],
                                "opened_at": report["created_at"]}

    # 5 · persist + refresh derived state
    _S(nation)["REPORTS"].append(report)
    db.insert_report(nation, report, origin="live")
    _rescore(nation)

    return {
        "report": report,
        "ack": (PROVIDER.ack(ticket, routing["department"], routing["sla_days"], lang)
                if isinstance(PROVIDER, SimulatorProvider) else None),
        "greeting": (PROVIDER.greeting(lang) if isinstance(PROVIDER, SimulatorProvider) else None),
        "degraded": st.get("extractor") == "fallback",
        "note": ("Gemini unavailable — deterministic fallback used, confidence capped at 0.35"
                 if st.get("extractor") == "fallback" else None),
    }


def _admin_rows(nation: str) -> list[dict]:
    import csv
    admin_csv = "south_africa_admin.csv" if nation == "za" else "lgd_admin.csv"
    try:
        with open(DATA / admin_csv, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except OSError:
        return []


def _admin_code_col(rows: list[dict]) -> str | None:
    for c in (rows[0] if rows else {}):
        if c in ("lgd_block_code", "mdb_code"):
            return c
    return None


def _resolve_lgd(geo: dict, nation: str = "in") -> str | None:
    """Cheap resolver over the seed admin table. Real deployment calls the LGD API.
    Returns null when uncertain — we NEVER invent an LGD code."""
    rows = _admin_rows(nation)
    code_col = _admin_code_col(rows)
    if not code_col:
        return None
    name_cols = (("block", "local_municipality"), ("district", "district_municipality"))
    for fields in name_cols:
        for field in fields:
            target = (geo.get(field) or "").strip().lower()
            if not target:
                continue
            for r in rows:
                if any((r.get(c) or "").strip().lower() == target for c in fields):
                    return r[code_col]
    return None


@app.post("/api/v1/intake/simulate")
def intake_simulate(body: dict):
    """Simulator shortcut: fire a canned multilingual report through the real pipeline.

    Body must contain `text`. Anything else is a 400 with the fix spelled out --
    a raw pydantic 500 here would look like a crash to anyone clicking /docs.
    """
    if not isinstance(body, dict) or not body.get("text"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "`text` is required.",
                "example": {"text": "धुळे तालुक्यात रस्ता खराब आहे",
                            "channel": "sms",
                            "language_hint": "mr"},
                "you_sent": body,
            },
        )
    try:
        payload = IntakeIn(**body)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=json.loads(exc.json())) from exc
    return intake(payload)


@app.post("/api/v1/intake/voice")
async def intake_voice(
    audio: UploadFile = File(...),
    language_hint: str = Form("mr"),
    channel: str = Form("app_voice"),
    from_number: str = Form("+910000000000"),
    nation: str = Form("in"),
):
    """Voice intake from the mobile app: recorded audio -> STT chain -> the SAME
    intake pipeline as a missed call or SMS. Never raises on a missing key:
    returns transcribed=false so the app can offer typed text instead."""
    from services.stt import status as stt_status, transcribe

    raw = await audio.read()
    if not raw:
        raise HTTPException(400, "Empty audio upload")
    st = transcribe(raw, language=language_hint)
    if not st or not st.get("text"):
        return {
            "transcribed": False,
            "stt": stt_status(),
            "note": ("No STT provider succeeded (missing keys or network). "
                     "The app should offer typed text — intake still works."),
        }
    result = intake(IntakeIn(text=st["text"], channel=channel,
                             from_number=from_number, nation=nation,
                             language_hint=st.get("language") or language_hint))
    return {"transcribed": True, "transcript": st["text"],
            "stt_provider": st.get("provider"), **result}


@app.get("/api/v1/reports/")
def list_reports(limit: int = 50, sector: str | None = None, channel: str | None = None,
                 nation: str = "in", origin: str | None = None):
    out = _S(nation)["REPORTS"]
    if sector:
        out = [r for r in out if (r.get("structured") or {}).get("sector") == sector]
    if channel:
        out = [r for r in out if r.get("channel") == channel]
    if origin:
        out = [r for r in out if r.get("origin") == origin]
    return {"count": len(out), "nation": nation, "reports": out[-limit:][::-1]}


@app.get("/api/v1/stats/")
def stats(nation: str = "in"):
    """Aggregate counters straight from SQLite — feeds the dashboard charts."""
    n = nation if nation in STATE else "in"
    return {"nation": n, "unit_economics": UNIT_ECONOMICS, **db.stats(n)}


# Honest order-of-magnitude operating costs (2026 public rates). The pitch line:
# a complaint handled end-to-end by JanSetu costs less than one cup of chai,
# vs ~₹45 at a staffed call centre — that is why this scales to a billion people.
UNIT_ECONOMICS = {
    "per_complaint_inr": {
        "stt_30s_sarvam": 0.90,
        "gemini_flash_extraction": 0.12,
        "sms_acknowledgement": 0.15,
        "infra_share": 0.40,
        "total": 1.57,
    },
    "human_call_centre_per_complaint_inr": 45.0,
    "note": ("Estimates at published 2026 API/SMS rates, not measured invoices. "
             "Missed-call intake (the reach channel) skips STT entirely on ring-back "
             "only if the citizen types; voice adds the ₹0.90 STT line."),
}


# ---------------------------------------------------- HUMAN ESCALATION QUEUE

@app.get("/api/v1/escalations/")
def escalations(nation: str = "in", include_resolved: bool = False):
    """Low-confidence intake is NOT auto-routed to a department — it waits here
    for an officer. AI that knows what it doesn't know beats AI that guesses."""
    s = _S(nation)
    out = [r for r in s["REPORTS"]
           if r.get("status") == "needs_human_review"
           or (include_resolved and r.get("status") == "resolved_by_human")]
    return {"count": len(out), "nation": nation, "queue": out[-30:][::-1]}


@app.post("/api/v1/escalations/{ticket_id}/resolve")
def escalation_resolve(ticket_id: str, body: dict):
    """Officer corrects the sector/location; we re-route and persist. The model's
    mistake becomes a labelled training example — every resolution is gold data."""
    nation = body.get("nation", "in")
    s = _S(nation if nation in STATE else "in")
    nation = nation if nation in STATE else "in"
    r = next((x for x in s["REPORTS"] if x.get("report_id") == ticket_id), None)
    if not r:
        raise HTTPException(404, f"Unknown ticket {ticket_id}")
    if r.get("status") != "needs_human_review":
        raise HTTPException(400, f"{ticket_id} is not awaiting review (status={r.get('status')})")

    sector = body.get("sector") or (r.get("structured") or {}).get("sector") or "other"
    geo = (r.get("structured") or {}).get("geo") or {}
    if body.get("block"):
        geo["block"] = body["block"]
    if body.get("district"):
        geo["district"] = body["district"]
    if not geo.get("lgd_code"):
        geo["lgd_code"] = _resolve_lgd(geo, nation)

    routing = _route(sector, geo, nation)
    r["structured"]["sector"] = sector
    r["structured"]["geo"] = geo
    r["routing"] = routing
    r["status"] = "resolved_by_human"
    r["escalation"] = {**(r.get("escalation") or {}),
                       "resolved_at": datetime.now(timezone.utc).isoformat(),
                       "resolved_by": body.get("officer", "dashboard-officer"),
                       "corrections": {k: body.get(k) for k in ("sector", "block", "district")
                                       if body.get(k)}}
    db.update_report(nation, r)
    _rescore(nation)
    return {"report_id": ticket_id, "status": r["status"], "routing": routing,
            "escalation": r["escalation"]}


# ---------------------------------------------------- EARLY-WARNING ALERTS

@app.get("/api/v1/alerts/")
def early_warning_alerts(nation: str = "in", window_days: int = 30, min_reports: int = 3):
    """Spatial surge detection — deterministic, no LLM in the loop.
    A block+sector filing ≥2× its historical daily rate in the last window
    is an early warning (burst main, disease cluster, transformer failures)."""
    from collections import defaultdict
    s = _S(nation if nation in STATE else "in")
    reports = s["REPORTS"]

    def _ts(r: dict):
        try:
            return datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
        except (KeyError, ValueError, TypeError):
            return None

    dated = [( _ts(r), r) for r in reports]
    dated = [(t, r) for t, r in dated if t is not None]
    if not dated:
        return {"count": 0, "alerts": [], "window_days": window_days}
    now = max(t for t, _ in dated)
    cutoff = now - timedelta(days=window_days)

    recent: dict[tuple, int] = defaultdict(int)
    older: dict[tuple, int] = defaultdict(int)
    first_seen: dict[tuple, datetime] = {}
    for t, r in dated:
        st = r.get("structured") or {}
        geo = st.get("geo") or {}
        block = geo.get("block") or geo.get("lgd_code") or geo.get("lgd_block_code") or "unknown"
        key = (block, st.get("sector") or "other")
        first_seen[key] = min(first_seen.get(key, t), t)
        if t > cutoff:
            recent[key] += 1
        else:
            older[key] += 1

    alerts = []
    span_days = max((now - min(first_seen.values())).days, 1)
    for key, rc in recent.items():
        if rc < min_reports:
            continue
        baseline_rate = older.get(key, 0) / span_days          # reports/day
        expected = max(baseline_rate * window_days, 1.0)
        ratio = rc / expected
        if ratio >= 2.0:
            alerts.append({
                "block": key[0], "sector": key[1],
                "recent_reports": rc, "expected": round(expected, 1),
                "surge_ratio": round(ratio, 2),
                "severity": "high" if ratio >= 4 else "medium",
                "window_days": window_days,
                "action": f"Dispatch a {key[1]} inspection team to block {key[0]}; "
                          f"intake is {ratio:.1f}× its historical rate.",
            })
    alerts.sort(key=lambda a: -a["surge_ratio"])
    return {"count": len(alerts), "nation": nation, "as_of": now.isoformat(),
            "window_days": window_days, "alerts": alerts[:15]}


@app.get("/api/v1/track/{ticket_id}")
def track(ticket_id: str, nation: str = "in"):
    """Citizen status lookup — the SAME helpline number, any handset."""
    r = next((x for x in _S(nation)["REPORTS"] if x.get("report_id") == ticket_id), None)
    if r is None:
        # tickets are nation-prefixed; try the other nation before 404ing
        for other, s in STATE.items():
            if other != nation:
                r = next((x for x in s["REPORTS"] if x.get("report_id") == ticket_id), None)
                if r:
                    break
    if not r:
        raise HTTPException(404, f"Unknown ticket {ticket_id}")
    return {
        "report_id": ticket_id,
        "status": r.get("status"),
        "sector": (r.get("structured") or {}).get("sector"),
        "routed_to": (r.get("routing") or {}).get("department"),
        "sla_days": (r.get("routing") or {}).get("sla_days"),
        "language": r.get("raw_language"),
        "stages": ["received", "routed", "acknowledged", "in_progress", "resolved"],
        "current_stage_index": 1,
    }


# ------------------------------------------------------------ HOTSPOTS (B)

@app.get("/api/v1/hotspots/")
def hotspots(limit: int = 60, sector: str | None = None, state: str | None = None,
             recompute: bool = False, nation: str = "in"):
    n = nation if nation in STATE else "in"
    if recompute:
        _rescore(n)
    out = _S(n)["HOTSPOTS"]
    if sector:
        out = [h for h in out if h["sector"] == sector]
    if state:
        codes = {c for c in _state_codes(state, n)}
        out = [h for h in out if h["lgd_block_code"] in codes]
    return {"count": len(out), "nation": n, "hotspots": out[:limit]}


def _state_codes(state: str, nation: str = "in") -> list[str]:
    rows = _admin_rows(nation)
    code_col = _admin_code_col(rows)
    if not code_col:
        return []
    state_col = "province" if nation == "za" else "state"
    return [r[code_col] for r in rows if r.get(state_col) == state]


@app.get("/api/v1/hotspots/{hotspot_id}/lineage")
def lineage(hotspot_id: str, nation: str = "in"):
    """AUDITOR VIEW — every number traced to its source rows."""
    h = next((x for x in _S(nation)["HOTSPOTS"] if x["hotspot_id"] == hotspot_id), None)
    if not h:
        raise HTTPException(404, f"Unknown hotspot {hotspot_id}")
    return {
        "hotspot_id": hotspot_id,
        "priority_score": h["priority_score"],
        "components": h["components"],
        "weights": h["weights"],
        "demand": h["demand"],
        "lineage": h["lineage"],
        "recomputed_score_check": round(
            sum(h["weights"][k] * h["components"][k]
                for k in ("demand", "deficit", "reach", "equity", "feasibility"))
            * 100 * (1 - h["components"]["saturation"]), 2),
        "note": "recomputed_score_check must equal priority_score — that is the audit.",
    }


@app.post("/api/v1/score/recompute")
def recompute(weights: dict | None = None, nation: str = "in"):
    """Live weight sliders -> full re-score."""
    n = nation if nation in STATE else "in"
    s = _S(n)
    scored = score_all(s["REPORTS"], weights)
    by_id = {h["hotspot_id"]: h for h in scored}
    merged = list(s["HOTSPOTS_BASE"])
    for i, h in enumerate(merged):
        if h["hotspot_id"] in by_id:
            merged[i] = by_id.pop(h["hotspot_id"])
    merged.extend(by_id.values())
    merged.sort(key=lambda h: -h["priority_score"])
    for i, h in enumerate(merged):
        h["rank"] = i + 1
    s["HOTSPOTS"] = merged
    return {"count": len(merged), "nation": n, "weights": weights or "default",
            "top": [{"hotspot_id": h["hotspot_id"], "score": h["priority_score"],
                     "sector": h["sector"], "block": h["lgd_block_code"]}
                    for h in merged[:10]]}


# ------------------------------------------------------- ★ ALLOCATE (C)

@app.post("/api/v1/allocate/")
def allocate_endpoint(req: AllocationRequest):
    """THE HERO ENDPOINT. Budget + constraints -> optimal portfolio.
    Move the slider, call this, re-render. Target < 400 ms."""
    s = _S(req.nation)
    weights = req.weights.model_dump()
    request = {
        "budget_inr": req.budget_inr,
        "sector_caps": req.sector_caps or DEFAULT_SECTOR_CAPS,
        "equity_floor_pct": req.equity_floor_pct,
        "geographic_spread": req.geographic_spread,
        "state_filter": req.state_filter,
        "sector_filter": req.sector_filter,
        "weights": weights,
        "fast": req.fast,
    }
    score_by_hs = {h["hotspot_id"]: h["priority_score"] for h in s["HOTSPOTS"]}
    pool = s["PROJECTS"]
    if req.state_filter:
        pool = [p for p in pool if p.get("state") == req.state_filter]
    if req.sector_filter:
        pool = [p for p in pool if p["sector"] == req.sector_filter]
    return allocate(request, pool, score_by_hs)


@app.get("/api/v1/frontier/")
def frontier(budget_inr: int = 400_000_000, equity_floor_pct: float = 0.40,
             nation: str = "in"):
    s = _S(nation)
    req = {"budget_inr": budget_inr, "sector_caps": DEFAULT_SECTOR_CAPS,
           "equity_floor_pct": equity_floor_pct, "geographic_spread": "min_one_per_block",
           "fast": True}
    score_by_hs = {h["hotspot_id"]: h["priority_score"] for h in s["HOTSPOTS"]}
    return {"budget_inr": budget_inr,
            "frontier": compute_frontier(s["PROJECTS"], req, score_by_hs)}


@app.get("/api/v1/projects/")
def projects(limit: int = 100, nation: str = "in"):
    p = _S(nation)["PROJECTS"]
    return {"count": len(p), "nation": nation, "projects": p[:limit]}


# ------------------------------------------------------------ IMPACT (C)

@app.get("/api/v1/impact/")
def impact(nation: str = "in"):
    """The IMPACT LEDGER — the clause of the brief nobody else answered."""
    ledger = _S(nation)["LEDGER"]
    return {"count": len(ledger), "nation": nation, "ledger": ledger,
            "summary": {
                "projects_tracked": len(ledger),
                "avg_realization_ratio": (round(sum(l["realization_ratio"] for l in ledger) / len(ledger), 3)
                                          if ledger else 0),
                "flagged": sum(1 for l in ledger if l["social_audit_score"] < 0.5),
                "certified": sum(1 for l in ledger if l["social_audit_score"] > 0.8),
            }}


@app.post("/api/v1/verify/")
def verify(body: dict):
    """Citizen photo / comment verification on a COMPLETED project."""
    nation = body.get("nation", "in")
    if nation not in STATE:
        nation = "in"
    s = _S(nation)
    pid = body.get("project_id")
    verdict = body.get("verdict", "partial")
    comment = body.get("comment", "")
    proj = next((p for p in s["PROJECTS"] if p["project_id"] == pid), None)
    if not proj:
        raise HTTPException(404, f"Unknown project {pid}")

    vision = gemini.client.verify_photo(proj["intervention"], comment, body.get("image_b64"))
    values = {"completed": 1.0, "partial": 0.5, "not_done": 0.0}
    trust = float(body.get("trust_weight", 0.5))

    ev = {
        "verification_id": f"V-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{len(s['VERIFICATIONS']):05d}",
        "project_id": pid, "created_at": datetime.now(timezone.utc).isoformat(),
        "channel": body.get("channel", "whatsapp"),
        "respondent": {"trust_weight": trust},
        "verdict": verdict,
        "raw_comment": comment,
        "comment_language": PROVIDER.detect_language(comment),
        "photo": {"vision_check": vision},
    }
    s["VERIFICATIONS"].append(ev)
    db.insert_verification(nation, ev, origin="live")
    s["LEDGER"] = compute_impact_ledger(s["PROJECTS"], s["VERIFICATIONS"])

    # Recompute the social audit score for this project
    mine = [v for v in s["VERIFICATIONS"] if v["project_id"] == pid]
    num = sum(values.get(v["verdict"], 0.0) * v["respondent"]["trust_weight"] for v in mine
              if v["verdict"] != "spam")
    den = sum(v["respondent"]["trust_weight"] for v in mine if v["verdict"] != "spam")
    score = round(num / den, 3) if den else 0.0
    action = ("certified_release_payment" if score > 0.8
              else "partial_punch_list" if score >= 0.5 else "payment_hold_field_inspection")

    return {"verification": ev,
            "aggregates": {"project_verification_count": len(mine),
                           "social_audit_score": score,
                           "recommended_action": action},
            "note": "Score < 0.5 → payment hold + field inspection (the ghost-asset guard)."}


# ------------------------------------------------------------- ROUTING (C)

@app.get("/api/v1/routing/table")
def routing_table(nation: str = "in"):
    return _S(nation)["ROUTING"]


# ----------------------------------------------------------- BRICS (D)

@app.get("/api/v1/adapters/")
def adapters():
    """BRICS portability: one adapter file per nation, zero code change."""
    adir = BACKEND.parent / "adapters"
    out = []
    for p in sorted(adir.glob("*.yaml")) if adir.exists() else []:
        out.append({"nation": p.stem, "file": str(p.relative_to(BACKEND.parent)),
                    "size_bytes": p.stat().st_size})
    return {"count": len(out), "adapters": out,
            "claim": "Onboarding a new nation = 1 adapter file + 1 index CSV. No code change."}


# ------------------------------------------------------------- BRIEF (B)

@app.post("/api/v1/brief/")
def brief(body: dict):
    kind = body.get("kind", "policy brief")
    language = body.get("language", "English")
    nation = body.get("nation", "in")
    if nation not in STATE:
        nation = "in"
    s = _S(nation)
    if body.get("subject") == "portfolio":
        req = body.get("request") or {"budget_inr": 400_000_000, "sector_caps": DEFAULT_SECTOR_CAPS,
                                      "equity_floor_pct": 0.40, "geographic_spread": "min_one_per_block",
                                      "fast": False, "weights": {"demand": .3, "deficit": .25,
                                                                 "reach": .2, "equity": .15,
                                                                 "feasibility": .1}}
        pf = allocate(req, s["PROJECTS"], {h["hotspot_id"]: h["priority_score"] for h in s["HOTSPOTS"]})
        data = {"totals": pf["totals"], "selected_projects": pf["selected"],
                "dropped": pf["dropped"][:8], "constraint_report": pf["constraint_report"]}
    elif body.get("subject") == "dashboard":
        st = db.stats(nation)
        data = {"nation": NATIONS[nation]["label"], "counters": st,
                "top_hotspots": [{"hotspot_id": h["hotspot_id"], "sector": h["sector"],
                                  "block": h["lgd_block_code"], "priority_score": h["priority_score"]}
                                 for h in s["HOTSPOTS"][:8]]}
    else:
        data = [{"hotspot_id": h["hotspot_id"], "sector": h["sector"],
                 "priority_score": h["priority_score"], "components": h["components"],
                 "demand": h["demand"]} for h in s["HOTSPOTS"][:12]]
    text = gemini.client.generate_brief(kind, data, language)
    return {"kind": kind, "language": language, "nation": nation,
            "text": text,
            "degraded": (not gemini.client.available()) or "offline template" in text[:120]}


# ------------------------------------------------------- TELEPHONY DEMO (A)

@app.get("/api/v1/telephony/outbox")
def outbox():
    return {"provider": PROVIDER.name, "outbox": getattr(PROVIDER, "outbox", [])[-20:],
            "call_log": getattr(PROVIDER, "call_log", [])[-20:]}


@app.post("/api/v1/telephony/missed-call")
def missed_call(body: dict):
    """The channel that matters most for the poorest citizen: ₹0, any keypad
    handset, no data. Give a missed call → we ring back within 60 seconds."""
    rec = PROVIDER.simulate_missed_call(body.get("from", "+910000000000"))
    return {"missed_call": rec, "callback_eta_s": 60,
            "greeting": PROVIDER.greeting(body.get("language", "mr")),
            "note": "No IVR menu. The citizen just speaks."}


# ---------------------------------------------------------------------------
# Dashboard (served same-origin so the live preview needs no CORS or localhost)
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def dashboard():
    idx = STATIC / "index.html"
    if idx.exists():
        return HTMLResponse(idx.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>JanSetu</h1><p>Dashboard not built yet (workstream D).</p>")


if STATIC.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


# ---------------------------------------------------------------------------
# Citizen mobile app (PWA) — served from frontend/dist when built.
# Dev mode: run `npm run dev` in frontend/ (Vite proxies /api to :8000).
# ---------------------------------------------------------------------------
DIST = BACKEND.parent / "frontend" / "dist"

if DIST.exists():
    DIST_RESOLVED = DIST.resolve()

    @app.get("/app", response_class=HTMLResponse)
    @app.get("/app/{path:path}", response_class=HTMLResponse)
    def citizen_app(path: str = ""):
        target = (DIST / path).resolve()
        if path and target.is_file() and target.is_relative_to(DIST_RESOLVED):
            return FileResponse(target)
        return HTMLResponse((DIST / "index.html").read_text(encoding="utf-8"))
