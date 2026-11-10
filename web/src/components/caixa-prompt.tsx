import { useId } from "react";
import { Copiar } from "@/components/copiar";

// Texto longo para copiar e colar no assistente: quebra linha em vez de rolar.
export function CaixaPrompt({ texto, rotulo, alturaMax }: { texto: string; rotulo: string; alturaMax?: boolean }) {
  const id = useId();
  return (
    <div className="rounded-md border border-border bg-muted">
      <div className="flex items-center justify-between gap-4 px-4 py-2">
        <span className="font-mono text-sm text-muted-fg">{rotulo}</span>
        <Copiar texto={texto} alvoId={id} />
      </div>
      <p
        id={id}
        tabIndex={alturaMax ? 0 : undefined}
        className={`texto-literal whitespace-pre-wrap p-4 font-mono text-sm leading-[1.6] [overflow-wrap:anywhere] ${
          alturaMax ? "max-h-[28rem] overflow-y-auto" : ""
        }`}
      >
        {texto}
      </p>
    </div>
  );
}
