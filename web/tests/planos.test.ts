import { test } from "node:test";
import assert from "node:assert/strict";
import { planos, rotuloPreco } from "../src/content/planos";

test("rotuloPreco", () => {
  assert.equal(rotuloPreco(planos.find((p) => p.id === "gratis")!), "Grátis");
  assert.equal(
    rotuloPreco({ id: "pessoal", nome: "Pessoal", paraQuem: "", inclui: [], disponivel: false }),
    "Em breve",
  );
  const brl = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
  const esperado = `${brl.format(19.9)}/mês ou ${brl.format(149)}/ano`;
  const rotulo = rotuloPreco({
    id: "pessoal",
    nome: "Pessoal",
    paraQuem: "",
    inclui: [],
    disponivel: true,
    preco: { mensal: 19.9, anual: 149 },
  });
  assert.equal(rotulo, esperado);
  assert.match(rotulo, /^R\$\s19,90\/mês ou R\$\s149,00\/ano$/);
});

test("nenhum plano publica preço nesta fase", () => assert.ok(planos.every((p) => !p.preco)));

test("três planos na ordem grátis, pessoal, profissional; só o grátis disponível", () => {
  assert.deepEqual(planos.map((p) => p.id), ["gratis", "pessoal", "profissional"]);
  assert.deepEqual(planos.map((p) => p.disponivel), [true, false, false]);
  assert.ok(planos.every((p) => p.inclui.length > 0 && p.paraQuem.length > 0));
});
