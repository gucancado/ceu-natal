// Páginas por técnica (/sinastria, /transitos...). Cada uma responde a uma busca em português e leva a
// pessoa a conectar o Céu Natal na IA. O texto descreve o que a tool calcula; a interpretação fica com a IA.
export type Tecnica = {
  slug: string;
  /** Nome curto, para links e listas. */
  nome: string;
  /** H1 e <title>. */
  titulo: string;
  /** Meta description, até ~160 caracteres. */
  descricao: string;
  tool: string;
  /** Linha acima do H1. */
  chamada: string;
  intro: string;
  calcula: string[];
  precisa: string[];
  pedidos: string[];
  perguntas: { p: string; r: string }[];
};

export const tecnicas: Tecnica[] = [
  {
    slug: "sinastria",
    nome: "sinastria",
    titulo: "Sinastria amorosa calculada, grátis, no seu chat",
    descricao:
      "Compare dois mapas astrais com as efemérides suíças: aspectos entre os planetas dos dois e em que casa do outro cai cada planeta. Grátis, dentro do ChatGPT ou do Claude.",
    tool: "calcular_sinastria",
    chamada: "dois mapas, um encontro",
    intro:
      "a sinastria compara o mapa de duas pessoas: como os planetas de uma conversam com os planetas da outra. a ia é boa para interpretar e ruim para calcular. com o céu natal conectado, ela recebe os aspectos calculados e lê a relação a partir deles.",
    calcula: [
      "os aspectos cruzados: cada planeta de uma pessoa contra cada planeta da outra, com o orbe",
      "em que casa do mapa de uma pessoa cai cada planeta da outra",
      "a contagem de aspectos harmônicos, tensos e neutros",
    ],
    precisa: [
      "a data de nascimento das duas pessoas",
      "hora e cidade de nascimento, se souber (sem elas não há casas nem ascendente)",
    ],
    pedidos: [
      "Faça a sinastria entre mim (12/03/1990, 14h30, Belo Horizonte) e ele (25/07/1992, 9h15, São Paulo). Onde a gente combina e onde a gente se estranha?",
      "Os planetas dela caem em quais casas do meu mapa?",
      "Qual é o aspecto mais forte entre os nossos mapas?",
    ],
    perguntas: [
      {
        p: "qual a diferença entre sinastria e mapa composto?",
        r: "a sinastria põe os dois mapas lado a lado e compara. o mapa composto cria um terceiro mapa, com os pontos médios dos dois, que representa a relação em si. o céu natal calcula os dois.",
      },
      {
        p: "dá para fazer sinastria sem a hora de nascimento?",
        r: "dá. os aspectos entre os planetas saem só com a data. sem a hora, ficam de fora as casas e o ascendente.",
      },
      {
        p: "serve para amizade, família e trabalho?",
        r: "serve. o cálculo é o mesmo para qualquer par de pessoas; o que muda é a pergunta que você faz para a ia.",
      },
    ],
  },
  {
    slug: "mapa-composto",
    nome: "mapa composto",
    titulo: "Mapa composto: o mapa astral da relação",
    descricao:
      "Calcule o mapa composto de duas pessoas pelo método dos pontos médios, com efemérides suíças, e converse sobre ele no ChatGPT ou no Claude. Grátis.",
    tool: "calcular_mapa_composto",
    chamada: "o terceiro mapa",
    intro:
      "o mapa composto junta dois mapas num só: cada planeta fica no ponto médio entre a posição dele no mapa de uma pessoa e no da outra. o resultado descreve a relação como uma coisa própria, separada das duas pessoas.",
    calcula: [
      "15 pontos compostos: sol, lua, planetas, nodos, quíron, ascendente e meio do céu",
      "os aspectos entre os pontos do composto",
      "o equilíbrio de elementos do mapa da relação",
    ],
    precisa: [
      "data de nascimento das duas pessoas",
      "hora e cidade das duas, para ter ascendente e meio do céu compostos",
    ],
    pedidos: [
      "Calcule o mapa composto entre mim (03/11/1988, 22h10, Recife) e minha esposa (17/05/1990, 6h40, Curitiba). Qual é o tema central da nossa relação?",
      "Onde está o Sol do nosso mapa composto e o que isso diz sobre o casal?",
    ],
    perguntas: [
      {
        p: "o mapa composto tem casas?",
        r: "não pelo método dos pontos médios: ele não corresponde a um instante nem a um lugar. o céu natal entrega ascendente e meio do céu compostos quando as duas pessoas têm hora e cidade.",
      },
      {
        p: "é melhor que a sinastria?",
        r: "são leituras diferentes. a sinastria mostra como uma pessoa afeta a outra; o composto mostra o que a relação é. muita gente olha os dois.",
      },
    ],
  },
  {
    slug: "transitos",
    nome: "trânsitos",
    titulo: "Trânsitos de hoje sobre o seu mapa astral",
    descricao:
      "Veja os trânsitos de hoje ou de qualquer data sobre o seu mapa natal, calculados com efemérides suíças: aspectos, casas e planetas lentos em destaque. Grátis, no seu chat.",
    tool: "calcular_transitos",
    chamada: "o céu de agora no seu mapa",
    intro:
      "trânsito é a posição dos planetas numa data comparada com o seu mapa de nascimento. é a técnica mais usada para entender uma fase. o céu natal calcula os trânsitos de qualquer dia, passado ou futuro, e a ia interpreta.",
    calcula: [
      "a posição dos 10 planetas na data que você escolher",
      "os aspectos de cada planeta em trânsito com o seu mapa natal, aplicando ou separando",
      "em que casa do seu mapa cada planeta está passando",
      "destaque para os planetas lentos (saturno, urano, netuno, plutão e quíron) com orbe menor que 2°",
    ],
    precisa: ["a sua data de nascimento", "hora e cidade de nascimento, para saber as casas"],
    pedidos: [
      "Quais são os trânsitos de hoje sobre o meu mapa? Nasci em 12/03/1990 às 14h30 em Belo Horizonte.",
      "Esse ano está pesado. Tem algum trânsito de Saturno no meu mapa?",
      "Como vai estar o céu para mim em 15/06/2027?",
    ],
    perguntas: [
      {
        p: "o que é retorno de saturno?",
        r: "é quando saturno volta ao ponto onde estava no seu nascimento, por volta dos 29 e dos 58 anos. aparece como trânsito de saturno em conjunção com o saturno natal.",
      },
      {
        p: "posso ver trânsitos de uma data passada?",
        r: "pode. qualquer data entre 1800 e 2399, para entender um momento que já aconteceu ou planejar um que vem.",
      },
    ],
  },
  {
    slug: "revolucao-solar",
    nome: "revolução solar",
    titulo: "Revolução solar: o mapa do seu ano, do aniversário em diante",
    descricao:
      "Calcule sua revolução solar com efemérides suíças: o instante exato em que o Sol volta à posição do seu nascimento, com ascendente, casas e aspectos. Grátis, no seu chat.",
    tool: "calcular_revolucao_solar",
    chamada: "feliz ano novo pessoal",
    intro:
      "a revolução solar é o mapa do instante em que o sol volta exatamente ao grau em que estava quando você nasceu. acontece perto do aniversário e vale até o próximo. é a técnica clássica de previsão anual.",
    calcula: [
      "o instante exato do retorno do sol, que pode cair um dia antes ou depois do aniversário",
      "o mapa completo desse momento: planetas, casas, ascendente e aspectos",
      "os aspectos entre o mapa da revolução e o seu mapa natal",
      "os destaques da leitura: ascendente da revolução e seus regentes, casa do sol e planetas angulares",
    ],
    precisa: [
      "data, hora e cidade de nascimento",
      "a cidade onde você vai estar no aniversário: ela muda o ascendente e as casas da revolução",
    ],
    pedidos: [
      "Calcule minha revolução solar de 2027. Nasci em 12/03/1990 às 14h30 em Belo Horizonte e vou passar o aniversário em Lisboa.",
      "Compare minha revolução solar de 2027 passando o aniversário em Salvador e em Florianópolis.",
      "Em que casa cai o Sol da minha revolução solar deste ano?",
    ],
    perguntas: [
      {
        p: "faz diferença onde eu passo o aniversário?",
        r: "faz para o ascendente e as casas da revolução. as posições dos planetas são as mesmas no mundo inteiro. por isso há quem escolha a cidade do aniversário pelo mapa.",
      },
      {
        p: "qual revolução solar vale hoje?",
        r: "a do último aniversário. ela vale até o retorno seguinte.",
      },
    ],
  },
  {
    slug: "revolucao-lunar",
    nome: "revolução lunar",
    titulo: "Revolução lunar: o mapa do seu mês",
    descricao:
      "Calcule sua revolução lunar com efemérides suíças: o momento em que a Lua volta à posição do seu nascimento, a cada 27 dias. Grátis, no ChatGPT ou no Claude.",
    tool: "calcular_revolucao_lunar",
    chamada: "um ciclo de 27 dias",
    intro:
      "a revolução lunar é como a revolução solar, só que com a lua: o mapa do instante em que ela volta ao grau do seu nascimento. isso acontece a cada 27,3 dias, então cada revolução lunar descreve um mês.",
    calcula: [
      "o próximo retorno da lua a partir da data que você escolher",
      "o mapa completo desse instante, com casas e aspectos",
      "os aspectos com o seu mapa natal e a casa onde a lua cai",
    ],
    precisa: ["data, hora e cidade de nascimento", "a cidade onde você vai estar no momento do retorno"],
    pedidos: [
      "Calcule minha próxima revolução lunar. Nasci em 12/03/1990 às 14h30 em Belo Horizonte e moro em São Paulo.",
      "O que a revolução lunar deste mês destaca para o trabalho?",
    ],
    perguntas: [
      {
        p: "qual a diferença para a revolução solar?",
        r: "a solar descreve o ano, do aniversário em diante. a lunar descreve um ciclo de cerca de 27 dias e muda a cada mês.",
      },
    ],
  },
  {
    slug: "progressoes",
    nome: "progressões",
    titulo: "Progressões secundárias: como o seu mapa evoluiu",
    descricao:
      "Calcule as progressões secundárias do seu mapa astral (um dia para cada ano de vida) com efemérides suíças: Lua e Sol progredidos e mudanças de signo. Grátis.",
    tool: "calcular_progressoes",
    chamada: "um dia para cada ano",
    intro:
      "nas progressões secundárias, cada dia depois do nascimento corresponde a um ano de vida. o mapa progredido mostra como o seu mapa amadureceu até hoje. a lua progredida muda de signo a cada dois anos e meio e marca as fases emocionais.",
    calcula: [
      "a posição progredida dos 10 planetas para a data escolhida",
      "os aspectos entre os planetas progredidos e o seu mapa natal",
      "o signo da lua e do sol progredidos, as mudanças de signo recentes e as próximas",
    ],
    precisa: ["data, hora e cidade de nascimento", "a data que você quer olhar (hoje ou outra)"],
    pedidos: [
      "Em que signo está a minha Lua progredida? Nasci em 12/03/1990 às 14h30 em Belo Horizonte.",
      "Meu Sol progredido vai mudar de signo nos próximos anos?",
    ],
    perguntas: [
      {
        p: "progressão é a mesma coisa que trânsito?",
        r: "não. trânsito é o céu de verdade numa data. progressão é um mapa simbólico, que avança um dia por ano a partir do nascimento. as duas se completam.",
      },
    ],
  },
];

export function tecnica(slug: string): Tecnica | undefined {
  return tecnicas.find((t) => t.slug === slug);
}
