"""
Testes do transporte stdio (`python -m app.stdio`): handshake MCP de verdade
num subprocesso, sem rede e sem cálculo (só listar tools e healthcheck).
"""
import json
import subprocess
import sys
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _mensagem(id_: int | None, metodo: str, params: dict | None = None) -> str:
    corpo: dict = {"jsonrpc": "2.0", "method": metodo}
    if id_ is not None:
        corpo["id"] = id_
    if params is not None:
        corpo["params"] = params
    return json.dumps(corpo)


def _conversar(mensagens: list[str], ultimo_id: int, timeout: float = 60) -> dict[int, dict]:
    """Manda as mensagens e só fecha a entrada depois da resposta `ultimo_id`.

    Fechar o stdin logo após escrever não serve: com a entrada encerrada, o
    SDK do MCP cancela os pedidos ainda em andamento (o healthcheck roda numa
    thread) e a resposta nunca sai. Cliente de verdade espera a resposta.
    """
    proc = subprocess.Popen(
        [sys.executable, "-m", "app.stdio"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True, encoding="utf-8", cwd=RAIZ,
    )
    respostas: dict[int, dict] = {}

    def ler() -> None:
        assert proc.stdout is not None
        for linha in proc.stdout:
            if linha.strip():
                r = json.loads(linha)
                if "id" in r:
                    respostas[r["id"]] = r
                if ultimo_id in respostas:
                    return

    leitor = threading.Thread(target=ler, daemon=True)
    leitor.start()
    try:
        assert proc.stdin is not None
        proc.stdin.write("\n".join(mensagens) + "\n")
        proc.stdin.flush()
        leitor.join(timeout)
    finally:
        proc.stdin.close()  # type: ignore[union-attr]
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    return respostas


def test_stdio_responde_initialize_lista_tools_e_healthcheck():
    respostas = _conversar([
        _mensagem(1, "initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "teste", "version": "0"},
        }),
        _mensagem(None, "notifications/initialized"),
        _mensagem(2, "tools/list"),
        _mensagem(3, "tools/call", {"name": "healthcheck", "arguments": {}}),
    ], ultimo_id=3)
    assert respostas[1]["result"]["serverInfo"]["name"] == "ceu-natal"
    nomes = {t["name"] for t in respostas[2]["result"]["tools"]}
    assert {"calcular_mapa_natal", "healthcheck"} <= nomes
    saude = respostas[3]["result"]
    assert saude["isError"] is False
    assert saude["structuredContent"]["status"] == "ok"
