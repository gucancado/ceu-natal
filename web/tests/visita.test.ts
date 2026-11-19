import { test } from "node:test";
import assert from "node:assert/strict";
import { corpoVisita, hostReferencia } from "../src/lib/visita";

test("referência guarda só o host de outro site", () => {
  assert.equal(hostReferencia("https://www.google.com/search?q=mapa+astral", "ceunatal.test"), "www.google.com");
  assert.equal(hostReferencia("https://ceunatal.test/sinastria", "ceunatal.test"), "");
  assert.equal(hostReferencia("", "ceunatal.test"), "");
  assert.equal(hostReferencia("lixo", "ceunatal.test"), "");
});

test("corpo leva página e referência; robô e não-rastrear não contam", () => {
  assert.deepEqual(JSON.parse(corpoVisita("/sinastria", "https://chatgpt.com/c/1", "ceunatal.test")!), {
    pagina: "/sinastria",
    referencia: "chatgpt.com",
  });
  assert.equal(corpoVisita("/", "", "ceunatal.test", { webdriver: true }), null);
  assert.equal(corpoVisita("/", "", "ceunatal.test", { doNotTrack: "1" }), null);
  assert.equal(corpoVisita("/", "", "ceunatal.test", { gpc: true }), null);
});
