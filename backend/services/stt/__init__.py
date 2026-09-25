"""
JanSetu — Speech-to-Text entry point  (Person 1, Day 1)
=======================================================
One function to call. It tries providers in order and never raises.

    from services.stt import transcribe
    result = transcribe(audio_bytes, language="mr")
    # -> {"text": "...", "language": "mr", "provider": "sarvam", "confidence": None}
    # -> None   (only if every provider failed or none are configured)

Order is set by the STT_CHAIN environment variable:
    STT_CHAIN=sarvam,bhashini,google      (default)

Self-test (works with NO keys — proves the chain degrades safely):
    cd backend && python -m services.stt --selftest
"""
from __future__ import annotations

import os

from services.stt.providers import (
    BhashiniProvider,
    GeminiAudioProvider,
    GoogleChirpProvider,
    SarvamProvider,
    STTProvider,
    bcp47,
    iso639,
)

PROVIDERS: dict[str, type[STTProvider]] = {
    "sarvam": SarvamProvider,
    "bhashini": BhashiniProvider,
    "gemini": GeminiAudioProvider,
    "google": GoogleChirpProvider,
}


def providers_in_order() -> list[STTProvider]:
    chain = os.getenv("STT_CHAIN", "sarvam,bhashini,gemini,google")
    out = []
    for name in (n.strip().lower() for n in chain.split(",")):
        cls = PROVIDERS.get(name)
        if cls:
            out.append(cls())
    return out


def transcribe(audio_bytes: bytes, language: str = "hi",
               sample_rate: int = 16000) -> dict | None:
    """Try each provider in order. Return the first success, else None.
    NEVER raises — a missing key or a dead network must not break the demo."""
    if not audio_bytes:
        return None
    for p in providers_in_order():
        try:
            result = p.transcribe(audio_bytes, language, sample_rate)
        except Exception:
            result = None
        if result and result.get("text"):
            return result
    return None


def status() -> dict:
    """Which providers are actually usable right now? Shown on the dashboard."""
    out = []
    for p in providers_in_order():
        try:
            ok = p.configured()
        except Exception:
            ok = False
        out.append({"provider": p.name, "configured": ok})
    return {"chain": [p.name for p in providers_in_order()],
            "providers": out,
            "any_configured": any(p["configured"] for p in out)}


# ---------------------------------------------------------------------------
# CLI self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import wave

    if "--selftest" in sys.argv:
        print("JanSetu STT self-test")
        print("=" * 52)
        st = status()
        print(f"chain: {st['chain']}")
        for p in st["providers"]:
            mark = "✅ configured" if p["configured"] else "⬜ not configured (will be skipped)"
            print(f"  {p['provider']:<14} {mark}")
        print(f"  any_configured = {st['any_configured']}")

        # Build 0.4 s of silence so we exercise the real call path with real bytes.
        import io
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
            w.writeframes(b"\x00\x00" * 6400)
        wav = buf.getvalue()

        print("\nCalling transcribe() with 0.4 s of silence…")
        r = transcribe(wav, language="mr")
        if r is None:
            print("  → returned None. CORRECT: no provider succeeded, and nothing crashed.")
            print("    Add a key to .env and re-run to get real transcription.")
        else:
            print(f"  → {r}")
        print("\n✅ Self-test passed — the chain degrades safely.")
    else:
        print(__doc__)
