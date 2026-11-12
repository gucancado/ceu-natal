"""
Testes do transporte stdio (`python -m app.stdio`): handshake MCP de verdade
num subprocesso, sem rede e sem cálculo (só listar tools e healthcheck).
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _mensagem(id_: int | None, metodo: str, params: dict | None = None) -> str:
    corpo: dict = {"jsonrpc": "2.0", "method": metodo}
    if id_ is not None:
        corpo["id"] = id_
    if params is not None:
        corpo["params"] = params
    return json.dumps(corpo)


def test_stdio_responde_initialize_lista_tools_e_healthcheck():
    entrada = "\n".join([
        _mensagem(1, "initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "teste", "version": "0"},
        }),
        _mensagem(None, "notifications/initialized"),
        _mensagem(2, "tools/list"),
        _mensagem(3, "tools/call", {"name": "healthcheck", "arguments": {}}),
    ]) + "\n"
    proc = subprocess.run(
        [sys.executable, "-m", "app.stdio"], input=entrada, capture_output=True,
        text=True, encoding="utf-8", cwd=RAIZ, timeout=60,
    )
    respostas = {
        r["id"]: r for r in (json.loads(linha) for linha in proc.stdout.splitlines() if linha.strip())
    }
    assert respostas[1]["result"]["serverInfo"]["name"] == "ceu-natal"
    nomes = {t["name"] for t in respostas[2]["result"]["tools"]}
    assert {"calcular_mapa_natal", "healthcheck"} <= nomes
    saude = respostas[3]["result"]
    assert saude["isError"] is False
    assert saude["structuredContent"]["status"] == "ok"
