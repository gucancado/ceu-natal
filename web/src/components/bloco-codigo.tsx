import { Copiar } from "@/components/copiar";
import { partesTextoGuia } from "@/lib/texto-guia";

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
  return (
    <>
      {partesTextoGuia(texto).map((p, i) => {
        if (p.tipo === "codigo")
          return (
            <code key={i} className="font-mono text-[0.9em] [overflow-wrap:anywhere]">
              {p.texto}
            </code>
          );
        if (p.tipo === "menu")
          return (
            <strong key={i} className="font-medium">
              {p.texto}
            </strong>
          );
        return <span key={i}>{p.texto}</span>;
      })}
    </>
  );
}
