import { Secao } from "@/components/secao";
import { tools } from "@/content/tools";

export function Ferramentas() {
  return (
    <Secao id="ferramentas" titulo="Nove ferramentas">
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
