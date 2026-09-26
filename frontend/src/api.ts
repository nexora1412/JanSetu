export interface Routing {
  department: string;
  scheme?: string;
  sla_days: number;
  ack_sent?: boolean;
}

export interface EvidencePayload {
  photo_b64?: string;
  gps_lat?: number;
  gps_lng?: number;
  gps_accuracy_m?: number;
  captured_at?: string;
}

export interface ProofOfLife {
  verdict: string;
  has_photo?: boolean;
  has_gps?: boolean;
  timestamp_fresh?: boolean;
  age_seconds?: number | null;
  flags?: string[];
  gps?: { lat: number; lng: number; accuracy_m?: number } | null;
}

export interface TimelineStage {
  stage: string;
  label: string;
  actor: string;
  status: string; // done | scheduled | pending
  at?: string;
  eta?: string;
}

export interface ReportEvidence {
  served_at?: string | null;
  captured_at?: string | null;
  proof_of_life?: ProofOfLife;
}

export interface IntakeResult {
  report: {
    report_id: string;
    structured: { sector: string; confidence: number; extractor: string };
    routing: Routing;
    evidence?: ReportEvidence | null;
    timeline?: TimelineStage[];
  };
  ack?: string | null;
  degraded: boolean;
  note?: string | null;
}

export interface VoiceResult extends IntakeResult {
  transcribed: boolean;
  transcript?: string;
  stt_provider?: string;
  note?: string | null;
}

export interface TrackResult {
  report_id: string;
  status: string;
  sector: string;
  routed_to: string;
  sla_days: number;
  language: string;
  stages: string[];
  current_stage_index: number;
  timeline?: TimelineStage[];
  progress_pct?: number;
  evidence?: {
    verdict?: string;
    photo_url?: string | null;
    captured_at?: string | null;
    gps?: { lat: number; lng: number; accuracy_m?: number } | null;
    flags?: string[];
  } | null;
  officer_ref?: string | null;
  scheme?: string | null;
}

export interface Project {
  project_id: string;
  intervention: string;
  district: string;
  state: string;
  sector: string;
  beneficiaries: number;
  scheme: string;
}

export interface VerifyResult {
  verification: {
    verification_id: string;
    verdict: string;
    photo?: { proof_of_life?: ProofOfLife | null };
  };
  aggregates: {
    project_verification_count: number;
    social_audit_score: number;
    recommended_action: string;
  };
}

export interface MissedCallResult {
  missed_call: Record<string, unknown>;
  callback_eta_s: number;
  greeting: string;
  note: string;
}

async function jsonOrThrow<T>(r: Response): Promise<T> {
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return (await r.json()) as T;
}

export async function submitText(
  text: string,
  language: string,
  evidence?: EvidencePayload,
): Promise<IntakeResult> {
  const r = await fetch("/api/v1/intake/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      channel: "app",
      language_hint: language,
      from_number: "+910000000000",
      ...(evidence ? { evidence } : {}),
    }),
  });
  return jsonOrThrow<IntakeResult>(r);
}

export async function submitVoice(
  blob: Blob,
  language: string,
  evidence?: EvidencePayload,
): Promise<VoiceResult> {
  const fd = new FormData();
  fd.append("audio", blob, `voice.${blob.type.includes("mp4") ? "m4a" : "webm"}`);
  fd.append("language_hint", language);
  fd.append("channel", "app_voice");
  if (evidence) {
    if (evidence.photo_b64) fd.append("photo_b64", evidence.photo_b64);
    if (evidence.gps_lat != null) fd.append("gps_lat", String(evidence.gps_lat));
    if (evidence.gps_lng != null) fd.append("gps_lng", String(evidence.gps_lng));
    if (evidence.gps_accuracy_m != null)
      fd.append("gps_accuracy_m", String(evidence.gps_accuracy_m));
    if (evidence.captured_at) fd.append("captured_at", evidence.captured_at);
  }
  const r = await fetch("/api/v1/intake/voice", { method: "POST", body: fd });
  return jsonOrThrow<VoiceResult>(r);
}

export async function track(id: string): Promise<TrackResult> {
  const r = await fetch(`/api/v1/track/${encodeURIComponent(id)}`);
  if (r.status === 404) throw new Error("404");
  return jsonOrThrow<TrackResult>(r);
}

export async function listProjects(): Promise<Project[]> {
  const r = await fetch("/api/v1/projects/?limit=100");
  const data = await jsonOrThrow<{ count: number; projects: Project[] }>(r);
  return data.projects;
}

export async function verifyProject(payload: {
  project_id: string;
  verdict: string;
  comment: string;
  image_b64?: string;
  gps_lat?: number;
  gps_lng?: number;
  gps_accuracy_m?: number;
  captured_at?: string;
}): Promise<VerifyResult> {
  const r = await fetch("/api/v1/verify/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ channel: "app", ...payload }),
  });
  return jsonOrThrow<VerifyResult>(r);
}

export async function missedCall(from: string, language: string): Promise<MissedCallResult> {
  const r = await fetch("/api/v1/telephony/missed-call", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ from, language }),
  });
  return jsonOrThrow<MissedCallResult>(r);
}
