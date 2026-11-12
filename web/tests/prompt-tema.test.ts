import { test } from "node:test";
import assert from "node:assert/strict";
import {
  promptRevolucaoSolar,
  promptSinastria,
  promptTransitos,
  type ResultadoRevolucao,
  type ResultadoSinastria,
  type ResultadoTransitos,
} from "../src/lib/prompt-tema";
import { site } from "../src/lib/site";

// Recortes de respostas reais do servidor (dados fictícios).
const nasc = { data: "12/03/1990", hora: "14:30", cidade: "Belo Horizonte, MG" };

const transitos: ResultadoTransitos = {
  transito: { data: "12/11/2026" },
  planetas_em_transito: {
    sol: { signo: "Escorpiao", grau: "20°06'", retrogrado: false, casa_natal: 4 },
    saturno: { signo: "Aries", grau: "8°38'", retrogrado: true, casa_natal: 9 },
  },
  aspectos_transito_natal: [
    { planeta_transito: "saturno", planeta_natal: "urano", tipo: "quadratura", orbe: 0.5045, aplicando: false },
    { planeta_transito: "urano", planeta_natal: "nodo_sul_verdadeiro", tipo: "quintil", orbe: 0.16, aplicando: true },
    { planeta_transito: "sol", planeta_natal: "sol", tipo: "trigono", orbe: 1.764, aplicando: true },
    { planeta_transito: "lua", planeta_natal: "jupiter", tipo: "oposicao", orbe: 5.41, aplicando: true },
  ],
  sintese: {
    transitos_lentos_destacados: [
      { planeta_transito: "urano", planeta_natal: "nodo_sul_verdadeiro", tipo: "quintil", orbe: 0.16 },
      { planeta_transito: "saturno", planeta_natal: "urano", tipo: "quadratura", orbe: 0.5045 },
    ],
  },
};

test("trânsitos: lentos primeiro, outros até 3° sem repetir, céu do dia com casa natal", () => {
  const p = promptTransitos(nasc, "12/11/2026", transitos);
  assert.match(p, /^# Meus trânsitos de 12\/11\/2026/);
  assert.match(p, /- Saturno em trânsito quadratura Urano natal \(orbe 0°30', separando\)/);
  assert.match(p, /- Sol em trânsito trígono Sol natal \(orbe 1°46', aplicando\)/);
  assert.equal(p.match(/Saturno em trânsito quadratura Urano/g)?.length, 1);
  assert.doesNotMatch(p, /Nodo Sul/);
  assert.doesNotMatch(p, /Lua em trânsito oposição/);
  assert.match(p, /\*\*Saturno:\*\* 8°38' Áries, na casa 9 natal, retrógrado/);
  assert.ok(p.includes(site.mcpEndpoint));
});

test("trânsitos: sem resultado, pede o que falta", () => {
  const p = promptTransitos({ data: "", hora: "", cidade: "" }, "12/11/2026", null);
  assert.match(p, /Ainda não calculado/);
  assert.match(p, /Ainda falta a data, a hora e a cidade/);
});

const sinastria: ResultadoSinastria = {
  pessoa_a: { sol: "Peixes", lua: "Libra", asc: "Cancer" },
  pessoa_b: { sol: "Leao", lua: "Gemeos", asc: null },
  aspectos_sinastria: [
    { planeta_a: "sol", planeta_b: "lua", tipo: "quintil", orbe: 0.2357 },
    { planeta_a: "nodo_sul_verdadeiro", planeta_b: "lua", tipo: "quintil", orbe: 0.04 },
    { planeta_a: "sol", planeta_b: "jupiter", tipo: "oposicao", orbe: 7.97 },
  ],
  ativacoes_de_casas: [],
  sintese_sinastria: { aspectos_harmonicos: 14, aspectos_tensao: 23, aspectos_neutros: 21 },
};

test("sinastria: resumo das duas pessoas, aspectos fortes e aviso de casas", () => {
  const p = promptSinastria(nasc, { data: "25/07/1992", hora: "", cidade: "" }, sinastria);
  assert.match(p, /\*\*Pessoa 1 \(eu\):\*\* .*Sol em Peixes, Lua em Libra, ascendente em Câncer/);
  assert.match(p, /\*\*Pessoa 2:\*\* 25\/07\/1992, sem hora, sem cidade \(Sol em Leão, Lua em Gêmeos\)/);
  assert.match(p, /14 harmônicos, 23 tensos e 21 neutros/);
  assert.match(p, /- Sol da pessoa 1 quintil Lua da pessoa 2 \(orbe 0°14'\)/);
  assert.doesNotMatch(p, /Nodo Sul|Júpiter da pessoa 2/);
  assert.match(p, /ainda não dá para ver os planetas de um nas casas do outro/);
  assert.match(p, /Ainda falta a hora da pessoa 2 e a cidade da pessoa 2/);
});

const revolucao: ResultadoRevolucao = {
  ano: 2026,
  revolucao: {
    instante_local: "2026-03-12T08:05:25-03:00",
    local: "Belo Horizonte, MG",
    vigencia: { fim_aproximado_utc: "2027-03-12T16:54:11+00:00" },
  },
  planetas: { sol: { signo: "Peixes", grau: "21°52'", casa: 11 } },
  angulos: { ascendente: { signo: "Aries", grau: "21°07'" } },
  aspectos_revolucao_natal: [
    { planeta_revolucao: "sol", planeta_natal: "sol", tipo: "conjuncao", orbe: 0, definicional: true },
    { planeta_revolucao: "netuno", planeta_natal: "jupiter", tipo: "quadratura", orbe: 0.2408 },
    { planeta_revolucao: "lua", planeta_natal: "jupiter", tipo: "oposicao", orbe: 2.2551 },
  ],
  destaques: {
    ascendente_revolucao: { signo: "Aries", grau: "21°07'", regente_moderno: "marte", regente_tradicional: "marte", casa_natal_onde_cai: 9 },
    sol_revolucao: { casa_revolucao: 11, casa_natal: 8 },
    lua_revolucao: { signo: "Capricornio", grau: "3°28'", casa_revolucao: 9, casa_natal: 6 },
    planetas_angulares: ["plutao"],
  },
};

test("revolução solar: instante local, vigência, destaques e aspectos até 2° sem o definicional", () => {
  const p = promptRevolucaoSolar(nasc, "2026", "", revolucao);
  assert.match(p, /^# Minha revolução solar de 2026/);
  assert.match(p, /12\/03\/2026 às 08:05 \(horário local\), em Belo Horizonte, MG; vale até por volta de 12\/03\/2027/);
  assert.match(p, /\*\*Ascendente da revolução:\*\* 21°07' Áries, regente Marte; cai na casa 9 natal/);
  assert.match(p, /casa 11 da revolução, casa 8 natal/);
  assert.match(p, /\*\*Planetas angulares:\*\* Plutão/);
  assert.match(p, /- Netuno da revolução quadratura Júpiter natal/);
  assert.doesNotMatch(p, /Sol da revolução conjunção Sol natal|Lua da revolução oposição/);
});
