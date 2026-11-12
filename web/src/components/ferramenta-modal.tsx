"use client";

import { useId, useRef } from "react";
import type { Ficha } from "@/content/fichas";

const foco = "rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";
const subtitulo = "mt-8 font-mono text-xs uppercase tracking-wider text-muted-fg";

// O nome da tool abre a ficha técnica num <dialog> nativo, sem sair da página: o navegador cuida do foco, do
// Esc e do fundo. Clicar fora da caixa também fecha. Quem abre quer o técnico: parâmetros e retorno.
export function FerramentaModal({ f }: { f: Ficha }) {
  const ref = useRef<HTMLDialogElement>(null);
  const titulo = useId();

  return (
    <>
      <button
        type="button"
        onClick={() => ref.current?.showModal()}
        aria-haspopup="dialog"
        className={`${foco} break-words text-left font-mono text-sm text-honey underline decoration-dotted underline-offset-4 hover:decoration-solid`}
      >
        {f.tool}
      </button>
      <dialog
        ref={ref}
        aria-labelledby={titulo}
        onClick={(e) => {
          if (e.target === ref.current) ref.current.close();
        }}
        className="m-auto max-h-[85svh] w-[min(42rem,calc(100vw-2rem))] overflow-y-auto rounded-md border border-border bg-bg p-0 text-fg backdrop:bg-black/80"
      >
        <div className="p-6 md:p-8">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <h3 id={titulo} className="break-words font-mono text-lg font-medium text-honey">
                {f.tool}
              </h3>
              <p className="mt-1 text-muted-fg">
                {f.titulo}: {f.resumo}
              </p>
            </div>
            <button
              type="button"
              onClick={() => ref.current?.close()}
              aria-label="Fechar"
              className={`${foco} -m-2 shrink-0 p-2 text-muted-fg transition-colors hover:text-fg`}
            >
              <svg viewBox="0 0 24 24" aria-hidden="true" className="size-5 fill-none stroke-current stroke-2" strokeLinecap="round">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>

          <h4 className={subtitulo}>parâmetros</h4>
          {f.parametros.length > 0 ? (
            <dl className="mt-3 space-y-3 text-sm">
              {f.parametros.map((p) => (
                <div key={p.nome}>
                  <dt className="font-mono">
                    {p.nome}
                    {p.obrigatorio ? <span className="ml-2 text-xs text-honey">obrigatório</span> : null}
                  </dt>
                  <dd className="mt-0.5 text-muted-fg">{p.desc}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <p className="mt-3 text-sm text-muted-fg">nenhum</p>
          )}

          <h4 className={subtitulo}>retorna</h4>
          <dl className="mt-3 space-y-3 text-sm">
            {f.retorna.map((r) => (
              <div key={r.campo}>
                <dt className="break-words font-mono">{r.campo}</dt>
                <dd className="mt-0.5 text-muted-fg">{r.desc}</dd>
              </div>
            ))}
          </dl>

          {f.notas?.length ? (
            <>
              <h4 className={subtitulo}>observações</h4>
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-muted-fg marker:text-honey">
                {f.notas.map((n) => (
                  <li key={n}>{n}</li>
                ))}
              </ul>
            </>
          ) : null}
        </div>
      </dialog>
    </>
  );
}
