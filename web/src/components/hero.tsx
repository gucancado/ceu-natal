import { Lua } from "@/components/lua";
import { RotadorPrompts } from "@/components/rotador-prompts";

// Primeira dobra: só os pedidos de exemplo, com a Lua cruzando o céu no sentido contrário às estrelas.
export function Hero() {
  return (
    <section aria-label="exemplos de pedidos" className="relative isolate overflow-hidden">
      <Lua className="absolute left-0 top-[10%] -z-10 size-[88px] md:size-[128px]" />
      {/* Ocupa a tela abaixo do cabeçalho (5rem), para a seção seguinte começar na segunda dobra. */}
      <div className="mx-auto grid min-h-[calc(100svh-5rem)] max-w-[72rem] place-items-center px-6 py-16">
        <div className="w-full max-w-[42rem]">
          <RotadorPrompts />
        </div>
      </div>
    </section>
  );
}
