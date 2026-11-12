"""Histórico dos mapas do site, vínculo com contato e contagem por mapa (sem Kerykeion)."""
from datetime import datetime, timezone

from starlette.testclient import TestClient

from app.config import Settings
from app.core import geocoder
from app.core.estatisticas import Estatisticas
from app.core.historico import Historico, id_valido
from app.server import create_app

SITE = "https://site.test"
TOKEN = "admin-secreto"
NAV = "11111111-1111-4111-8111-111111111111"
MAPA = "22222222-2222-4222-8222-222222222222"
OUTRO_MAPA = "33333333-3333-4333-8333-333333333333"
RESOLVIDO = {"local_resolvido": {"lat": -19.9, "lng": -43.9, "fuso": "America/Sao_Paulo"}}


def _app(tmp_path, monkeypatch):
    app = create_app(Settings(
        public_site_url=SITE, contatos_admin_token=TOKEN,
        contatos_path=str(tmp_path / "contatos.jsonl"),
        estatisticas_path=str(tmp_path / "e.sqlite3"),
        historico_path=str(tmp_path / "h.sqlite3"),
    ))
    monkeypatch.setattr(app.state.ceu, "dispatch", lambda nome, args: dict(RESOLVIDO))
    monkeypatch.setattr(geocoder, "ao_resolver", None)
    return TestClient(app), app.state.ceu


def _mapa(client, **corpo):
    return client.post("/mapa-rapido", json=corpo, headers={"Origin": SITE})


def test_id_valido():
    assert id_valido(NAV.upper()) == NAV
    assert id_valido("x") is None and id_valido(None) is None


def test_mapa_completado_conta_um_e_guarda_a_ultima_versao(tmp_path, monkeypatch):
    client, ceu = _app(tmp_path, monkeypatch)
    _mapa(client, data="01/02/1990", visitante=NAV, mapa=MAPA)
    _mapa(client, data="01/02/1990", hora="10:30", local="Belo Horizonte, MG", visitante=NAV, mapa=MAPA)
    _mapa(client, data="05/06/1985", visitante=NAV, mapa=OUTRO_MAPA)

    resumo = ceu.estatisticas.resumo()
    assert resumo["totais"]["calculos"] == 2
    assert resumo["por_origem"] == {"site": 2}

    hist = ceu.historico.por_visitante()
    assert len(hist) == 1 and hist[0]["visitante"] == NAV
    primeiro = next(m for m in hist[0]["mapas"] if m["id"] == MAPA)
    assert (primeiro["data"], primeiro["hora"], primeiro["local"]) == ("01/02/1990", "10:30", "Belo Horizonte, MG")
    assert (primeiro["lat"], primeiro["fuso"], primeiro["calculos"]) == (-19.9, "America/Sao_Paulo", 2)


def test_contato_liga_mapas_feitos_antes_e_rotas_admin(tmp_path, monkeypatch):
    client, _ = _app(tmp_path, monkeypatch)
    _mapa(client, data="01/02/1990", hora="10:30", local="Belo Horizonte, MG", visitante=NAV, mapa=MAPA)
    r = client.post("/contato", json={"contato": "Fulano@Exemplo.com", "visitante": NAV}, headers={"Origin": SITE})
    assert r.status_code == 200

    auth = {"Authorization": f"Bearer {TOKEN}"}
    contatos = client.get("/contatos", headers=auth).json()["contatos"]
    assert contatos[0]["contato"] == "fulano@exemplo.com"
    assert contatos[0]["visitantes"] == [NAV]
    assert [m["id"] for m in contatos[0]["mapas"]] == [MAPA]

    hist = client.get("/historico", headers=auth).json()
    assert hist["visitantes"][0]["contatos"] == ["fulano@exemplo.com"]
    assert client.get("/historico").status_code == 401


