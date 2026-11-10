import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { site } from "../src/lib/site";

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

test("política aponta o canal de contato nas duas ocorrências, sem endereço de e-mail", () => {
  const texto = fs.readFileSync(path.resolve(__dirname, "../src/content/legal/privacidade.md"), "utf8");
  assert.ok(texto.includes(`Contato: pelos canais em ${site.autorUrl}`));
  assert.ok(texto.includes(`fale comigo pelos canais em ${site.autorUrl}`));
  assert.ok(!texto.includes("rodapé"));
  assert.ok(!texto.includes("@"));
});

test("termos apontam o canal de contato, sem endereço de e-mail", () => {
  const texto = fs.readFileSync(path.resolve(__dirname, "../src/content/legal/termos.md"), "utf8");
  assert.ok(texto.includes(`fale comigo pelos canais em ${site.autorUrl}`));
  assert.ok(!texto.includes("@"));
});
