import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { cliente, clientes, clientesDaGrade } from "../src/content/clientes";
import { site } from "../src/lib/site";
import { partesTextoGuia } from "../src/lib/texto-guia";

test("a home mostra um botão só para o Claude e o Manus depois do Gemini", () => {
  assert.deepEqual(
    clientesDaGrade.map((c) => c.nome),
    ["Claude", "ChatGPT", "Gemini", "Manus", "Cursor", "n8n"],
  );
});

test("8 clientes com slugs únicos, passos e pelo menos 1 fonte", () => {
  assert.deepEqual(
    clientes.map((c) => c.slug),
    ["claude-ai", "claude-desktop", "claude-code", "chatgpt", "gemini", "manus", "cursor", "n8n"],
  );
  assert.equal(new Set(clientes.map((c) => c.slug)).size, 8);
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
        c.snippet.codigo.includes(site.mcpEndpoint),
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
    "Testado e funcionando no Plus. No Pro, só ferramentas de leitura (as do Céu Natal são todas de leitura). Em Business, Enterprise e Edu, depende do administrador.",
  );
});

test("host do servidor MCP só entra via site.*, nunca literal", () => {
  const host = "astrologia-mcp.gustavocancado.com.br";
  // Fonte: nenhum módulo de cliente escreve o host à mão.
  const dir = join(dirname(fileURLToPath(import.meta.url)), "../src/content/clientes");
  for (const f of readdirSync(dir)) assert.ok(!readFileSync(join(dir, f), "utf8").includes(host), f);
  // Texto renderizado: fora das interpolações de site.mcpEndpoint, o host não aparece.
  for (const c of clientes)
    for (const s of [c.resumo, ...c.passos, ...c.limitacoes]) {
      const resto = s.split(site.mcpEndpoint).join("");
      assert.ok(!resto.includes(host), `${c.slug}: ${s}`);
    }
});

test("partesTextoGuia: `código` vira código, **menu** vira menu, o resto é texto", () => {
  assert.deepEqual(partesTextoGuia("Abra **Configurações › Conectores** e cole `https://x.y/mcp/`."), [
    { tipo: "texto", texto: "Abra " },
    { tipo: "menu", texto: "Configurações › Conectores" },
    { tipo: "texto", texto: " e cole " },
    { tipo: "codigo", texto: "https://x.y/mcp/" },
    { tipo: "texto", texto: "." },
  ]);
  assert.deepEqual(partesTextoGuia("sem marcação * nem ` solto"), [
    { tipo: "texto", texto: "sem marcação * nem ` solto" },
  ]);
});

test("todo guia de conexão tem passos em inglês para a /en", async () => {
  const { guiasEn } = await import("../src/content/clientes/en");
  for (const c of clientes) {
    const en = guiasEn[c.slug];
    assert.ok(en && en.passos.length > 0, c.slug);
    if (c.abrir) assert.ok(en.abrir, `${c.slug} sem rótulo do botão em inglês`);
  }
});
