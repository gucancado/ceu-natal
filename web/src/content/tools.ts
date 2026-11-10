// Ferramentas do servidor MCP. Os números das descrições vêm da saída real de cada tool:
// 29 posições = 10 planetas + 3 pontos (nodos e Quíron) + 4 ângulos + 12 casas; 15 pontos = 10 planetas + 3 pontos + ASC e MC.
export type GrupoTool = "natal" | "relacoes" | "tempo" | "util";

export type Tool = { nome: string; descricao: string; grupo: GrupoTool };

export const tools: Tool[] = [
  {
    nome: "calcular_mapa_natal",
    descricao: "calcula 29 posições de um mapa natal e os aspectos entre elas.",
    grupo: "natal",
  },
  {
    nome: "calcular_sinastria",
    descricao: "calcula os aspectos entre dois mapas e em qual casa do outro cai cada planeta.",
    grupo: "relacoes",
  },
  {
    nome: "calcular_transitos",
    descricao: "calcula os 10 planetas em uma data e os aspectos deles com o mapa natal.",
    grupo: "tempo",
  },
  {
    nome: "calcular_progressoes",
    descricao: "calcula os 10 planetas progredidos para uma data e os aspectos com o mapa natal.",
    grupo: "tempo",
  },
  {
    nome: "calcular_mapa_composto",
    descricao: "calcula 15 pontos médios entre dois mapas e os aspectos entre eles.",
    grupo: "relacoes",
  },
  {
    nome: "calcular_revolucao_solar",
    descricao: "calcula o instante em que o sol volta à posição natal no ano e o mapa desse momento.",
    grupo: "tempo",
  },
  {
    nome: "calcular_revolucao_lunar",
    descricao: "calcula o próximo retorno da lua à posição natal e o mapa desse momento.",
    grupo: "tempo",
  },
  {
    nome: "listar_aspectos_tipos",
    descricao: "lista os 8 aspectos calculados, com ângulo e orbe de cada um.",
    grupo: "util",
  },
  {
    nome: "healthcheck",
    descricao: "informa se o servidor está no ar e qual a versão.",
    grupo: "util",
  },
];
