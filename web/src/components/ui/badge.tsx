// Cópia leve do primitivo do @beeads/ui: o pacote é um barrel único "use client" e levaria ~430 KB ao navegador.
// Voltar a importar do DS quando ele publicar entradas por componente (gucancado/beeads-ui).
// Classes copiadas de node_modules/@beeads/ui/dist/index.mjs (v0.7.1), sem mudança visual.
import type { ComponentProps } from "react";
import { cn } from "./cn";

// Só a variante usada no site: o Badge "outline" do DS com border-border, font-normal e text-muted-fg
// (o resultado que o tailwind-merge dava para as classes que planos e profissionais passavam).
export function Badge({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      data-slot="badge"
      className={cn(
        "inline-flex items-center rounded-md border border-border px-2.5 py-0.5 text-xs font-normal text-muted-fg transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        className,
      )}
      {...props}
    />
  );
}
