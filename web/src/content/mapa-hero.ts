// Mapa exibido no hero: fundação de Brasília. Valores calculados pelo servidor em 2026-11-03.
export type LinhaMapa = {
  glifo: string;
  corpo: string;
  signo: string;
  grau: string;
  casa: number | null;
  retrogrado: boolean;
};

export type MapaHero = {
  titulo: string;
  nascimento: string;
  linhas: LinhaMapa[];
  angulos: { ascendente: string; meioDoCeu: string };
};

export const mapaHero: MapaHero = {
  titulo: "Brasília",
  nascimento: "21/04/1960, 09:30, Brasília, DF",
  linhas: [
    { glifo: "☉", corpo: "Sol", signo: "Touro", grau: "1°24'", casa: 11, retrogrado: false },
    { glifo: "☽", corpo: "Lua", signo: "Peixes", grau: "9°15'", casa: 9, retrogrado: false },
    { glifo: "☿", corpo: "Mercúrio", signo: "Áries", grau: "7°40'", casa: 10, retrogrado: false },
    { glifo: "♀", corpo: "Vênus", signo: "Áries", grau: "14°52'", casa: 10, retrogrado: false },
    { glifo: "♂", corpo: "Marte", signo: "Peixes", grau: "14°50'", casa: 9, retrogrado: false },
    { glifo: "♃", corpo: "Júpiter", signo: "Capricórnio", grau: "3°37'", casa: 7, retrogrado: true },
    { glifo: "♄", corpo: "Saturno", signo: "Capricórnio", grau: "18°24'", casa: 8, retrogrado: false },
    { glifo: "♅", corpo: "Urano", signo: "Leão", grau: "16°56'", casa: 3, retrogrado: true },
    { glifo: "♆", corpo: "Netuno", signo: "Escorpião", grau: "7°57'", casa: 5, retrogrado: true },
    { glifo: "♇", corpo: "Plutão", signo: "Virgem", grau: "3°43'", casa: 3, retrogrado: true },
  ],
  angulos: { ascendente: "13°49' Gêmeos", meioDoCeu: "18°12' Peixes" },
};
