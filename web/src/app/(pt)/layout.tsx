import type { Metadata } from "next";
import { Documento, metadataBase } from "@/components/documento";

export const metadata: Metadata = metadataBase;

// Layout raiz das páginas em português. O das páginas em inglês fica em `(en)/layout.tsx`.
export default function LayoutPt({ children }: { children: React.ReactNode }) {
  return <Documento idioma="pt">{children}</Documento>;
}
