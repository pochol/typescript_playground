import type { Photo, Stage } from "./types";

/** Dane demonstracyjne — pokazują dashboard zanim podłączysz Firebase. */
const DAY = 24 * 3600 * 1000;
const start = Date.UTC(2026, 5, 1, 9, 0, 0);

function mk(i: number, stage: Stage, col: number, pins: number): Photo {
  return {
    id: `demo_${i}`,
    imageUrl: `https://picsum.photos/seed/mush${i}/600/450`,
    capturedAt: start + i * DAY,
    analysis: {
      stage,
      colonization_pct: col,
      pins_detected: pins > 0,
      pin_count_estimate: pins,
      morphology: pins > 0 ? "normal" : "none",
      condensation: i > 7 ? "light" : "none",
      temperature_c: 21 + Math.round(Math.sin(i) * 2 * 10) / 10,
      humidity_pct: 80 + Math.round(Math.cos(i) * 8 * 10) / 10,
      issues: i === 6 ? ["wilgotność lekko za niska"] : [],
      recommendation:
        pins > 0 ? "Utrzymuj wysoką wilgotność i wietrz 2× dziennie." : "Czekaj, kolonizacja postępuje.",
      confidence: 0.8,
    },
  };
}

export const SAMPLE_PHOTOS: Photo[] = [
  mk(0, "inoculation", 5, 0),
  mk(1, "colonization", 18, 0),
  mk(2, "colonization", 34, 0),
  mk(3, "colonization", 52, 0),
  mk(4, "colonization", 70, 0),
  mk(5, "fully_colonized", 92, 0),
  mk(6, "fully_colonized", 98, 0),
  mk(7, "pinning", 100, 4),
  mk(8, "pinning", 100, 9),
  mk(9, "fruiting", 100, 12),
  mk(10, "fruiting", 100, 14),
  mk(11, "harvest_ready", 100, 14),
];
