"use client";

import { useEffect, useState } from "react";
import { prompts } from "@/content/prompts";

const MS_POR_LETRA = 22;
const PAUSA_MS = 6500;
const FADE_MS = 600;

// Um pedido por vez: digita rápido, fica na tela, some com fade e o próximo começa.
// O primeiro já vem escrito do servidor. Leitores de tela recebem a lista inteira, estática.
// Com "reduzir movimento" o primeiro pedido fica parado; o mouse em cima pausa.
export function RotadorPrompts() {
  const [i, setI] = useState(0);
  const [letras, setLetras] = useState(prompts[0].texto.length);
  const [visivel, setVisivel] = useState(true);
  const [reduzido, setReduzido] = useState(false);
  const [emCima, setEmCima] = useState(false);

  const texto = prompts[i].texto;
  const digitando = letras < texto.length;
  const parado = reduzido || emCima;

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const aplicar = () => {
      setReduzido(mq.matches);
      if (mq.matches) {
        setI(0);
        setLetras(prompts[0].texto.length);
        setVisivel(true);
      }
    };
    aplicar();
    mq.addEventListener("change", aplicar);
    return () => mq.removeEventListener("change", aplicar);
  }, []);

  useEffect(() => {
    if (parado) return;
    if (digitando) {
      const t = setTimeout(() => setLetras((n) => n + 1), MS_POR_LETRA);
      return () => clearTimeout(t);
    }
    let troca: ReturnType<typeof setTimeout> | undefined;
    const espera = setTimeout(() => {
      setVisivel(false);
      troca = setTimeout(() => {
        setI((n) => (n + 1) % prompts.length);
        setLetras(0);
        setVisivel(true);
      }, FADE_MS);
    }, PAUSA_MS);
    return () => {
      clearTimeout(espera);
      if (troca) clearTimeout(troca);
      // Pausou no meio do fade: o texto volta a aparecer.
      setVisivel(true);
    };
  }, [letras, digitando, parado]);

  return (
    <div onMouseEnter={() => setEmCima(true)} onMouseLeave={() => setEmCima(false)}>
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
        {parado ? null : (
          <span className="cursor-digitacao ml-0.5 inline-block h-[1em] w-[2px] translate-y-[0.15em] bg-honey" />
        )}
      </blockquote>
    </div>
  );
}
