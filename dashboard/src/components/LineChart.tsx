interface Series {
  label: string;
  color: string;
  points: { x: number; y: number | null }[];
}

interface Props {
  series: Series[];
  yMin?: number;
  yMax?: number;
  height?: number;
  yUnit?: string;
}

/** Lekki wykres liniowy w czystym SVG (bez zewnętrznych bibliotek). */
export function LineChart({ series, yMin = 0, yMax = 100, height = 220, yUnit = "" }: Props) {
  const width = 760;
  const padL = 44;
  const padB = 28;
  const padT = 12;
  const padR = 12;
  const plotW = width - padL - padR;
  const plotH = height - padT - padB;

  const allX = series.flatMap((s) => s.points.map((p) => p.x));
  const xMin = Math.min(...allX);
  const xMax = Math.max(...allX);
  const spanX = xMax - xMin || 1;

  const sx = (x: number) => padL + ((x - xMin) / spanX) * plotW;
  const sy = (y: number) => padT + plotH - ((y - yMin) / (yMax - yMin || 1)) * plotH;

  const yTicks = 5;
  const ticks = Array.from({ length: yTicks + 1 }, (_, i) => yMin + ((yMax - yMin) / yTicks) * i);

  const fmtDate = (ms: number) =>
    new Date(ms).toLocaleDateString("pl-PL", { day: "2-digit", month: "2-digit" });

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={padL} y1={sy(t)} x2={width - padR} y2={sy(t)} stroke="#eee" />
          <text x={padL - 6} y={sy(t) + 4} textAnchor="end" fontSize="11" fill="#888">
            {Math.round(t)}
            {yUnit}
          </text>
        </g>
      ))}
      {/* etykiety osi X: pierwszy, środkowy, ostatni */}
      {[xMin, xMin + spanX / 2, xMax].map((x, i) => (
        <text key={i} x={sx(x)} y={height - 8} textAnchor="middle" fontSize="11" fill="#888">
          {fmtDate(x)}
        </text>
      ))}
      {series.map((s) => {
        const path = s.points
          .filter((p) => p.y !== null)
          .map((p, i) => `${i === 0 ? "M" : "L"} ${sx(p.x)} ${sy(p.y as number)}`)
          .join(" ");
        return (
          <g key={s.label}>
            <path d={path} fill="none" stroke={s.color} strokeWidth="2" />
            {s.points
              .filter((p) => p.y !== null)
              .map((p, i) => (
                <circle key={i} cx={sx(p.x)} cy={sy(p.y as number)} r="2.5" fill={s.color} />
              ))}
          </g>
        );
      })}
    </svg>
  );
}
