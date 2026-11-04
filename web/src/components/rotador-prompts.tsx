"use client";

import { useEffect, useState } from "react";
import { prompts } from "@/content/prompts";

const INTERVALO_MS = 4200;
const FADE_MS = 700;

// Um pedido por vez, trocando com fade. Leitores de tela recebem a lista inteira, estática.
export function RotadorPrompts() {
  const [i, setI] = useState(0);
  const [visivel, setVisivel] = useState(true);

  useEffect(() => {
    let fade: ReturnType<typeof setTimeout> | undefined;
    const ciclo = setInterval(() => {
      setVisivel(false);
      fade = setTimeout(() => {
        setI((n) => (n + 1) % prompts.length);
        setVisivel(true);
      }, FADE_MS);
    }, INTERVALO_MS);
    return () => {
      clearInterval(ciclo);
      if (fade) clearTimeout(fade);
    };
  }, []);

  const p = prompts[i];
  return (
    <div className="rounded-md border border-border bg-card p-6 md:p-8">
      <p className="font-mono text-sm text-muted-fg">Com o Céu Natal conectado, peça:</p>
      <ul className="sr-only">
        {prompts.map((x) => (
          <li key={x.texto}>{x.texto}</li>
        ))}
      </ul>
      <div
        aria-hidden="true"
        className="mt-5 min-h-[9.5rem] transition-[opacity,transform] ease-out motion-reduce:transition-none sm:min-h-[8rem]"
        style={{
          transitionDuration: `${FADE_MS}ms`,
          opacity: visivel ? 1 : 0,
          transform: visivel ? "translateY(0)" : "translateY(4px)",
        }}
      >
        <blockquote className="font-display text-2xl italic leading-[1.4] md:text-[28px]">“{p.texto}”</blockquote>
        <p className="mt-4 font-mono text-sm text-honey">usa {p.tool}</p>
      </div>
      <div aria-hidden="true" className="mt-6 flex gap-1.5">
        {prompts.map((x, n) => (
          <span
            key={x.texto}
            className={`h-1 w-5 rounded-full transition-colors duration-700 ${n === i ? "bg-honey" : "bg-border"}`}
          />
        ))}
      </div>
    </div>
  );
}
