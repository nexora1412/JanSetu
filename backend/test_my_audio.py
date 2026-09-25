"""
JanSetu — test STT with YOUR OWN voice  (Person 1)
==================================================
Record yourself on your phone saying one sentence about a local problem.
Any Indian language. Copy the audio file here. Run this. See if it comes back
as text.

HOW TO RUN
----------
    cd backend
    python test_my_audio.py myvoice.m4a mr

    (language codes: mr=Marathi hi=Hindi bn=Bengali ta=Tamil te=Telugu
                     pa=Punjabi gu=Gujarati kn=Kannada en=English)

    If you have no audio file yet, run with no arguments to check whether your
    keys are wired up at all:
        python test_my_audio.py

WHAT GOOD LOOKS LIKE
--------------------
    provider: sarvam        <- a real provider answered, not a fallback
    text: धुळे तालुक्यात रस्ता खराब आहे

WHAT FAILS LOOKS LIKE — AND WHAT TO DO
--------------------------------------
    "no providers configured"  -> your .env has no SARVAM_API_KEY, or the
                                  server was started BEFORE you saved it.
                                  Fix: save .env, then RESTART the server.

    "transcribe() returned None"  -> keys were found but every provider failed.
                                  Copy the exact error shown and send it to the
                                  group. Do NOT change any code.

    "provider: bhashini" or "provider: google"  -> Sarvam failed, the chain
                                  fell through to the next one. Still a pass,
                                  but tell the group which one answered.

RECORDING TIPS (30 seconds of your life)
----------------------------------------
    - Phone voice recorder is fine. Any format: .m4a .mp3 .wav .ogg .opus
    - Keep it under 30 seconds (Sarvam's REST endpoint caps at 30s)
    - Speak normally, in your own language, about a real local problem
    - Example: "धुळे तालुक्यात रस्ता खराब आहे" / "गाँव में पानी नहीं आ रहा"
"""
from __future__ import annotations

import sys
from pathlib import Path


def check_keys() -> None:
    """Show which providers are configured, without needing an audio file."""
    print("=" * 62)
    print("PROVIDER STATUS")
    print("=" * 62)
    try:
        from services.stt import providers_in_order
    except Exception as exc:  # noqa: BLE001
        print(f"  could not import STT module: {exc}")
        return

    configured = 0
    for p in providers_in_order():
        try:
            ok = bool(p.configured())
        except Exception:  # noqa: BLE001
            ok = False
        configured += ok
        print(f"  {'READY    ' if ok else 'no key   '} {p.name}")
    print()
    if configured == 0:
        print("  >>> no providers configured.")
        print("  >>> 1. open backend/.env and set SARVAM_API_KEY=...")
        print("  >>> 2. RESTART the server (it only reads .env at startup)")
        print("  >>> 3. run this script again")
    else:
        print(f"  >>> {configured} provider(s) ready. Record audio and run:")
        print("  >>> python test_my_audio.py myvoice.m4a mr")


def transcribe_file(path: Path, language: str) -> None:
    print("=" * 62)
    print(f"TRANSCRIBING: {path.name}  (language={language})")
    print("=" * 62)

    audio = path.read_bytes()
    print(f"  size: {len(audio):,} bytes\n")

    from services.stt import transcribe

    result = transcribe(audio, language=language)

    if not result:
        print("  RESULT: None")
        print("  >>> transcribe() returned None — every provider failed or none")
        print("  >>> are configured. Run without arguments to see key status.")
        return

    print("  RESULT")
    print(f"    provider   : {result.get('provider')}")
    print(f"    language   : {result.get('language')}")
    print(f"    confidence : {result.get('confidence')}")
    print(f"    text       : {result.get('text')}")
    print()

    if result.get("provider") == "sarvam":
        print("  >>> PASS — Sarvam answered. Voice input is real. Screenshot this.")
    else:
        print(f"  >>> PASS (via {result.get('provider')}) — chain fell through.")
        print("  >>> Tell the group which provider answered.")


def main() -> None:
    if len(sys.argv) < 2:
        check_keys()
        return

    path = Path(sys.argv[1])
    language = sys.argv[2] if len(sys.argv) > 2 else "hi"

    if not path.exists():
        print(f"  file not found: {path}")
        print("  put the audio file inside the backend/ folder, then retry.")
        return

    transcribe_file(path, language)


if __name__ == "__main__":
    main()
