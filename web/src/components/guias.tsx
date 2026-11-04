"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@beeads/ui";
import { GuiaCorpo } from "@/components/guia";
import { cliente, clientes } from "@/content/clientes";

const padrao = "claude-ai";

export function GuiasAbas({ inicial = padrao }: { inicial?: string }) {
  return (
    <Tabs defaultValue={inicial}>
      <TabsList
        aria-label="Escolha onde conectar"
        className="h-auto max-w-full justify-start overflow-x-auto"
      >
        {clientes.map((c) => (
          <TabsTrigger
            key={c.slug}
            value={c.slug}
            className="shrink-0 whitespace-nowrap data-[selected]:shadow-none"
          >
            {c.nome}
          </TabsTrigger>
        ))}
      </TabsList>
      {clientes.map((c) => (
        <TabsContent key={c.slug} value={c.slug} keepMounted className="mt-10">
          <GuiaCorpo c={c} Titulo="h3" />
          <Link
            href={`/conectar/${c.slug}`}
            className="mt-8 inline-block text-honey underline underline-offset-4"
          >
            Guia completo
          </Link>
        </TabsContent>
      ))}
    </Tabs>
  );
}

// Lê ?cliente=<slug>; precisa de <Suspense> em volta (a página é estática).
export function Guias() {
  const slug = useSearchParams().get("cliente") ?? "";
  return <GuiasAbas key={slug} inicial={cliente(slug)?.slug ?? padrao} />;
}
