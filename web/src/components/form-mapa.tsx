"use client";

import { useState, type FormEvent } from "react";
import { Button, Input, Label } from "@beeads/ui";
import { CaixaPrompt } from "@/components/caixa-prompt";
import { textoMapa, type MapaRapido } from "@/lib/mapa-texto";
import { site } from "@/lib/site";

// "1990-05-15" (input date) vira "15/05/1990" (formato do servidor).
function dataBr(iso: string): string {
  const [a, m, d] = iso.split("-");
  return `${d}/${m}/${a}`;
}

type Estado =
  | { tipo: "vazio" }
  | { tipo: "calculando" }
  | { tipo: "erro"; mensagem: string }
  | { tipo: "pronto"; texto: string };

export function FormMapa() {
  const [estado, setEstado] = useState<Estado>({ tipo: "vazio" });

  async function enviar(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const data = String(f.get("data") || "");
    if (!data) return;
    setEstado({ tipo: "calculando" });
    try {
      const r = await fetch(`${site.mcpUrl}/mapa-rapido`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: dataBr(data),
          hora: String(f.get("hora") || ""),
          local: String(f.get("local") || ""),
        }),
      });
      const corpo = await r.json().catch(() => null);
      if (!r.ok || !corpo || corpo.erro) {
        setEstado({ tipo: "erro", mensagem: corpo?.erro || "Não foi possível calcular agora. Tente de novo." });
        return;
      }
      setEstado({ tipo: "pronto", texto: textoMapa(corpo as MapaRapido) });
    } catch {
      setEstado({ tipo: "erro", mensagem: "Sem conexão com o servidor. Tente de novo em instantes." });
    }
  }

  return (
    <div className="grid gap-10">
      <form onSubmit={enviar} className="grid max-w-[36rem] gap-5">
        <div className="grid gap-2">
          <Label htmlFor="data">Data de nascimento</Label>
          <Input id="data" name="data" type="date" required min="1800-01-01" max="2100-12-31" />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="hora">Hora (opcional, mas sem ela não há ascendente nem casas)</Label>
          <Input id="hora" name="hora" type="time" />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="local">Cidade (opcional)</Label>
          <Input id="local" name="local" type="text" placeholder="Belo Horizonte, MG" maxLength={120} autoComplete="off" />
        </div>
        <div>
          <Button type="submit" size="lg" disabled={estado.tipo === "calculando"}>
            {estado.tipo === "calculando" ? "Calculando…" : "Calcular meu mapa"}
          </Button>
        </div>
        <p aria-live="polite" role="status" className="text-sm text-muted-fg">
          {estado.tipo === "erro" ? <span className="text-fg">{estado.mensagem}</span> : null}
        </p>
      </form>
      {estado.tipo === "pronto" ? (
        <div className="grid max-w-[48rem] gap-4">
          <p className="text-lg">
            Copie o texto abaixo e cole no seu assistente de IA. Ele já vai com o pedido para conectar o {site.nome}.
          </p>
          <CaixaPrompt texto={estado.texto} rotulo="mapa + prompt" alturaMax />
        </div>
      ) : null}
    </div>
  );
}
