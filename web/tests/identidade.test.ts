import { test } from "node:test";
import assert from "node:assert/strict";
import { criarIdsDeMapa, idVisitante } from "../src/lib/identidade";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

test("idVisitante guarda e reaproveita o id", () => {
  const mem = new Map<string, string>();
  const s = { getItem: (k: string) => mem.get(k) ?? null, setItem: (k: string, v: string) => void mem.set(k, v) };
  const a = idVisitante(s);
  assert.match(a, UUID);
  assert.equal(idVisitante(s), a);
});

test("idVisitante sem armazenamento usa um id da página", () => {
  const quebrado = {
    getItem: () => {
      throw new Error("bloqueado");
    },
    setItem: () => {},
  };
  const a = idVisitante(quebrado);
  assert.match(a, UUID);
  assert.equal(idVisitante(quebrado), a);
});

test("mesmo mapa enquanto a data não muda", () => {
  const idMapa = criarIdsDeMapa();
  const a = idMapa("01/02/1990");
  assert.equal(idMapa("01/02/1990"), a);
  assert.notEqual(idMapa("05/06/1985"), a);
});
