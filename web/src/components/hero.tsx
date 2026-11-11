import { Lua } from "@/components/lua";
import { RotadorPrompts } from "@/components/rotador-prompts";
import { site } from "@/lib/site";

// Primeira dobra: só os pedidos de exemplo, com a Lua cruzando o céu no sentido contrário às estrelas.
export function Hero() {
  return (
    // Sem `isolate`: o mix-blend-mode da Lua precisa misturar com o céu da página, não com um grupo vazio.
    <section aria-label="exemplos de pedidos" className="relative overflow-hidden">
      <Lua className="absolute left-0 top-[6%] size-[120px] md:size-[180px]" />
      {/* Ocupa a tela abaixo do cabeçalho (5rem), para a seção seguinte começar na segunda dobra. */}
      <div className="relative mx-auto grid min-h-[calc(100svh-5rem)] max-w-[72rem] place-items-center px-6 py-16">
        <div className="w-full max-w-[42rem]">
          <RotadorPrompts />
          <p className="mt-10 text-center text-muted-fg">
            autor:{" "}
            <a
              href={site.autorUrl}
              className="rounded-sm underline underline-offset-4 transition-colors hover:text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              gustavo cançado
            </a>
          </p>
        </div>
      </div>
    </section>
  );
}
