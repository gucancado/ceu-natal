import type { Metadata } from "next";
import { Cabecalho } from "@/components/cabecalho";
import { ContadorVisita } from "@/components/contador-visita";
import { EstrelasCadentes } from "@/components/estrelas-cadentes";
import { Rodape } from "@/components/rodape";
import { jetbrainsMono } from "@/lib/fontes";
import type { Idioma } from "@/lib/idioma";
import { alternativaLlms, descricaoSite, imagemOg, site, verificacaoBing } from "@/lib/site";
import { scriptCopiar } from "@/lib/script-copiar";
import "@/app/globals.css";

// Metadata comum aos layouts raiz. Há um layout por idioma (grupos de rota `(pt)` e `(en)`) só para o
// <html lang> sair certo em cada um; o resto do documento é este componente.
export const metadataBase: Metadata = {
  metadataBase: new URL(site.url),
  title: { default: site.nome, template: "%s · Céu Natal" },
  description: descricaoSite,
  // Canonical relativo: resolve para a rota atual via metadataBase.
  alternates: { canonical: "./", types: alternativaLlms },
  authors: [{ name: site.autor, url: site.autorUrl }],
  verification: { other: { "msvalidate.01": verificacaoBing } },
  // A imagem é a do app/opengraph-image.tsx, apontada aqui à mão: com um layout raiz por grupo de rota, a
  // convenção de arquivo na raiz de app/ não chega às páginas.
  // Sem title/description aqui: o Next herda os de cada página (senão toda página teria og:title da home).
  openGraph: {
    type: "website",
    locale: "pt_BR",
    siteName: site.nome,
    url: "./",
    images: [imagemOg],
  },
  twitter: { card: "summary_large_image", images: [imagemOg] },
};

const langDo: Record<Idioma, string> = { pt: "pt-BR", en: "en" };
const pular: Record<Idioma, string> = { pt: "Pular para o conteúdo", en: "Skip to content" };

export function Documento({ idioma, children }: { idioma: Idioma; children: React.ReactNode }) {
  return (
    // Tema único escuro: a classe fica fixa no HTML, sem provedor de tema no cliente.
    <html lang={langDo[idioma]} className={`dark ${jetbrainsMono.variable}`}>
      <body className="text-base leading-[1.6]">
        <script dangerouslySetInnerHTML={{ __html: scriptCopiar }} />
        <EstrelasCadentes />
        <a
          href="#conteudo"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:bg-bg focus:px-3 focus:py-2 focus:outline-2 focus:outline-honey"
        >
          {pular[idioma]}
        </a>
        <Cabecalho />
        <main id="conteudo">{children}</main>
        <Rodape idioma={idioma} />
        <ContadorVisita />
      </body>
    </html>
  );
}
