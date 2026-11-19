import type { Metadata } from "next";
import { Documento, metadataBase } from "@/components/documento";

export const metadata: Metadata = metadataBase;

// Layout raiz das páginas em inglês: o mesmo documento, com <html lang="en">.
export default function LayoutEn({ children }: { children: React.ReactNode }) {
  return <Documento idioma="en">{children}</Documento>;
}
