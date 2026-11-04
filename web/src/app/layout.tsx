import type { Metadata } from "next";
import { ThemeProvider } from "@beeads/ui";
import { Cabecalho } from "@/components/cabecalho";
import { Rodape } from "@/components/rodape";
import { newsreader, plexMono } from "@/lib/fontes";
import { descricaoSite, site } from "@/lib/site";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: { default: site.nome, template: "%s · Céu Natal" },
  description: descricaoSite,
  // Canonical relativo: resolve para a rota atual via metadataBase.
  alternates: { canonical: "./" },
  // og:image/twitter:image vêm do app/opengraph-image.tsx (convenção de arquivo).
  // Sem title/description aqui: o Next herda os de cada página (senão toda página teria og:title da home).
  openGraph: {
    type: "website",
    locale: "pt_BR",
    siteName: site.nome,
    url: "./",
  },
  twitter: { card: "summary_large_image" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" suppressHydrationWarning className={`${newsreader.variable} ${plexMono.variable}`}>
      <body className="text-base leading-[1.6]">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <a
            href="#conteudo"
            className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:bg-bg focus:px-3 focus:py-2 focus:outline-2 focus:outline-honey"
          >
            Pular para o conteúdo
          </a>
          <Cabecalho />
          <main id="conteudo">{children}</main>
          <Rodape />
        </ThemeProvider>
      </body>
    </html>
  );
}
