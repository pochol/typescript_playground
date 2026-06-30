import type { Photo } from "../types";
import { STAGE_COLOR, STAGE_LABEL } from "../types";

const MORPHOLOGY_LABEL: Record<string, string> = {
  none: "—",
  normal: "prawidłowa",
  long_stems: "długie nóżki ⚠️",
  large_caps: "duże kapelusze",
  leggy_thin: "wątłe/wyciągnięte ⚠️",
  aborts: "poronienia ⚠️",
};

const CONDENSATION_LABEL: Record<string, string> = {
  none: "brak",
  light: "lekka",
  heavy: "duża ⚠️",
  standing_water: "stojąca woda ⚠️",
};

export function PhotoCard({ photo }: { photo: Photo }) {
  const a = photo.analysis;
  const date = new Date(photo.capturedAt).toLocaleString("pl-PL");

  return (
    <div className="card">
      <a href={photo.imageUrl} target="_blank" rel="noreferrer">
        <img src={photo.imageUrl} alt={date} loading="lazy" />
      </a>
      <div className="card-body">
        <div className="card-date">{date}</div>
        {a ? (
          <>
            <span className="badge" style={{ background: STAGE_COLOR[a.stage] }}>
              {STAGE_LABEL[a.stage]}
            </span>
            {a.pins_detected && (
              <span className="badge pin">🌱 piny: {a.pin_count_estimate}</span>
            )}
            <div className="kv">
              <span>Kolonizacja</span>
              <div className="bar">
                <div style={{ width: `${a.colonization_pct}%` }} />
              </div>
              <b>{a.colonization_pct}%</b>
            </div>
            <div className="meta">
              {a.temperature_c != null && <span>🌡️ {a.temperature_c}°C</span>}
              {a.humidity_pct != null && <span>💧 {a.humidity_pct}%</span>}
              <span>🍄 {MORPHOLOGY_LABEL[a.morphology]}</span>
              <span>💦 {CONDENSATION_LABEL[a.condensation]}</span>
            </div>
            {a.issues.length > 0 && (
              <ul className="issues">
                {a.issues.map((i, k) => (
                  <li key={k}>⚠️ {i}</li>
                ))}
              </ul>
            )}
            {a.recommendation && <p className="rec">💡 {a.recommendation}</p>}
          </>
        ) : (
          <div className="card-date">Bez analizy AI</div>
        )}
      </div>
    </div>
  );
}
