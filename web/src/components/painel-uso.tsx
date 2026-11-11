import type { Contagem, Estatisticas } from "@/lib/estatisticas";
import { formatarInteiro, nomePais } from "@/lib/estatisticas";

function Numero({ valor, rotulo, nota }: { valor: string; rotulo: string; nota?: string }) {
  return (
    <div className="border border-border bg-card p-5">
      <p className="font-display text-3xl tabular-nums md:text-4xl">{valor}</p>
      <p className="mt-2 text-sm text-muted-fg">{rotulo}</p>
      {nota ? <p className="mt-1 text-xs text-muted-fg/70">{nota}</p> : null}
    </div>
  );
}

function Barras({ titulo, itens, formatar = (r: string) => r }: {
  titulo: string;
  itens: Contagem[];
  formatar?: (rotulo: string) => string;
}) {
  if (itens.length === 0) return null;
  const maior = Math.max(...itens.map((i) => i.chamadas), 1);
  return (
    <div className="border border-border bg-card p-5">
      <h3 className="text-sm text-muted-fg">{titulo}</h3>
      <ul className="mt-4 space-y-3">
        {itens.slice(0, 10).map((i) => (
          <li key={i.rotulo}>
            <div className="flex items-baseline justify-between gap-4 text-sm">
              <span className="[overflow-wrap:anywhere]">{formatar(i.rotulo)}</span>
              <span className="tabular-nums text-muted-fg">{formatarInteiro(i.chamadas)}</span>
            </div>
            <div className="mt-1 h-1.5 bg-muted" aria-hidden="true">
              <div className="h-full bg-honey" style={{ width: `${(i.chamadas / maior) * 100}%` }} />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function SerieDiaria({ dias }: { dias: Estatisticas["porDia"] }) {
  const maior = Math.max(...dias.map((d) => d.calculos), 1);
  const total = dias.reduce((s, d) => s + d.calculos, 0);
  return (
    <div className="border border-border bg-card p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-sm text-muted-fg">cálculos por dia, últimos 30 dias</h3>
        <span className="text-sm tabular-nums text-muted-fg">{formatarInteiro(total)} no período</span>
      </div>
      <div className="mt-5 flex h-40 items-end gap-[2px]" role="img" aria-label={`${total} cálculos nos últimos 30 dias`}>
        {dias.map((d) => (
          <div
            key={d.dia}
            className="flex-1 bg-honey/80 hover:bg-honey"
            style={{ height: `${Math.max((d.calculos / maior) * 100, d.calculos ? 3 : 0.5)}%` }}
            title={`${d.dia.split("-").reverse().join("/")}: ${d.calculos} cálculos, ${d.pessoasSite} pessoas no site, ${d.sessoesMcp} conversas na ia`}
          />
        ))}
      </div>
      <div className="mt-2 flex justify-between text-xs text-muted-fg">
        <span>{dias[0]?.dia.split("-").reverse().slice(0, 2).join("/")}</span>
        <span>hoje</span>
      </div>
    </div>
  );
}

export function PainelUso({ e }: { e: Estatisticas }) {
  const hoje = e.porDia[e.porDia.length - 1];
  const t = e.totais;
  const origem: Contagem[] = [
    { rotulo: "dentro da ia (mcp)", chamadas: e.porOrigem.mcp },
    { rotulo: "formulário do site", chamadas: e.porOrigem.site },
  ].filter((o) => o.chamadas > 0);
  return (
    <section aria-labelledby="uso-titulo" className="mt-16">
      <h2 id="uso-titulo" className="font-display text-3xl font-medium">Uso</h2>
      <p className="mt-2 text-sm text-muted-fg">
        {e.desde ? `contando desde ${e.desde.split("-").reverse().join("/")}. ` : ""}
        só números agregados: nenhum dado de nascimento, nome ou cidade aparece aqui.
      </p>

      <div className="mt-8 grid grid-cols-2 gap-3 md:grid-cols-4">
        <Numero valor={formatarInteiro(t.calculos)} rotulo="cálculos feitos" />
        <Numero valor={formatarInteiro(t.sessoesMcp)} rotulo="conversas na ia" nota="sessões mcp únicas por dia" />
        <Numero valor={formatarInteiro(t.pessoasDiaSite)} rotulo="pessoas no site" nota="únicas por dia, somadas" />
        <Numero valor={formatarInteiro(t.cidades)} rotulo={`cidades em ${formatarInteiro(t.paises)} países`} />
        <Numero valor={formatarInteiro(hoje?.calculos ?? 0)} rotulo="cálculos hoje" />
        <Numero
          valor={formatarInteiro((hoje?.sessoesMcp ?? 0) + (hoje?.pessoasSite ?? 0))}
          rotulo="pessoas e conversas hoje"
        />
        <Numero valor={`${formatarInteiro(Math.round(t.tempoMedioMs))} ms`} rotulo="tempo médio por chamada" />
        <Numero
          valor={`${(t.taxaErro * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%`}
          rotulo="chamadas com erro"
          nota="inclui data inválida e cidade não encontrada"
        />
      </div>

      <div className="mt-3">
        <SerieDiaria dias={e.porDia} />
      </div>

      <div className="mt-3 grid gap-3 md:grid-cols-2">
        <Barras titulo="ferramentas" itens={e.porFerramenta} />
        <Barras titulo="apps de ia" itens={e.porApp} />
        <Barras titulo="países de nascimento" itens={e.paises} formatar={nomePais} />
        <Barras titulo="por onde" itens={origem} />
      </div>
    </section>
  );
}
