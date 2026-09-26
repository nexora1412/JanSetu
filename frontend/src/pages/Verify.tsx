import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../App";
import { listProjects, verifyProject, type Project, type VerifyResult } from "../api";
import { VerdictChip } from "../components/Timeline";
import { useLiveCapture } from "../evidence";

function scoreColor(s: number) {
  return s > 0.8 ? "#34d399" : s >= 0.5 ? "#ff9933" : "#f87171";
}

export default function Verify() {
  const { t } = useApp();
  const [projects, setProjects] = useState<Project[] | null>(null);
  const [selected, setSelected] = useState<Project | null>(null);
  const [verdict, setVerdict] = useState("");
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<VerifyResult | null>(null);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const cap = useLiveCapture();

  useEffect(() => {
    listProjects()
      .then(setProjects)
      .catch(() => setProjects([]));
  }, []);

  async function submit() {
    if (!selected || !verdict || busy) return;
    setBusy(true);
    setError("");
    try {
      const ev = cap.toPayload();
      const res = await verifyProject({
        project_id: selected.project_id,
        verdict,
        comment,
        image_b64: ev?.photo_b64,
        gps_lat: ev?.gps_lat,
        gps_lng: ev?.gps_lng,
        gps_accuracy_m: ev?.gps_accuracy_m,
        captured_at: ev?.captured_at,
      });
      setResult(res);
    } catch {
      setError(t("errorGeneric"));
    } finally {
      setBusy(false);
    }
  }

  if (result && selected) {
    const score = result.aggregates.social_audit_score;
    return (
      <>
        <div className="success-hero">
          <div className="tick">✓</div>
          <h1>{t("verifyThanks")}</h1>
          <div className="muted" style={{ marginBottom: 10 }}>
            {selected.intervention}
          </div>
          <span
            className="score-pill"
            style={{ background: `${scoreColor(score)}22`, color: scoreColor(score) }}
          >
            {(score * 100).toFixed(0)}%
          </span>
          <div className="muted" style={{ marginTop: 4 }}>
            {t("auditScore")} · {result.aggregates.project_verification_count} verifications
          </div>
        </div>
        <div className="card" style={{ margin: "16px 0" }}>
          <div className="kv">
            <span className="k">{t("govAction")}</span>
            <span className="v">{result.aggregates.recommended_action.replaceAll("_", " ")}</span>
          </div>
          {result.verification.photo?.proof_of_life && (
            <div className="kv">
              <span className="k">{t("proofTitle")}</span>
              <span className="v">
                <VerdictChip verdict={result.verification.photo.proof_of_life.verdict} />
              </span>
            </div>
          )}
        </div>
        <Link to="/" className="btn" style={{ textDecoration: "none", textAlign: "center" }}>
          {t("back")}
        </Link>
      </>
    );
  }

  if (!selected) {
    return (
      <>
        <Link to="/" className="backlink" style={{ textDecoration: "none" }}>
          ← {t("back")}
        </Link>
        <h1>{t("verifyTitle")}</h1>
        <p className="muted">{t("verifyPick")}</p>
        {projects === null && <p className="muted">{t("sending")}</p>}
        {projects?.length === 0 && <p className="muted">{t("offlineBanner")}</p>}
        {projects?.map((p) => (
          <button key={p.project_id} className="project-row" onClick={() => setSelected(p)}>
            <b>{p.intervention}</b>
            <span className="meta">
              {p.district}, {p.state} · {p.beneficiaries.toLocaleString("en-IN")} {t("beneficiaries")}
            </span>
            <span className="sector-tag">{p.sector}</span>
          </button>
        ))}
      </>
    );
  }

  return (
    <>
      <button className="backlink" onClick={() => setSelected(null)}>← {t("verifyPick")}</button>
      <h1 style={{ fontSize: 18 }}>{selected.intervention}</h1>
      <p className="muted">
        {selected.district}, {selected.state} · {selected.scheme}
      </p>

      {error && <div className="banner err">⚠️ {error}</div>}

      <label>{t("verifyVerdict")}</label>
      <div className="chips">
        {(
          [
            ["completed", "verdictCompleted", "on-good"],
            ["partial", "verdictPartial", "on-mid"],
            ["not_done", "verdictNotDone", "on-bad"],
          ] as const
        ).map(([val, key, cls]) => (
          <button
            key={val}
            className={`chip ${verdict === val ? cls : ""}`}
            onClick={() => setVerdict(val)}
          >
            {t(key)}
          </button>
        ))}
      </div>

      <label>{t("addPhoto")}</label>
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        capture="environment"
        style={{ display: "none" }}
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) void cap.capture(f);
        }}
      />
      <button
        className="btn secondary"
        onClick={() => fileRef.current?.click()}
        disabled={cap.capturing}
      >
        {cap.capturing ? `📡 ${t("locating")}` : cap.proof ? `📷 ${t("retakePhoto")}` : `📷 ${t("addPhoto")}`}
      </button>
      {cap.error === "location-denied" && (
        <div className="banner pending" style={{ marginTop: 8 }}>📍 {t("locationDenied")}</div>
      )}
      {cap.proof && (
        <>
          <div className="photo-preview">
            <img src={cap.proof.previewUrl} alt="preview" />
          </div>
          <div className="chips proof-chips">
            <span className={`chip ${cap.hasGps ? "on-good" : "on-bad"}`}>
              📍 {cap.hasGps ? t("gpsLocked") : t("noGps")}
            </span>
            <span className="chip on-good">⏱ {t("timeStamped")}</span>
          </div>
        </>
      )}

      <label>{t("yourComment")}</label>
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        dir="auto"
        style={{ minHeight: 80 }}
      />

      <button className="btn" onClick={submit} disabled={busy || !verdict}>
        {busy ? t("sending") : t("submitVerification")}
      </button>
    </>
  );
}
