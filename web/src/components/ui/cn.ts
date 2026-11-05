// Cópia leve do primitivo do @beeads/ui: o pacote é um barrel único "use client" e levaria ~430 KB ao navegador.
// Voltar a importar do DS quando ele publicar entradas por componente (gucancado/beeads-ui).
// Classes copiadas de node_modules/@beeads/ui/dist/index.mjs (v0.7.1). Sem twMerge: base e variantes
// não podem repetir a mesma família de utilitário (text-*, px-*, h-*, rounded-*…), senão vence a ordem do CSS.

/** Junta classes, ignorando vazios. Sem twMerge: base e variantes não podem repetir a mesma família de utilitário. */
export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}
