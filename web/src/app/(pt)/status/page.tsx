import type { Metadata } from "next";
import { PainelUso } from "@/components/painel-uso";
import { lerEstatisticas } from "@/lib/estatisticas";
import { lerSaude } from "@/lib/saude";
import { site } from "@/lib/site";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Status",
  description: "Se o servidor do Céu Natal está no ar agora e quanto ele é usado.",
  robots: { index: false, follow: false },
};

export default async function Status() {
  const [s, e] = await Promise.all([lerSaude(site.mcpUrl), lerEstatisticas(site.mcpUrl)]);
  return (
    <article className="mx-auto max-w-[72rem] px-6 py-16 md:py-24">
      <h1 className="font-display text-4xl font-medium leading-[1.15] tracking-tight md:text-5xl">Status</h1>
      <div className="mt-8 max-w-[36rem]">
        {s.ok ? (
          <p className="font-display text-2xl">
            <span>No ar</span> · versão <span className="font-mono">{s.versao}</span> · limites{" "}
            <span className="font-mono">
              {s.limites.por_sessao_por_min}/{s.limites.global_por_min}
            </span>
          </p>
        ) : (
          <p className="font-display text-2xl">Fora do ar: {s.motivo}</p>
        )}
        {s.ok ? (
          <p className="mt-4 text-muted-fg">
            Até {s.limites.por_sessao_por_min} chamadas por minuto em cada conversa e{" "}
            {s.limites.global_por_min} por minuto no total.
          </p>
        ) : null}
        <p className="mt-4 text-muted-fg">
          Servidor consultado: <span className="font-mono [overflow-wrap:anywhere]">{site.mcpUrl}</span>. Recarregue
          a página para ver de novo.
        </p>
      </div>
      {e ? <PainelUso e={e} /> : null}
    </article>
  );
}
