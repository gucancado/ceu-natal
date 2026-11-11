import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { cliente, clientes } from "../src/content/clientes";
import { faq } from "../src/content/faq";
import { tools } from "../src/content/tools";
import { gerarLlmsFull, gerarLlmsTxt } from "../src/lib/llms";
import { site } from "../src/lib/site";

test("llms.txt: título, endpoint, 9 tools, 8 guias e privacidade", () => {
  const txt = gerarLlmsTxt();
  assert.ok(txt.startsWith("# Céu Natal\n"));
  assert.ok(txt.includes(site.mcpEndpoint));
  assert.equal(tools.length, 9);
  for (const t of tools) assert.ok(txt.includes(t.nome), t.nome);
  assert.equal(clientes.length, 8);
  for (const c of clientes) assert.ok(txt.includes(`${site.url}/?cliente=${c.slug}#conectar`), c.slug);
  assert.ok(txt.includes(`${site.url}/privacidade`));
  assert.ok(txt.includes(String(site.limites.porSessaoPorMin)));
  assert.ok(txt.includes(String(site.limites.globalPorMin)));
  assert.ok(txt.includes("90 dias"));
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

test("llms-full.txt: política na íntegra, sem o H1 do arquivo", () => {
  const full = gerarLlmsFull();
  const md = readFileSync(join(process.cwd(), "src/content/legal/privacidade.md"), "utf8");
  const linhas = md.split(/\r?\n/);
  const h1 = linhas.find((l) => l.startsWith("# "));
  const primeira = linhas.find((l) => l.trim() !== "" && !l.startsWith("#"));
  assert.ok(h1 && primeira);
  assert.ok(full.includes(primeira.trim()));
  assert.ok(!full.includes(h1));
});
