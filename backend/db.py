"""
JanSetu — SQLite persistence (stdlib only, zero new dependencies)
==================================================================
Citizen submissions from the mobile app / helpline are written here so they
survive restarts and show up on the officer dashboard. The DB is seeded from
fixtures on first run; fixture rows are marked `origin='seed'` and live
submissions `origin='live'` so the dashboard can tell demo data from real intake.

File: backend/data/jansetu.db  (gitignored via *.db)
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "jansetu.db"

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None


def _get() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _conn.execute("PRAGMA journal_mode=WAL")
    return _conn


def init() -> None:
    with _lock:
        c = _get()
        c.executescript("""
        CREATE TABLE IF NOT EXISTS reports (
            report_id  TEXT NOT NULL,
            nation     TEXT NOT NULL,
            created_at TEXT NOT NULL,
            sector     TEXT,
            channel    TEXT,
            status     TEXT,
            origin     TEXT NOT NULL DEFAULT 'live',
            payload    TEXT NOT NULL,
            PRIMARY KEY (nation, report_id)
        );
        CREATE INDEX IF NOT EXISTS ix_reports_created ON reports(nation, created_at);
        CREATE INDEX IF NOT EXISTS ix_reports_sector  ON reports(nation, sector);

        CREATE TABLE IF NOT EXISTS verifications (
            verification_id TEXT NOT NULL,
            nation          TEXT NOT NULL,
            project_id      TEXT NOT NULL,
            created_at      TEXT NOT NULL,
            verdict         TEXT,
            origin          TEXT NOT NULL DEFAULT 'live',
            payload         TEXT NOT NULL,
            PRIMARY KEY (nation, verification_id)
        );

        CREATE TABLE IF NOT EXISTS admins (
            username      TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt          TEXT NOT NULL,
            created_at    TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS citizens (
            phone      TEXT PRIMARY KEY,
            name       TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS otps (
            phone      TEXT PRIMARY KEY,
            code       TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            attempts   INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token      TEXT PRIMARY KEY,
            role       TEXT NOT NULL,
            subject    TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        );
        """)
        c.commit()


def _report_cols(r: dict) -> tuple:
    st = r.get("structured") or {}
    return (r.get("report_id"), r.get("created_at") or "", st.get("sector") or "other",
            r.get("channel"), r.get("status"), json.dumps(r, ensure_ascii=False))


def insert_reports(nation: str, reports: list[dict], origin: str = "live") -> None:
    if not reports:
        return
    rows = [(rid, nation, created, sector, channel, status, origin, payload)
            for rid, created, sector, channel, status, payload in
            (_report_cols(r) for r in reports)]
    with _lock:
        c = _get()
        c.executemany(
            "INSERT OR REPLACE INTO reports "
            "(report_id,nation,created_at,sector,channel,status,origin,payload) "
            "VALUES (?,?,?,?,?,?,?,?)", rows)
        c.commit()


def insert_report(nation: str, report: dict, origin: str = "live") -> None:
    rid, created, sector, channel, status, payload = _report_cols(report)
    with _lock:
        c = _get()
        c.execute(
            "INSERT OR REPLACE INTO reports "
            "(report_id,nation,created_at,sector,channel,status,origin,payload) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (rid, nation, created, sector, channel, status, origin, payload))
        c.commit()


def all_reports(nation: str) -> list[dict]:
    with _lock:
        rows = _get().execute(
            "SELECT payload, origin FROM reports WHERE nation=? ORDER BY created_at, report_id",
            (nation,)).fetchall()
    out = []
    for payload, origin in rows:
        r = json.loads(payload)
        r["origin"] = origin
        out.append(r)
    return out


def count_reports(nation: str) -> int:
    with _lock:
        return _get().execute(
            "SELECT COUNT(*) FROM reports WHERE nation=?", (nation,)).fetchone()[0]


def report_by_id(nation: str, report_id: str) -> dict | None:
    with _lock:
        row = _get().execute(
            "SELECT payload FROM reports WHERE nation=? AND report_id=?",
            (nation, report_id)).fetchone()
    return json.loads(row[0]) if row else None


def update_report(nation: str, report: dict) -> None:
    insert_report(nation, report, origin="live")


def insert_verification(nation: str, ev: dict, origin: str = "live") -> None:
    with _lock:
        c = _get()
        c.execute(
            "INSERT OR REPLACE INTO verifications "
            "(verification_id,nation,project_id,created_at,verdict,origin,payload) "
            "VALUES (?,?,?,?,?,?,?)",
            (ev.get("verification_id"), nation, ev.get("project_id"),
             ev.get("created_at") or "", ev.get("verdict"), origin,
             json.dumps(ev, ensure_ascii=False)))
        c.commit()


def all_verifications(nation: str) -> list[dict]:
    with _lock:
        rows = _get().execute(
            "SELECT payload FROM verifications WHERE nation=? ORDER BY created_at",
            (nation,)).fetchall()
    return [json.loads(r[0]) for r in rows]


def max_ticket_seq(nation: str, prefix: str) -> int:
    """Highest numeric suffix among ticket ids like JS-2026-000123 -> 123."""
    with _lock:
        rows = _get().execute(
            "SELECT report_id FROM reports WHERE nation=?", (nation,)).fetchall()
    best = 0
    for (rid,) in rows:
        if rid and rid.startswith(prefix):
            tail = rid.rsplit("-", 1)[-1]
            if tail.isdigit():
                best = max(best, int(tail))
    return best


def stats(nation: str) -> dict:
    with _lock:
        c = _get()
        total = c.execute("SELECT COUNT(*) FROM reports WHERE nation=?", (nation,)).fetchone()[0]
        live = c.execute("SELECT COUNT(*) FROM reports WHERE nation=? AND origin='live'",
                         (nation,)).fetchone()[0]
        by_sector = c.execute(
            "SELECT sector, COUNT(*) FROM reports WHERE nation=? GROUP BY sector "
            "ORDER BY COUNT(*) DESC", (nation,)).fetchall()
        by_channel = c.execute(
            "SELECT channel, COUNT(*) FROM reports WHERE nation=? GROUP BY channel "
            "ORDER BY COUNT(*) DESC", (nation,)).fetchall()
        by_day = c.execute(
            "SELECT substr(created_at,1,10) d, COUNT(*) FROM reports WHERE nation=? "
            "GROUP BY d ORDER BY d", (nation,)).fetchall()
        verifications = c.execute(
            "SELECT COUNT(*) FROM verifications WHERE nation=?", (nation,)).fetchone()[0]
        by_status = c.execute(
            "SELECT COALESCE(status,'unknown'), COUNT(*) FROM reports WHERE nation=? "
            "GROUP BY status ORDER BY COUNT(*) DESC", (nation,)).fetchall()
        by_verdict = c.execute(
            "SELECT COALESCE(verdict,'unknown'), COUNT(*) FROM verifications WHERE nation=? "
            "GROUP BY verdict ORDER BY COUNT(*) DESC", (nation,)).fetchall()
        by_block = c.execute(
            "SELECT payload FROM reports WHERE nation=?", (nation,)).fetchall()
    blocks: dict[str, int] = {}
    for (payload,) in by_block:
        geo = ((json.loads(payload).get("structured") or {}).get("geo") or {})
        key = geo.get("block") or geo.get("municipality") or geo.get("lgd_block_code") or "unknown"
        blocks[key] = blocks.get(key, 0) + 1
    top_blocks = sorted(blocks.items(), key=lambda kv: -kv[1])[:10]
    return {"total": total, "live": live,
            "by_sector": [{"sector": s, "count": n} for s, n in by_sector],
            "by_channel": [{"channel": s, "count": n} for s, n in by_channel],
            "by_day": [{"day": d, "count": n} for d, n in by_day],
            "by_status": [{"status": s, "count": n} for s, n in by_status],
            "by_verdict": [{"verdict": s, "count": n} for s, n in by_verdict],
            "top_blocks": [{"block": s, "count": n} for s, n in top_blocks],
            "verifications": verifications}


# ------------------------------------------------------------------ AUTH ----
# Sessions/OTP live in SQLite so a restart does not log everyone out mid-demo.


def get_admin(username: str) -> dict | None:
    with _lock:
        row = _get().execute(
            "SELECT username, password_hash, salt FROM admins WHERE username=?",
            (username,)).fetchone()
    return {"username": row[0], "password_hash": row[1], "salt": row[2]} if row else None


def create_admin(username: str, password_hash: str, salt: str, created_at: str) -> None:
    with _lock:
        c = _get()
        c.execute("INSERT OR REPLACE INTO admins (username,password_hash,salt,created_at) "
                  "VALUES (?,?,?,?)", (username, password_hash, salt, created_at))
        c.commit()


def admin_count() -> int:
    with _lock:
        return _get().execute("SELECT COUNT(*) FROM admins").fetchone()[0]


def upsert_citizen(phone: str, name: str | None, created_at: str) -> None:
    with _lock:
        c = _get()
        c.execute("INSERT INTO citizens (phone,name,created_at) VALUES (?,?,?) "
                  "ON CONFLICT(phone) DO UPDATE SET name=COALESCE(?, name)",
                  (phone, name, created_at, name))
        c.commit()


def get_citizen(phone: str) -> dict | None:
    with _lock:
        row = _get().execute(
            "SELECT phone, name, created_at FROM citizens WHERE phone=?", (phone,)).fetchone()
    return {"phone": row[0], "name": row[1], "created_at": row[2]} if row else None


def set_otp(phone: str, code: str, expires_at: str, created_at: str) -> None:
    with _lock:
        c = _get()
        c.execute("INSERT OR REPLACE INTO otps (phone,code,expires_at,attempts,created_at) "
                  "VALUES (?,?,?,0,?)", (phone, code, expires_at, created_at))
        c.commit()


def get_otp(phone: str) -> dict | None:
    with _lock:
        row = _get().execute(
            "SELECT code, expires_at, attempts FROM otps WHERE phone=?", (phone,)).fetchone()
    return {"code": row[0], "expires_at": row[1], "attempts": row[2]} if row else None


def bump_otp_attempts(phone: str) -> None:
    with _lock:
        c = _get()
        c.execute("UPDATE otps SET attempts=attempts+1 WHERE phone=?", (phone,))
        c.commit()


def delete_otp(phone: str) -> None:
    with _lock:
        c = _get()
        c.execute("DELETE FROM otps WHERE phone=?", (phone,))
        c.commit()


def create_session(token: str, role: str, subject: str,
                   created_at: str, expires_at: str) -> None:
    with _lock:
        c = _get()
        c.execute("INSERT OR REPLACE INTO sessions (token,role,subject,created_at,expires_at) "
                  "VALUES (?,?,?,?,?)", (token, role, subject, created_at, expires_at))
        c.commit()


def get_session(token: str) -> dict | None:
    with _lock:
        row = _get().execute(
            "SELECT role, subject, expires_at FROM sessions WHERE token=?", (token,)).fetchone()
    return {"role": row[0], "subject": row[1], "expires_at": row[2]} if row else None


def delete_session(token: str) -> None:
    with _lock:
        c = _get()
        c.execute("DELETE FROM sessions WHERE token=?", (token,))
        c.commit()
