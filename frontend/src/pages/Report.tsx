import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../App";
import { submitText, submitVoice, type IntakeResult } from "../api";
import { addPending, saveTicket } from "../store";

export default function Report() {
  const { t, lang, refreshPending } = useApp();
  const [text, setText] = useState("");
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<IntakeResult | null>(null);
  const [queued, setQueued] = useState(false);
  const [error, setError] = useState("");
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);

  function remember(res: IntakeResult, sourceText: string) {
    saveTicket({
      id: res.report.report_id,
      text: sourceText,
      sector: res.report.structured.sector,
      department: res.report.routing.department,
      sla_days: res.report.routing.sla_days,
      lang,
      created_at: new Date().toISOString(),
      ack: res.ack ?? undefined,
    });
    setResult(res);
  }

  async function sendText() {
    const value = text.trim();
    if (!value || busy) return;
    setBusy(true);
    setError("");
    try {
      const res = await submitText(value, lang);
      remember(res, value);
    } catch {
      addPending({ text: value, lang, created_at: new Date().toISOString() });
      refreshPending();
      setQueued(true);
    } finally {
      setBusy(false);
    }
  }

  async function toggleRecord() {
    if (recording) {
      recorder.current?.stop();
      recorder.current?.stream.getTracks().forEach((tr) => tr.stop());
      setRecording(false);
      return;
    }
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      chunks.current = [];
      rec.ondataavailable = (e) => e.data.size && chunks.current.push(e.data);
      rec.onstop = async () => {
        stream.getTracks().forEach((tr) => tr.stop());
        const blob = new Blob(chunks.current, { type: rec.mimeType || "audio/webm" });
        setBusy(true);
        try {
          const res = await submitVoice(blob, lang);
          if (res.transcribed) {
            setTranscript(res.transcript ?? "");
            remember(res, res.transcript ?? "");
          } else {
            setError(t("voiceUnavailable"));
          }
        } catch {
          setError(t("voiceUnavailable"));
        } finally {
          setBusy(false);
        }
      };
      recorder.current = rec;
      rec.start();
      setRecording(true);
    } catch {
      setError(t("voiceUnavailable"));
    }
  }

  if (queued) {
    return (
      <>
        <div className="success-hero">
          <div className="tick">📴</div>
          <h1>{t("queuedOffline")}</h1>
        </div>
        <Link to="/" className="btn secondary" style={{ textDecoration: "none", textAlign: "center" }}>
          {t("back")}
        </Link>
      </>
    );
  }

  if (result) {
    const r = result.report;
    return (
      <>
        <div className="success-hero">
          <div className="tick">✓</div>
          <h1>{t("successTitle")}</h1>
          <div className="ticket-id">{r.report_id}</div>
        </div>
        <div className="card" style={{ margin: "16px 0" }}>
          <div className="kv">
            <span className="k">{t("routedTo")}</span>
            <span className="v">{r.routing.department}</span>
          </div>
          {r.routing.scheme && (
            <div className="kv">
              <span className="k">Scheme</span>
              <span className="v">{r.routing.scheme}</span>
            </div>
          )}
          <div className="kv">
            <span className="k">{t("sla")}</span>
            <span className="v">
              {r.routing.sla_days} {t("days")}
            </span>
          </div>
        </div>
        {result.ack && <div className="banner pending">💬 {result.ack}</div>}
        <p className="muted">{t("ackNote")}</p>
        <div style={{ display: "grid", gap: 10, marginTop: 14 }}>
          <Link to="/track" className="btn" style={{ textDecoration: "none", textAlign: "center" }}>
            {t("trackTitle")}
          </Link>
          <Link
            to="/"
            className="btn secondary"
            style={{ textDecoration: "none", textAlign: "center" }}
          >
            {t("back")}
          </Link>
        </div>
      </>
    );
  }

  return (
    <>
      <Link to="/" className="backlink" style={{ textDecoration: "none" }}>
        ← {t("back")}
      </Link>
      <h1>{t("reportTitle")}</h1>

      {error && <div className="banner err">⚠️ {error}</div>}

      <button
        className={`btn mic ${recording ? "recording" : ""}`}
        onClick={toggleRecord}
        disabled={busy}
      >
        {busy ? t("sending") : recording ? `⏹ ${t("stop")}` : `🎙 ${t("tapToSpeak")}`}
      </button>
      {recording && (
        <p className="muted" style={{ textAlign: "center" }}>
          🔴 {t("listening")}
        </p>
      )}
      {transcript && !result && (
        <div className="banner pending">
          <span>
            {t("weHeard")} <b>{transcript}</b>
          </span>
        </div>
      )}

      <div className="divider" />
      <p className="muted" style={{ textAlign: "center", marginTop: 0 }}>
        {t("orTypeIt")}
      </p>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={t("typePlaceholder")}
        dir="auto"
      />
      <button className="btn" onClick={sendText} disabled={busy || !text.trim()}>
        {busy ? t("sending") : t("submitReport")}
      </button>
    </>
  );
}
