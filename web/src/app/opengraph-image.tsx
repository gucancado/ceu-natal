import { ImageResponse } from "next/og";
import { site } from "@/lib/site";

export const alt = "Céu Natal";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

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
          background: "#F3F6FA",
          color: "#1D2342",
          fontFamily: "serif",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 128, lineHeight: 1.05, letterSpacing: "-0.02em" }}>{site.nome}</div>
          <div style={{ fontSize: 48, marginTop: 32, lineHeight: 1.25 }}>Seu chat inventa o seu ascendente.</div>
        </div>
        <div
          style={{
            display: "flex",
            borderTop: "2px solid #B5121B",
            paddingTop: 24,
            fontSize: 28,
            color: "#B5121B",
          }}
        >
          {host}
        </div>
      </div>
    ),
    size,
  );
}
