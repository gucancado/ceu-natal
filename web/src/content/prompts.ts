// Pedidos que funcionam com o Céu Natal conectado. Giram na primeira dobra.
export type Prompt = { texto: string; tool: string };

export const prompts: Prompt[] = [
  { texto: "Calcule meu mapa natal: nasci em 12/03/1990 às 14h30 em Belo Horizonte.", tool: "calcular_mapa_natal" },
  { texto: "Quais trânsitos estão ativos sobre o meu mapa nesta semana?", tool: "calcular_transitos" },
  {
    texto: "Faça a sinastria entre mim e minha parceira, nascida em 25/07/1992 às 9h15 em São Paulo.",
    tool: "calcular_sinastria",
  },
  {
    texto: "Como fica minha revolução solar de 2027 se eu passar o aniversário em Lisboa?",
    tool: "calcular_revolucao_solar",
  },
  { texto: "Em que signo e casa está a minha Lua progredida hoje?", tool: "calcular_progressoes" },
  { texto: "Monte o mapa composto do nosso casal e mostre os aspectos mais fortes.", tool: "calcular_mapa_composto" },
  { texto: "Quando começa a minha próxima revolução lunar e onde cai o ascendente dela?", tool: "calcular_revolucao_lunar" },
];
