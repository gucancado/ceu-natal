import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { normalizar, sugerirCidades, type Municipio } from "../src/lib/cidades";

const lista = JSON.parse(readFileSync(join(process.cwd(), "public/municipios.json"), "utf8")) as Municipio[];
const primeira = (q: string) => sugerirCidades(lista, q)[0];

test("lista do IBGE com todos os municípios, do mais populoso para o menos", () => {
  assert.ok(lista.length > 5500);
  assert.deepEqual(lista[0], ["São Paulo", "SP"]);
});

test("iniciais e apelidos: bh, jf, poa, floripa", () => {
  assert.deepEqual(primeira("bh"), ["Belo Horizonte", "MG"]);
  assert.deepEqual(primeira("jf"), ["Juiz de Fora", "MG"]);
  assert.deepEqual(primeira("poa"), ["Porto Alegre", "RS"]);
  assert.deepEqual(primeira("floripa"), ["Florianópolis", "SC"]);
});

test("começo do nome, sem acento, e filtro por UF depois da vírgula", () => {
  assert.deepEqual(primeira("sao"), ["São Paulo", "SP"]);
  assert.deepEqual(primeira("belo h"), ["Belo Horizonte", "MG"]);
  assert.deepEqual(primeira("santa maria, rs"), ["Santa Maria", "RS"]);
  assert.deepEqual(primeira("campo grande"), ["Campo Grande", "MS"]);
  assert.equal(sugerirCidades(lista, "b").length, 0);
  assert.ok(sugerirCidades(lista, "santa").length <= 6);
});

test("normalizar tira acento, caixa e pontuação", () => {
  assert.equal(normalizar("  São  João d'Aliança "), "sao joao d alianca");
});
