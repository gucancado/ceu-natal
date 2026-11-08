import assert from "node:assert/strict";
import { test } from "node:test";
import { scriptCopiar } from "../src/lib/script-copiar";

// Roda o script com um DOM mínimo e dispara um clique no botão de copiar.
async function clicar(clipboard: unknown, execOk: boolean) {
  let aoClicar: (e: unknown) => void = () => {};
  const atributos: Record<string, string> = {};
  const caixa = {
    setAttribute: (k: string, v: string) => (atributos[k] = v),
    removeAttribute: (k: string) => delete atributos[k],
  };
  const botao = {
    parentNode: caixa,
    getAttribute: (k: string) => (k === "data-copiar" ? "o prompt" : null),
    closest: () => botao,
  };
  const area = { value: "", style: {}, select() {}, remove() {} };
  let copiadoAntigo = "";
  const documento = {
    activeElement: null,
    addEventListener: (_: string, f: (e: unknown) => void) => (aoClicar = f),
    createElement: () => area,
    body: { appendChild() {} },
    execCommand: () => {
      copiadoAntigo = area.value;
      return execOk;
    },
    getElementById: () => null,
  };
  const relogio = () => 0;
  new Function("document", "navigator", "window", "setTimeout", "clearTimeout", scriptCopiar)(
    documento,
    { clipboard },
    { getSelection: () => ({ selectAllChildren() {} }) },
    relogio,
    relogio,
  );
  aoClicar({ target: botao });
  await new Promise((r) => setImmediate(r));
  return { estado: atributos["data-estado"], copiadoAntigo };
}

test("copia pela Clipboard API e marca copiado", async () => {
  let recebido = "";
  const r = await clicar({ writeText: async (t: string) => void (recebido = t) }, false);
  assert.equal(recebido, "o prompt");
  assert.equal(r.estado, "copiado");
  assert.equal(r.copiadoAntigo, "");
});

test("Clipboard API recusada: copia pelo caminho antigo", async () => {
  const r = await clicar({ writeText: () => Promise.reject(new Error("NotAllowedError")) }, true);
  assert.equal(r.copiadoAntigo, "o prompt");
  assert.equal(r.estado, "copiado");
});

test("sem Clipboard API: copia pelo caminho antigo", async () => {
  const r = await clicar(undefined, true);
  assert.equal(r.copiadoAntigo, "o prompt");
  assert.equal(r.estado, "copiado");
});

test("nada copiou: marca falha em vez de fingir sucesso", async () => {
  const r = await clicar(undefined, false);
  assert.equal(r.estado, "falhou");
});
