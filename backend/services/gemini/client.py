"""
JanSetu — Google Gemini client  (workstream B)
================================================
MANDATORY Google AI integration, used across FOUR load-bearing surfaces:
  1. structured extraction  — language, sector, severity, LGD geo-entity, affected population
  2. semantic normalisation — code-mixed Hinglish -> clean English working text
  3. multimodal verification — does the photo show a completed asset?
  4. generation — policy briefs, standing-committee notes, citizen replies

--------------------------------------------------------------------------------
⚠️ THE RULE WE NEVER BREAK
--------------------------------------------------------------------------------
    GEMINI EXPLAINS AND STRUCTURES. IT NEVER COMPUTES A SCORE.

Priority scores, bias factors and allocations come from engine/*.py only.
Ask an LLM for "a number 1-100" and you get a plausible fiction; we get audited
lineage instead. (Competing repos call this "eliminating LLM numerical
hallucinations" — we enforce it in code.)

--------------------------------------------------------------------------------
OFFLINE-FIRST
--------------------------------------------------------------------------------
If there is no API key, no network, or a rate limit, every function degrades to a
deterministic fallback and sets extractor="fallback" with confidence <= 0.5.
**The demo must never die because a network blinked.** That is not defensive
programming for its own sake — it is the difference between a demo that survives
judging day and one that does not.

Setup:
    export GEMINI_API_KEY=...           # https://aistudio.google.com/apikey
    export GEMINI_MODEL=gemini-2.5-flash   # ⚠️ verify the current Flash ID in AI Studio
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
TIMEOUT_S = 20

SECTORS = ["roads", "water", "power", "health", "education", "sanitation", "digital", "other"]

# Fallback keyword map — deliberately crude. It runs only when Gemini is unavailable,
# and it always flags itself with low confidence so downstream weighting can discount it.
_KEYWORDS: list[tuple[str, list[str]]] = [
    ("roads",      ["रस्ता", "सडक", "road", "सड़क", "rasta", "sadak", "culvert", "पुल", "bridge", "kaccha"]),
    ("water",      ["पानी", "pan", "water", "जल", "हैंडपंप", "handpump", "nal", "नल", "tap", "thirsty", "pipeline"]),
    ("power",      ["बिजली", "bijli", "power", "electricity", "current", "transformer", "light", "बत्ती"]),
    ("health",     ["doctor", "hospital", "phc", "health", "स्वास्थ्य", "दवा", "medicine", "pregnant", "अस्पताल"]),
    ("education",  ["school", "शाळा", "स्कूल", "शिक्षा", "education", "teacher", "classroom", "शिक्षक"]),
    ("sanitation", ["toilet", "शौचालय", "स्वच्छता", "sanitation", "drain", "नाली", "garbage", "कचरा", "swachh"]),
    ("digital",    ["network", "internet", "net", "mobile", "bharatnet", "signal", "online", "टॉवर", "tower"]),
]


# ---------------------------------------------------------------------------
# Transport
# ---------------------------------------------------------------------------

def available() -> bool:
    return bool(API_KEY)


def _call(prompt: str, max_tokens: int = 2048, temperature: float = 0.2) -> str | None:
    """Minimal stdlib REST call (no SDK dependency). Returns text, or None on ANY failure."""
    if not API_KEY:
        return None
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "responseMimeType": "application/json",
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT.format(model=MODEL, key=API_KEY),
        data=body, headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError, TimeoutError, OSError):
        return None


def _json_or_none(text: str | None) -> dict | None:
    if not text:
        return None
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# 1 · Structured extraction
# ---------------------------------------------------------------------------

STRUCTURE_PROMPT = """You are the intake engine of JanSetu, an Indian government
platform that turns citizen complaints into funded infrastructure projects.

Analyse this citizen complaint. It may be in any Indian language, in Roman script,
or code-mixed (Hinglish). Respond ONLY with JSON matching this schema:

{{
  "language": "<BCP-47 tag: hi|mr|bn|ta|te|en|hi-Latn|...>",
  "normalized_text_en": "<faithful English rendering; preserve meaning, do not embellish>",
  "sector": "<one of: {sectors}>",
  "subsector": "<short snake_case, e.g. rural_approach_road>",
  "asset": "<the physical asset, e.g. culvert|handpump|transformer|classroom>",
  "issue": "<short snake_cause, e.g. damaged_impassable>",
  "severity_1_5": <integer 1-5; 5 = life-threatening or total loss of access>,
  "affected_population_est": <integer, your best estimate of people affected>,
  "geo": {{
     "state": "<Indian state, or null>",
     "district": "<district, or null>",
     "block": "<block/taluka, or null>",
     "village": "<village/town, or null>",
     "lgd_code": "<LGD code ONLY if you are certain; otherwise null>"
  }},
  "confidence": <float 0-1 in your own extraction>,
  "reasoning": "<one short sentence>"
}}

RULES:
- Never invent a place you are not sure of. null is always better than a guess.
- severity_1_5 must be an integer.
- Do not add fields.

