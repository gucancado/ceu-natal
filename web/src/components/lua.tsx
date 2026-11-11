// Lua cheia desenhada em SVG: disco com luz de um lado, mares escuros desfocados, crateras com raios
// (Tycho e Copérnico), textura de ruído e borda escurecida. Só decoração; a travessia fica em globals.css (.lua).
export function Lua({ className = "" }: { className?: string }) {
  return (
    <div aria-hidden="true" className={`lua ${className}`}>
      <svg viewBox="0 0 200 200" className="size-full">
        <defs>
          <radialGradient id="lua-luz" cx="42%" cy="38%" r="65%">
            <stop offset="0" stopColor="#fbf9f1" />
            <stop offset="0.55" stopColor="#e8e3d4" />
            <stop offset="0.85" stopColor="#cdc6b3" />
            <stop offset="1" stopColor="#a39b88" />
          </radialGradient>
          <radialGradient id="lua-borda" cx="50%" cy="50%" r="50%">
            <stop offset="0.7" stopColor="#000" stopOpacity="0" />
            <stop offset="1" stopColor="#1a1712" stopOpacity="0.45" />
          </radialGradient>
          <radialGradient id="lua-raio" cx="50%" cy="50%" r="50%">
            <stop offset="0" stopColor="#fffdf6" stopOpacity="0.9" />
            <stop offset="1" stopColor="#fffdf6" stopOpacity="0" />
          </radialGradient>
          <filter id="lua-mar" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3.2" />
          </filter>
          <filter id="lua-textura">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="7" />
            <feColorMatrix values="0 0 0 0 0.35  0 0 0 0 0.33  0 0 0 0 0.3  0 0 0 0.55 -0.12" />
          </filter>
          <clipPath id="lua-disco">
            <circle cx="100" cy="100" r="96" />
          </clipPath>
        </defs>
        <g clipPath="url(#lua-disco)">
          <circle cx="100" cy="100" r="96" fill="url(#lua-luz)" />
          {/* Mares (as manchas escuras que se veem a olho nu). */}
          <g fill="#7f786a" opacity="0.5" filter="url(#lua-mar)">
            <ellipse cx="62" cy="88" rx="30" ry="44" transform="rotate(12 62 88)" />
            <ellipse cx="88" cy="58" rx="24" ry="19" />
            <ellipse cx="118" cy="66" rx="15" ry="14" />
            <ellipse cx="132" cy="94" rx="20" ry="16" />
            <ellipse cx="152" cy="74" rx="9" ry="10" />
            <ellipse cx="124" cy="122" rx="13" ry="10" />
            <ellipse cx="80" cy="128" rx="16" ry="11" />
          </g>
          <g fill="#6f685b" opacity="0.35" filter="url(#lua-mar)">
            <ellipse cx="70" cy="80" rx="14" ry="20" />
            <ellipse cx="128" cy="92" rx="9" ry="7" />
          </g>
          {/* Crateras: fundo escuro e borda clara. */}
          <g>
            <circle cx="96" cy="166" r="5" fill="#d9d3c3" stroke="#fffaf0" strokeWidth="1.2" />
            <circle cx="96" cy="166" r="22" fill="url(#lua-raio)" opacity="0.5" />
            <circle cx="84" cy="98" r="3.5" fill="#d6cfbe" stroke="#f8f3e6" strokeWidth="1" />
            <circle cx="84" cy="98" r="12" fill="url(#lua-raio)" opacity="0.35" />
            <circle cx="46" cy="96" r="2.5" fill="#efe9da" />
            <circle cx="150" cy="140" r="4" fill="#bfb8a6" stroke="#ece6d6" strokeWidth="0.8" />
            <circle cx="60" cy="150" r="3" fill="#c3bcaa" stroke="#ebe5d5" strokeWidth="0.7" />
            <circle cx="140" cy="44" r="2.6" fill="#c7c0ae" stroke="#eee8d9" strokeWidth="0.6" />
            <circle cx="112" cy="150" r="2.2" fill="#c5bead" />
            <circle cx="40" cy="128" r="2" fill="#c8c1af" />
          </g>
          <rect width="200" height="200" filter="url(#lua-textura)" opacity="0.6" />
          <circle cx="100" cy="100" r="96" fill="url(#lua-borda)" />
        </g>
      </svg>
    </div>
  );
}
