"""
JanSetu — .env loader
=====================
⚠️ WHY THIS FILE EXISTS (a real bug we hit)

`os.getenv()` reads REAL environment variables. It does NOT read your `.env` file.
Without this loader, you can paste your Gemini key into `.env` until you're blue in
the face and the app will still report "not configured" — because the file is never
read. Everything silently falls back and the demo looks dumb for no visible reason.

**Import this module BEFORE anything calls os.getenv().**

    try:
        import env_boot      # noqa: F401  — loads .env into os.environ
    except ImportError:
        pass

It uses python-dotenv if installed, otherwise falls back to a built-in parser, so it
works even if someone forgets `pip install -r requirements.txt`.
"""
from __future__ import annotations

import os
from pathlib import Path


def find_env_file() -> Path | None:
    """Walk up from this file looking for a .env (repo root is 2 levels up)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / ".env"
        if candidate.is_file():
            return candidate
    # Also honour an explicit override, useful on Cloud Run / Render.
    explicit = os.getenv("JANSETU_ENV_FILE")
    if explicit and Path(explicit).is_file():
        return Path(explicit)
    return None


def _parse_and_apply(path: Path, override: bool = False) -> int:
    """Minimal, dependency-free .env parser. Returns how many vars were set."""
    count = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()

        # Strip matching surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        else:
            # Drop inline comments only when the value isn't quoted
            if "  #" in value:
                value = value.split("  #", 1)[0].strip()
            elif value.startswith("#"):
                continue

        if override or key not in os.environ:
            os.environ[key] = value
            count += 1
    return count


def load(override: bool = False) -> Path | None:
    path = find_env_file()
    if not path:
        return None
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv(dotenv_path=path, override=override)
    except ImportError:
        _parse_and_apply(path, override=override)
    return path


# Runs on import — that's the whole point.
LOADED_FROM = load()


def report() -> dict:
    """Chat-friendly diagnostic: is .env being read, and which keys arrived?"""
    keys = ["GEMINI_API_KEY", "GEMINI_MODEL", "STT_CHAIN", "SARVAM_API_KEY",
            "BHASHINI_USER_ID", "BHASHINI_ULCA_API_KEY", "BHASHINI_PIPELINE_ID",
            "TELEPHONY_PROVIDER"]
    return {
        "env_file": str(LOADED_FROM) if LOADED_FROM else None,
        "env_file_found": LOADED_FROM is not None,
        "keys": {k: ("set" if os.getenv(k) else "EMPTY") for k in keys},
    }


if __name__ == "__main__":
    from pprint import pprint
    pprint(report())
