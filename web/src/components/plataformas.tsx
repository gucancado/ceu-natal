"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState, type MouseEvent } from "react";
import { GuiaCorpo } from "@/components/guia";
import { cliente, clientesDaGrade } from "@/content/clientes";
import { logos, type Logo } from "@/content/logos";

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
  const l = logos[logoDe[slug] ?? "claude"];
  // Marcação estática do próprio repositório (content/logo-manus.ts), sem dado de usuário.
  if ("svg" in l)
    return <svg viewBox="0 0 24 24" aria-hidden="true" className="size-7 shrink-0" dangerouslySetInnerHTML={{ __html: l.svg }} />;
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="size-7 shrink-0 fill-current">
      <path d={l.d} />
    </svg>
  );
}

// Cada cartão é um link para o guia completo; com JavaScript, abre o passo a passo aqui mesmo.
export function PlataformasGrade({ inicial }: { inicial: string | null }) {
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
                href={`/conectar/${c.slug}`}
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
              <GuiaCorpo c={atual} Titulo="h3" />
            </div>
            <Link href={`/conectar/${atual.slug}`} className="mt-8 inline-block text-honey underline underline-offset-4">
              guia completo
            </Link>
          </div>
        ) : null}
      </div>
    </div>
  );
}

// Lê ?cliente=<slug>; precisa de <Suspense> em volta (a página é estática).
export function Plataformas() {
  const slug = useSearchParams().get("cliente") ?? "";
  return <PlataformasGrade key={slug} inicial={cliente(slug)?.slug ?? null} />;
}
