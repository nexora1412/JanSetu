import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useApp } from "../App";
import { requestOtp, verifyOtp } from "../api";
import { setToken } from "../store";

export default function Login() {
  const { t } = useApp();
  const nav = useNavigate();
  const loc = useLocation();
  const from = (loc.state as { from?: string } | null)?.from || "/";

  const [phone, setPhone] = useState("+91");
  const [name, setName] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [otp, setOtp] = useState("");
  const [demoOtp, setDemoOtp] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function sendCode() {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const res = await requestOtp(phone.trim(), name.trim() || undefined);
      setDemoOtp(res.demo_otp ?? null);
      setStep("otp");
    } catch {
      setError(t("errorGeneric"));
    } finally {
      setBusy(false);
    }
  }

  async function confirm() {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const res = await verifyOtp(phone.trim(), otp.trim(), name.trim() || undefined);
      setToken(res.token);
      nav(from, { replace: true });
    } catch {
      setError(t("loginWrong"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Link to="/" className="backlink" style={{ textDecoration: "none" }}>
        ← {t("back")}
      </Link>
      <h1>{t("loginTitle")}</h1>

      <div className="card" style={{ marginBottom: 14 }}>
        <p className="muted" style={{ marginTop: 0 }}>
          {t("loginSub")}
        </p>

        {error && <div className="banner err">⚠️ {error}</div>}

        {step === "phone" ? (
          <>
            <label>{t("loginPhone")}</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+91 98XXXXXXXX"
              inputMode="tel"
            />
            <label>{t("loginName")}</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="—"
            />
            <button className="btn" onClick={sendCode} disabled={busy}>
              {busy ? t("loginSending") : `📩 ${t("loginSendOtp")}`}
            </button>
          </>
        ) : (
          <>
            {demoOtp && (
              <div className="banner pending" style={{ marginTop: 0 }}>
                🔑 {t("loginDemoOtp", { code: demoOtp })}
              </div>
            )}
            <label>{t("loginOtpLabel")}</label>
            <input
              type="text"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
              placeholder="000000"
              inputMode="numeric"
              autoComplete="one-time-code"
            />
            <button className="btn" onClick={confirm} disabled={busy || otp.length !== 6}>
              {busy ? t("loginSending") : `✅ ${t("loginVerify")}`}
            </button>
            <button
              className="btn ghost"
              onClick={sendCode}
              disabled={busy}
              style={{ marginTop: 8 }}
            >
              ↻ {t("loginResend")}
            </button>
          </>
        )}
      </div>
    </>
  );
}
