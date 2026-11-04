import { Copiar } from "@/components/copiar";

export function BlocoCodigo({ codigo }: { codigo: string }) {
  return (
    <div className="relative max-w-[48rem] rounded-md border border-border bg-muted">
      <pre className="overflow-x-auto p-4 pr-24 font-mono text-sm leading-[1.6]">
        <code>{codigo}</code>
      </pre>
      <div className="absolute right-2 top-2">
        <Copiar texto={codigo} />
      </div>
    </div>
  );
}

// Texto dos guias: `código` vira font-mono, **menu** vira peso médio. Nada mais é interpretado.
export function TextoGuia({ texto }: { texto: string }) {
  const partes = texto.split(/(`[^`]+`|\*\*[^*]+\*\*)/);
  return (
    <>
      {partes.map((p, i) => {
        if (p.startsWith("`") && p.endsWith("`") && p.length > 1)
          return (
            <code key={i} className="font-mono text-[0.9em] [overflow-wrap:anywhere]">
              {p.slice(1, -1)}
            </code>
          );
        if (p.startsWith("**") && p.endsWith("**") && p.length > 3)
          return (
            <strong key={i} className="font-medium">
              {p.slice(2, -2)}
            </strong>
          );
        return <span key={i}>{p}</span>;
      })}
    </>
  );
}
