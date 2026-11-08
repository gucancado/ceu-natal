import { buttonVariants } from "@/components/ui/button";

type Props = {
  texto: string;
  rotulo?: string;
  copiado?: string;
  variant?: "default" | "outline";
  size?: "sm" | "lg";
  /** id do elemento que mostra o texto; se a cópia falhar, ele fica selecionado para copiar à mão. */
  alvoId?: string;
};

// A cópia e a troca de rótulo ficam em lib/script-copiar.ts, para funcionar antes da hidratação.
export function Copiar({
  texto,
  rotulo = "Copiar",
  copiado = "Copiado",
  variant = "outline",
  size = "sm",
  alvoId,
}: Props) {
  return (
    <span className="contents">
      <button type="button" data-copiar={texto} data-alvo={alvoId} className={buttonVariants({ variant, size })}>
        <span className="copiar-rotulo">{rotulo}</span>
        <span className="copiar-ok items-center gap-2">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
            className="size-4 shrink-0 fill-none stroke-current stroke-[3]"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M5 13l4 4L19 7" />
          </svg>
          {copiado}
        </span>
        <span className="copiar-falha">{alvoId ? "Selecione e copie" : "Não consegui copiar. Tente de novo"}</span>
      </button>
      <span className="sr-only" aria-live="polite">
        <span className="copiar-ok">Copiado para a área de transferência.</span>
        <span className="copiar-falha">Não foi possível copiar.</span>
      </span>
    </span>
  );
}
