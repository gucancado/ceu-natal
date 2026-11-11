// U+FE0E pede a forma de texto, não o emoji colorido.
const t = (c: string) => `${c}︎`;

export const signos = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"].map(t);

export const planeta = {
  sol: t("☉"),
  lua: t("☽"),
  mercurio: t("☿"),
  venus: t("♀"),
  marte: t("♂"),
  jupiter: t("♃"),
  saturno: t("♄"),
  netuno: t("♆"),
} as const;

// Símbolo de cada ponto do mapa, pela chave que o servidor devolve. Ângulos usam as siglas da astrologia.
export const glifoPonto: Record<string, string> = {
  sol: t("☉"),
  lua: t("☽"),
  mercurio: t("☿"),
  venus: t("♀"),
  marte: t("♂"),
  jupiter: t("♃"),
  saturno: t("♄"),
  urano: t("♅"),
  netuno: t("♆"),
  plutao: t("♇"),
  nodo_norte_verdadeiro: t("☊"),
  nodo_sul_verdadeiro: t("☋"),
  chiron: t("⚷"),
  ascendente: "AC",
  meio_do_ceu: "MC",
  descendente: "DC",
  fundo_do_ceu: "IC",
};
