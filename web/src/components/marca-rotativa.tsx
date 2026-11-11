"use client";

import { useEffect, useState } from "react";
import { LogoMarca } from "@/components/logo-marca";
import { logos, type Logo } from "@/content/logos";

// Cores oficiais das marcas, em versão para fundo escuro: o laranja do Claude, o degradê azul-roxo-rosa
// do Gemini, e branco no ChatGPT e no Manus, cujos logos oficiais são monocromáticos.
const marcas: { nome: string; logo: Logo; cor: string; degrade?: string }[] = [
  { nome: "claude", logo: "claude", cor: "#D97757" },
  { nome: "chatgpt", logo: "openai", cor: "#FFFFFF" },
  { nome: "gemini", logo: "gemini", cor: "#9177C7", degrade: "linear-gradient(90deg, #4796E3, #9177C7, #CA6673)" },
  { nome: "manus", logo: "manus", cor: "#FFFFFF" },
];

const TROCA_MS = 2600;

// Troca a marca com fade. Leitores de tela leem a lista inteira, parada.
export function MarcaRotativa() {
  const [i, setI] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setI((n) => (n + 1) % marcas.length), TROCA_MS);
    return () => clearInterval(t);
  }, []);

  return (
    <>
      <span className="sr-only">{marcas.map((m) => m.nome).join(", ").replace(/, ([^,]*)$/, " ou $1")}</span>
      <span aria-hidden="true" className="relative block h-[1.3em]">
        {marcas.map((m, n) => (
          <span
            key={m.nome}
            style={{ color: m.cor }}
            className={`absolute inset-0 flex items-center gap-[0.35em] transition-all duration-700 ease-out ${
              n === i ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0"
            }`}
          >
            {m.degrade ? <LogoGemini /> : <LogoMarca logo={m.logo} className="size-[0.85em]" />}
            <span
              style={m.degrade ? { backgroundImage: m.degrade, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" } : undefined}
            >
              {m.nome}
            </span>
          </span>
        ))}
      </span>
    </>
  );
}

// Estrela do Gemini pintada com o degradê oficial.
function LogoGemini() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="size-[0.85em] shrink-0">
      <defs>
        <linearGradient id="marca-degrade-gemini" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#4796E3" />
          <stop offset="0.5" stopColor="#9177C7" />
          <stop offset="1" stopColor="#CA6673" />
        </linearGradient>
      </defs>
      <path d={logos.gemini.d} fill="url(#marca-degrade-gemini)" />
    </svg>
  );
}
