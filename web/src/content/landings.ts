// Landing pages por intenção de busca (/sinastria, /revolucao-solar, /transitos). Têm o layout da home,
// com texto e pedidos da busca. Uma landing pode juntar várias técnicas: quem procura "sinastria" quase
// sempre quer também o mapa do casal (composto). O /mapa (mapa astral grátis) é uma página própria, com o
// formulário. Páginas antigas absorvidas por uma landing redirecionam (301) em next.config.ts.
import type { Prompt } from "./prompts";

export type Landing = {
  slug: string;
  /** <title> e og:title. */
  titulo: string;
  /** Meta description, até ~160 caracteres. */
  descricao: string;
  /** H1 da primeira dobra; a marca da IA entra girando logo depois. */
  chamada: string;
  /** Perguntas que giram na primeira dobra. */
  prompts: Prompt[];
  /** Título da segunda dobra. */
  titulo2: string;
  /** Texto curto abaixo do título da segunda dobra. */
  intro: string;
  /** Tools que a página cobre; a primeira é a principal. Calcula, pedidos e perguntas vêm de tecnicas.ts. */
  tools: string[];
};

export const landings: Landing[] = [
  {
    slug: "sinastria",
    titulo: "Sinastria amorosa grátis: compare dois mapas no seu chat",
    descricao:
      "Sinastria e mapa composto calculados com as efemérides suíças: aspectos entre os dois mapas, casas e o mapa da relação. Grátis, dentro do ChatGPT ou do Claude.",
    chamada: "sinastria e mapa do casal, calculados no",
    prompts: [
      { texto: "Eu e ele combinamos de verdade ou é só química?", tool: "calcular_sinastria" },
      { texto: "Por que a gente briga sempre pelo mesmo motivo?", tool: "calcular_sinastria" },
      { texto: "Qual é o tema central da nossa relação?", tool: "calcular_mapa_composto" },
      { texto: "Os planetas dela caem em quais casas do meu mapa?", tool: "calcular_sinastria" },
    ],
    titulo2: "compare o seu mapa com o de outra pessoa, direto na conversa com a ia",
    intro:
      "a sinastria põe os dois mapas lado a lado. o mapa composto junta os dois num terceiro, o mapa da relação. o céu natal calcula os dois e a ia lê a relação a partir deles. grátis e sem cadastro.",
    tools: ["calcular_sinastria", "calcular_mapa_composto"],
  },
  {
    slug: "revolucao-solar",
    titulo: "Revolução solar grátis: o mapa do seu ano no seu chat",
    descricao:
      "Calcule sua revolução solar com efemérides suíças: o instante exato em que o Sol volta à posição do seu nascimento, com ascendente, casas e aspectos. Grátis, no seu chat.",
    chamada: "revolução solar, o mapa do seu ano, calculada no",
    prompts: [
      { texto: "Como vai ser o meu próximo ano, do meu aniversário em diante?", tool: "calcular_revolucao_solar" },
      { texto: "Vale a pena passar o aniversário em outra cidade?", tool: "calcular_revolucao_solar" },
      { texto: "O que o ascendente da minha revolução solar diz sobre este ano?", tool: "calcular_revolucao_solar" },
    ],
    titulo2: "veja o seu ano novo pessoal, do aniversário em diante, direto na conversa com a ia",
    intro:
      "a revolução solar é o mapa do instante em que o sol volta ao grau do seu nascimento. vale de um aniversário ao outro e muda com a cidade onde você passa o aniversário. grátis e sem cadastro.",
    tools: ["calcular_revolucao_solar"],
  },
  {
    slug: "transitos",
    titulo: "Trânsitos de hoje sobre o seu mapa astral, grátis no seu chat",
    descricao:
      "Trânsitos de hoje ou de qualquer data, progressões e revolução lunar sobre o seu mapa natal, calculados com efemérides suíças. Grátis, dentro do ChatGPT ou do Claude.",
    chamada: "trânsitos de hoje sobre o seu mapa, calculados no",
    prompts: [
      { texto: "Esse ano está pesado. É algum trânsito?", tool: "calcular_transitos" },
      { texto: "O que o céu de hoje mexe no meu mapa?", tool: "calcular_transitos" },
      { texto: "Quando termina o meu retorno de Saturno?", tool: "calcular_transitos" },
      { texto: "Em que signo está a minha Lua progredida?", tool: "calcular_progressoes" },
      { texto: "O que a revolução lunar deste mês destaca?", tool: "calcular_revolucao_lunar" },
    ],
    titulo2: "entenda a fase que você está vivendo, direto na conversa com a ia",
    intro:
      "trânsito é o céu de uma data comparado com o seu mapa de nascimento. as progressões mostram como o mapa amadureceu, e a revolução lunar descreve cada mês. o céu natal calcula as três e a ia interpreta. grátis e sem cadastro.",
    tools: ["calcular_transitos", "calcular_progressoes", "calcular_revolucao_lunar"],
  },
];

export function landing(slug: string): Landing | undefined {
  return landings.find((l) => l.slug === slug);
}

/** Páginas antigas, uma por técnica, que agora fazem parte de uma landing. */
export const redirecionadas: { de: string; para: string }[] = [
  { de: "/mapa-composto", para: "/sinastria" },
  { de: "/progressoes", para: "/transitos" },
  { de: "/revolucao-lunar", para: "/transitos" },
];
