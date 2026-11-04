import { test } from "node:test";
import assert from "node:assert/strict";
import { grauMinuto, textoMapa, type MapaRapido } from "../src/lib/mapa-texto";
import { promptSetup } from "../src/content/setup";
import { site } from "../src/lib/site";

const completo: MapaRapido = {
  nascimento: { data: "15/05/1990", hora: "14:30", local: "Belo Horizonte, MG" },
  sistema_casas: "Placidus",
  planetas: {
    sol: { signo: "Touro", grau: "24°37'", casa: 8, retrogrado: false },
    mercurio: { signo: "Touro", grau: "7°59'", casa: 8, retrogrado: true },
    lua: { signo: "Capricornio", grau: "30°00'", casa: 5 },
  },
  pontos_sensiveis: { chiron: { signo: "Cancer", grau: "13°14'", casa: 10 } },
  angulos: { ascendente: { signo: "Libra", grau: "2°15'" } },
  casas: { casa_1: { signo: "Libra", grau: "2°15'" }, casa_10: { signo: "Cancer", grau: "1°36'" } },
  aspectos: [
    { planeta_a: "nodo_norte_verdadeiro", planeta_b: "nodo_sul_verdadeiro", tipo: "oposicao", orbe: 0 },
    { planeta_a: "venus", planeta_b: "chiron", tipo: "quadratura", orbe: 0.151 },
  ],
};

test("grauMinuto", () => {
  assert.equal(grauMinuto(0.151), "0°09'");
  assert.equal(grauMinuto(3.6457), "3°39'");
  assert.equal(grauMinuto(0), "0°00'");
});

test("texto do mapa: prompt de integração, acentos, casas e aspectos", () => {
  const t = textoMapa(completo);
  assert.ok(t.includes(site.mcpEndpoint));
  assert.ok(t.includes(`${site.url}/conectar`));
  assert.ok(t.includes("Nascimento: 15/05/1990, 14:30, Belo Horizonte, MG"));
  assert.ok(t.includes("Sistema de casas: Placidus"));
  assert.ok(t.includes("- Sol: 24°37' Touro, casa 8"));
  assert.ok(t.includes("- Mercúrio: 7°59' Touro, casa 8, retrógrado"));
  assert.ok(t.includes("- Lua: 30°00' Capricórnio, casa 5"));
  assert.ok(t.includes("- Quíron: 13°14' Câncer, casa 10"));
  assert.ok(t.includes("- Ascendente: 2°15' Libra"));
  assert.ok(t.includes("- Casa 10: 1°36' Câncer"));
  assert.ok(t.includes("- Vênus quadratura Quíron (orbe 0°09')"));
  assert.ok(!t.includes("Nodo Norte oposição Nodo Sul"));
});

test("texto do mapa sem hora: sem casas nem ângulos", () => {
  const t = textoMapa({ nascimento: { data: "15/05/1990", hora: null, local: null }, planetas: completo.planetas });
  assert.ok(t.includes("Nascimento: 15/05/1990\n"));
  assert.ok(t.includes("Sem hora ou cidade: sem casas nem ângulos."));
  assert.ok(!t.includes("Cúspides"));
  assert.ok(!t.includes("Sistema de casas"));
});

test("prompt de setup: endpoint, guia e healthcheck", () => {
  assert.ok(promptSetup.includes(site.mcpEndpoint));
  assert.ok(promptSetup.includes(`${site.url}/conectar`));
  assert.ok(promptSetup.includes("healthcheck"));
  assert.ok(promptSetup.length < 600);
});
