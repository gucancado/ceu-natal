import { Secao } from "@/components/secao";
import { planeta } from "@/lib/glifos";

type Linha = { tema: string; sem: string; com: string };

const linhas: Linha[] = [
  {
    tema: "Posições dos planetas",
    sem: "O modelo estima de memória. Erra graus e, às vezes, o signo.",
    com: "Calculadas com as efemérides suíças, ao minuto de arco.",
  },
  {
    tema: "Ascendente e casas",
    sem: "Dependem da hora exata e do fuso da época. O modelo costuma chutar.",
    com: "A cidade vira coordenada e fuso histórico antes do cálculo.",
  },
  {
    tema: "Trânsitos e revoluções",
    sem: "Exigem calcular o céu de outra data. O modelo inventa.",
    com: "Calculados para a data e o lugar que você pedir.",
  },
  {
    tema: "Sinastria e composto",
    sem: "Aspectos aproximados entre dois mapas também aproximados.",
    com: "Aspectos entre os dois mapas com o orbe exato.",
  },
  {
    tema: "Consistência",
    sem: "Cada conversa pode dar um mapa diferente.",
    com: "Os mesmos dados dão sempre o mesmo mapa.",
  },
  {
    tema: "Interpretação",
    sem: "Feita pelo assistente, em cima de números incertos.",
    com: "Feita pelo mesmo assistente, em cima de números calculados.",
  },
];

export function Comparacao() {
  return (
    <Secao id="comparacao" titulo="por que eu criei isso" simbolo={planeta.mercurio}>
      <div className="max-w-[60rem]">
        <p className="mb-10 max-w-[36rem] text-lg text-muted-fg">pedi meu mapa pra várias ias. cada uma me deu um céu diferente. é isso que muda:</p>
        <div aria-hidden="true" className="hidden grid-cols-[12rem_1fr_1fr] gap-8 pb-3 font-mono text-sm text-muted-fg md:grid">
          <span />
          <span>só a ia</span>
          <span className="text-honey">a ia com o céu natal</span>
        </div>
        <dl>
          {linhas.map((l) => (
            <div key={l.tema} className="grid gap-3 py-5 md:grid-cols-[12rem_1fr_1fr] md:gap-8">
              <dt className="font-display text-lg font-medium">{l.tema}</dt>
              <dd className="text-muted-fg">
                <span className="font-mono text-xs md:sr-only">só a ia: </span>
                {l.sem}
              </dd>
              <dd>
                <span className="font-mono text-xs text-honey md:sr-only">com o céu natal: </span>
                {l.com}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </Secao>
  );
}
