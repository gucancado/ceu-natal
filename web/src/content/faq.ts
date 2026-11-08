// Perguntas frequentes. Limites vêm de site.limites; privacidade segue docs/legal/privacidade.md.
import { site } from "../lib/site";

export type ItemFaq = { pergunta: string; resposta: string };

const { porSessaoPorMin, globalPorMin } = site.limites;

export const faq: ItemFaq[] = [
  {
    pergunta: "Os cálculos são precisos?",
    resposta:
      "Sim. O cálculo usa as efemérides suíças (Swiss Ephemeris), as mesmas do astro.com. As posições saem em graus e minutos de cada signo.",
  },
  {
    pergunta: "E se eu não souber a hora de nascimento?",
    resposta:
      "Sem a hora, o mapa sai sem casas e sem ascendente. Você ainda recebe as posições dos planetas nos signos e os aspectos entre eles. Trânsitos, sinastria e progressões também funcionam, só que sem as casas. As revoluções solar e lunar precisam da hora.",
  },
  {
    pergunta: "Quais sistemas de casas posso usar?",
    resposta:
      "O padrão é Placidus (P). Você também pode pedir Koch (K), Signos inteiros (W), Casas iguais (E), Regiomontanus (R), Campanus (C), Porfírio (O), Alcabitius (B), Morinus (M) ou Topocêntrico (T).",
  },
  {
    pergunta: "O que acontece com os meus dados?",
    resposta:
      "Data, hora e local de nascimento servem só para o cálculo e não ficam guardados. Os logs registram o nome da ferramenta, o status, a duração e, quando há cidade, a cidade e o país; nunca a data ou a hora de nascimento, e sem identificador de sessão. Eles ficam guardados por até 90 dias. Os detalhes estão em /privacidade.",
  },
  {
    pergunta: "Existe limite de uso?",
    resposta: `Sim. São ${porSessaoPorMin} chamadas por minuto por sessão MCP e ${globalPorMin} por minuto no total do servidor. Se passar do limite, a resposta volta como um erro pedindo para aguardar e tentar de novo.`,
  },
];
