import { useCallback, useState } from "react";

export interface EvidencePayload {
  photo_b64?: string;
  gps_lat?: number;
  gps_lng?: number;
  gps_accuracy_m?: number;
  captured_at?: string;
}

export interface LiveProof {
  photo_b64: string;
  previewUrl: string;
  gps_lat: number;
  gps_lng: number;
  gps_accuracy_m: number;
  captured_at: string;
}

/** Shrink a picked image to a small JPEG and return its base64 (no data-url prefix). */
export async function fileToSmallB64(file: File, max = 800, quality = 0.7): Promise<string> {
  const bitmap = await createImageBitmap(file);
  const scale = Math.min(1, max / Math.max(bitmap.width, bitmap.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(bitmap.width * scale);
  canvas.height = Math.round(bitmap.height * scale);
  canvas.getContext("2d")!.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", quality).split(",", 2)[1];
}

function getPosition(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    if (!("geolocation" in navigator)) return reject(new Error("no-geolocation"));
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 12000,
      maximumAge: 0,
    });
  });
}

/**
 * Anti-fake capture: the photo, a live GPS fix and the device clock are bound
 * together at the moment of the shutter. The backend re-checks freshness and
 * accuracy, so a recycled gallery photo (no fresh GPS) is flagged, not trusted.
 */
export function useLiveCapture() {
  const [proof, setProof] = useState<LiveProof | null>(null);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState("");

  const capture = useCallback(async (file: File) => {
    setError("");
    setLocating(true);
    // Stamp the clock and grab GPS at capture time — before encoding, so the
    // timestamp reflects the shutter, not the upload.
    const captured_at = new Date().toISOString();
    let pos: GeolocationPosition | null = null;
    try {
      pos = await getPosition();
    } catch {
      pos = null;
    }
    setLocating(false);
    try {
      const photo_b64 = await fileToSmallB64(file);
      const previewUrl = URL.createObjectURL(file);
      setProof({
        photo_b64,
        previewUrl,
        gps_lat: pos?.coords.latitude ?? NaN,
        gps_lng: pos?.coords.longitude ?? NaN,
        gps_accuracy_m: pos?.coords.accuracy ?? NaN,
        captured_at,
      });
      if (!pos) setError("location-denied");
    } catch {
      setError("photo-failed");
    }
  }, []);

  const toPayload = useCallback((): EvidencePayload | undefined => {
    if (!proof) return undefined;
    const p: EvidencePayload = { photo_b64: proof.photo_b64, captured_at: proof.captured_at };
    if (Number.isFinite(proof.gps_lat) && Number.isFinite(proof.gps_lng)) {
      p.gps_lat = proof.gps_lat;
      p.gps_lng = proof.gps_lng;
      p.gps_accuracy_m = Number.isFinite(proof.gps_accuracy_m) ? proof.gps_accuracy_m : undefined;
    }
    return p;
  }, [proof]);

  const clear = useCallback(() => {
    setProof(null);
    setError("");
  }, []);

  const hasGps = !!proof && Number.isFinite(proof.gps_lat) && Number.isFinite(proof.gps_lng);

  return { proof, capturing: locating, error, hasGps, capture, toPayload, clear };
}
