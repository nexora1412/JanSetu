import { useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../App";
import { missedCall, type MissedCallResult } from "../api";

export default function MissedCall() {
  const { t, lang } = useApp();
  const [number, setNumber] = useState("+91");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<MissedCallResult | null>(null);
  const [error, setError] = useState("");

  async function send() {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      setResult(await missedCall(number.trim() || "+910000000000", lang));
    } catch {
      setError(t("errorGeneric"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Link to="/" className="backlink" style={{ textDecoration: "none" }}>
        ← {t("back")}
      </Link>
      <h1>{t("missedTitle")}</h1>

      <div className="helpline">
        <div className="num">155 205</div>
        <div className="muted">toll-free · 24×7 · any handset</div>
      </div>

      <p className="muted">{t("missedExplain")}</p>

      {error && <div className="banner err">⚠️ {error}</div>}

      {result ? (
        <div className="card" style={{ marginBottom: 14 }}>
          <div className="banner pending" style={{ margin: 0 }}>
            📞 {t("callBackEta", { n: result.callback_eta_s })}
          </div>
          <div className="kv" style={{ marginTop: 10 }}>
            <span className="k">{lang === "en" ? "Greeting you will hear" : "Greeting"}</span>
            <span className="v">“{result.greeting}”</span>
          </div>
          <p className="muted" style={{ marginBottom: 0 }}>{result.note}</p>
        </div>
      ) : (
        <>
          <label>{t("yourNumber")}</label>
          <input
            type="tel"
            value={number}
            onChange={(e) => setNumber(e.target.value)}
            placeholder="+91 98XXXXXXXX"
            inputMode="tel"
          />
          <button className="btn" onClick={send} disabled={busy}>
            {busy ? t("sending") : `📞 ${t("missedBtn")}`}
          </button>
        </>
      )}
    </>
  );
}
