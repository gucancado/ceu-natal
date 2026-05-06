"""
Compara as tools efetivamente deployadas (via GET /tools de produção)
com a tabela "Tools já implementadas em app/tools/" do CLAUDE.md.
Atualiza a coluna "Status em produção" e o timestamp de última sincronização.

Sai com erro (não-zero) só se a produção estiver inacessível ou se
o CLAUDE.md estiver malformado — drift normal é resolvido reescrevendo o arquivo.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Garante UTF-8 no stdout (necessário em Windows; no-op no Linux).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROD_URL = os.environ.get("PROD_URL", "https://ceu-natal-api.pu5h6p.easypanel.host")
CLAUDE_MD = Path("CLAUDE.md")

DEPLOYED_MARK = "✅ deployada"
PENDING_MARK = "⏳ aguardando deploy"

# Marker HTML antigo (versão deprecada que carregava timestamp). Mantido aqui
# só pra ser removido em arquivos legados — não geramos mais.
LEGACY_MARKER_RE = re.compile(r"\n*<!-- sync-tools-status:.*?-->\n*")


def fetch_deployed_tools() -> set[str]:
    """Lê GET /tools da produção e devolve o conjunto de nomes deployados."""
    url = f"{PROD_URL.rstrip('/')}/tools"
    req = urllib.request.Request(url, headers={"User-Agent": "ceu-natal-sync"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status != 200:
            raise RuntimeError(f"GET {url} retornou HTTP {resp.status}")
        data = json.loads(resp.read().decode("utf-8"))
    nomes = {t["name"] for t in data.get("tools", []) if "name" in t}
    if not nomes:
        raise RuntimeError(f"Resposta de {url} sem tools — formato inesperado.")
    return nomes


def update_status_column(content: str, deployed: set[str]) -> tuple[str, list[str]]:
    """Reescreve a coluna 'Status em produção' linha a linha. Devolve
    (novo_conteudo, lista_de_mudancas) para log."""
    lines = content.split("\n")
    out: list[str] = []
    mudancas: list[str] = []
    in_table = False

    for line in lines:
        # Detecção do header da tabela
        if "Status em produção" in line and line.lstrip().startswith("|"):
            in_table = True
            out.append(line)
            continue

        if in_table:
            # Saída da tabela: primeira linha que não começa com '|'
            if not line.lstrip().startswith("|"):
                in_table = False
                out.append(line)
                continue

            # Pular linha separadora |---|---|---|
            if re.match(r"^\s*\|[\s\-|:]+\|\s*$", line):
                out.append(line)
                continue

            # Linha de dados: extrair nome da tool da primeira célula
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                out.append(line)
                continue

            tool_match = re.search(r"`([^`]+)`", cells[0])
            if not tool_match:
                out.append(line)
                continue

            tool_name = tool_match.group(1)
            novo = DEPLOYED_MARK if tool_name in deployed else PENDING_MARK
            antigo = cells[2]

            if novo != antigo:
                mudancas.append(f"  {tool_name}: {antigo!r} -> {novo!r}")

            cells[2] = novo
            out.append("| " + " | ".join(cells) + " |")
        else:
            out.append(line)

    return "\n".join(out), mudancas


def remove_legacy_marker(content: str) -> str:
    """Remove o marker de sincronização legado (gerado por versões antigas
    deste script) — não geramos mais. A informação 'última sincronização'
    fica no histórico do GitHub Actions e nos commits."""
    return LEGACY_MARKER_RE.sub("\n", content).rstrip() + "\n"


def main() -> int:
    if not CLAUDE_MD.exists():
        print(f"ERRO: {CLAUDE_MD} não encontrado.", file=sys.stderr)
        return 2

    try:
        deployed = fetch_deployed_tools()
    except Exception as exc:
        print(f"ERRO acessando produção: {exc}", file=sys.stderr)
        return 3

    print(f"Tools deployadas em produção ({len(deployed)}): {sorted(deployed)}")

    original = CLAUDE_MD.read_text(encoding="utf-8")
    novo, mudancas = update_status_column(original, deployed)
    novo = remove_legacy_marker(novo)

    if novo == original:
        print("Sem drift — CLAUDE.md já reflete a produção.")
        return 0

    if mudancas:
        print("Drift detectado:")
        for m in mudancas:
            print(m)
    else:
        print("Limpeza de marker legado.")

    CLAUDE_MD.write_text(novo, encoding="utf-8")
    print(f"{CLAUDE_MD} atualizado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
