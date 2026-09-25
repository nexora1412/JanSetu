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
from datetime import datetime, timezone
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
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# State — seeded from fixtures so the app is demoable from the first request
# ---------------------------------------------------------------------------
REPORTS: list[dict] = []
HOTSPOTS: list[dict] = []
PROJECTS: list[dict] = []
VERIFICATIONS: list[dict] = []
ROUTING: dict = {}
PROVIDER = get_provider()
LEDGER: list[dict] = []


def _load(name: str) -> Any:
    with open(FIX / name, encoding="utf-8") as f:
        return json.load(f)


def _bootstrap() -> None:
    global REPORTS, HOTSPOTS, PROJECTS, VERIFICATIONS, ROUTING, LEDGER
    REPORTS = _load("reports_8lang.json")
    HOTSPOTS = _load("hotspots.json")
    PROJECTS = _load("projects.json")
    VERIFICATIONS = _load("verifications.json")
    with open(DATA / "routing.json", encoding="utf-8") as f:
        ROUTING = json.load(f)
    LEDGER = compute_impact_ledger(PROJECTS, VERIFICATIONS)


_bootstrap()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _route(sector: str, geo: dict) -> dict:
    """Department Routing Table lookup. Data-driven: no code change to add a dept."""
    rural = not geo.get("urban", False)
    for rule in ROUTING.get("rules", []):
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
    return {"department": ROUTING["rules"][-1]["department"], "scheme": "District Plan",
            "officer_ref": "UNROUTED", "sla_days": ROUTING.get("_default_sla_days", 30),
            "routed_at": datetime.now(timezone.utc).isoformat(), "ack_sent": False}


def _next_ticket() -> str:
    return f"JS-2026-{len(REPORTS) + 1:06d}"


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
        "counts": {"reports": len(REPORTS), "hotspots": len(HOTSPOTS),
                   "projects": len(PROJECTS), "verifications": len(VERIFICATIONS),
                   "ledger_entries": len(LEDGER)},
        "contracts_version": "1.0",
    }


# ------------------------------------------------------------------ INTAKE (A)

class IntakeIn(BaseModel):
    text: str
    channel: str = "sms"
    from_number: str | None = None
    language_hint: str | None = None
    audio_uri: str | None = None


@app.post("/api/v1/intake/")
def intake(body: IntakeIn):
    """
    THE SINGLE HELPLINE entrypoint. Any channel, any language -> one CitizenReport
    -> structured by Gemini -> resolved to an LGD code -> auto-routed to the right
    department -> acknowledged by SMS in the citizen's own language.
    """
    # 1 · normalise the channel payload
    partial = PROVIDER.parse_inbound({
        "channel": body.channel, "text": body.text, "from": body.from_number or "+910000000000",
    })

    # 2 · Gemini structures it (degrades to the keyword fallback if unavailable)
    st = structure_report(body.text, body.language_hint)
    geo = st.get("geo") or {}

    # 3 · resolve an LGD code from the seed admin table when Gemini left it null
    if not geo.get("lgd_code"):
        code = _resolve_lgd(geo)
        geo["lgd_code"] = code

    # 4 · route + acknowledge
    routing = _route(st.get("sector", "other"), geo)
    ticket = _next_ticket()
    lang = st.get("language", "en")
    if isinstance(PROVIDER, SimulatorProvider):
        ack = PROVIDER.ack(ticket, routing["department"], routing["sla_days"], lang)
        PROVIDER.send_sms(partial["channel_meta"].get("msisdn_hash") or "unknown", ack, lang)
        routing["ack_sent"] = True

    report = {
        **partial,
        "report_id": ticket,
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
    }
    REPORTS.append(report)

    return {
        "report": report,
        "ack": (PROVIDER.ack(ticket, routing["department"], routing["sla_days"], lang)
                if isinstance(PROVIDER, SimulatorProvider) else None),
        "greeting": (PROVIDER.greeting(lang) if isinstance(PROVIDER, SimulatorProvider) else None),
        "degraded": st.get("extractor") == "fallback",
        "note": ("Gemini unavailable — deterministic fallback used, confidence capped at 0.35"
                 if st.get("extractor") == "fallback" else None),
    }


def _resolve_lgd(geo: dict) -> str | None:
    """Cheap resolver over the seed admin table. Real deployment calls the LGD API.
    Returns null when uncertain — we NEVER invent an LGD code."""
    try:
        import csv
        with open(DATA / "lgd_admin.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except OSError:
        return None
    for field in ("block", "district"):
        target = (geo.get(field) or "").strip().lower()
        if not target:
            continue
        for r in rows:
            if r[field].strip().lower() == target:
                return r["lgd_block_code"]
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
                             from_number=from_number,
                             language_hint=st.get("language") or language_hint))
    return {"transcribed": True, "transcript": st["text"],
            "stt_provider": st.get("provider"), **result}


@app.get("/api/v1/reports/")
def list_reports(limit: int = 50, sector: str | None = None, channel: str | None = None):
    out = REPORTS
    if sector:
        out = [r for r in out if (r.get("structured") or {}).get("sector") == sector]
    if channel:
        out = [r for r in out if r.get("channel") == channel]
    return {"count": len(out), "reports": out[-limit:][::-1]}


@app.get("/api/v1/track/{ticket_id}")
def track(ticket_id: str):
    """Citizen status lookup — the SAME helpline number, any handset."""
    r = next((x for x in REPORTS if x.get("report_id") == ticket_id), None)
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
             recompute: bool = False):
    global HOTSPOTS
    if recompute:
        HOTSPOTS = score_all(REPORTS)
    out = HOTSPOTS
    if sector:
        out = [h for h in out if h["sector"] == sector]
    if state:
        codes = {c for c in _state_codes(state)}
        out = [h for h in out if h["lgd_block_code"] in codes]
    return {"count": len(out), "hotspots": out[:limit]}


