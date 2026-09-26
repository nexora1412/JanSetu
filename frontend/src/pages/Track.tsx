import { useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../App";
import { track, type TrackResult } from "../api";
import { MiniTimeline, VerdictChip } from "../components/Timeline";
import { STAGE_KEYS } from "../i18n";
import { getTickets } from "../store";

export default function Track() {
  const { t, online } = useApp();
  const tickets = getTickets();
  const [id, setId] = useState("");
  const [result, setResult] = useState<TrackResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function lookup(ticketId: string) {
    const value = ticketId.trim();
    if (!value || busy) return;
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult(await track(value));
    } catch {
      setError(t(online ? "notFound" : "offlineBanner"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Link to="/" className="backlink" style={{ textDecoration: "none" }}>
        ← {t("back")}
      </Link>
      <h1>{t("trackTitle")}</h1>

      {!online && <div className="banner offline">📴 {t("offlineBanner")}</div>}

      <div style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          value={id}
          onChange={(e) => setId(e.target.value)}
          placeholder={t("trackPlaceholder")}
          autoCapitalize="characters"
        />
        <button
          className="btn"
          style={{ width: "auto", padding: "13px 20px" }}
          onClick={() => lookup(id)}
          disabled={busy || !id.trim()}
        >
          {t("trackBtn")}
        </button>
      </div>

      {error && <div className="banner err" style={{ marginTop: 12 }}>⚠️ {error}</div>}

      {result && (
        <div className="card" style={{ marginTop: 16 }}>
          <div className="ticket-id">{result.report_id}</div>
          <div className="kv">
            <span className="k">{t("routedTo")}</span>
            <span className="v">{result.routed_to}</span>
          </div>
          {result.scheme && (
            <div className="kv">
              <span className="k">Scheme</span>
              <span className="v">{result.scheme}</span>
            </div>
          )}
          <div className="kv">
            <span className="k">{t("sla")}</span>
            <span className="v">
              {result.sla_days} {t("days")}
            </span>
          </div>

          {result.evidence?.verdict && (
            <div className="kv">
              <span className="k">{t("proofTitle")}</span>
              <span className="v">
                <VerdictChip verdict={result.evidence.verdict} />
              </span>
            </div>
          )}

          {result.timeline && result.timeline.length > 0 ? (
            <>
              {typeof result.progress_pct === "number" && (
                <div className="progress">
                  <div className="progress-bar" style={{ width: `${result.progress_pct}%` }} />
                  <span className="progress-label">{Math.round(result.progress_pct)}%</span>
                </div>
              )}
              <p className="muted gov-hint">🏛 {t("govTimelineSub")}</p>
              <MiniTimeline stages={result.timeline} />
            </>
          ) : (
            <ul className="timeline">
              {result.stages.map((s, i) => {
                const cls =
                  i < result.current_stage_index
                    ? "done"
                    : i === result.current_stage_index
                      ? "current"
                      : "";
                return (
                  <li key={s} className={cls}>
                    <span className="dot">{i < result.current_stage_index ? "✓" : i + 1}</span>
                    <span className="t">{t(STAGE_KEYS[s] ?? s)}</span>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}

      <h2>{t("myReports")}</h2>
      {tickets.length === 0 && <p className="muted">{t("trackNone")}</p>}
      {tickets.map((tk) => (
        <button key={tk.id} className="ticket-row" onClick={() => lookup(tk.id)}>
          <b>{tk.id}</b> · {tk.department} · {tk.sla_days} {t("days")}
          <div className="snippet">{tk.text}</div>
        </button>
      ))}
    </>
  );
}
