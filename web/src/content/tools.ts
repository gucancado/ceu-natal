// Ferramentas do servidor MCP. Descrições copiadas de app/static/llms.txt ("## Tools").
export type GrupoTool = "natal" | "relacoes" | "tempo" | "util";

export type Tool = { nome: string; descricao: string; grupo: GrupoTool };

export const tools: Tool[] = [
  {
    nome: "calcular_mapa_natal",
    descricao: "posições, casas, ângulos, aspectos e síntese de um mapa natal.",
    grupo: "natal",
  },
  {
    nome: "calcular_sinastria",
    descricao: "aspectos cruzados entre duas pessoas e planetas de A nas casas de B.",
    grupo: "relacoes",
  },
  {
    nome: "calcular_transitos",
    descricao: "posições em uma data, aspectos com o mapa natal e destaque de trânsitos lentos.",
    grupo: "tempo",
  },
  {
    nome: "calcular_progressoes",
    descricao: "progressões secundárias (1 dia = 1 ano) para uma data alvo, com Lua e Sol progredidos.",
    grupo: "tempo",
  },
  {
    nome: "calcular_mapa_composto",
    descricao: "mapa composto por midpoints de duas pessoas.",
    grupo: "relacoes",
  },
  {
    nome: "calcular_revolucao_solar",
    descricao: "revolução solar de um ano (natal com hora e local, ano, local da revolução).",
    grupo: "tempo",
  },
  {
    nome: "calcular_revolucao_lunar",
    descricao:
      "próxima revolução lunar a partir de uma data (natal, data de referência, local da revolução).",
    grupo: "tempo",
  },
  {
    nome: "listar_aspectos_tipos",
    descricao: "tipos de aspectos suportados, ângulos e orbes.",
    grupo: "util",
  },
  {
    nome: "healthcheck",
    descricao: "status do servidor.",
    grupo: "util",
  },
];