def test_mapa_sem_ids_ainda_funciona(tmp_path, monkeypatch):
    client, ceu = _app(tmp_path, monkeypatch)
    assert _mapa(client, data="01/02/1990").status_code == 200
    assert _mapa(client, data="01/02/1990", mapa="nao-e-uuid").status_code == 200
    assert ceu.estatisticas.resumo()["totais"]["calculos"] == 2
    assert ceu.historico.por_visitante() == [{"visitante": None, "contatos": [], "mapas_sem_navegador": 2}]


def test_historico_desligado_nao_guarda(tmp_path, monkeypatch):
    app = create_app(Settings(public_site_url=SITE, contatos_admin_token=TOKEN))
    monkeypatch.setattr(app.state.ceu, "dispatch", lambda nome, args: {})
    client = TestClient(app)
    assert _mapa(client, data="01/02/1990", visitante=NAV, mapa=MAPA).status_code == 200
    assert client.get("/historico", headers={"Authorization": f"Bearer {TOKEN}"}).status_code == 503


def test_dia_vira_no_horario_de_brasilia(tmp_path):
    def relogio():
        return datetime(2026, 11, 12, 0, 44, tzinfo=timezone.utc)  # 21h44 de 11/11 em Brasília

    est = Estatisticas(str(tmp_path / "e.sqlite3"), relogio=relogio)
    est.registrar_mapa_site(MAPA)
    assert est.resumo()["por_dia"][-1] == {
        "dia": "2026-11-11", "calculos": 1, "pessoas_site": 0, "sessoes_mcp": 0,
    }


def test_vinculo_repetido_nao_duplica(tmp_path):
    h = Historico(str(tmp_path / "h.sqlite3"))
    h.vincular("a@b.com", NAV)
    h.vincular("a@b.com", NAV)
    assert h.do_contato("a@b.com") == {"visitantes": [NAV], "mapas": []}


def test_apagar_contato_leva_os_mapas_so_dele(tmp_path, monkeypatch):
    client, ceu = _app(tmp_path, monkeypatch)
    outro_nav = "44444444-4444-4444-8444-444444444444"
    _mapa(client, data="01/02/1990", visitante=NAV, mapa=MAPA)
    _mapa(client, data="05/06/1985", visitante=outro_nav, mapa=OUTRO_MAPA)
    for contato, nav in (("a@b.com", NAV), ("a@b.com", outro_nav), ("c@d.com", outro_nav)):
        client.post("/contato", json={"contato": contato, "visitante": nav}, headers={"Origin": SITE})
    auth = {"Authorization": f"Bearer {TOKEN}"}

    assert client.request("DELETE", "/contatos", json={"contato": "a@b.com"}).status_code == 401
    r = client.request("DELETE", "/contatos", json={"contato": "A@B.com"}, headers=auth)
    assert r.json() == {"contato_removido": True, "visitantes": 2, "mapas": 1}
    # O navegador compartilhado com c@d.com mantém o mapa.
    restantes = client.get("/contatos", headers=auth).json()["contatos"]
    assert [c["contato"] for c in restantes] == ["c@d.com"]
    assert [m["id"] for m in restantes[0]["mapas"]] == [OUTRO_MAPA]
    assert client.request("DELETE", "/contatos", json={}, headers=auth).status_code == 400


def test_apagar_mapa_e_visitante(tmp_path, monkeypatch):
    client, ceu = _app(tmp_path, monkeypatch)
    _mapa(client, data="01/02/1990", visitante=NAV, mapa=MAPA)
    _mapa(client, data="05/06/1985", visitante=NAV, mapa=OUTRO_MAPA)
    auth = {"Authorization": f"Bearer {TOKEN}"}
    assert client.request("DELETE", "/historico", json={"mapa": MAPA}, headers=auth).json() == {"mapas": 1}
    r = client.request("DELETE", "/historico", json={"visitante": NAV}, headers=auth)
    assert r.json() == {"mapas": 1, "vinculos": 0}
    assert ceu.historico.por_visitante() == []
    assert client.request("DELETE", "/historico", json={"mapa": "x"}, headers=auth).status_code == 400
