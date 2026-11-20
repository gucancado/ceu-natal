// Umami: contagem de visitas sem cookie, hospedada no próprio servidor. Complementa o contador do
// servidor MCP (POST /visita) com origem, aparelho e eventos. Os eventos nunca levam dado pessoal
// (data de nascimento, nome, cidade, contato): só o que a pessoa fez e onde.
export const umami = {
  origem: "https://estatisticas.gustavocancado.com.br",
  script: "https://estatisticas.gustavocancado.com.br/visita.js",
  siteId: "d9f86bab-1b70-4f98-8cfe-5c1d707b47f5",
} as const;

type DadosEvento = Record<string, string | number>;
type Umami = { track: (nome: string, dados?: DadosEvento) => unknown };

// Manda um evento. Sem o script carregado (bloqueador, DNT, servidor fora), não faz nada.
export function rastrear(nome: string, dados?: DadosEvento): void {
  try {
    (window as Window & { umami?: Umami }).umami?.track(nome, dados);
  } catch {
    // Contagem nunca atrapalha a página.
  }
}
