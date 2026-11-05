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
