"""Endpoint público /contato e normalização de contatos (sem Kerykeion)."""
import json

import pytest
from starlette.testclient import TestClient

from app.config import Settings
from app.core.contatos import RegistroContatos, normalizar_contato
from app.server import CONTATO_BODY_MAX, create_app

SITE = "https://mistico.exemplo.com"


@pytest.mark.parametrize(
    ("bruto", "esperado"),
    [
        ("Fulano@Exemplo.COM ", ("email", "fulano@exemplo.com")),
        ("(31) 99999-0000", ("telefone", "+5531999990000")),
        ("31 3333-0000", ("telefone", "+553133330000")),
        ("+1 415 555 0100", ("telefone", "+14155550100")),
    ],
)
def test_normaliza_email_e_telefone(bruto, esperado):
    assert normalizar_contato(bruto) == esperado


@pytest.mark.parametrize("bruto", ["", "fulano@", "abc", "12345", "+12 34", "a@b", "x" * 300])
def test_rejeita_contato_invalido(bruto):
    with pytest.raises(ValueError):
        normalizar_contato(bruto)


def test_registro_ignora_repetido(tmp_path):
    reg = RegistroContatos(str(tmp_path / "c.jsonl"))
    assert reg.registrar("email", "a@b.com") is True
    assert reg.registrar("email", "a@b.com") is False
    linhas = (tmp_path / "c.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 1
    assert set(json.loads(linhas[0])) == {"contato", "tipo", "em"}


def _client(tmp_path, caminho=True):
    app = create_app(Settings(
        api_key="segredo", public_site_url=SITE,
        contatos_path=str(tmp_path / "contatos.jsonl") if caminho else "",
    ))
    return TestClient(app)


def test_grava_contato_sem_chave_e_com_cors(tmp_path):
    client = _client(tmp_path)
    r = client.post("/contato", json={"contato": "fulano@exemplo.com"}, headers={"Origin": SITE})
    assert r.status_code == 200
    assert r.json() == {"ok": True, "tipo": "email"}
    assert r.headers["access-control-allow-origin"] == SITE
    assert "fulano@exemplo.com" in (tmp_path / "contatos.jsonl").read_text(encoding="utf-8")


def test_contato_invalido_da_400(tmp_path):
    client = _client(tmp_path)
    assert client.post("/contato", json={"contato": "abc"}).status_code == 400
    assert client.post("/contato", json={"outro": 1}).status_code == 400
    assert client.post("/contato", content=b"nao e json").status_code == 400


def test_corpo_grande_da_413(tmp_path):
    client = _client(tmp_path)
    r = client.post("/contato", content=b"x" * (CONTATO_BODY_MAX + 1))
    assert r.status_code == 413


def test_sem_caminho_configurado_da_503(tmp_path):
    client = _client(tmp_path, caminho=False)
    assert client.post("/contato", json={"contato": "a@b.com"}).status_code == 503


def test_limite_por_ip(tmp_path):
    client = _client(tmp_path)
    codigos = [client.post("/contato", json={"contato": f"p{i}@exemplo.com"}).status_code for i in range(4)]
    assert codigos == [200, 200, 200, 429]


def test_preflight_so_para_o_site(tmp_path):
    client = _client(tmp_path)
    ok = client.options("/contato", headers={"Origin": SITE, "Access-Control-Request-Method": "POST"})
    assert ok.status_code == 204
    assert ok.headers["access-control-allow-origin"] == SITE
    fora = client.options("/contato", headers={"Origin": "https://malicioso.com"})
    assert "access-control-allow-origin" not in fora.headers


def _client_admin(tmp_path, token="admin-secreto", api_key=""):
    app = create_app(Settings(
        api_key=api_key, public_site_url=SITE, contatos_admin_token=token,
        contatos_path=str(tmp_path / "contatos.jsonl"),
    ))
    return TestClient(app)


def test_listar_contatos_com_token(tmp_path):
    client = _client_admin(tmp_path)
    client.post("/contato", json={"contato": "fulano@exemplo.com"}, headers={"Origin": SITE})
    client.post("/contato", json={"contato": "(31) 99999-0000"}, headers={"Origin": SITE})
    r = client.get("/contatos", headers={"Authorization": "Bearer admin-secreto"})
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["total"] == 2
    assert [c["contato"] for c in corpo["contatos"]] == ["fulano@exemplo.com", "+5531999990000"]
    assert r.headers["cache-control"] == "no-store"


def test_listar_contatos_sem_token_ou_errado_da_401(tmp_path):
    client = _client_admin(tmp_path)
    assert client.get("/contatos").status_code == 401
    assert client.get("/contatos", headers={"Authorization": "Bearer outro"}).status_code == 401
    assert client.get("/contatos?key=admin-secreto").status_code == 401


def test_listar_contatos_nao_aceita_a_chave_do_mcp(tmp_path):
    client = _client_admin(tmp_path, api_key="chave-mcp")
    assert client.get("/contatos", headers={"Authorization": "Bearer chave-mcp"}).status_code == 401
    assert client.get("/contatos", headers={"Authorization": "Bearer admin-secreto"}).status_code == 200


def test_listar_contatos_sem_token_configurado_da_404(tmp_path):
    client = _client_admin(tmp_path, token="")
    assert client.get("/contatos", headers={"Authorization": "Bearer "}).status_code == 404


def test_listar_pula_linha_corrompida(tmp_path):
    caminho = tmp_path / "c.jsonl"
    caminho.write_text('{"contato": "a@b.com"}\nlixo\n[1]\n', encoding="utf-8")
    assert RegistroContatos(str(caminho)).listar() == [{"contato": "a@b.com"}]
    assert RegistroContatos(str(tmp_path / "nada.jsonl")).listar() == []


def test_remover_contato(tmp_path):
    caminho = tmp_path / "c.jsonl"
    reg = RegistroContatos(str(caminho))
    reg.registrar("email", "a@b.com")
    reg.registrar("email", "c@d.com")
    assert reg.remover("a@b.com") is True
    assert reg.remover("a@b.com") is False
    assert [c["contato"] for c in reg.listar()] == ["c@d.com"]
