import { Secao } from "@/components/secao";
import { tools } from "@/content/tools";
import { planeta } from "@/lib/glifos";

export function Ferramentas() {
  return (
    <Secao id="ferramentas" titulo="ferramentas do mcp" simbolo={planeta.saturno}>
      <dl className="grid gap-x-12 gap-y-6 md:grid-cols-2">
        {tools.map((t) => (
          <div key={t.nome}>
            <dt className="break-words font-mono text-sm">{t.nome}</dt>
            <dd className="mt-1 text-muted-fg">{t.descricao}</dd>
          </div>
        ))}
      </dl>
    </Secao>
  );
}
