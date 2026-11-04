import { test } from "node:test";
import assert from "node:assert/strict";
import { cliente, clientes } from "../src/content/clientes";
import { faq } from "../src/content/faq";
import { tools } from "../src/content/tools";
import { gerarLlmsFull, gerarLlmsTxt } from "../src/lib/llms";
import { site } from "../src/lib/site";

test("llms.txt: título, endpoint, 9 tools, 7 guias e privacidade", () => {
  const txt = gerarLlmsTxt();
  assert.ok(txt.startsWith("# Céu Natal\n"));
  assert.ok(txt.includes(site.mcpEndpoint));
  assert.equal(tools.length, 9);
  for (const t of tools) assert.ok(txt.includes(t.nome), t.nome);
  assert.equal(clientes.length, 7);
  for (const c of clientes) assert.ok(txt.includes(`${site.url}/conectar/${c.slug}`), c.slug);
  assert.ok(txt.includes(`${site.url}/privacidade`));
});

test("llms-full.txt: passos dos guias, FAQ e política de privacidade", () => {
  const full = gerarLlmsFull();
  assert.ok(full.startsWith(gerarLlmsTxt()));
  assert.ok(full.includes("Política de privacidade"));
  const claudeAi = cliente("claude-ai");
  assert.ok(claudeAi);
  assert.ok(full.includes(claudeAi.passos[0]));
  assert.ok(full.includes(faq[0].pergunta));
});
