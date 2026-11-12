import { buttonVariants } from "@/components/ui/button";
import type { Idioma } from "@/lib/idioma";

type Props = {
  texto: string;
  rotulo?: string;
  copiado?: string;
  variant?: "default" | "outline";
  size?: "sm" | "lg";
  /** id do elemento que mostra o texto; se a cópia falhar, ele fica selecionado para copiar à mão. */
  alvoId?: string;
  idioma?: Idioma;
};

const textos = {
  pt: {
    rotulo: "Copiar",
    copiado: "Copiado",
    selecione: "Selecione e copie",
    tente: "Não consegui copiar. Tente de novo",
    ok: "Copiado para a área de transferência.",
    falha: "Não foi possível copiar.",
  },
  en: {
    rotulo: "Copy",
    copiado: "Copied",
    selecione: "Select and copy",
    tente: "Couldn't copy. Try again",
    ok: "Copied to the clipboard.",
    falha: "Couldn't copy.",
  },
} as const;

// A cópia e a troca de rótulo ficam em lib/script-copiar.ts, para funcionar antes da hidratação.
export function Copiar({ texto, rotulo, copiado, variant = "outline", size = "sm", alvoId, idioma = "pt" }: Props) {
  const t = textos[idioma];
  return (
    <span className="contents">
      <button type="button" data-copiar={texto} data-alvo={alvoId} className={buttonVariants({ variant, size })}>
        <span className="copiar-rotulo">{rotulo ?? t.rotulo}</span>
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
          {copiado ?? t.copiado}
        </span>
        <span className="copiar-falha">{alvoId ? t.selecione : t.tente}</span>
      </button>
      <span className="sr-only" aria-live="polite">
        <span className="copiar-ok">{t.ok}</span>
        <span className="copiar-falha">{t.falha}</span>
      </span>
    </span>
  );
}
