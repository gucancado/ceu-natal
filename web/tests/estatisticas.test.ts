import { test } from "node:test";
import assert from "node:assert/strict";
import { interpretarEstatisticas, lerEstatisticas, nomePais } from "../src/lib/estatisticas";

const exemplo = {
  desde: "2026-11-11",
  atualizado_em: "2026-11-11T12:00:00+00:00",
  totais: {
    chamadas: 10, calculos: 8, taxa_erro: 0.1, tempo_medio_ms: 120.5,
    cidades: 4, paises: 2, pessoas_dia_site: 3, sessoes_mcp: 5,
  },
  por_dia: [{ dia: "2026-11-11", calculos: 8, pessoas_site: 3, sessoes_mcp: 5 }],
  por_origem: { mcp: 6, site: 2 },
  por_ferramenta: [{ ferramenta: "calcular_mapa_natal", chamadas: 7 }],
  por_app: [{ app: "Claude", chamadas: 6 }],
  paises: [{ pais: "BR", chamadas: 8 }],
};

test("interpreta a resposta do servidor", () => {
  const e = interpretarEstatisticas(exemplo);
  assert.ok(e);
  assert.equal(e.totais.calculos, 8);
  assert.equal(e.porDia[0].pessoasSite, 3);
  assert.deepEqual(e.porApp, [{ rotulo: "Claude", chamadas: 6 }]);
  assert.deepEqual(e.porOrigem, { mcp: 6, site: 2 });
});

test("resposta sem totais vira null", () => {
  assert.equal(interpretarEstatisticas({ erro: "x" }), null);
  assert.equal(interpretarEstatisticas(null), null);
});

test("lerEstatisticas devolve null com o servidor fora ou desligado", async () => {
  assert.equal(await lerEstatisticas("https://m", async () => new Response("x", { status: 503 })), null);
  assert.equal(
    await lerEstatisticas("https://m", async () => {
      throw new Error("rede");
    }),
    null,
  );
  const ok = await lerEstatisticas("https://m", async () => new Response(JSON.stringify(exemplo)));
  assert.equal(ok?.totais.chamadas, 10);
});

test("nomePais", () => {
  assert.equal(nomePais("BR"), "Brasil");
  assert.equal(nomePais("outros"), "outros");
});
