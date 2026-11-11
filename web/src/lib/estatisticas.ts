// Lê o /estatisticas do servidor MCP para o painel da página /status.
// O servidor só publica agregados: nada de cidades, nomes ou contatos.
export type Contagem = { rotulo: string; chamadas: number };

export type Estatisticas = {
  desde: string | null;
  atualizadoEm: string;
  totais: {
    chamadas: number;
    calculos: number;
    taxaErro: number;
    tempoMedioMs: number;
    cidades: number;
    paises: number;
    pessoasDiaSite: number;
    sessoesMcp: number;
  };
  porDia: { dia: string; calculos: number; pessoasSite: number; sessoesMcp: number }[];
  porOrigem: { mcp: number; site: number };
  porFerramenta: Contagem[];
  porApp: Contagem[];
  paises: Contagem[];
};

const num = (v: unknown): number => (typeof v === "number" && Number.isFinite(v) ? v : 0);

function contagens(lista: unknown, chave: string): Contagem[] {
  if (!Array.isArray(lista)) return [];
  return lista
    .filter((x): x is Record<string, unknown> => typeof x === "object" && x !== null)
    .map((x) => ({ rotulo: String(x[chave] ?? ""), chamadas: num(x.chamadas) }))
    .filter((x) => x.rotulo);
}

export function interpretarEstatisticas(j: unknown): Estatisticas | null {
  if (typeof j !== "object" || j === null) return null;
  const o = j as Record<string, unknown>;
  const t = o.totais as Record<string, unknown> | undefined;
  if (!t || !Array.isArray(o.por_dia)) return null;
  const origem = (o.por_origem ?? {}) as Record<string, unknown>;
  return {
    desde: typeof o.desde === "string" ? o.desde : null,
    atualizadoEm: typeof o.atualizado_em === "string" ? o.atualizado_em : "",
    totais: {
      chamadas: num(t.chamadas),
      calculos: num(t.calculos),
      taxaErro: num(t.taxa_erro),
      tempoMedioMs: num(t.tempo_medio_ms),
      cidades: num(t.cidades),
      paises: num(t.paises),
      pessoasDiaSite: num(t.pessoas_dia_site),
      sessoesMcp: num(t.sessoes_mcp),
    },
    porDia: (o.por_dia as Record<string, unknown>[]).map((d) => ({
      dia: String(d.dia ?? ""),
      calculos: num(d.calculos),
      pessoasSite: num(d.pessoas_site),
      sessoesMcp: num(d.sessoes_mcp),
    })),
    porOrigem: { mcp: num(origem.mcp), site: num(origem.site) },
    porFerramenta: contagens(o.por_ferramenta, "ferramenta"),
    porApp: contagens(o.por_app, "app"),
    paises: contagens(o.paises, "pais"),
  };
}

export async function lerEstatisticas(
  mcpUrl: string,
  fetchImpl: typeof fetch = fetch,
): Promise<Estatisticas | null> {
  try {
    const r = await fetchImpl(`${mcpUrl}/estatisticas`, {
      signal: AbortSignal.timeout(5000),
      next: { revalidate: 60 },
    } as RequestInit);
    if (!r.ok) return null;
    return interpretarEstatisticas(await r.json());
  } catch {
    return null;
  }
}

const regioes = new Intl.DisplayNames(["pt-BR"], { type: "region" });

// "BR" → "Brasil"; "outros" fica como está.
export function nomePais(codigo: string): string {
  if (!/^[A-Z]{2}$/.test(codigo)) return codigo;
  try {
    return regioes.of(codigo) ?? codigo;
  } catch {
    return codigo;
  }
}

const inteiro = new Intl.NumberFormat("pt-BR");
export const formatarInteiro = (n: number) => inteiro.format(n);
