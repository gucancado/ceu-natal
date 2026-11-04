export type ParteTextoGuia = { tipo: "texto" | "codigo" | "menu"; texto: string };

// Texto dos guias: `código` vira código, **menu** vira menu. Nada mais é interpretado.
export function partesTextoGuia(texto: string): ParteTextoGuia[] {
  return texto
    .split(/(`[^`]+`|\*\*[^*]+\*\*)/)
    .filter((p) => p !== "")
    .map((p): ParteTextoGuia => {
      if (p.startsWith("`") && p.endsWith("`") && p.length > 1) return { tipo: "codigo", texto: p.slice(1, -1) };
      if (p.startsWith("**") && p.endsWith("**") && p.length > 3) return { tipo: "menu", texto: p.slice(2, -2) };
      return { tipo: "texto", texto: p };
    });
}
