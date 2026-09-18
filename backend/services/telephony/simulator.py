"""
JanSetu — Telephony SIMULATOR  (workstream A)
===============================================
A phone that lives in the browser. The default provider.

The simulator exists because we cannot provision an Indian toll-free number in a
hackathon window, and because four people must not block on telecom KYC. It is
also genuinely useful: it makes the demo deterministic and reproducible.

It is NOT a fake in the dishonest sense — it exercises the real parse_inbound
path and produces real CitizenReports. Swapping to a real provider changes one
env var and nothing else.

Channels simulated: missed_call · voice_call · sms · ivr · whatsapp · web · kiosk
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

from services.telephony.base import TelephonyProvider, hash_msisdn

# Ack templates in the languages the demo actually uses. TTS fills {ticket}.
ACK_TEMPLATES = {
    "en": "JanSetu: your report {ticket} has been registered and sent to {dept}. "
          "Expected response in {sla} days. Quote {ticket} for updates.",
    "hi": "जनसेतु: आपकी शिकायत {ticket} दर्ज हो गई है और {dept} को भेज दी गई है। "
          "{sla} दिनों में जवाब की उम्मीद है। जानकारी के लिए {ticket} बताएं।",
    "mr": "जनसेतु: आपकी तक्रार {ticket} नोंदवली गेली आणि {dept} कडे पाठवली गेली. "
          "{sla} दिवसांत उत्तराची अपेक्षा. माहितीसाठी {ticket} सांगा.",
    "bn": "লোকনিবেশ: আপনার অভিযোগ {ticket} নথিভুক্ত হয়েছে এবং {dept}-এ পাঠানো হয়েছে। "
          "{sla} দিনের মধ্যে উত্তর আশা করুন। আপডেটের জন্য {ticket} উল্লেখ করুন।",
    "ta": "லோக்நிவேஷ்: உங்கள் புகார் {ticket} பதிவு செய்யப்பட்டு {dept} க்கு அனுப்பப்பட்டது. "
          "{sla} நாட்களில் பதில் எதிர்பார்க்கலாம். விவரங்களுக்கு {ticket} ஐக் குறிப்பிடவும்.",
    "te": "లోక్నివేష్: మీ ఫిర్యాదు {ticket} నమోదు చేయబడి {dept} కు పంపబడింది. "
          "{sla} రోజుల్లో సమాధానం ఆశించండి. వివరాలకు {ticket} చెప్పండి.",
}

# The single-helpline greeting. NO IVR MENU — that is the whole design point.
GREETING = {
    "en": "Hello. You have reached JanSetu. Please describe your problem in your own language.",
    "hi": "नमस्ते। आप जनसेतु से जुड़े हैं। कृपया अपनी समस्या अपनी भाषा में बताइए।",
    "mr": "नमस्कार. आपण जनसेतु शी जोडले आहात. कृपया आपली समस्या आपल्या भाषेत सांगा.",
    "bn": "নমস্কার। আপনি লোকনিবেশে যুক্ত হয়েছেন। অনুগ্রহ করে আপনার সমস্যা নিজের ভাষায় বলুন।",
    "ta": "வணக்கம். நீங்கள் லோக்நிவேஷை அடைந்துள்ளீர்கள். உங்கள் பிரச்சனையை உங்கள் மொழியில் சொல்லுங்கள்.",
    "te": "నమస్కారం. మీరు లోక్నివేష్ కి చేరుకున్నారు. దయచేసి మీ సమస్యను మీ భాషలో చెప్పండి.",
}


class SimulatorProvider(TelephonyProvider):
    name = "simulator"

    def __init__(self) -> None:
        self.outbox: list[dict] = []       # every SMS/call we "sent" — shown in the demo UI
        self.call_log: list[dict] = []

    # ---------------------------------------------------------------- inbound
    def parse_inbound(self, payload: dict) -> dict:
        """Accepts the simulator's own payload shape (and tolerates Twilio/Exotel-ish keys)."""
        channel = payload.get("channel", "sms")
        text = payload.get("text") or payload.get("Body") or payload.get("speech") or ""
        frm = payload.get("from") or payload.get("From") or payload.get("msisdn") or "+910000000000"

        meta = {
            "handset_class": payload.get("handset_class")
            or ("feature_phone" if channel in ("sms", "missed_call", "ivr") else "smartphone"),
            "duration_s": payload.get("duration_s"),
            "audio_uri": payload.get("audio_uri"),
        }
        report = self.build_report(channel, text, frm, **meta)

        if channel == "missed_call":
            # A missed call carries no content — we call back and capture speech.
            report["channel_meta"]["callback_required"] = True
            report["channel_meta"]["callback_within_s"] = 60
        if channel == "ivr":
            # DTMF keypress: 1 = yes/confirm, 2 = no
            report["channel_meta"]["dtmf"] = payload.get("dtmf")
        return report

    # --------------------------------------------------------------- outbound
    def send_sms(self, to_hash: str, body: str, language: str = "en") -> dict:
        rec = {"type": "sms", "to": to_hash, "body": body, "language": language,
               "sent_at": datetime.now(timezone.utc).isoformat(), "provider": "simulator"}
        self.outbox.append(rec)
        return {"ok": True, **rec}

    def make_call(self, to_hash: str, tts_text: str, language: str = "en") -> dict:
        rec = {"type": "call", "to": to_hash, "tts": tts_text, "language": language,
               "sent_at": datetime.now(timezone.utc).isoformat(), "provider": "simulator"}
        self.outbox.append(rec)
        self.call_log.append(rec)
        return {"ok": True, **rec}

    # ------------------------------------------------------------- demo glue
    def greeting(self, language: str = "en") -> str:
        return GREETING.get(language, GREETING["en"])

    def ack(self, ticket: str, dept: str, sla: int, language: str = "en") -> str:
        tmpl = ACK_TEMPLATES.get(language, ACK_TEMPLATES["en"])
        return tmpl.format(ticket=ticket, dept=dept, sla=sla)

    def simulate_missed_call(self, from_number: str) -> dict:
        """The single most important channel for the poorest citizen. Zero cost,
        any keypad handset, no data. We ring back within 60 seconds."""
        rec = {"type": "inbound_missed_call", "from_hash": hash_msisdn(from_number),
               "at": datetime.now(timezone.utc).isoformat(), "callback_eta_s": 60}
        self.call_log.append(rec)
        return rec


def get_provider() -> TelephonyProvider:
    """Factory. One env var decides the whole channel layer."""
    import os
    name = os.getenv("TELEPHONY_PROVIDER", "simulator").lower()
    if name == "simulator":
        return SimulatorProvider()
    if name == "exotel":
        from services.telephony.exotel import ExotelProvider  # noqa: PLC0415
        return ExotelProvider()
    if name == "twilio":
        from services.telephony.twilio import TwilioProvider  # noqa: PLC0415
        return TwilioProvider()
    return SimulatorProvider()
