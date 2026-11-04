import { Copiar } from "@/components/copiar";

// Texto longo para copiar e colar no assistente: quebra linha em vez de rolar.
export function CaixaPrompt({ texto, rotulo, alturaMax }: { texto: string; rotulo: string; alturaMax?: boolean }) {
  return (
    <div className="rounded-md border border-border bg-muted">
      <div className="flex items-center justify-between gap-4 border-b border-border px-4 py-2">
        <span className="font-mono text-sm text-muted-fg">{rotulo}</span>
        <Copiar texto={texto} />
      </div>
      <p
        tabIndex={alturaMax ? 0 : undefined}
        className={`whitespace-pre-wrap p-4 font-mono text-sm leading-[1.6] [overflow-wrap:anywhere] ${
          alturaMax ? "max-h-[28rem] overflow-y-auto" : ""
        }`}
      >
        {texto}
      </p>
    </div>
  );
}
