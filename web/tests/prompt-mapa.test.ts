import { test } from "node:test";
import assert from "node:assert/strict";
import { promptMapa } from "../src/lib/prompt-mapa";
import { dataValida, signoSolar } from "../src/lib/signo-solar";
import { glifoPonto } from "../src/lib/glifos";
import { site } from "../src/lib/site";
import type { MapaRapido } from "../src/lib/mapa-texto";

test("signoSolar: signo pelo dia e mês, com cúspide na troca", () => {
  assert.deepEqual(signoSolar(15, 5), { signo: "Touro", cuspide: false });
  assert.deepEqual(signoSolar(10, 1), { signo: "Capricórnio", cuspide: false });
  assert.deepEqual(signoSolar(20, 1), { signo: "Aquário", cuspide: true });
  assert.deepEqual(signoSolar(19, 1), { signo: "Capricórnio", cuspide: true });
  assert.deepEqual(signoSolar(1, 3), { signo: "Peixes", cuspide: false });
  assert.equal(signoSolar(31, 4), null);
  assert.equal(signoSolar(1, 13), null);
});

test("dataValida: 29/02 só em ano bissexto e anos de 1800 a 2100", () => {
  assert.ok(dataValida(29, 2, 2000));
  assert.ok(!dataValida(29, 2, 1900));
  assert.ok(!dataValida(1, 1, 1799));
  assert.ok(dataValida(31, 12, 2100));
});

const vazio = { dia: "", mes: "", ano: "", hora: "", cidade: "", solPelaData: null, mapa: null };

test("prompt só com dia e mês: sol pela data e pede o que falta", () => {
  const p = promptMapa({ ...vazio, dia: "5", mes: "8", solPelaData: { signo: "Leão", cuspide: false } });
  assert.ok(p.startsWith("# Meu mapa natal\n\n**Nascimento:** 05/08 (ainda sem o ano), sem hora, sem cidade"));
  assert.ok(p.includes(`- ${glifoPonto.sol} **Sol:** Leão (pelo dia e mês)`));
  // Mapa primeiro, instruções depois.
  assert.ok(p.indexOf("**Sol:**") < p.indexOf("## Instruções para a IA"));
  assert.ok(p.includes("Ainda falta a data completa, a hora e a cidade."));
  assert.ok(p.includes(site.mcpEndpoint));
  assert.ok(p.includes("### Sobre o Céu Natal"));
});

test("prompt com o mapa completo: seções em markdown e nada faltando", () => {
  const mapa: MapaRapido = {
    nascimento: { data: "15/05/1990", hora: "14:30", local: "Belo Horizonte, MG" },
    sistema_casas: "Placidus",
    planetas: { sol: { signo: "Touro", grau: "24°10'", casa: 9 } },
    angulos: { ascendente: { signo: "Virgem", grau: "3°02'" } },
    casas: { casa_1: { signo: "Virgem", grau: "3°02'" } },
    aspectos: [
      { planeta_a: "sol", planeta_b: "lua", tipo: "trigono", orbe: 1.5 },
      { planeta_a: "nodo_norte_verdadeiro", planeta_b: "nodo_sul_verdadeiro", tipo: "oposicao", orbe: 0 },
    ],
  };
  const p = promptMapa({ ...vazio, dia: "15", mes: "05", ano: "1990", hora: "14:30", cidade: "Belo Horizonte, MG", mapa });
  assert.ok(p.includes(`- ${glifoPonto.sol} **Sol:** 24°10' Touro, casa 9`));
  assert.ok(p.includes(`- AC **Ascendente:** 3°02' Virgem`));
  assert.ok(p.includes("### Ângulos"));
  assert.ok(p.includes("### Cúspides das casas (Placidus)"));
  assert.ok(p.includes("- Sol trígono Lua (orbe 1°30')"));
  assert.ok(!p.includes("Nodo Norte oposição"));
  assert.ok(!p.includes("Ainda falta"));
  assert.ok(!p.includes("ainda não há ascendente"));
});
