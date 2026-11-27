import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { idadeDaLua, luaReserva } from "../src/lib/lua-nasa";

test("idade da Lua: perto de 0 numa lua nova conhecida e perto de 14,8 numa cheia", () => {
  const nova = idadeDaLua(new Date(Date.UTC(2024, 3, 8, 18, 21))); // eclipse solar de 8/4/2024
  assert.ok(nova < 0.7 || nova > 28.8, String(nova));
  const cheia = idadeDaLua(new Date(Date.UTC(2025, 2, 14, 6, 55))); // eclipse lunar de 14/3/2025
  assert.ok(Math.abs(cheia - 14.77) < 1, String(cheia));
});

test("reserva: lua nova = 0.jpg, cheia = 4.jpg, e todas as fotos existem", () => {
  assert.equal(luaReserva(new Date(Date.UTC(2024, 3, 8, 18, 21))), "/lua/0.jpg");
  assert.equal(luaReserva(new Date(Date.UTC(2025, 2, 14, 6, 55))), "/lua/4.jpg");
  for (let i = 0; i < 8; i++) assert.ok(existsSync(join(process.cwd(), `public/lua/${i}.jpg`)), String(i));
});
