// Perguntas que giram na primeira dobra: em primeira pessoa, para a pessoa se reconhecer, e cada uma
// respondível por uma tool do Céu Natal (a IA interpreta em cima do cálculo).
export type Prompt = { texto: string; tool: string };

export const prompts: Prompt[] = [
  { texto: "Por que eu sempre me apaixono pelo mesmo tipo de pessoa?", tool: "calcular_mapa_natal" },
  { texto: "Esse ano está pesado. É algum trânsito?", tool: "calcular_transitos" },
  { texto: "Eu e ele combinamos de verdade ou é só química?", tool: "calcular_sinastria" },
  { texto: "O que o meu mapa diz sobre essa vontade de largar tudo e recomeçar?", tool: "calcular_mapa_natal" },
  { texto: "Como vai ser o meu próximo ano, do meu aniversário em diante?", tool: "calcular_revolucao_solar" },
];

// Os mesmos pedidos para a home em inglês (/en).
export const promptsEn: Prompt[] = [
  { texto: "Why do I always fall for the same kind of person?", tool: "calcular_mapa_natal" },
  { texto: "This year feels heavy. Is it a transit?", tool: "calcular_transitos" },
  { texto: "Are we really a match, or is it just chemistry?", tool: "calcular_sinastria" },
  { texto: "What does my chart say about this urge to drop everything and start over?", tool: "calcular_mapa_natal" },
  { texto: "What will my next year look like, from my birthday on?", tool: "calcular_revolucao_solar" },
];
