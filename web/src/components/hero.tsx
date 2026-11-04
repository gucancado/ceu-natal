import { Button } from "@beeads/ui";
import { tools } from "@/content/tools";
import { TabelaEfemeride } from "@/components/tabela-efemeride";

export function Hero() {
  return (
    <section aria-labelledby="hero-titulo" className="mx-auto max-w-[72rem] px-6">
      <div className="grid gap-16 py-16 md:py-24 lg:grid-cols-12 lg:gap-12">
        <div className="lg:col-span-6">
          <h1
            id="hero-titulo"
            className="font-display text-[44px] font-medium leading-[1.1] tracking-tight md:text-[52px]"
          >
            Seu chat inventa o seu ascendente.
          </h1>
          <p className="mt-6 max-w-[36rem] text-xl leading-[1.5]">
            Modelos de linguagem não calculam posições planetárias: inventam. O Céu Natal calcula
            com as efemérides suíças, em português, dentro do Claude, do ChatGPT, do Cursor ou do
            n8n que você já usa.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <Button asChild size="lg">
              <a href="#conectar">Conectar agora</a>
            </Button>
            <Button asChild size="lg" variant="outline">
              <a href="#ferramentas">Ver as {tools.length} ferramentas</a>
            </Button>
          </div>
        </div>
        <div className="lg:col-span-6 lg:pl-6">
          <TabelaEfemeride />
        </div>
      </div>
    </section>
  );
}
