export interface LocalTicket {
  id: string;
  text: string;
  sector: string;
  department: string;
  sla_days: number;
  lang: string;
  created_at: string;
  ack?: string;
}

export interface PendingReport {
  text: string;
  lang: string;
  created_at: string;
}

const TICKETS_KEY = "jansetu.tickets";
const PENDING_KEY = "jansetu.pending";
const LANG_KEY = "jansetu.lang";

function read<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function write(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage full or blocked — the app still works for this session */
  }
}

export function getTickets(): LocalTicket[] {
  return read<LocalTicket[]>(TICKETS_KEY, []);
}

export function saveTicket(t: LocalTicket) {
  write(TICKETS_KEY, [t, ...getTickets()].slice(0, 50));
}

export function getPending(): PendingReport[] {
  return read<PendingReport[]>(PENDING_KEY, []);
}

export function addPending(p: PendingReport) {
  write(PENDING_KEY, [...getPending(), p]);
}

export function setPending(list: PendingReport[]) {
  write(PENDING_KEY, list);
}

export function getLang(): string | null {
  return localStorage.getItem(LANG_KEY);
}

export function setLang(code: string) {
  localStorage.setItem(LANG_KEY, code);
}
