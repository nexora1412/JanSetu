"""
JanSetu — Shared API contracts (Pydantic v2)
==============================================
CONTRACT VERSION 1.0 — LOCKED. Changing a model here is a team-wide event.
Every workstream imports from this file. No duplicate schema definitions anywhere.

  A (Access)  -> CitizenReport -> B (Intelligence) -> Hotspot -> C (Engine) -> Portfolio -> D (Console)
  A (Access)  -> VerificationEvent -> C (Engine)
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Channel(str, Enum):
    """Every intake channel normalises into ONE CitizenReport."""
    MISSED_CALL = "missed_call"
    VOICE_CALL = "voice_call"
    SMS = "sms"
    IVR = "ivr"
    WHATSAPP = "whatsapp"
    WEB = "web"
    KIOSK = "kiosk"


class Sector(str, Enum):
    ROADS = "roads"
    WATER = "water"
    POWER = "power"
    HEALTH = "health"
    EDUCATION = "education"
    SANITATION = "sanitation"
    DIGITAL = "digital"
    OTHER = "other"


class HandsetClass(str, Enum):
    FEATURE_PHONE = "feature_phone"
    SMARTPHONE = "smartphone"
    WEB = "web"
    KIOSK = "kiosk"


class ReportStatus(str, Enum):
    RECEIVED = "received"
    ROUTED = "routed"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class Verdict(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    NOT_DONE = "not_done"
    SPAM = "spam"


class VisionVerdict(str, Enum):
    PLAUSIBLE = "plausible"
    UNCLEAR = "unclear"
    IMPLAUSIBLE = "implausible"


# ---------------------------------------------------------------------------
# 1. CitizenReport  — produced by A, consumed by B
# ---------------------------------------------------------------------------

class ChannelMeta(BaseModel):
    msisdn_hash: str | None = Field(default=None, description="sha256 of MSISDN; never store raw numbers")
    duration_s: int | None = None
    audio_uri: str | None = None
    provider: Literal["simulator", "exotel", "twilio"] = "simulator"
    handset_class: HandsetClass = HandsetClass.FEATURE_PHONE


class GeoResolution(BaseModel):
    state: str | None = None
    district: str | None = None
    block: str | None = None
    village: str | None = None
    lgd_code: str | None = Field(default=None, description="Real LGD code. null if unresolvable — NEVER invent one.")
    lat: float | None = None
    lon: float | None = None
    geohash: str | None = None


class StructuredReport(BaseModel):
    sector: Sector = Sector.OTHER
    subsector: str | None = None
    asset: str | None = None
    issue: str | None = None
    severity_1_5: int = Field(default=3, ge=1, le=5, description="Integer 1-5. No halves.")
    affected_population_est: int = 0
    geo: GeoResolution = Field(default_factory=GeoResolution)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    extractor: Literal["gemini", "fallback"] = "gemini"


class Evidence(BaseModel):
    type: Literal["photo", "audio", "document"] = "photo"
    uri: str | None = None
    vision_verdict: VisionVerdict | None = None
    vision_score: float | None = Field(default=None, ge=0.0, le=1.0)
    vision_note: str | None = None


class Routing(BaseModel):
    department: str | None = None
    scheme: str | None = None
    officer_ref: str | None = None
    sla_days: int | None = None
    routed_at: datetime | None = None
    ack_sent: bool = False


class Consent(BaseModel):
    given: bool = True
    pii_minimized: bool = True
    retention_days: int = 730


class CitizenReport(BaseModel):
    report_id: str
    created_at: datetime
    channel: Channel
    channel_meta: ChannelMeta = Field(default_factory=ChannelMeta)
    raw_text: str
    raw_language: str = Field(default="en", description="BCP-47. Use hi-Latn for code-mixed Hinglish.")
    normalized_text_en: str | None = None
    structured: StructuredReport = Field(default_factory=StructuredReport)
    evidence: list[Evidence] = Field(default_factory=list)
    me_too: int = 0
    dedupe_key: str | None = None
    is_duplicate: bool = False
    duplicate_of: str | None = None
    routing: Routing = Field(default_factory=Routing)
    consent: Consent = Field(default_factory=Consent)
    status: ReportStatus = ReportStatus.RECEIVED


# ---------------------------------------------------------------------------
# 2. Hotspot  — produced by B, consumed by C + D
# ---------------------------------------------------------------------------

class DemandComponents(BaseModel):
    raw: float = Field(default=0.0, ge=0.0, le=1.0)
    expected_reports: float = 0.0
    observed_reports: float = 0.0
    bias_factor: float = Field(default=1.0, ge=0.50, le=3.00, description="ALWAYS clipped to [0.5, 3.0]")
    adjusted: float = Field(default=0.0, ge=0.0, le=1.0)
    model: str = "poisson_glm_v1"


class ScoreComponents(BaseModel):
    demand: float = Field(default=0.0, ge=0.0, le=1.0)
    deficit: float = Field(default=0.0, ge=0.0, le=1.0)
    reach: float = Field(default=0.0, ge=0.0, le=1.0)
    equity: float = Field(default=0.0, ge=0.0, le=1.0)
    feasibility: float = Field(default=0.0, ge=0.0, le=1.0)
    saturation: float = Field(default=0.0, ge=0.0, le=1.0)


class ScoreWeights(BaseModel):
    demand: float = 0.30
    deficit: float = 0.25
    reach: float = 0.20
    equity: float = 0.15
    feasibility: float = 0.10

    @field_validator("demand", "deficit", "reach", "equity", "feasibility")
    @classmethod
    def in_unit_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("weight must be in [0,1]")
        return v

    def normalised(self) -> "ScoreWeights":
        """UI sliders may not sum to 1 — renormalise before scoring."""
        total = self.demand + self.deficit + self.reach + self.equity + self.feasibility
        if total <= 0:
            return ScoreWeights()
        return ScoreWeights(
            demand=self.demand / total, deficit=self.deficit / total, reach=self.reach / total,
            equity=self.equity / total, feasibility=self.feasibility / total,
        )


class Lineage(BaseModel):
    census_row: str | None = None
    nidi_row: str | None = None
    model_version: str = "score_v1.2"
    computed_at: datetime | None = None


class Hotspot(BaseModel):
    hotspot_id: str
    created_at: datetime
    lgd_block_code: str
    sector: Sector
    centroid: dict[str, float]
    radius_m: int = 500
    report_count: int = 0
    me_too_total: int = 0
    report_ids: list[str] = Field(default_factory=list)
    demand: DemandComponents = Field(default_factory=DemandComponents)
    components: ScoreComponents = Field(default_factory=ScoreComponents)
    weights: ScoreWeights = Field(default_factory=ScoreWeights)
    priority_score: float = Field(default=0.0, ge=0.0, le=100.0)
    rank: int | None = None
    lineage: Lineage = Field(default_factory=Lineage)


# ---------------------------------------------------------------------------
# 3. ProjectCandidate  — produced by C, consumed by C + D
# ---------------------------------------------------------------------------

class Eligibility(BaseModel):
    eligible: bool = True
    conditions_met: list[str] = Field(default_factory=list)
    conditions_failed: list[str] = Field(default_factory=list)
    funding_split: dict[str, float] = Field(default_factory=dict)


class PredictedOutcome(BaseModel):
    kpi: str
    baseline_value: float = 0.0
    predicted_value: float = 0.0
    confidence: float = 0.7


class Feasibility(BaseModel):
    land_available: bool = True
    agency_capacity: float = Field(default=0.7, ge=0.0, le=1.0)
    lead_time_days: int = 180


class ConstraintTags(BaseModel):
    deprivation_flag: bool = False
    aspirational_district: bool = False
    block: str | None = None
    exclusive_group: str | None = None


class ProjectCandidate(BaseModel):
    project_id: str
    hotspot_id: str
    lgd_block_code: str
    sector: Sector
    intervention: str
    intervention_code: str | None = None
    cost_inr: int = Field(gt=0, description="Must trace to a named rate in data/sor_rates.csv")
    cost_basis: str = Field(default="", description="REQUIRED. A project without a cost basis does not ship.")
    beneficiaries: int = 0
    cost_per_beneficiary_inr: int = 0
    scheme: str | None = None
    eligibility: Eligibility = Field(default_factory=Eligibility)
    constraint_tags: ConstraintTags = Field(default_factory=ConstraintTags)
    predicted_outcome: PredictedOutcome | None = None
    feasibility: Feasibility = Field(default_factory=Feasibility)


# ---------------------------------------------------------------------------
# 4. Portfolio  ★ THE HERO OBJECT — produced by C, consumed by D
# ---------------------------------------------------------------------------

class AllocationRequest(BaseModel):
    budget_inr: int = Field(default=40_000_000, gt=0)
    sector_caps: dict[str, float] = Field(default_factory=dict)
    equity_floor_pct: float = Field(default=0.40, ge=0.0, le=1.0)
    geographic_spread: Literal["none", "min_one_per_block"] = "min_one_per_block"
    state_filter: str | None = None
    sector_filter: str | None = None
    weights: ScoreWeights = Field(default_factory=ScoreWeights)
    fast: bool = Field(default=False, description="Use greedy+2-opt instead of exact ILP")


class DroppedProject(BaseModel):
    project_id: str
    reason: Literal["budget_exhausted", "sector_cap_binding", "exclusive_group", "ineligible", "below_cutoff"]
    detail: str = ""
    would_need_inr: int | None = None


class ConstraintReport(BaseModel):
    constraint: str
    binding: bool
    slack_inr: int | None = None
    slack_pct: float | None = None
    blocks_uncovered: int | None = None


class FrontierPoint(BaseModel):
    equity_floor_pct: float
    beneficiaries: int
    cost_per_beneficiary_inr: int


class InfeasibleReport(BaseModel):
    reason: str
    detail: str
    relaxation_suggestion: dict[str, Any] = Field(default_factory=dict)
    nearest_feasible_beneficiaries: int | None = None


class PortfolioTotals(BaseModel):
    projects: int = 0
    cost_inr: int = 0
    budget_utilisation: float = 0.0
    beneficiaries: int = 0
    cost_per_beneficiary_inr: int = 0
    equity_share: float = 0.0
    blocks_covered: int = 0
    sector_breakdown: dict[str, float] = Field(default_factory=dict)


class Portfolio(BaseModel):
    portfolio_id: str
    computed_at: datetime
    solver: dict[str, Any] = Field(default_factory=dict)
    request: AllocationRequest
    selected: list[str] = Field(default_factory=list)
    totals: PortfolioTotals = Field(default_factory=PortfolioTotals)
    dropped: list[DroppedProject] = Field(default_factory=list)
    constraint_report: list[ConstraintReport] = Field(default_factory=list)
    frontier: list[FrontierPoint] = Field(default_factory=list)
    infeasible: InfeasibleReport | None = None


# ---------------------------------------------------------------------------
# 5. VerificationEvent  — produced by A, consumed by B + C
# ---------------------------------------------------------------------------

class Respondent(BaseModel):
    msisdn_hash: str | None = None
    prior_verifications: int = 0
    trust_weight: float = Field(default=0.5, ge=0.0, le=1.0)


class VisionCheck(BaseModel):
    matches_scope: bool = False
    asset_visible: bool = False
    completion_est: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    note: str = ""


class VerifyPhoto(BaseModel):
    uri: str | None = None
    vision_check: VisionCheck = Field(default_factory=VisionCheck)


class VerificationAggregates(BaseModel):
    project_verification_count: int = 0
    positive: int = 0
    partial: int = 0
    negative: int = 0
    social_audit_score: float = Field(default=0.0, ge=0.0, le=1.0)
    recommended_action: str = ""


class VerificationEvent(BaseModel):
    verification_id: str
    project_id: str
    report_id: str | None = None
    created_at: datetime
    channel: Channel
    respondent: Respondent = Field(default_factory=Respondent)
    verdict: Verdict
    raw_comment: str | None = None
    comment_language: str | None = None
    comment_en: str | None = None
    photo: VerifyPhoto | None = None
    geo_check: dict[str, Any] = Field(default_factory=dict)
    aggregates: VerificationAggregates = Field(default_factory=VerificationAggregates)


# ---------------------------------------------------------------------------
# Error envelope — every AI call site wraps in this
# ---------------------------------------------------------------------------

class ErrorEnvelope(BaseModel):
    """degraded=True means: the request SUCCEEDED, just with lower confidence.
    The system must never hard-fail in front of a judge."""
    code: str
    message: str
    degraded: bool = True
    fallback_used: str | None = None
    confidence_penalty: float = 0.0


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "jansetu"
    version: str = "0.1.0"
    gemini: bool = False
    telephony_provider: str = "simulator"
    contracts_version: str = "1.0"
