"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState, type MouseEvent } from "react";
import { GuiaPassos } from "@/components/guia";
import { cliente, clientesDaGrade } from "@/content/clientes";
import { LogoMarca } from "@/components/logo-marca";
import type { Logo } from "@/content/logos";
import { homeDo, type Idioma } from "@/lib/idioma";

const logoDe: Record<string, Logo> = {
  "claude-ai": "claude",
  "claude-desktop": "claude",
  "claude-code": "claude",
  chatgpt: "openai",
  gemini: "gemini",
  manus: "manus",
  cursor: "cursor",
  n8n: "n8n",
};

function IconeLogo({ slug }: { slug: string }) {
  return <LogoMarca logo={logoDe[slug] ?? "claude"} />;
}

// Cada cartão abre o passo a passo aqui mesmo; sem JavaScript, o link recarrega a home com ?cliente=.
export function PlataformasGrade({ inicial, idioma = "pt" }: { inicial: string | null; idioma?: Idioma }) {
  const [aberto, setAberto] = useState<string | null>(inicial);
  const atual = aberto ? cliente(aberto) : undefined;
  const titulo = useRef<HTMLHeadingElement>(null);
  // Só leva o foco quando a pessoa abriu um guia; o aberto pela URL (?cliente=) não rouba o foco.
  const abriuAgora = useRef(false);

  useEffect(() => {
    if (aberto && abriuAgora.current) titulo.current?.focus();
    abriuAgora.current = false;
  }, [aberto]);

  function alternar(e: MouseEvent<HTMLAnchorElement>, slug: string) {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
    e.preventDefault();
    abriuAgora.current = aberto !== slug;
    setAberto((s) => (s === slug ? null : slug));
  }

  return (
    <div>
      <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {clientesDaGrade.map((c) => {
          const ativo = c.slug === aberto;
          return (
            <li key={c.slug}>
              <a
                href={`${homeDo[idioma]}?cliente=${c.slug}#conectar`}
                onClick={(e) => alternar(e, c.slug)}
                aria-expanded={ativo}
                aria-controls="passo-a-passo"
                className={`flex h-full items-center gap-3 rounded-md p-4 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                  ativo ? "bg-card text-honey" : "text-fg hover:bg-card"
                }`}
              >
                <IconeLogo slug={c.slug} />
                <span className="font-display text-lg font-medium leading-tight">{c.nome}</span>
              </a>
            </li>
          );
        })}
      </ul>
      <div id="passo-a-passo" className={atual ? "mt-10" : undefined}>
        {atual ? (
          <div className="rounded-md bg-card p-6 md:p-8">
            <h3 ref={titulo} tabIndex={-1} className="flex items-center gap-3 font-display text-2xl font-medium focus:outline-none">
              <IconeLogo slug={atual.slug} />
              {atual.nome}
            </h3>
            <div className="mt-6">
              <GuiaPassos c={atual} idioma={idioma} />
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

// Lê ?cliente=<slug>; precisa de <Suspense> em volta (a página é estática).
export function Plataformas({ idioma = "pt" }: { idioma?: Idioma }) {
  const slug = useSearchParams().get("cliente") ?? "";
  return <PlataformasGrade key={slug} inicial={cliente(slug)?.slug ?? null} idioma={idioma} />;
}
