import { Alert, AlertDescription } from "@/components/ui/alert";
import { BlocoCodigo, TextoGuia } from "@/components/bloco-codigo";
import { buttonVariants } from "@/components/ui/button";
import type { Cliente } from "@/content/clientes";
import { verificadoEm } from "@/content/setup";

export const avisoConfianca = `Este guia foi verificado em ${verificadoEm}; a interface deste app muda com frequência.`;

// Versão curta, para o painel da home: só os passos, o link direto e o que copiar.
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

// Corpo completo, da página de cada cliente.
export function GuiaCorpo({ c, Titulo }: { c: Cliente; Titulo: "h2" | "h3" }) {
  return (
    <div className="max-w-[36rem] space-y-6">
      <p className="text-lg leading-[1.5]">{c.resumo}</p>
      <p className="text-muted-fg">{c.planoMinimo}</p>
      {c.confianca !== "alta" ? (
        <Alert role="note">
          <AlertDescription>{avisoConfianca}</AlertDescription>
        </Alert>
      ) : null}
      {c.abrir ? (
        <div className="space-y-3">
          <a href={c.abrir.url} target="_blank" rel="noopener" className={buttonVariants({ variant: "default", size: "lg" })}>
            {c.abrir.rotulo}
          </a>
          {c.snippet ? <BlocoCodigo codigo={c.snippet.codigo} /> : null}
        </div>
      ) : null}
      <ol className="list-decimal space-y-3 pl-6 marker:font-mono marker:text-honey">
        {c.passos.map((p) => (
          <li key={p} className="pl-1">
            <TextoGuia texto={p} />
          </li>
        ))}
      </ol>
      {c.snippet && !c.abrir ? <BlocoCodigo codigo={c.snippet.codigo} /> : null}
      {c.limitacoes.length > 0 ? (
        <div>
          <Titulo className="font-display text-xl font-medium">Bom saber</Titulo>
          <ul className="mt-3 list-disc space-y-2 pl-6 text-muted-fg">
            {c.limitacoes.map((l) => (
              <li key={l}>
                <TextoGuia texto={l} />
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
