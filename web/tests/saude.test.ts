import { test } from "node:test";
import assert from "node:assert/strict";
import { lerSaude } from "../src/lib/saude";

test("lerSaude ok", async () => {
  const r = await lerSaude("https://m", async () =>
    new Response(JSON.stringify({ versao: "2.1.0", limites: { por_sessao_por_min: 30, global_por_min: 600 } })),
  );
  assert.equal(r.ok, true);
  if (r.ok) {
    assert.equal(r.versao, "2.1.0");
    assert.deepEqual(r.limites, { por_sessao_por_min: 30, global_por_min: 600 });
  }
});

test("lerSaude fora do ar", async () => {
  const r = await lerSaude("https://m", async () => {
    throw new Error("rede");
  });
  assert.equal(r.ok, false);
});

test("lerSaude 5xx", async () => {
  const r = await lerSaude("https://m", async () => new Response("x", { status: 503 }));
  assert.equal(r.ok, false);
});
