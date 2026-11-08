import { Secao } from "@/components/secao";
import { tools } from "@/content/tools";
import { planeta } from "@/lib/glifos";

export function Ferramentas() {
  return (
    <Secao id="ferramentas" titulo="o que deixei aí dentro" simbolo={planeta.saturno}>
      <p className="mb-10 max-w-[36rem] text-lg text-muted-fg">nove ferramentas. você não precisa decorar nenhuma: a ia escolhe sozinha qual usar.</p>
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
