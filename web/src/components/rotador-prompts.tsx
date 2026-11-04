"use client";

import { useEffect, useState } from "react";
import { prompts } from "@/content/prompts";

const MS_POR_LETRA = 22;
const PAUSA_MS = 6500;
const FADE_MS = 600;

// Um pedido por vez: digita rápido, fica na tela, some com fade e o próximo começa.
// O primeiro já vem escrito do servidor. Leitores de tela recebem a lista inteira, estática.
export function RotadorPrompts() {
  const [i, setI] = useState(0);
  const [letras, setLetras] = useState(prompts[0].texto.length);
  const [visivel, setVisivel] = useState(true);

  const texto = prompts[i].texto;
  const digitando = letras < texto.length;

  useEffect(() => {
    const reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (digitando) {
      if (reduzido) {
        setLetras(texto.length);
        return;
      }
      const t = setTimeout(() => setLetras((n) => n + 1), MS_POR_LETRA);
      return () => clearTimeout(t);
    }
    let troca: ReturnType<typeof setTimeout> | undefined;
    const espera = setTimeout(() => {
      setVisivel(false);
      troca = setTimeout(
        () => {
          setI((n) => (n + 1) % prompts.length);
          setLetras(0);
          setVisivel(true);
        },
        reduzido ? 0 : FADE_MS,
      );
    }, PAUSA_MS);
    return () => {
      clearTimeout(espera);
      if (troca) clearTimeout(troca);
    };
  }, [digitando, texto]);

  return (
    <div>
      <ul className="sr-only">
        {prompts.map((x) => (
          <li key={x.texto}>{x.texto}</li>
        ))}
      </ul>
      <blockquote
        aria-hidden="true"
        className="min-h-[9rem] font-display text-2xl italic leading-[1.4] transition-opacity ease-out sm:min-h-[7.5rem] md:text-[30px]"
        style={{ transitionDuration: `${FADE_MS}ms`, opacity: visivel ? 1 : 0 }}
      >
        “{texto.slice(0, letras)}
        {digitando ? null : "”"}
        <span className="cursor-digitacao ml-0.5 inline-block h-[1em] w-[2px] translate-y-[0.15em] bg-honey" />
      </blockquote>
    </div>
  );
}
