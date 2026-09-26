import type { TimelineStage } from "../api";

export function VerdictChip({ verdict }: { verdict?: string | null }) {
  if (!verdict) return null;
  const map: Record<string, { cls: string; label: string }> = {
    live_verified: { cls: "on-good", label: "✓ Live-verified (photo + GPS + fresh time)" },
    partially_verified: { cls: "on-mid", label: "◐ Partially verified" },
    unverified: { cls: "on-bad", label: "✗ Unverified" },
  };
  const m = map[verdict] ?? { cls: "", label: verdict };
  return <span className={`chip ${m.cls}`}>{m.label}</span>;
}

function when(s: TimelineStage): string {
  const iso = s.at || s.eta;
  if (!iso) return "";
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { day: "numeric", month: "short" });
  } catch {
    return "";
  }
}

/**
 * The citizen-visible promise: WHO handles the complaint and WHEN, stage by
 * stage. Done stages show a real timestamp; future stages show an ETA derived
 * from the routing SLA. Officers advance stages via the dashboard.
 */
export function MiniTimeline({ stages }: { stages: TimelineStage[] }) {
  return (
    <ul className="timeline gov">
      {stages.map((s) => {
        const cls = s.status === "done" ? "done" : s.status === "scheduled" ? "current" : "";
        const dot = s.status === "done" ? "✓" : s.status === "scheduled" ? "◷" : "·";
        return (
          <li key={s.stage} className={cls}>
            <span className="dot">{dot}</span>
            <span className="t">
              <b>{s.label}</b>
              <span className="actor">{s.actor}</span>
              <span className="when">
                {s.status === "done" ? "" : "ETA "}
                {when(s)}
              </span>
            </span>
          </li>
        );
      })}
    </ul>
  );
}
