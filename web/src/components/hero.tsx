import Link from "next/link";
import { Button } from "@beeads/ui";
import { Copiar } from "@/components/copiar";
import { RotadorPrompts } from "@/components/rotador-prompts";
import { promptSetup } from "@/content/setup";

export function Hero() {
  return (
    <section aria-labelledby="hero-titulo" className="mx-auto max-w-[72rem] px-6">
      <div className="grid items-center gap-12 py-12 md:py-20 lg:grid-cols-12 lg:gap-12">
        <div className="lg:col-span-6">
          <h1
            id="hero-titulo"
            className="font-display text-[40px] font-medium leading-[1.1] tracking-tight md:text-[48px]"
          >
            conecte sua IA favorita e faça análises astrológicas muito mais precisas.
          </h1>
          <p className="mt-5 max-w-[34rem] text-lg leading-[1.5]">
            Grátis e sem cadastro. Copie o prompt, cole no Claude, no ChatGPT, no Gemini ou no Cursor e o próprio
            assistente guia a conexão.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Copiar texto={promptSetup} rotulo="Copiar prompt para começar" copiado="Copiado. Cole no seu assistente" variant="default" size="lg" />
            <Button asChild size="lg" variant="outline">
              <Link href="/mapa">Fazer meu mapa grátis</Link>
            </Button>
          </div>
        </div>
        <div className="lg:col-span-6">
          <RotadorPrompts />
        </div>
      </div>
    </section>
  );
}
