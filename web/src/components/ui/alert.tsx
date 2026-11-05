// Cópia leve do primitivo do @beeads/ui: o pacote é um barrel único "use client" e levaria ~430 KB ao navegador.
// Voltar a importar do DS quando ele publicar entradas por componente (gucancado/beeads-ui).
// Classes copiadas de node_modules/@beeads/ui/dist/index.mjs (v0.7.1), sem mudança visual.
import type { ComponentProps } from "react";
import { cn } from "./cn";

export function Alert({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      data-slot="alert"
      role="alert"
      className={cn(
        "relative w-full rounded-lg border p-4 [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-fg [&>svg~*]:pl-7 bg-card text-card-fg border-border",
        className,
      )}
      {...props}
    />
  );
}

export function AlertDescription({ className, ...props }: ComponentProps<"div">) {
  return <div data-slot="alert-description" className={cn("text-sm [&_p]:leading-relaxed", className)} {...props} />;
}
