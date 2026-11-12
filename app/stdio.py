# SPDX-License-Identifier: AGPL-3.0-or-later
"""Transporte stdio: o mesmo servidor MCP, falando por stdin/stdout.

Uso: `python -m app.stdio`. Serve a clientes que só abrem processo local e a
diretórios que inspecionam o servidor por stdio (Glama). Lê as mesmas
variáveis de ambiente do servidor HTTP; o log vai para stderr.
"""
import anyio
from mcp.server.stdio import stdio_server

from app.config import Settings
from app.server import Aplicacao, configurar_logging


async def rodar(settings: Settings) -> None:
    """Atende uma sessão MCP por stdio até o cliente fechar a entrada."""
    ceu = Aplicacao(settings)
    async with stdio_server() as (leitura, escrita):
        await ceu.server.run(leitura, escrita, ceu.server.create_initialization_options())


def main() -> None:
    configurar_logging()
    anyio.run(rodar, Settings.do_ambiente())


if __name__ == "__main__":
    main()
