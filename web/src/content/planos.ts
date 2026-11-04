// Planos do produto (spec, seção 4.1). Só o grátis está disponível; nenhum preço publicado.
export type Plano = {
  id: "gratis" | "pessoal" | "profissional";
  nome: string;
  paraQuem: string;
  inclui: string[];
  disponivel: boolean;
  /** Plano cujos itens este também inclui (ex.: Profissional herda tudo do Pessoal). */
  herdaDe?: Plano["id"];
  preco?: { mensal: number; anual: number };
};

const brl = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export function rotuloPreco(p: Plano): string {
  if (p.id === "gratis") return "Grátis";
  if (!p.preco) return "Em breve";
  return `${brl.format(p.preco.mensal)}/mês ou ${brl.format(p.preco.anual)}/ano`;
}

/** O plano inclui o item, diretamente ou pela cadeia de herdaDe. */
export function planoInclui(plano: Plano, item: string, todos: Plano[] = planos): boolean {
  if (plano.inclui.includes(item)) return true;
  const pai = plano.herdaDe ? todos.find((p) => p.id === plano.herdaDe) : undefined;
  return pai ? planoInclui(pai, item, todos) : false;
}

export const planos: Plano[] = [
  {
    id: "gratis",
    nome: "Grátis",
    paraQuem: "Para quem usa Claude, ChatGPT, Cursor ou n8n.",
    inclui: [
      "As 9 ferramentas de cálculo no endpoint aberto",
      "Sem conta e sem login",
      "Limite por sessão MCP e teto global do endpoint",
    ],
    disponivel: true,
  },
  {
    id: "pessoal",
    nome: "Pessoal",
    paraQuem: "Para quem estuda o próprio mapa toda semana.",
    inclui: [
      "Login",
      "Minhas pessoas: guarde até 20 mapas",
      "Histórico de leituras",
      'Ferramentas por nome, como os trânsitos de hoje para "Amanda"',
      "Sem limite duro de uso",
      "Resumo semanal, em fase posterior",
    ],
    disponivel: false,
  },
  {
    id: "profissional",
    nome: "Profissional",
    paraQuem: "Para astrólogos que atendem.",
    herdaDe: "pessoal",
    inclui: [
      "Clientes ilimitados, com consentimento LGPD registrado",
      "Notas por cliente",
      "preparar_sessao: natal, trânsitos, progressões e revolução solar vigente numa chamada",
      "Roda do mapa em SVG e PDF",
      "Link de relatório para o cliente",
    ],
    disponivel: false,
  },
];
