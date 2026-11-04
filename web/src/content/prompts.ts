// Prompts de exemplo. Textos de docs/distribuicao.md ("Bloco de texto reutilizável").
export type Prompt = { titulo: string; texto: string; tool: string };

export const prompts: Prompt[] = [
  {
    titulo: "Mapa natal",
    texto: "Calcule meu mapa natal: nasci em 12/03/1990 às 14h30 em Belo Horizonte.",
    tool: "calcular_mapa_natal",
  },
  {
    titulo: "Trânsitos de hoje",
    texto: "Quais são os trânsitos de hoje sobre o meu mapa natal?",
    tool: "calcular_transitos",
  },
  {
    titulo: "Sinastria",
    texto:
      "Faça a sinastria entre mim (12/03/1990, 14h30, Belo Horizonte) e minha parceira (25/07/1992, 9h15, São Paulo).",
    tool: "calcular_sinastria",
  },
];
