import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { Copiar } from "@/components/copiar";
import { promptSetup } from "@/content/setup";

export function Comecar() {
  return (
    <section aria-label="como começar" className="mx-auto max-w-[72rem] px-6">
      <div className="py-12 md:py-20">
        <p className="max-w-[34rem] text-lg leading-[1.5]">
          é grátis e sem cadastro. copie o prompt, cole no claude, no chatgpt, no gemini ou no cursor, e a própria ia te
          guia na conexão.
        </p>
        {/* Fonte monoespaçada é larga: abaixo de 360 px, o botão só cabe com letra e margem menores. */}
        <div className="mt-8 flex flex-wrap gap-3 max-[359px]:[&_a]:px-3 max-[359px]:[&_a]:text-sm max-[359px]:[&_button]:px-3 max-[359px]:[&_button]:text-sm">
          <Copiar texto={promptSetup} rotulo="Copiar prompt para começar" copiado="Copiado. Cole na sua IA" variant="outline" size="lg" />
          <Link href="/mapa" className={buttonVariants({ size: "lg", variant: "outline" })}>
            Fazer meu mapa astral grátis
          </Link>
        </div>
      </div>
    </section>
  );
}
