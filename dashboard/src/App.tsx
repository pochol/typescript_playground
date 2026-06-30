import { useEffect, useMemo, useState } from "react";
import type { Photo } from "./types";
import { STAGE_LABEL } from "./types";
import { PhotoCard } from "./components/PhotoCard";
import { LineChart } from "./components/LineChart";
import { SAMPLE_PHOTOS } from "./sampleData";

const HAS_FIREBASE = Boolean(import.meta.env.VITE_FIREBASE_API_KEY);

export default function App() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [demo, setDemo] = useState(false);

  useEffect(() => {
    if (!HAS_FIREBASE) {
      setPhotos(SAMPLE_PHOTOS);
      setDemo(true);
      return;
    }
    let unsub = () => {};
    // Import dynamiczny — bez konfiguracji Firebase moduł by się wywalił.
    import("./firebase").then(({ subscribePhotos }) => {
      unsub = subscribePhotos(setPhotos);
    });
    return () => unsub();
  }, []);

  const latest = photos[photos.length - 1];

  // Pierwszy moment wykrycia pinningu — "kiedy grzybnia wyszła na zewnątrz".
  const firstPin = useMemo(
    () => photos.find((p) => p.analysis?.pins_detected),
    [photos]
  );

  const colonizationSeries = useMemo(
    () => [
      {
        label: "Kolonizacja %",
        color: "#26a69a",
        points: photos.map((p) => ({
          x: p.capturedAt,
          y: p.analysis ? p.analysis.colonization_pct : null,
        })),
      },
    ],
    [photos]
  );

  const climateSeries = useMemo(
    () => [
      {
        label: "Temp °C",
        color: "#ef5350",
        points: photos.map((p) => ({ x: p.capturedAt, y: p.analysis?.temperature_c ?? null })),
      },
      {
        label: "Wilgotność %",
        color: "#42a5f5",
        points: photos.map((p) => ({ x: p.capturedAt, y: p.analysis?.humidity_pct ?? null })),
      },
    ],
    [photos]
  );

  return (
    <div className="app">
      <header>
        <h1>🍄 Mushroom Growth Monitor</h1>
        {demo && <span className="demo">tryb DEMO — podłącz Firebase (.env.local)</span>}
      </header>

      {photos.length === 0 ? (
        <p className="empty">Brak zdjęć. Uruchom most (relay/) z podłączonym telefonem.</p>
      ) : (
        <>
          <section className="stats">
            <Stat label="Zdjęć" value={String(photos.length)} />
            <Stat
              label="Etap"
              value={latest?.analysis ? STAGE_LABEL[latest.analysis.stage] : "—"}
            />
            <Stat
              label="Kolonizacja"
              value={latest?.analysis ? `${latest.analysis.colonization_pct}%` : "—"}
            />
            <Stat
              label="Temp / Wilg."
              value={
                latest?.analysis
                  ? `${latest.analysis.temperature_c ?? "?"}°C / ${latest.analysis.humidity_pct ?? "?"}%`
                  : "—"
              }
            />
          </section>

          {firstPin && (
            <div className="alert">
              🌱 <b>Pinning wykryty!</b> Pierwsze zawiązki pojawiły się{" "}
              {new Date(firstPin.capturedAt).toLocaleString("pl-PL")} — grzybnia zaczęła
              wychodzić na zewnątrz (start owocowania).
            </div>
          )}

          <section className="charts">
            <div className="chart-box">
              <h3>Postęp kolonizacji</h3>
              <LineChart series={colonizationSeries} yMin={0} yMax={100} yUnit="%" />
            </div>
            <div className="chart-box">
              <h3>Klimat w boxie (z wyświetlacza)</h3>
              <LineChart series={climateSeries} yMin={0} yMax={100} />
              <div className="legend">
                <span style={{ color: "#ef5350" }}>● Temperatura °C</span>
                <span style={{ color: "#42a5f5" }}>● Wilgotność %</span>
              </div>
            </div>
          </section>

          <h2>Galeria ({photos.length})</h2>
          <section className="gallery">
            {[...photos].reverse().map((p) => (
              <PhotoCard key={p.id} photo={p} />
            ))}
          </section>
        </>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
