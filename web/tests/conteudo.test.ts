import { test } from "node:test";
import assert from "node:assert/strict";
import { tools } from "../src/content/tools";
import { prompts } from "../src/content/prompts";
import { faq } from "../src/content/faq";

test("9 tools, prompts do hero com tools existentes, 5 FAQ", () => {
  assert.equal(tools.length, 9);
  assert.equal(new Set(tools.map((t) => t.nome)).size, 9);
  assert.ok(tools.some((t) => t.nome === "calcular_mapa_natal" && t.grupo === "natal"));
  assert.ok(prompts.length >= 5);
  const nomes = new Set(tools.map((t) => t.nome));
  assert.ok(prompts.every((p) => nomes.has(p.tool)));
  assert.equal(new Set(prompts.map((p) => p.texto)).size, prompts.length);
  assert.equal(faq.length, 5);
  assert.ok(faq.some((f) => f.resposta.includes("/privacidade")));
});

test("a FAQ não fala em cancelar", () => {
  assert.ok(faq.every((f) => !/cancel/i.test(`${f.pergunta} ${f.resposta}`)));
});
