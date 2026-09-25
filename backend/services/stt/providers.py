"""
JanSetu — Speech-to-Text providers  (Person 1, Day 1)
=====================================================
Three providers behind one interface, tried in order. If the first fails,
we fall through to the next. If ALL fail, we return None and the caller
carries on — the demo must never die because one API is unreachable.

    1. Sarvam AI   (saaras:v3)   — fastest to sign up, simple REST, 22 Indic languages
    2. Bhashini    (ULCA/Dhruva) — free, Government of India, best story for a DPI pitch
    3. Google Cloud Speech-to-Text (Chirp_2) — best accuracy, needs a GCP project

Return shape from every provider:
    {"text": str, "language": str, "provider": str, "confidence": float|None}
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod

try:
    import env_boot  # noqa: F401  — MUST run before any os.getenv() below
except ImportError:
    pass

TIMEOUT_S = 25

# ISO-639-1 (Bhashini) <-> BCP-47 (Sarvam / Google). Keep them together so
# one language code works everywhere.
LANG_ALIASES = {
    "hi": "hi-IN", "mr": "mr-IN", "bn": "bn-IN", "ta": "ta-IN", "te": "te-IN",
    "gu": "gu-IN", "kn": "kn-IN", "ml": "ml-IN", "pa": "pa-IN", "or": "or-IN",
    "as": "as-IN", "ur": "ur-IN", "en": "en-IN", "ne": "ne-IN", "sd": "sd-IN",
    "sa": "sa-IN", "ks": "ks-IN", "mni": "mni-IN", "brx": "brx-IN", "doi": "doi-IN",
}


def bcp47(lang: str) -> str:
    """'mr' -> 'mr-IN'. Already-tagged codes pass through unchanged."""
    if not lang:
        return "en-IN"
    if "-" in lang:
        return lang
    return LANG_ALIASES.get(lang, f"{lang}-IN")


def iso639(lang: str) -> str:
    """'mr-IN' -> 'mr'."""
    return (lang or "en").split("-")[0]


class STTProvider(ABC):
    name = "base"

    @abstractmethod
    def configured(self) -> bool:
        """True when this provider has the credentials it needs."""

    @abstractmethod
    def transcribe(self, audio_bytes: bytes, language: str,
                   sample_rate: int = 16000) -> dict | None:
        """Return the standard dict, or None if this provider cannot do it."""


# ===========================================================================
# 1 · Sarvam AI — saaras:v3
# ===========================================================================
class SarvamProvider(STTProvider):
    """
    Sign up:  https://dashboard.sarvam.ai  →  API key ("api-subscription-key")
    Docs:     https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/overview

    Endpoint: POST https://api.sarvam.ai/speech-to-text
    Model:    saaras:v3   (mode: transcribe | translate | verbatim | translit | codemix)
    Limit:    30 seconds per REST request
    """
    name = "sarvam"
    URL = os.getenv("SARVAM_STT_URL", "https://api.sarvam.ai/speech-to-text")

    def __init__(self) -> None:
        self.key = os.getenv("SARVAM_API_KEY", "").strip()
        self.model = os.getenv("SARVAM_MODEL", "saaras:v3").strip()

    def configured(self) -> bool:
        return bool(self.key)

    def transcribe(self, audio_bytes: bytes, language: str,
                   sample_rate: int = 16000) -> dict | None:
        if not self.configured():
            return None

        # multipart/form-data assembled by hand — avoids a `requests` dependency.
        boundary = "----JanSetuBoundary7MA4YWxk"
        fields = {
            "model": self.model,
            "mode": os.getenv("SARVAM_MODE", "transcribe"),
            "language_code": bcp47(language),
        }
        body = b""
        for k, v in fields.items():
            body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n"
                     f"{v}\r\n").encode()
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
                 f"filename=\"audio.wav\"\r\nContent-Type: audio/wav\r\n\r\n").encode()
        body += audio_bytes + f"\r\n--{boundary}--\r\n".encode()

        req = urllib.request.Request(
            self.URL, data=body, method="POST",
            headers={"api-subscription-key": self.key,
                     "Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                data = json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
            return None

        text = data.get("transcript") or data.get("text") or ""
        if not text:
            return None
        return {"text": text.strip(), "language": iso639(data.get("language_code", language)),
                "provider": self.name, "confidence": None}


# ===========================================================================
# 2 · Bhashini (ULCA / Dhruva) — Government of India
# ===========================================================================
class BhashiniProvider(STTProvider):
    """
    Sign up:  https://meity-auth.ulca.ai   (register → create an app → get keys)
              You need THREE things:
                BHASHINI_USER_ID       your ULCA user id
                BHASHINI_ULCA_API_KEY  key for the pipeline CONFIG call
                BHASHINI_PIPELINE_ID   the pipeline id issued to your app

    How it works (two steps — this trips everyone up):
      STEP A · CONFIG CALL   POST /ulca/apis/v0/model/getModelsPipeline
              You send the task ("asr") + the language. Bhashini replies with
              the model's serviceId AND a short-lived inference API key.
      STEP B · INFERENCE     POST <callbackUrl from step A>
              You send base64 audio with that serviceId and that key.

    Docs: https://bhashini.gitbook.io/bhashini-apis
    """
    name = "bhashini"
    CONFIG_URL = os.getenv(
        "BHASHINI_CONFIG_URL",
        "https://meity-auth.ulca.ai/ulca/apis/v0/model/getModelsPipeline")
    INFERENCE_URL = os.getenv(
        "BHASHINI_INFERENCE_URL",
        "https://dhruva-api.bhashini.gov.in/services/inference/pipeline")

    def __init__(self) -> None:
        self.user_id = os.getenv("BHASHINI_USER_ID", "").strip()
        self.ulca_key = os.getenv("BHASHINI_ULCA_API_KEY", "").strip()
        self.pipeline_id = os.getenv("BHASHINI_PIPELINE_ID", "").strip()
        self._cache: dict[str, dict] = {}   # language -> config response

    def configured(self) -> bool:
        return bool(self.user_id and self.ulca_key and self.pipeline_id)

    # --- STEP A -----------------------------------------------------------
    def _get_config(self, language: str) -> dict | None:
        if language in self._cache:
            return self._cache[language]

        payload = {
            "pipelineTasks": [{"taskType": "asr",
                               "config": {"language": {"sourceLanguage": iso639(language)}}}],
            "pipelineRequestConfig": {"pipelineId": self.pipeline_id},
        }
        req = urllib.request.Request(
            self.CONFIG_URL, data=json.dumps(payload).encode(), method="POST",
            headers={"userID": self.user_id, "ulcaApiKey": self.ulca_key,
                     "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                data = json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
            return None

        try:
            cfg = data["pipelineResponseConfig"][0]["config"][0]
            ep = data["pipelineInferenceAPIEndPoint"]
            result = {
                "serviceId": cfg["serviceId"],
                "callbackUrl": ep["callbackUrl"],
                "inferenceApiKey": ep["inferenceApiKey"]["value"],
                "keyName": ep["inferenceApiKey"].get("name", "Authorization"),
            }
        except (KeyError, IndexError, TypeError):
            return None

        self._cache[language] = result
        return result

    # --- STEP B -----------------------------------------------------------
    def transcribe(self, audio_bytes: bytes, language: str,
                   sample_rate: int = 16000) -> dict | None:
        if not self.configured():
            return None
        cfg = self._get_config(language)
        if not cfg:
            return None

        payload = {
            "pipelineTasks": [{
                "taskType": "asr",
                "config": {
                    "language": {"sourceLanguage": iso639(language)},
                    "serviceId": cfg["serviceId"],
                    "audioFormat": "wav",
                    "samplingRate": sample_rate,
                },
            }],
            "inputData": {"audio": [{"audioContent": base64.b64encode(audio_bytes).decode()}]},
        }
        req = urllib.request.Request(
            cfg["callbackUrl"], data=json.dumps(payload).encode(), method="POST",
            headers={cfg["keyName"]: cfg["inferenceApiKey"],
                     "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                data = json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
            return None

        try:
            text = data["pipelineResponse"][0]["output"][0]["source"]
        except (KeyError, IndexError, TypeError):
            return None
        if not text:
            return None
        return {"text": text.strip(), "language": iso639(language),
                "provider": self.name, "confidence": None}


# ===========================================================================
# 3 · Google Cloud Speech-to-Text (Chirp_2)
# ===========================================================================
class GoogleChirpProvider(STTProvider):
    """
    Setup (heaviest, but best accuracy and it satisfies "uses Google AI"):
      1. https://console.cloud.google.com → create a project
      2. Enable the "Speech-to-Text API"
      3. Create a service account → download the JSON key
      4. pip install google-cloud-speech
      5. Set GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

    Model: chirp_2  (or "long"/"short" for the classic models)
    """
    name = "google_chirp"

    def __init__(self) -> None:
        self.creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        self.model = os.getenv("GOOGLE_STT_MODEL", "chirp_2").strip()

    def configured(self) -> bool:
        if not self.creds or not os.path.exists(self.creds):
            return False
        try:
            import google.cloud.speech  # noqa: F401
            return True
        except ImportError:
            return False

    def transcribe(self, audio_bytes: bytes, language: str,
                   sample_rate: int = 16000) -> dict | None:
        if not self.configured():
            return None
        try:
            from google.cloud import speech
            client = speech.SpeechClient()
            audio = speech.RecognitionAudio(content=audio_bytes)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=sample_rate,
                language_code=bcp47(language),
                model=self.model,
            )
            resp = client.recognize(config=config, audio=audio)
            if not resp.results:
                return None
            top = resp.results[0]
            return {"text": top.alternatives[0].transcript.strip(),
                    "language": iso639(language),
                    "provider": self.name,
                    "confidence": float(top.alternatives[0].confidence or 0)}
        except Exception:
            return None


# ===========================================================================
# 4 · Google Gemini Multimodal Audio (Gemini 2.5 Flash)
# ===========================================================================
class GeminiAudioProvider(STTProvider):
    """
    Direct multimodal audio transcription using Google Gemini 2.5 Flash.
    No GCP Speech-to-Text service account needed — uses the same GEMINI_API_KEY!
    Works seamlessly across all Indian and BRICS languages (Marathi, Hindi,
    isiXhosa, isiZulu, Afrikaans, English).
    """
    name = "gemini_audio"

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

    def configured(self) -> bool:
        return bool(self.api_key)

    def transcribe(self, audio_bytes: bytes, language: str = "hi",
                   sample_rate: int = 16000) -> dict | None:
        if not self.configured():
            return None

        # Determine audio MIME type from magic header or default to audio/wav
        mime = "audio/wav"
        if audio_bytes[:4] == b"RIFF":
            mime = "audio/wav"
        elif audio_bytes[:3] == b"ID3" or audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
            mime = "audio/mp3"
        elif audio_bytes[4:8] == b"ftyp":
            mime = "audio/mp4"
        elif audio_bytes[:4] == b"\x1a\x45\xdf\xa3":
            mime = "audio/webm"

        b64 = base64.b64encode(audio_bytes).decode("ascii")
        prompt = (
            f"Transcribe this citizen voice audio complaint verbatim in its original spoken language. "
            f"Language hint: {language}. Return ONLY a JSON object with two keys: "
            f"'text': verbatim transcription in native script, and 'language': BCP-47 / ISO code."
        )

        body = json.dumps({
            "contents": [{
                "role": "user",
                "parts": [
                    {"inline_data": {"mime_type": mime, "data": b64}},
                    {"text": prompt}
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            self.endpoint.format(model=self.model, key=self.api_key),
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw_text)
            text = (parsed.get("text") or "").strip()
            if not text:
                return None
            detected_lang = iso639(parsed.get("language") or language)
            return {
                "text": text,
                "language": detected_lang,
                "provider": self.name,
                "confidence": 0.95
            }
        except Exception:
            return None
