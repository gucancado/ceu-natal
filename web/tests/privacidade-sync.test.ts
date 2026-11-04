import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

test("política do site é idêntica à canônica", () => {
  const canonica = path.resolve(__dirname, "../../docs/legal/privacidade.md");
  if (!fs.existsSync(canonica)) return; // dentro do Docker só existe a cópia
  assert.equal(
    fs.readFileSync(path.resolve(__dirname, "../src/content/legal/privacidade.md"), "utf8"),
    fs.readFileSync(canonica, "utf8"),
  );
});
