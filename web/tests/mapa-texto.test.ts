import { test } from "node:test";
import assert from "node:assert/strict";
import { grauMinuto, motivoSemCasas, outroSignoPossivel, textoMapa, type MapaRapido } from "../src/lib/mapa-texto";
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
  assert.ok(t.includes(`${site.url}/#conectar`));
  // Orientações para a IA no fim: o que é e quando sugerir a conexão.
  const ini = t.indexOf("PARA A IA");
  assert.ok(ini > t.indexOf("Calculado em"));
  const fim = t.slice(ini);
  assert.ok(fim.includes(site.mcpEndpoint));
  assert.ok(fim.includes("calcular_transitos") && fim.includes("calcular_sinastria"));
  assert.ok(fim.includes("Sugira conectar"));
  assert.ok(fim.includes(`${site.url}/mapa`));
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
  assert.ok(t.includes("Sem hora e cidade, ainda não há ascendente nem casas."));
  assert.ok(t.includes("calculadas para 12:00 no horário local"));
  assert.ok(!t.includes("Cúspides"));
  assert.ok(!t.includes("Sistema de casas"));
});

test("sem hora com cidade: fala só da hora e marca a Lua e os aspectos dela", () => {
  const t = textoMapa({
    nascimento: { data: "01/01/1990", hora: null, local: "Belo Horizonte, MG" },
    planetas: {
      lua: {
        signo: "Escorpiao", grau: "27°10'", grau_decimal: 27.17,
        posicao_incerta: true, margem_graus: 6.4, signo_pode_mudar: true,
      },
    },
    aspectos: [{ planeta_a: "sol", planeta_b: "lua", tipo: "sextil", orbe: 2, incerto: true }],
  });
  assert.ok(t.includes("Sem hora, ainda não há ascendente nem casas."));
  assert.ok(!t.includes("cidade, ainda"));
  assert.ok(t.includes("- Lua: 27°10' Escorpião, posição incerta, até 6,4° para cada lado; pode estar em Sagitário"));
  assert.ok(t.includes("ela pode estar em Sagitário"));
  assert.ok(t.includes("Não interprete a Lua nem os aspectos dela como certos."));
  assert.ok(t.includes("- Sol sextil Lua (orbe 2°00', incerto)"));
});

test("outroSignoPossivel: perto do início aponta o signo anterior, com volta em Peixes", () => {
  assert.equal(
    outroSignoPossivel({ signo: "Aries", grau: "2°00'", grau_decimal: 2, margem_graus: 6.5, signo_pode_mudar: true }),
    "Peixes",
  );
  assert.equal(
    outroSignoPossivel({ signo: "Aries", grau: "15°00'", grau_decimal: 15, margem_graus: 6.5, signo_pode_mudar: false }),
    null,
  );
});

test("com hora e cidade mas sem casas (latitude): não pede dado que já existe", () => {
  assert.equal(
    motivoSemCasas({ data: "01/01/1990", hora: "10:00", local: "Longyearbyen" }),
    "Nesta latitude não há casas nem ascendente confiáveis.",
  );
  assert.equal(motivoSemCasas({ data: "01/01/1990", hora: "10:00", local: null }), "Sem cidade, ainda não há ascendente nem casas.");
});

test("prompt de setup: endpoint, guia e healthcheck", () => {
  assert.ok(promptSetup.includes(site.mcpEndpoint));
  assert.ok(promptSetup.includes(`${site.url}/#conectar`));
  assert.ok(promptSetup.includes("healthcheck"));
  // Sem conversa picada e terminando no mapa, não na confirmação técnica.
  assert.ok(promptSetup.includes("numa única mensagem"));
  assert.ok(!promptSetup.includes("um passo por vez"));
  assert.ok(promptSetup.includes("data, hora e cidade de nascimento"));
  assert.ok(promptSetup.indexOf("calcular_mapa_natal") > promptSetup.indexOf("healthcheck"));
  assert.ok(promptSetup.includes(`${site.url}/mapa`));
  assert.ok(promptSetup.length < 1600);
});
