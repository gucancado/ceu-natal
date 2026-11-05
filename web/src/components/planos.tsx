import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Secao } from "@/components/secao";
import { planoInclui, planos, rotuloPreco } from "@/content/planos";
import { planeta } from "@/lib/glifos";

// Linhas = união dos itens de inclusão, na ordem em que aparecem de Grátis a Profissional.
const linhas = [...new Set(planos.flatMap((p) => p.inclui))];

export function Planos() {
  return (
    <Secao id="planos" titulo="o que vem por aí" simbolo={planeta.netuno}>
      {/* relative: os sr-only (position absolute) da tabela ficam presos ao invólucro e não alargam a página */}
      <div
        className="relative overflow-x-auto"
        tabIndex={0}
        role="region"
        aria-label="Comparação de planos"
      >
        <table className="tabular w-full min-w-[44rem] border-collapse text-left">
          <caption className="sr-only">O que cada plano inclui</caption>
          <thead>
            <tr className="border-b border-border align-bottom">
              <th scope="col" className="w-[40%] py-4 pr-6">
                <span className="sr-only">Item</span>
              </th>
              {planos.map((p) => (
                <th key={p.id} scope="col" className="px-4 py-4 font-normal">
                  <span className="flex flex-wrap items-center gap-2 font-display text-xl font-medium">
                    {p.nome}
                    {!p.disponivel ? (
                      <Badge>
                        Em breve
                      </Badge>
                    ) : null}
                  </span>
                  <span className="mt-1 block text-sm text-muted-fg">{p.paraQuem}</span>
                  {p.disponivel || p.preco ? (
                    <span className="mt-2 block font-mono text-sm">{rotuloPreco(p)}</span>
                  ) : null}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {linhas.map((item) => (
              <tr key={item} className="border-b border-border">
                <th scope="row" className="py-3 pr-6 font-normal">
                  {item}
                </th>
                {planos.map((p) => (
                  <td key={p.id} className="px-4 py-3">
                    {planoInclui(p, item) ? (
                      <>
                        <span aria-hidden="true" className="text-honey">
                          ✓
                        </span>
                        <span className="sr-only">incluído</span>
                      </>
                    ) : (
                      <span className="sr-only">não incluído</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-8 max-w-[36rem] text-muted-fg">
        por enquanto é tudo grátis. quando os planos com conta chegarem, eu conto aqui primeiro.
      </p>
      <div className="mt-6">
        <a href="#conectar" className={buttonVariants({ size: "lg" })}>
          Conectar agora
        </a>
      </div>
    </Secao>
  );
}