def _state_codes(state: str) -> list[str]:
    import csv
    with open(DATA / "lgd_admin.csv", newline="", encoding="utf-8") as f:
        return [r["lgd_block_code"] for r in csv.DictReader(f) if r["state"] == state]


@app.get("/api/v1/hotspots/{hotspot_id}/lineage")
def lineage(hotspot_id: str):
    """AUDITOR VIEW — every number traced to its source rows."""
    h = next((x for x in HOTSPOTS if x["hotspot_id"] == hotspot_id), None)
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
def recompute(weights: dict | None = None):
    """Live weight sliders -> full re-score."""
    global HOTSPOTS
    HOTSPOTS = score_all(REPORTS, weights)
    return {"count": len(HOTSPOTS), "weights": weights or "default",
            "top": [{"hotspot_id": h["hotspot_id"], "score": h["priority_score"],
                     "sector": h["sector"], "block": h["lgd_block_code"]}
                    for h in HOTSPOTS[:10]]}


# ------------------------------------------------------- ★ ALLOCATE (C)

@app.post("/api/v1/allocate/")
def allocate_endpoint(req: AllocationRequest):
    """THE HERO ENDPOINT. Budget + constraints -> optimal portfolio.
    Move the slider, call this, re-render. Target < 400 ms."""
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
    score_by_hs = {h["hotspot_id"]: h["priority_score"] for h in HOTSPOTS}
    pool = PROJECTS
    if req.state_filter:
        pool = [p for p in pool if p.get("state") == req.state_filter]
    if req.sector_filter:
        pool = [p for p in pool if p["sector"] == req.sector_filter]
    return allocate(request, pool, score_by_hs)


@app.get("/api/v1/frontier/")
def frontier(budget_inr: int = 400_000_000, equity_floor_pct: float = 0.40):
    req = {"budget_inr": budget_inr, "sector_caps": DEFAULT_SECTOR_CAPS,
           "equity_floor_pct": equity_floor_pct, "geographic_spread": "min_one_per_block",
           "fast": True}
    score_by_hs = {h["hotspot_id"]: h["priority_score"] for h in HOTSPOTS}
    return {"budget_inr": budget_inr,
            "frontier": compute_frontier(PROJECTS, req, score_by_hs)}


@app.get("/api/v1/projects/")
def projects(limit: int = 100):
    return {"count": len(PROJECTS), "projects": PROJECTS[:limit]}


# ------------------------------------------------------------ IMPACT (C)

@app.get("/api/v1/impact/")
def impact():
    """The IMPACT LEDGER — the clause of the brief nobody else answered."""
    return {"count": len(LEDGER), "ledger": LEDGER,
            "summary": {
                "projects_tracked": len(LEDGER),
                "avg_realization_ratio": (round(sum(l["realization_ratio"] for l in LEDGER) / len(LEDGER), 3)
                                          if LEDGER else 0),
                "flagged": sum(1 for l in LEDGER if l["social_audit_score"] < 0.5),
                "certified": sum(1 for l in LEDGER if l["social_audit_score"] > 0.8),
            }}


@app.post("/api/v1/verify/")
def verify(body: dict):
    """Citizen photo / comment verification on a COMPLETED project."""
    pid = body.get("project_id")
    verdict = body.get("verdict", "partial")
    comment = body.get("comment", "")
    proj = next((p for p in PROJECTS if p["project_id"] == pid), None)
    if not proj:
        raise HTTPException(404, f"Unknown project {pid}")

    vision = gemini.client.verify_photo(proj["intervention"], comment, body.get("image_b64"))
    values = {"completed": 1.0, "partial": 0.5, "not_done": 0.0}
    trust = float(body.get("trust_weight", 0.5))

    ev = {
        "verification_id": f"V-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{len(VERIFICATIONS):05d}",
        "project_id": pid, "created_at": datetime.now(timezone.utc).isoformat(),
        "channel": body.get("channel", "whatsapp"),
        "respondent": {"trust_weight": trust},
        "verdict": verdict,
        "raw_comment": comment,
        "comment_language": PROVIDER.detect_language(comment),
        "photo": {"vision_check": vision},
    }
    VERIFICATIONS.append(ev)

    # Recompute the social audit score for this project
    mine = [v for v in VERIFICATIONS if v["project_id"] == pid]
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
def routing_table():
    return ROUTING


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
    if body.get("subject") == "portfolio":
        req = body.get("request") or {"budget_inr": 400_000_000, "sector_caps": DEFAULT_SECTOR_CAPS,
                                      "equity_floor_pct": 0.40, "geographic_spread": "min_one_per_block",
                                      "fast": False, "weights": {"demand": .3, "deficit": .25,
                                                                 "reach": .2, "equity": .15,
                                                                 "feasibility": .1}}
        pf = allocate(req, PROJECTS, {h["hotspot_id"]: h["priority_score"] for h in HOTSPOTS})
        data = {"totals": pf["totals"], "selected_projects": pf["selected"],
                "dropped": pf["dropped"][:8], "constraint_report": pf["constraint_report"]}
    else:
        data = [{"hotspot_id": h["hotspot_id"], "sector": h["sector"],
                 "priority_score": h["priority_score"], "components": h["components"],
                 "demand": h["demand"]} for h in HOTSPOTS[:12]]
    return {"kind": kind, "language": language,
            "text": gemini.client.generate_brief(kind, data, language),
            "degraded": not gemini.client.available()}


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
