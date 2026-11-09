import assert from "node:assert/strict";
import { test } from "node:test";
import { scriptEmail } from "../src/lib/script-email";

function clicar(atributos: Record<string, string>, comLink = true) {
  let aoClicar: (e: unknown) => void = () => {};
  let cancelado = false;
  const local = { href: "" };
  const link = { getAttribute: (k: string) => atributos[k] ?? null };
  new Function("document", "location", scriptEmail)(
    { addEventListener: (_: string, f: (e: unknown) => void) => (aoClicar = f) },
    local,
  );
  aoClicar({ target: { closest: () => (comLink ? link : null) }, preventDefault: () => (cancelado = true) });
  return { href: local.href, cancelado };
}

const base = { "data-email-usuario": "fulana", "data-email-dominio": "exemplo.com" };

test("monta o mailto no clique", () => {
  assert.deepEqual(clicar(base), { href: "mailto:fulana@exemplo.com", cancelado: true });
});

test("codifica o assunto", () => {
  const { href } = clicar({ ...base, "data-email-assunto": "Céu Natal" });
  assert.equal(href, "mailto:fulana@exemplo.com?subject=C%C3%A9u%20Natal");
});

test("ignora cliques fora do link", () => {
  assert.deepEqual(clicar(base, false), { href: "", cancelado: false });
});
