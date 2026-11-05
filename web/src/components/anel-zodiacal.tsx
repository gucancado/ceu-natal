import { signos } from "@/lib/glifos";

// Decorativo: os doze signos num anel que gira devagar.
export function AnelZodiacal({ className = "" }: { className?: string }) {
  const r = 44;
  return (
    <svg viewBox="0 0 100 100" aria-hidden="true" className={`anel-zodiacal pointer-events-none ${className}`}>
      <circle cx="50" cy="50" r="49" fill="none" stroke="currentColor" strokeWidth="0.15" />
      <circle cx="50" cy="50" r="39" fill="none" stroke="currentColor" strokeWidth="0.15" />
      {signos.map((s, n) => {
        const a = ((n * 30 - 90) * Math.PI) / 180;
        const x = 50 + r * Math.cos(a);
        const y = 50 + r * Math.sin(a);
        const b = (((n * 30 + 15) - 90) * Math.PI) / 180;
        return (
          <g key={s}>
            <line
              x1={50 + 39 * Math.cos(b)}
              y1={50 + 39 * Math.sin(b)}
              x2={50 + 49 * Math.cos(b)}
              y2={50 + 49 * Math.sin(b)}
              stroke="currentColor"
              strokeWidth="0.15"
            />
            <text x={x} y={y} textAnchor="middle" dominantBaseline="central" fontSize="5" fill="currentColor" className="glifo">
              {s}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
