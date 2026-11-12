"""Estatísticas agregadas de uso e a rota pública /estatisticas (sem Kerykeion)."""
import sqlite3
from datetime import datetime, timedelta, timezone

from starlette.testclient import TestClient

from app.config import Settings
from app.core import geocoder
from app.core.estatisticas import Estatisticas, app_publico, normalizar_app
from app.server import create_app


class Relogio:
    def __init__(self, inicio: datetime) -> None:
        self.agora = inicio

    def __call__(self) -> datetime:
        return self.agora


def _est(tmp_path, dia="2026-11-11"):
    relogio = Relogio(datetime.fromisoformat(f"{dia}T12:00:00+00:00"))
    return Estatisticas(str(tmp_path / "e.sqlite3"), relogio=relogio), relogio


def test_conta_chamadas_ferramentas_e_tempo(tmp_path):
    est, _ = _est(tmp_path)
    est.registrar_chamada("mcp", "calcular_mapa_natal", "claude-ai", "ok", 100)
    est.registrar_chamada("mcp", "calcular_mapa_natal", "claude-ai", "ok", 200)
    est.registrar_chamada("site", "mapa_rapido", "site", "value_error", 30)
    est.registrar_chamada("mcp", "healthcheck", "claude-ai", "ok", 1)
    r = est.resumo()
    assert r["totais"]["chamadas"] == 4
    assert r["totais"]["calculos"] == 2  # healthcheck e erro não contam
    assert r["totais"]["taxa_erro"] == 0.25
    assert r["totais"]["tempo_medio_ms"] == 82.8
    assert r["por_ferramenta"][0] == {"ferramenta": "calcular_mapa_natal", "chamadas": 2}
    assert r["por_app"] == [{"app": "Claude", "chamadas": 3}]
    assert r["desde"] == "2026-11-11"
    assert r["por_dia"][-1]["calculos"] == 2
    assert len(r["por_dia"]) == 30


def test_unicos_do_dia_sem_guardar_o_identificador(tmp_path):
    est, relogio = _est(tmp_path)
    for ip in ("203.0.113.1", "203.0.113.1", "203.0.113.2"):
        est.registrar_unico("site", ip)
    est.registrar_unico("mcp", "sessao-a")
    est.registrar_unico("site", None)
    r = est.resumo()
    assert r["por_dia"][-1]["pessoas_site"] == 2
    assert r["por_dia"][-1]["sessoes_mcp"] == 1

    con = sqlite3.connect(str(tmp_path / "e.sqlite3"))
    despejo = "\n".join(con.iterdump())
    assert "203.0.113" not in despejo and "sessao-a" not in despejo

    # Dia seguinte: a mesma pessoa conta de novo, e hashes e sal de ontem somem.
    relogio.agora += timedelta(days=1)
    est.registrar_unico("site", "203.0.113.1")
    r = est.resumo()
    assert [d["pessoas_site"] for d in r["por_dia"][-2:]] == [2, 1]
    assert r["totais"]["pessoas_dia_site"] == 3
    assert con.execute("SELECT COUNT(*) FROM sal WHERE dia < '2026-11-12'").fetchone()[0] == 0
    assert con.execute(
        "SELECT COUNT(*) FROM unicos_abertos WHERE dia < '2026-11-12'"
    ).fetchone()[0] == 0


def test_paises_pequenos_viram_outros_e_cidades_nao_saem(tmp_path):
    est, _ = _est(tmp_path)
    for _ in range(5):
        est.registrar_lugar("Belo Horizonte", "BR")
    est.registrar_lugar("Lisboa", "PT")
    est.registrar_lugar("Algum Lugar", None)
    r = est.resumo()
    assert r["paises"] == [{"pais": "BR", "chamadas": 5}, {"pais": "outros", "chamadas": 2}]
    assert r["totais"]["cidades"] == 3
    assert r["totais"]["paises"] == 2
    assert "Belo Horizonte" not in str(r) and "Lisboa" not in str(r)


def test_app_desconhecido_nunca_aparece_pelo_nome():
    assert normalizar_app("Claude-AI") == "claude-ai"
    assert normalizar_app(None) == "desconhecido"
    assert normalizar_app("<script>João</script>") == "scriptjooscript"
    assert app_publico("openai-mcp") == "ChatGPT"
    assert app_publico("cursor-vscode") == "Cursor"
    assert app_publico("maria-da-silva-bot") == "outros"


def test_rota_publica_e_registro_do_mapa_rapido(tmp_path, monkeypatch):
    app = create_app(Settings(
        api_key="segredo", estatisticas_path=str(tmp_path / "e.sqlite3"),
        public_site_url="https://site.test",
    ))
    try:
        ceu = app.state.ceu
        monkeypatch.setattr(ceu, "dispatch", lambda nome, args: {"ok": True})
        client = TestClient(app)
        r = client.post("/mapa-rapido", json={"data": "01/01/2000"}, headers={"Origin": "https://site.test"})
        assert r.status_code == 200
        r = client.get("/estatisticas")  # sem chave: rota pública
        assert r.status_code == 200
        corpo = r.json()
        assert corpo["totais"]["calculos"] == 1
        assert corpo["por_origem"] == {"site": 1}
        assert corpo["por_dia"][-1]["pessoas_site"] == 1
        assert geocoder.ao_resolver == ceu.estatisticas.registrar_lugar
    finally:
        geocoder.ao_resolver = None


def test_rota_desligada_sem_caminho():
    client = TestClient(create_app(Settings()))
    assert client.get("/estatisticas").status_code == 503


def test_settings_le_estatisticas_path(monkeypatch):
    monkeypatch.setenv("ESTATISTICAS_PATH", " /dados/e.sqlite3 ")
    assert Settings.do_ambiente().estatisticas_path == "/dados/e.sqlite3"


def test_relogio_padrao_e_utc(tmp_path):
    est = Estatisticas(str(tmp_path / "e.sqlite3"))
    assert est._relogio().tzinfo == timezone.utc


def test_zerar_pela_rota_administrativa(tmp_path):
    app = create_app(Settings(
        estatisticas_path=str(tmp_path / "e.sqlite3"), contatos_admin_token="admin-secreto",
    ))
    ceu = app.state.ceu
    ceu.estatisticas.registrar_chamada("mcp", "calcular_mapa_natal", "claude-ai", "ok", 10)
    ceu.estatisticas.registrar_unico("site", "203.0.113.1")
    client = TestClient(app)
    assert client.get("/estatisticas").json()["totais"]["calculos"] == 1
    assert client.delete("/estatisticas").status_code == 401
    assert client.delete("/estatisticas", headers={"Authorization": "Bearer admin-secreto"}).json() == {"zerado": True}
    totais = client.get("/estatisticas").json()["totais"]
    assert (totais["calculos"], totais["chamadas"]) == (0, 0)
