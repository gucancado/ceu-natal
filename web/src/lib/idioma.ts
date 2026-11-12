// Idiomas do site. A home existe em português (/) e em inglês (/en), com o mesmo layout.
export type Idioma = "pt" | "en";

/** Caminho da home em cada idioma. */
export const homeDo: Record<Idioma, string> = { pt: "/", en: "/en" };
