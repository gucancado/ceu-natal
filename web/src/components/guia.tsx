import { Alert, AlertDescription } from "@beeads/ui";
import { BlocoCodigo, TextoGuia } from "@/components/bloco-codigo";
import type { Cliente } from "@/content/clientes";

export const avisoConfianca =
  "Este guia foi verificado em novembro de 2026; a interface deste app muda com frequência.";

// Corpo comum ao painel da aba e à página do cliente.
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
      <ol className="list-decimal space-y-3 pl-6 marker:font-mono marker:text-honey">
        {c.passos.map((p) => (
          <li key={p} className="pl-1">
            <TextoGuia texto={p} />
          </li>
        ))}
      </ol>
      {c.snippet ? <BlocoCodigo codigo={c.snippet.codigo} /> : null}
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
