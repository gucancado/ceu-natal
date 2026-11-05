// Cópia leve do primitivo do @beeads/ui: o pacote é um barrel único "use client" e levaria ~430 KB ao navegador.
// Voltar a importar do DS quando ele publicar entradas por componente (gucancado/beeads-ui).
// Classes copiadas de node_modules/@beeads/ui/dist/index.mjs (v0.7.1). Sem twMerge: base e variantes
// não podem repetir a mesma família de utilitário (text-*, px-*, h-*, rounded-*…), senão vence a ordem do CSS.
import type { ComponentProps } from "react";
import { cn } from "./cn";

const base =
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:size-4 [&_svg]:shrink-0";

const variantes = {
  default: "bg-primary text-primary-fg hover:bg-primary/90",
  outline: "border border-input bg-bg hover:bg-muted hover:text-fg",
  ghost: "hover:bg-muted hover:text-fg",
} as const;

const tamanhos = {
  // text-sm saiu da base para cá: o lg usa text-base e, sem twMerge, as duas classes iriam juntas.
  sm: "h-8 px-3 text-sm",
  default: "h-9 px-4 py-2 text-sm",
  lg: "h-10 px-6 text-base",
} as const;

export type VarianteBotao = keyof typeof variantes;
export type TamanhoBotao = keyof typeof tamanhos;

/** Classes do botão do DS; serve também para estilizar um <a> ou <Link> como botão. */
export function buttonVariants({
  variant = "default",
  size = "default",
  className,
}: { variant?: VarianteBotao; size?: TamanhoBotao; className?: string } = {}): string {
  return cn(base, variantes[variant], tamanhos[size], className);
}

type Props = ComponentProps<"button"> & { variant?: VarianteBotao; size?: TamanhoBotao };

export function Button({ className, variant, size, ...props }: Props) {
  return <button data-slot="button" className={buttonVariants({ variant, size, className })} {...props} />;
}
