"""
JanSetu — Telephony abstraction  (workstream A)
=================================================
THE SINGLE HELPLINE, made architectural.

Every channel — missed call, toll-free voice, SMS, IVR, WhatsApp, web, kiosk —
normalises into ONE CitizenReport. Downstream never branches on channel. That is
what makes "one number for all departments" a real property of the system rather
than a marketing line.

Provider is config-only:
    TELEPHONY_PROVIDER=simulator   (default — no number, no KYC, demos perfectly)
    TELEPHONY_PROVIDER=exotel      (Indian CPaaS — the real gov-deployment story)
    TELEPHONY_PROVIDER=twilio      (fastest to provision for the video)

Swapping is ONE env var. We will not get an Indian toll-free number provisioned
inside a hackathon window, so the simulator is the default and it is not a
cop-out: it is what lets four people build in parallel without blocking on a
telecom KYC process.
"""
from __future__ import annotations

import hashlib
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any


def hash_msisdn(number: str) -> str:
    """Never store a raw phone number. DPDP Act 2023 hygiene, enforced at the boundary."""
    salt = os.getenv("MSISDN_HASH_SALT", "jansetu-demo-salt")
    return "sha256:" + hashlib.sha256(f"{salt}:{number}".encode()).hexdigest()


class TelephonyProvider(ABC):
    """One interface, many channels."""

    name = "base"

    # --- inbound ---------------------------------------------------------
    @abstractmethod
    def parse_inbound(self, payload: dict) -> dict:
        """Raw provider webhook -> partial CitizenReport dict."""

    # --- outbound --------------------------------------------------------
    @abstractmethod
    def send_sms(self, to_hash: str, body: str, language: str = "en") -> dict:
        """Send an SMS. `to_hash` is a hashed MSISDN; the provider resolves it."""

    @abstractmethod
    def make_call(self, to_hash: str, tts_text: str, language: str = "en") -> dict:
        """Place an outbound call that speaks `tts_text` (used for missed-call callback)."""

    # --- shared helpers --------------------------------------------------
    @staticmethod
    def detect_language(text: str) -> str:
        """Cheap script-based language ID. Gemini refines it during structuring."""
        if not text:
            return "en"
        if re.search(r"[ऀ-ॿ]", text):
            return "hi"          # Devanagari covers hi + mr
        if re.search(r"[ঀ-৿]", text):
            return "bn"
        if re.search(r"[஀-௿]", text):
            return "ta"
        if re.search(r"[ఀ-౿]", text):
            return "te"
        if re.search(r"[਀-੿]", text):
            return "pa"
        if re.search(r"[a-zA-Z]", text):
            return "en"
        return "en"

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def build_report(channel: str, raw_text: str, from_number: str | None = None,
                     **meta: Any) -> dict:
        return {
            "created_at": TelephonyProvider.now().isoformat(),
            "channel": channel,
            "channel_meta": {
                "msisdn_hash": hash_msisdn(from_number) if from_number else None,
                "provider": TelephonyProvider.name,
                **meta,
            },
            "raw_text": raw_text,
            "raw_language": TelephonyProvider.detect_language(raw_text),
            "status": "received",
        }
