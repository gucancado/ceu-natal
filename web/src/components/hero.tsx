import { Autor } from "@/components/autor";
import { Lua } from "@/components/lua";
import { MarcaRotativa } from "@/components/marca-rotativa";
import { RotadorPrompts } from "@/components/rotador-prompts";
import { Sol } from "@/components/sol";
import { prompts as promptsPt, promptsEn, type Prompt } from "@/content/prompts";
import type { Idioma } from "@/lib/idioma";

type Props = {
  idioma?: Idioma;
  /** Frase antes da marca da IA. Nas landings ela é o H1 da página (o termo da busca). */
  chamada?: string;
  prompts?: Prompt[];
  /** A chamada vira o H1 (landings); na home o H1 fica na segunda dobra. */
  comoH1?: boolean;
};

// Primeira dobra: só os pedidos de exemplo, com a Lua cruzando o céu no sentido contrário às estrelas.
export function Hero({ idioma = "pt", chamada, prompts, comoH1 = false }: Props) {
  const en = idioma === "en";
  const texto = chamada ?? (en ? "free mcp for astrological calculations with" : "mcp grátis para cálculos astrológicos com");
  const Chamada = comoH1 ? "h1" : "p";
  return (
    <section aria-label={en ? "example requests" : "exemplos de pedidos"} className="relative overflow-hidden">
      {/* O Sol vem antes no DOM: fica atrás da Lua quando os dois se cruzam. */}
      <Sol className="absolute left-0 top-[3%] size-[16px] md:size-[22px]" />
      <Lua className="absolute left-0 top-[6%] size-[120px] md:size-[180px]" />
      {/* Ocupa a tela abaixo do cabeçalho (5rem), para a seção seguinte começar na segunda dobra.
          A primeira linha reserva a faixa por onde a Lua passa sobre o texto (6% do topo + o disco + a
          descida do arco nas bordas do texto, ~9vh): com espaço, o texto fica centrado; em tela baixa,
          desce em vez de ficar por baixo da Lua. */}
      <div className="relative mx-auto grid min-h-[calc(100svh-5rem)] max-w-[72rem] grid-rows-[minmax(calc(15svh+120px+1.5rem),1fr)_auto_1fr] justify-items-center px-6 pb-16 md:grid-rows-[minmax(calc(15svh+180px+1.5rem),1fr)_auto_1fr]">
        <div className="row-start-2 w-full max-w-[42rem]">
          <Chamada className="mb-8 text-center text-sm font-normal text-muted-fg md:text-base">
            {texto} <MarcaRotativa emLinha idioma={idioma} />
          </Chamada>
          <RotadorPrompts prompts={prompts ?? (en ? promptsEn : promptsPt)} />
          <Autor className="mt-10" idioma={idioma} />
        </div>
      </div>
    </section>
  );
}
