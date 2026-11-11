"use client";

import { useEffect, useState } from "react";
import { LogoMarca } from "@/components/logo-marca";
import type { Logo } from "@/content/logos";

const marcas: { nome: string; logo: Logo }[] = [
  { nome: "claude", logo: "claude" },
  { nome: "chatgpt", logo: "openai" },
  { nome: "gemini", logo: "gemini" },
  { nome: "manus", logo: "manus" },
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
            className={`absolute inset-0 flex items-center gap-[0.35em] text-honey transition-all duration-700 ease-out ${
              n === i ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0"
            }`}
          >
            <LogoMarca logo={m.logo} className="size-[0.85em]" />
            {m.nome}
          </span>
        ))}
      </span>
    </>
  );
}
