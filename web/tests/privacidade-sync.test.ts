import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { contato } from "../src/lib/site";

test("política do site é idêntica à canônica", (t) => {
  const canonica = path.resolve(__dirname, "../../docs/legal/privacidade.md");
  // Dentro do Docker só existe a cópia.
  if (!fs.existsSync(canonica)) {
    t.skip("docs/ ausente");
    return;
  }
  assert.equal(
    fs.readFileSync(path.resolve(__dirname, "../src/content/legal/privacidade.md"), "utf8"),
    fs.readFileSync(canonica, "utf8"),
  );
});

test("política traz o email de contato em texto, nas duas ocorrências", () => {
  const texto = fs.readFileSync(path.resolve(__dirname, "../src/content/legal/privacidade.md"), "utf8");
  assert.ok(texto.includes(`Contato: ${contato.email}`));
  assert.ok(texto.includes(`escreva para ${contato.email}`));
  assert.ok(!texto.includes("rodapé"));
});
