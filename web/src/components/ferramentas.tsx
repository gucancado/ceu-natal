import { FerramentaModal } from "@/components/ferramenta-modal";
import { Secao } from "@/components/secao";
import { fichaDa } from "@/content/fichas";
import { tools } from "@/content/tools";
import type { Idioma } from "@/lib/idioma";

// Em português, o nome de cada tool abre a ficha técnica num modal, sem sair da página. A ficha existe só
// em português: em inglês o nome fica como texto.
export function Ferramentas({ idioma = "pt" }: { idioma?: Idioma }) {
  const en = idioma === "en";
  return (
    <Secao id="ferramentas" titulo={en ? "mcp tools" : "ferramentas do mcp"}>
      <dl className="grid gap-x-12 gap-y-6 md:grid-cols-2">
        {tools.map((t) => {
          const ficha = en ? undefined : fichaDa(t.nome);
          return (
            <div key={t.nome}>
              <dt>
                {ficha ? <FerramentaModal f={ficha} /> : <span className="break-words font-mono text-sm">{t.nome}</span>}
              </dt>
              <dd className="mt-1 text-muted-fg">{en ? t.descricaoEn : t.descricao}</dd>
            </div>
          );
        })}
      </dl>
      {en ? (
        <p className="mt-10 max-w-[40rem] text-muted-fg">
          Tool names and results are in Portuguese. Your assistant reads them and answers in your language. Dates go in
          as DD/MM/YYYY and any city in the world works.
        </p>
      ) : null}
    </Secao>
  );
}
