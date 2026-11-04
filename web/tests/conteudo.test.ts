import { test } from "node:test";
import assert from "node:assert/strict";
import { tools } from "../src/content/tools";
import { prompts } from "../src/content/prompts";
import { faq } from "../src/content/faq";
import { mapaHero } from "../src/content/mapa-hero";

test("9 tools, 3 prompts com tools distintas, 6 FAQ, 10 corpos no hero", () => {
  assert.equal(tools.length, 9);
  assert.equal(new Set(tools.map((t) => t.nome)).size, 9);
  assert.ok(tools.some((t) => t.nome === "calcular_mapa_natal" && t.grupo === "natal"));
  assert.equal(prompts.length, 3);
  assert.equal(new Set(prompts.map((p) => p.tool)).size, 3);
  const nomes = new Set(tools.map((t) => t.nome));
  assert.ok(prompts.every((p) => nomes.has(p.tool)));
  assert.equal(faq.length, 6);
  assert.ok(faq.some((f) => f.resposta.includes("/privacidade")));
  assert.equal(mapaHero.linhas.length, 10);
});

test("hero: 4 retrógrados e ascendente 13°49' Gêmeos", () => {
  assert.equal(mapaHero.linhas.filter((l) => l.retrogrado).length, 4);
  assert.equal(mapaHero.angulos.ascendente, "13°49' Gêmeos");
  assert.equal(mapaHero.angulos.meioDoCeu, "18°12' Peixes");
  assert.equal(mapaHero.titulo, "Brasília");
  assert.equal(mapaHero.nascimento, "21/04/1960, 09:30, Brasília, DF");
  assert.deepEqual(mapaHero.linhas[0], {
    glifo: "☉", corpo: "Sol", signo: "Touro", grau: "1°24'", casa: 11, retrogrado: false,
  });
  assert.deepEqual(
    mapaHero.linhas.filter((l) => l.retrogrado).map((l) => l.corpo),
    ["Júpiter", "Urano", "Netuno", "Plutão"],
  );
});
