import { BlocoCodigo, TextoGuia } from "@/components/bloco-codigo";
import { buttonVariants } from "@/components/ui/button";
import type { Cliente } from "@/content/clientes";

// Guia de conexão do painel "como conectar": os passos, o que copiar e o link direto.
export function GuiaPassos({ c }: { c: Cliente }) {
  return (
    <div className="max-w-[36rem] space-y-6">
      <ol className="list-decimal space-y-3 pl-6 marker:font-mono marker:text-honey">
        {c.passos.map((p) => (
          <li key={p} className="pl-1">
            <TextoGuia texto={p} />
          </li>
        ))}
      </ol>
      {c.snippet ? <BlocoCodigo codigo={c.snippet.codigo} /> : null}
      {c.abrir ? (
        <a href={c.abrir.url} target="_blank" rel="noopener" className={buttonVariants({ variant: "default", size: "lg" })}>
          {c.abrir.rotulo}
        </a>
      ) : null}
    </div>
  );
}