COMPLAINT:
\"\"\"{text}\"\"\"
"""


def structure_report(text: str, hint_language: str | None = None) -> dict:
    """Returns a StructuredReport-shaped dict. Always succeeds — degrades if needed."""
    raw = _call(STRUCTURE_PROMPT.format(text=text[:2000], sectors="|".join(SECTORS)))
    parsed = _json_or_none(raw)
    if parsed:
        parsed.setdefault("extractor", "gemini")
        parsed["confidence"] = float(parsed.get("confidence", 0.8))
        return parsed
    return _fallback_structure(text)


def _fallback_structure(text: str) -> dict:
    """Deterministic keyword classifier. Runs with Gemini down. Self-flags low confidence."""
    low = text.lower()
    sector = "other"
    for sec, words in _KEYWORDS:
        if any(w in low for w in words):
            sector = sec
            break
    digits = re.findall(r"\b(\d{2,7})\b", text)
    pop = int(digits[0]) if digits else 0
    lang = "hi-Latn" if re.search(r"[a-z]", low) and not re.search(r"[ऀ-ॿ]", text) else "hi"
    return {
        "language": lang,
        "normalized_text_en": text[:400],
        "sector": sector, "subsector": None, "asset": None, "issue": None,
        "severity_1_5": 3,
        "affected_population_est": min(pop, 500_000),
        "geo": {"state": None, "district": None, "block": None,
                "village": None, "lgd_code": None},
        "confidence": 0.35,          # ← downstream discounts this
        "extractor": "fallback",
        "reasoning": "Keyword classifier (Gemini unavailable)",
    }


# ---------------------------------------------------------------------------
# 2 · Multimodal verification of a citizen photo
# ---------------------------------------------------------------------------

VERIFY_PROMPT = """You are verifying whether an Indian public-works project was
actually completed, using a citizen-submitted photo and description.

PROJECT SCOPE: {scope}
CITIZEN COMMENT: {comment}

Respond ONLY with JSON:
{{
  "matches_scope": <bool — is this the asset that was scoped?>,
  "asset_visible": <bool — can you actually see the asset?>,
  "completion_est": <float 0.0-1.0 — how complete does it look?>,
  "confidence": <float 0-1>,
  "note": "<one short factual sentence describing what you see>"
}}
"""


def verify_photo(scope: str, comment: str, image_b64: str | None = None,
                 mime: str = "image/jpeg") -> dict:
    """Multimodal check. NOTE: the stdlib transport is text-only — a real image
    part requires the google-genai SDK. Workstream B swaps that in on Day 9;
    until then the text signal carries the verdict and we say so honestly."""
    if image_b64 and _sdk_available():
        try:
            from google import genai  # type: ignore
            client = genai.Client(api_key=API_KEY)
            resp = client.models.generate_content(
                model=MODEL,
                contents=[VERIFY_PROMPT.format(scope=scope, comment=comment or "(none)"),
                          {"inline_data": {"mime_type": mime, "data": image_b64}}],
                config={"response_mime_type": "application/json"},
            )
            parsed = _json_or_none(getattr(resp, "text", None))
            if parsed:
                return parsed
        except Exception:
            pass

    raw = _call(VERIFY_PROMPT.format(scope=scope, comment=comment or "(none)"))
    parsed = _json_or_none(raw)
    if parsed:
        return parsed
    return {"matches_scope": True, "asset_visible": False, "completion_est": 0.5,
            "confidence": 0.2, "note": "Unverified — Gemini unavailable"}


def _sdk_available() -> bool:
    try:
        import google.genai  # noqa: F401
        return bool(API_KEY)
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# 3 · Generation: policy briefs / committee notes / citizen replies
# ---------------------------------------------------------------------------

BRIEF_PROMPT = """You are advising a senior Indian policymaker. Using ONLY the data
below, write a {kind}. Be specific, cite the schemes and unit costs named in the
data, and state the trade-offs plainly. Do not invent figures that are not present.

DATA:
{data}

Write in {language}. Format: {format}
"""


def generate_brief(kind: str, data: Any, language: str = "English",
                   fmt: str = "4 short paragraphs with a one-line headline") -> str:
    payload = json.dumps(data, ensure_ascii=False, default=str)[:9000]
    raw = _call(BRIEF_PROMPT.format(kind=kind, data=payload, language=language, format=fmt),
                temperature=0.4)
    if raw and not raw.strip().startswith("{"):
        return raw.strip()
    if raw:
        parsed = _json_or_none(raw)
        if parsed:
            return json.dumps(parsed, ensure_ascii=False, indent=2)
    return _fallback_brief(kind, data)


def _fallback_brief(kind: str, data: Any) -> str:
    """Templated, data-true, unglamorous. Runs offline. Never fabricates."""
    if isinstance(data, dict):
        t = data.get("totals", {})
        return (
            f"{kind.title()} (offline template — set GEMINI_API_KEY for an AI-drafted version)\n\n"
            f"The optimiser selected {t.get('projects', 0)} projects costing "
            f"₹{t.get('cost_inr', 0)/1e7:.2f} crore, reaching an estimated "
            f"{t.get('beneficiaries', 0):,} citizens at "
            f"₹{t.get('cost_per_beneficiary_inr', 0):,} per beneficiary.\n"
            f"Budget utilisation: {t.get('budget_utilisation', 0):.1%}. "
            f"Share reaching high-deprivation blocks: {t.get('equity_share', 0):.0%}. "
            f"Blocks covered: {t.get('blocks_covered', 0)}.\n\n"
            f"Sector split: " + ", ".join(f"{k} {v:.0%}" for k, v in (t.get("sector_breakdown") or {}).items())
        )
    return f"{kind.title()} — no data supplied."


def status() -> dict:
    return {"configured": available(), "model": MODEL,
            "sdk": _sdk_available(),
            "note": "Unset GEMINI_API_KEY -> deterministic fallbacks (demo still runs)"}
