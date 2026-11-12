"use client";

import { useId, useRef } from "react";
import { CaixaPrompt } from "@/components/caixa-prompt";
import type { Tecnica } from "@/content/tecnicas";

const foco = "rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

// O nome da tool abre o detalhe num <dialog> nativo, sem sair da página: o navegador cuida do foco, do Esc
// e do fundo. Clicar fora da caixa também fecha.
export function FerramentaModal({ t }: { t: Tecnica }) {
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
        {t.tool}
      </button>
      <dialog
        ref={ref}
        aria-labelledby={titulo}
        onClick={(e) => {
          if (e.target === ref.current) ref.current.close();
        }}
        className="m-auto max-h-[85svh] w-[min(40rem,calc(100vw-2rem))] overflow-y-auto rounded-md border border-border bg-bg p-0 text-fg backdrop:bg-black/80"
      >
        <div className="p-6 md:p-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 id={titulo} className="font-display text-2xl font-medium">
                {t.nome}
              </h3>
              <p className="mt-1 break-words font-mono text-sm text-muted-fg">{t.tool}</p>
            </div>
            <button
              type="button"
              onClick={() => ref.current?.close()}
              aria-label="Fechar"
              className={`${foco} -m-2 p-2 text-muted-fg transition-colors hover:text-fg`}
            >
              <svg viewBox="0 0 24 24" aria-hidden="true" className="size-5 fill-none stroke-current stroke-2" strokeLinecap="round">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>
          <p className="mt-6 text-muted-fg">{t.intro}</p>
          <h4 className="mt-8 font-display text-lg font-medium italic">o que é calculado</h4>
          <ul className="mt-3 list-disc space-y-1 pl-6 marker:text-honey">
            {t.calcula.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
          <h4 className="mt-8 font-display text-lg font-medium italic">o que você precisa</h4>
          <ul className="mt-3 list-disc space-y-1 pl-6 marker:text-honey">
            {t.precisa.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
          <h4 className="mt-8 font-display text-lg font-medium italic">exemplo de pedido</h4>
          <div className="mt-3">
            <CaixaPrompt texto={t.pedidos[0]} rotulo="pedido" />
          </div>
        </div>
      </dialog>
    </>
  );
}
