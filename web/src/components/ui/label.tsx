// Cópia leve do primitivo do @beeads/ui: o pacote é um barrel único "use client" e levaria ~430 KB ao navegador.
// Voltar a importar do DS quando ele publicar entradas por componente (gucancado/beeads-ui).
// Classes copiadas de node_modules/@beeads/ui/dist/index.mjs (v0.7.1). Sem twMerge: base e variantes
// não podem repetir a mesma família de utilitário (text-*, px-*, h-*, rounded-*…), senão vence a ordem do CSS.
import type { ComponentProps } from "react";
import { cn } from "./cn";

export function Label({ className, ...props }: ComponentProps<"label">) {
  return (
    <label
      data-slot="label"
      className={cn(
        "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
        className,
      )}
      {...props}
    />
  );
}
