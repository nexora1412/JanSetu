import { submitText } from "./api";
import { getPending, saveTicket } from "./store";
import type { PendingReport } from "./store";

export { getLang, setLang, getPending, setPending, addPending } from "./store";

/**
 * Try to send every queued offline report. Items that succeed become local
 * tickets; items that fail (still offline / server down) stay in the queue.
 * Returns whatever is left unsent.
 */
export async function submitTextSync(queue: PendingReport[] = getPending()): Promise<PendingReport[]> {
  const rest: PendingReport[] = [];
  for (const item of queue) {
    try {
      const res = await submitText(item.text, item.lang);
      saveTicket({
        id: res.report.report_id,
        text: item.text,
        sector: res.report.structured.sector,
        department: res.report.routing.department,
        sla_days: res.report.routing.sla_days,
        lang: item.lang,
        created_at: item.created_at,
        ack: res.ack ?? undefined,
      });
    } catch {
      rest.push(item);
    }
  }
  return rest;
}
