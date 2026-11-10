import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { semBarraFinal } from "../src/lib/site";

test("semBarraFinal tira uma ou mais barras finais", () => {
  assert.equal(semBarraFinal("https://x.y/"), "https://x.y");
  assert.equal(semBarraFinal("https://x.y//"), "https://x.y");
  assert.equal(semBarraFinal("https://x.y"), "https://x.y");
});

test("site lê defaults e monta os endpoints", () => {
  // Processo novo, sem as NEXT_PUBLIC_*: o import estático acima já avaliou o módulo com o env atual.
  const env = { ...process.env };
  delete env.NEXT_PUBLIC_SITE_URL;
  delete env.NEXT_PUBLIC_MCP_URL;
  delete env.NEXT_PUBLIC_REPO_URL;
  const saida = execFileSync(
    process.execPath,
    [
      "--import",
      "tsx",
      "--input-type=module",
      "-e",
      'const { site } = await import("./src/lib/site.ts"); console.log(JSON.stringify(site));',
    ],
    { cwd: path.resolve(__dirname, ".."), env, encoding: "utf8" },
  );
  const site = JSON.parse(saida);
  assert.equal(site.mcpUrl, "https://astrologia-mcp.gustavocancado.com.br");
  assert.equal(site.mcpEndpoint, "https://astrologia-mcp.gustavocancado.com.br/mcp/");
  assert.equal(site.url, "https://mistico.gustavocancado.com.br");
  assert.equal(site.repoUrl, "https://github.com/gucancado/ceu-natal");
  assert.equal(site.autorUrl, "https://gustavocancado.com.br");
});
