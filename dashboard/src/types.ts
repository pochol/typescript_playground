export type Stage =
  | "inoculation"
  | "colonization"
  | "fully_colonized"
  | "pinning"
  | "fruiting"
  | "harvest_ready"
  | "contamination"
  | "unknown";

export interface Analysis {
  stage: Stage;
  colonization_pct: number;
  pins_detected: boolean;
  pin_count_estimate: number;
  morphology: "none" | "normal" | "long_stems" | "large_caps" | "leggy_thin" | "aborts";
  condensation: "none" | "light" | "heavy" | "standing_water";
  temperature_c: number | null;
  humidity_pct: number | null;
  issues: string[];
  recommendation: string;
  confidence: number;
}

export interface Photo {
  id: string;
  imageUrl: string;
  capturedAt: number; // ms epoch
  analysis: Analysis | null;
}

export const STAGE_LABEL: Record<Stage, string> = {
  inoculation: "Inokulacja",
  colonization: "Kolonizacja",
  fully_colonized: "Zarośnięte",
  pinning: "Pinning (zawiązki)",
  fruiting: "Owocowanie",
  harvest_ready: "Do zbioru",
  contamination: "Kontaminacja",
  unknown: "Nieznane",
};

export const STAGE_COLOR: Record<Stage, string> = {
  inoculation: "#9e9e9e",
  colonization: "#42a5f5",
  fully_colonized: "#26a69a",
  pinning: "#ffa726",
  fruiting: "#66bb6a",
  harvest_ready: "#8bc34a",
  contamination: "#ef5350",
  unknown: "#bdbdbd",
};
