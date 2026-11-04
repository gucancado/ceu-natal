import { test } from "node:test";
import assert from "node:assert/strict";
import { semBarraFinal } from "../src/lib/site";

test("semBarraFinal tira uma ou mais barras finais", () => {
  assert.equal(semBarraFinal("https://x.y/"), "https://x.y");
  assert.equal(semBarraFinal("https://x.y//"), "https://x.y");
  assert.equal(semBarraFinal("https://x.y"), "https://x.y");
});

test("site lê defaults e monta os endpoints", async () => {
  delete process.env.NEXT_PUBLIC_MCP_URL;
  const { site } = await import("../src/lib/site");
  assert.equal(site.mcpUrl, "https://astrologia-mcp.gustavocancado.com.br");
  assert.equal(site.mcpEndpoint, "https://astrologia-mcp.gustavocancado.com.br/mcp/");
  assert.equal(site.sseEndpoint, "https://astrologia-mcp.gustavocancado.com.br/sse");
  assert.equal(site.url, "https://mistico.gustavocancado.com.br");
});
