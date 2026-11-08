import fs from "node:fs";
import path from "node:path";
import type { Metadata } from "next";
import { Markdown } from "@/components/markdown";

export const metadata: Metadata = {
  title: "Termos de uso",
  description: "Regras de uso do serviço gratuito do Céu Natal.",
};

export default function Termos() {
  const texto = fs.readFileSync(path.join(process.cwd(), "src/content/legal/termos.md"), "utf8");
  return (
    <article className="mx-auto max-w-[72rem] px-6 py-16 md:py-24">
      <Markdown texto={texto} />
    </article>
  );
}
