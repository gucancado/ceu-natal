import Link from "next/link";
import { Secao } from "@/components/secao";
import { tecnicas } from "@/content/tecnicas";
import { tools } from "@/content/tools";

// Tool com página de técnica ganha o link "saiba mais"; o mapa natal aponta para o /mapa.
const paginaDa = new Map<string, { href: string; nome: string }>([
  ["calcular_mapa_natal", { href: "/mapa", nome: "mapa natal" }],
  ...tecnicas.map((t) => [t.tool, { href: `/${t.slug}`, nome: t.nome }] as const),
]);

export function Ferramentas() {
  return (
    <Secao id="ferramentas" titulo="ferramentas do mcp">
      <dl className="grid gap-x-12 gap-y-6 md:grid-cols-2">
        {tools.map((t) => {
          const pagina = paginaDa.get(t.nome);
          return (
            <div key={t.nome}>
              <dt className="break-words font-mono text-sm">{t.nome}</dt>
              <dd className="mt-1 text-muted-fg">
                {t.descricao}
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
    </Secao>
  );
}
