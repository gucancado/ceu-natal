import fs from "node:fs";
import path from "node:path";
import type { Metadata } from "next";
import { Markdown } from "@/components/markdown";

export const metadata: Metadata = {
  title: "Política de privacidade",
  description: "O que o servidor do Céu Natal faz com os dados que o seu assistente de IA envia.",
};

export default function Privacidade() {
  const texto = fs.readFileSync(path.join(process.cwd(), "src/content/legal/privacidade.md"), "utf8");
  return (
    <article className="mx-auto max-w-[72rem] px-6 py-16 md:py-24">
      <Markdown texto={texto} />
    </article>
  );
}
