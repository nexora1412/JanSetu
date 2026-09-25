import { Link } from "react-router-dom";
import { useApp } from "../App";
import { getTickets } from "../store";

const CARDS = [
  {
    to: "/report",
    icon: "🎙",
    cls: "ico-report",
    t: "cardReportT",
    d: "cardReportD",
  },
  { to: "/track", icon: "🔎", cls: "ico-track", t: "cardTrackT", d: "cardTrackD" },
  { to: "/verify", icon: "✅", cls: "ico-verify", t: "cardVerifyT", d: "cardVerifyD" },
  { to: "/missed-call", icon: "📞", cls: "ico-missed", t: "cardMissedT", d: "cardMissedD" },
] as const;

export default function Home() {
  const { t, online, pending } = useApp();
  const tickets = getTickets();

  return (
    <>
      <h1>{t("homeGreeting")}</h1>

      {!online && <div className="banner offline">📴 {t("offlineBanner")}</div>}
      {pending > 0 && (
        <div className="banner pending">⏳ {t("pendingBanner", { n: pending })}</div>
      )}

      {CARDS.map((c) => (
        <Link key={c.to} to={c.to} className="home-card">
          <span className={`ico ${c.cls}`} aria-hidden>
            {c.icon}
          </span>
          <span>
            <b>{t(c.t)}</b>
            <span>{t(c.d)}</span>
          </span>
        </Link>
      ))}

      {tickets.length > 0 && (
        <>
          <h2>{t("myReports")}</h2>
          {tickets.slice(0, 3).map((tk) => (
            <div className="ticket-row" key={tk.id}>
              <b>{tk.id}</b> · {tk.department}
              <div className="snippet">{tk.text}</div>
            </div>
          ))}
        </>
      )}
    </>
  );
}
