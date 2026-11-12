// Ficha técnica de cada tool, para o modal da seção "ferramentas do mcp": parâmetros e o que volta.
// Fonte: inputSchema em app/server.py (TOOLS) e os dicionários montados em app/tools/ e app/core/revolucoes.py.
// Mudou um parâmetro ou um campo de retorno lá, mude aqui.
export type Parametro = { nome: string; obrigatorio?: boolean; desc: string };
export type Ficha = {
  tool: string;
  titulo: string;
  resumo: string;
  parametros: Parametro[];
  retorna: { campo: string; desc: string }[];
  notas?: string[];
};

const pessoa = "objeto pessoa: data (DD/MM/AAAA, obrigatória), hora (HH:MM), local (\"Cidade, UF\" ou \"Cidade, País\"), nome, is_dst";
const casas: Parametro = {
  nome: "sistema_casas",
  desc: "P (Placidus, padrão), K, W (Whole Sign), E, R, C, O, B, M ou T",
};

export const fichas: Ficha[] = [
  {
    tool: "calcular_mapa_natal",
    titulo: "mapa natal",
    resumo: "posições de um mapa natal com casas, ângulos, aspectos e síntese.",
    parametros: [
      { nome: "data", obrigatorio: true, desc: "DD/MM/AAAA" },
      { nome: "hora", desc: "HH:MM; sem ela, usa 12:00 local" },
      { nome: "local", desc: "\"Cidade, UF\" ou \"Cidade, País\"; vira coordenadas e fuso histórico" },
      { nome: "nome", desc: "só para identificação" },
      { nome: "is_dst", desc: "desempata hora ambígua na troca do horário de verão" },
      casas,
    ],
    retorna: [
      { campo: "planetas", desc: "sol a plutão: signo, grau e casa" },
      { campo: "pontos_sensiveis", desc: "nodos verdadeiros e quíron" },
      { campo: "angulos", desc: "ascendente, meio do céu, descendente e fundo do céu" },
      { campo: "casas", desc: "as 12 cúspides" },
      { campo: "aspectos", desc: "8 tipos, com orbe" },
      { campo: "sintese", desc: "elementos, qualidades, hemisférios e stelliums" },
      { campo: "local_resolvido", desc: "latitude, longitude e fuso usados" },
    ],
    notas: [
      "sem hora ou sem local: só posições por signo, sem casas nem ângulos",
      "sem hora, a lua vem marcada como incerta (posicao_incerta, signo_pode_mudar)",
    ],
  },
  {
    tool: "calcular_sinastria",
    titulo: "sinastria",
    resumo: "compara dois mapas natais: aspectos cruzados e planetas de um nas casas do outro.",
    parametros: [
      { nome: "pessoa_a", obrigatorio: true, desc: pessoa },
      { nome: "pessoa_b", obrigatorio: true, desc: "mesmo formato de pessoa_a" },
      casas,
    ],
    retorna: [
      { campo: "pessoa_a, pessoa_b", desc: "resumo de cada mapa: sol, lua e ascendente" },
      { campo: "aspectos_sinastria", desc: "cada planeta de A contra cada planeta de B, com orbe" },
      { campo: "ativacoes_de_casas", desc: "em que casa do mapa de um cai cada planeta do outro" },
      { campo: "sintese_sinastria", desc: "contagem de aspectos harmônicos, tensos e neutros" },
    ],
    notas: ["casas e ativações só para quem tem hora e local"],
  },
  {
    tool: "calcular_mapa_composto",
    titulo: "mapa composto",
    resumo: "um terceiro mapa, com o ponto médio de cada planeta das duas pessoas.",
    parametros: [
      { nome: "pessoa_a", obrigatorio: true, desc: pessoa },
      { nome: "pessoa_b", obrigatorio: true, desc: "mesmo formato de pessoa_a" },
      casas,
    ],
    retorna: [
      { campo: "planetas_compostos", desc: "ponto médio de cada planeta: signo e grau" },
      { campo: "pontos_sensiveis_compostos", desc: "nodos e quíron compostos" },
      { campo: "angulos_compostos", desc: "ascendente e meio do céu compostos" },
      { campo: "aspectos_compostos", desc: "aspectos entre os pontos do composto" },
      { campo: "sintese", desc: "distribuição de elementos e stelliums" },
    ],
    notas: [
      "método dos pontos médios: não tem casas",
      "ângulos compostos só quando as duas pessoas têm hora e local",
    ],
  },
  {
    tool: "calcular_transitos",
    titulo: "trânsitos",
    resumo: "o céu de uma data comparado com um mapa natal.",
    parametros: [
      { nome: "natal", obrigatorio: true, desc: pessoa },
      { nome: "data_transito", obrigatorio: true, desc: "DD/MM/AAAA" },
      { nome: "hora_transito", desc: "HH:MM; padrão 12:00 UTC" },
      { nome: "local_transito", desc: "local de observação; padrão Greenwich" },
      casas,
    ],
    retorna: [
      { campo: "planetas_em_transito", desc: "posição de cada planeta na data e a casa natal onde cai" },
      { campo: "aspectos_transito_natal", desc: "aspectos com o mapa natal, com orbe, aplicando ou separando" },
      {
        campo: "sintese",
        desc: "aspectos aplicando e separando, trânsitos para luminares e pessoais, lentos em destaque",
      },
    ],
    notas: [
      "exige hora e local de nascimento, para as casas natais",
      "lentos em destaque: saturno, urano, netuno, plutão e quíron com orbe menor que 2°",
    ],
  },
  {
    tool: "calcular_progressoes",
    titulo: "progressões secundárias",
    resumo: "o mapa progredido (um dia depois do nascimento = um ano de vida) numa data alvo.",
    parametros: [
      { nome: "natal", obrigatorio: true, desc: pessoa },
      { nome: "data_alvo", obrigatorio: true, desc: "DD/MM/AAAA" },
      casas,
    ],
    retorna: [
      { campo: "planetas_progredidos", desc: "posição progredida de cada planeta" },
      { campo: "aspectos_progredido_natal", desc: "aspectos entre progredidos e natais" },
      {
        campo: "destaques",
        desc: "lua e sol progredidos (signo, casa natal), ingressos recentes e mudanças de signo próximas",
      },
      { campo: "idade_aproximada, metodo", desc: "idade na data alvo e a regra usada" },
    ],
  },
  {
    tool: "calcular_revolucao_solar",
    titulo: "revolução solar",
    resumo: "o mapa do instante exato em que o sol volta ao grau natal num ano.",
    parametros: [
      { nome: "natal", obrigatorio: true, desc: `${pessoa}; hora e local são necessários` },
      { nome: "ano", obrigatorio: true, desc: "1800 a 2200, a partir do ano de nascimento" },
      { nome: "local_revolucao", obrigatorio: true, desc: "cidade onde a pessoa estará no aniversário" },
      casas,
    ],
    retorna: [
      { campo: "revolucao", desc: "instante em UTC e local, local, coordenadas, fuso e vigência" },
      { campo: "planetas, angulos, casas", desc: "o mapa completo da revolução" },
      { campo: "aspectos_internos", desc: "aspectos dentro do mapa da revolução" },
      { campo: "aspectos_revolucao_natal", desc: "aspectos entre a revolução e o natal" },
      { campo: "sobreposicao", desc: "planetas de um mapa nas casas do outro, nos dois sentidos" },
      {
        campo: "destaques",
        desc: "ascendente da revolução e seus regentes, casa do sol e planetas angulares",
      },
    ],
    notas: [
      "local_revolucao muda só ascendente, meio do céu e casas; as posições dos planetas são as mesmas",
      "pode cair um dia antes ou depois do aniversário; vale até o retorno seguinte",
    ],
  },
  {
    tool: "calcular_revolucao_lunar",
    titulo: "revolução lunar",
    resumo: "o mapa do próximo retorno da lua ao grau natal, um ciclo de ~27,3 dias.",
    parametros: [
      { nome: "natal", obrigatorio: true, desc: `${pessoa}; hora e local são necessários` },
      { nome: "data_referencia", obrigatorio: true, desc: "DD/MM/AAAA; devolve o primeiro retorno nessa data ou depois" },
      { nome: "local_revolucao", obrigatorio: true, desc: "cidade onde a pessoa estará no retorno" },
      casas,
    ],
    retorna: [
      { campo: "revolucao", desc: "instante em UTC e local, local, coordenadas e fuso" },
      { campo: "planetas, angulos, casas", desc: "o mapa completo da revolução" },
      { campo: "aspectos_internos, aspectos_revolucao_natal", desc: "aspectos internos e com o natal" },
      { campo: "sobreposicao", desc: "planetas de um mapa nas casas do outro" },
      { campo: "destaques", desc: "casa da lua, ascendente e regentes, planetas angulares" },
      { campo: "ciclo_em_curso", desc: "quando o ciclo vigente começou antes da data de referência" },
    ],
  },
  {
    tool: "listar_aspectos_tipos",
    titulo: "tipos de aspecto",
    resumo: "a tabela dos 8 aspectos usados nos cálculos.",
    parametros: [],
    retorna: [
      {
        campo: "aspectos",
        desc: "tipo, ângulo, orbe padrão, orbe com luminar, orbe de exato e natureza (harmônico, tensão ou neutro)",
      },
    ],
  },
  {
    tool: "healthcheck",
    titulo: "verificar o servidor",
    resumo: "confirma que o servidor está no ar.",
    parametros: [],
    retorna: [
      { campo: "status", desc: "\"ok\" quando o servidor responde" },
      { campo: "versao, transporte", desc: "versão do servidor e transporte (streamable-http)" },
      { campo: "proximo_passo, codigo_fonte", desc: "o que pedir em seguida e o link do repositório" },
    ],
  },
];

export function fichaDa(tool: string): Ficha | undefined {
  return fichas.find((f) => f.tool === tool);
}
