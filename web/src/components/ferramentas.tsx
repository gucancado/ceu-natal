import Link from "next/link";
import { Secao } from "@/components/secao";
import { tecnicas } from "@/content/tecnicas";
import { tools } from "@/content/tools";
import type { Idioma } from "@/lib/idioma";

// Tool com página de técnica ganha o link "saiba mais"; o mapa natal aponta para o /mapa.
// As páginas de técnica só existem em português: em inglês o link não aparece.
const paginaDa = new Map<string, { href: string; nome: string }>([
  ["calcular_mapa_natal", { href: "/mapa", nome: "mapa natal" }],
  ...tecnicas.map((t) => [t.tool, { href: `/${t.slug}`, nome: t.nome }] as const),
]);

export function Ferramentas({ idioma = "pt" }: { idioma?: Idioma }) {
  const en = idioma === "en";
  return (
    <Secao id="ferramentas" titulo={en ? "mcp tools" : "ferramentas do mcp"}>
      <dl className="grid gap-x-12 gap-y-6 md:grid-cols-2">
        {tools.map((t) => {
          const pagina = en ? undefined : paginaDa.get(t.nome);
          return (
            <div key={t.nome}>
              <dt className="break-words font-mono text-sm">{t.nome}</dt>
              <dd className="mt-1 text-muted-fg">
                {en ? t.descricaoEn : t.descricao}
                {pagina ? (
                  <>
                    {" "}
                    <Link href={pagina.href} className="text-honey underline underline-offset-4">
                      sobre {pagina.nome}
                    </Link>
                  </>
                ) : null}
              </dd>
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
