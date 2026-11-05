import { ImageResponse } from "next/og";
import { fraseHome, site, tituloHome } from "@/lib/site";

export const alt = tituloHome;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

// O next/og não lê as variáveis CSS: as cores repetem os tokens de :root em globals.css
// (--color-bg, --color-fg, --color-muted-fg, --color-honey).
const cor = { fundo: "#05060F", texto: "#ECEEF8", apagado: "#9BA2C2", destaque: "#F0616B" };

// Fonte padrão do next/og: nenhum fetch de fonte no build nem em runtime.
export default function OpengraphImage() {
  const host = new URL(site.url).host;
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "88px 96px",
          background: cor.fundo,
          color: cor.texto,
          fontFamily: "serif",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 128, lineHeight: 1.05, letterSpacing: "-0.02em" }}>{site.nome}</div>
          <div style={{ fontSize: 52, marginTop: 32, lineHeight: 1.25, color: cor.apagado }}>{fraseHome}</div>
        </div>
        <div
          style={{
            display: "flex",
            borderTop: `2px solid ${cor.destaque}`,
            paddingTop: 24,
            fontSize: 28,
            color: cor.destaque,
          }}
        >
          {host}
        </div>
      </div>
    ),
    size,
  );
}
