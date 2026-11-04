import type { Metadata } from "next";
import { ThemeProvider } from "@beeads/ui";
import { Cabecalho } from "@/components/cabecalho";
import { Rodape } from "@/components/rodape";
import { newsreader, plexMono } from "@/lib/fontes";
import { site } from "@/lib/site";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: site.nome,
  description: "Mapa astral calculado com efemérides suíças dentro do seu assistente de IA.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" suppressHydrationWarning className={`${newsreader.variable} ${plexMono.variable}`}>
      <body className="text-base leading-[1.6]">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <Cabecalho />
          <main>{children}</main>
          <Rodape />
        </ThemeProvider>
      </body>
    </html>
  );
}
