import { test } from "node:test";
import assert from "node:assert/strict";
import { cliente, clientes } from "../src/content/clientes";
import { site } from "../src/lib/site";

test("7 clientes com slugs únicos, passos e pelo menos 1 fonte", () => {
  assert.deepEqual(
    clientes.map((c) => c.slug),
    ["claude-ai", "claude-desktop", "claude-code", "chatgpt", "gemini", "cursor", "n8n"],
  );
  assert.equal(new Set(clientes.map((c) => c.slug)).size, 7);
  for (const c of clientes) {
    assert.ok(c.nome && c.resumo && c.planoMinimo, c.slug);
    assert.ok(c.passos.length > 0, c.slug);
    assert.ok(c.fontes.length > 0, c.slug);
    assert.ok(c.fontes.every((f) => f.titulo && /^https:\/\//.test(f.url)), c.slug);
    assert.ok(["alta", "media", "baixa"].includes(c.confianca), c.slug);
  }
});

test("snippets usam o endpoint do site, não URL literal", () => {
  for (const c of clientes)
    if (c.snippet)
      assert.ok(
        c.snippet.codigo.includes(site.mcpEndpoint) || c.snippet.codigo.includes(site.sseEndpoint),
        c.slug,
      );
});

test("cliente('chatgpt') existe e cliente('x') é undefined", () => {
  assert.equal(cliente("chatgpt")?.nome, "ChatGPT");
  assert.equal(cliente("x"), undefined);
});

test("ChatGPT e Gemini levam o aviso de confiança; ChatGPT com a linha de planos decidida", () => {
  assert.notEqual(cliente("chatgpt")?.confianca, "alta");
  assert.notEqual(cliente("gemini")?.confianca, "alta");
  assert.equal(
    cliente("chatgpt")?.planoMinimo,
    "Disponível nos planos Business, Enterprise e Edu; no Pro, só ferramentas de leitura (as do Céu Natal são todas de leitura); no Plus, confira na sua conta.",
  );
});
