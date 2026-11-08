// Formato de um guia de conexão. Passos e limitações aceitam `código` e **menu**.
export type Cliente = {
  slug: string;
  nome: string;
  resumo: string;
  planoMinimo: string;
  semLogin: boolean;
  confianca: "alta" | "media" | "baixa";
  /** Link direto para a tela onde o conector é adicionado. */
  abrir?: { rotulo: string; url: string };
  passos: string[];
  snippet?: { linguagem: "json" | "bash" | "text"; codigo: string };
  limitacoes: string[];
  fontes: { titulo: string; url: string }[];
};

// Frase fixa para passo ou menu que a pesquisa não confirmou.
export const confira = "(confira o nome exato na versão atual do app)";
