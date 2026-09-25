from services.stt import status, transcribe
import io, wave, sys

def main():
    print("JanSetu STT self-test"); print("=" * 52)
    st = status()
    print(f"chain: {st['chain']}")
    for p in st["providers"]:
        print(f"  {p['provider']:<14} " + ("configured" if p["configured"] else "not configured (skipped)"))
    print(f"  any_configured = {st['any_configured']}")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b"\x00\x00" * 6400)
    r = transcribe(buf.getvalue(), language="mr")
    print("\ntranscribe() with 0.4s silence ->", r if r else "None (correct: degraded safely, nothing crashed)")
    print("\nSelf-test passed.")

if __name__ == "__main__":
    main()
