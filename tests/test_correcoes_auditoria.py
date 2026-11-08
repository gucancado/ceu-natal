# SPDX-License-Identifier: AGPL-3.0-or-later
"""Regressões da auditoria: ângulos reais, sistema Equal, polar e limites de texto."""
import asyncio
import json

import pytest

from app.tools.composto import calcular_mapa_composto
from app.tools.mapa_natal import calcular_mapa_natal
from app.tools.sinastria import calcular_sinastria
from tests.conftest import ANA, BH, BRUNO

SISTEMAS = ("P", "K", "O", "R", "C", "E", "W", "B", "M", "T")
TROMSO = {"lat": 69.65, "lng": 18.96, "tz_str": "Europe/Oslo"}
POLAR = {"nome": "Bia", "data": "12/03/1990", "hora": "14:30", "local": "Tromso, NO", **TROMSO}


def _natal(sistema):
    return calcular_mapa_natal(
        data="12/03/1990", hora="14:30", local="Belo Horizonte, MG",
        sistema_casas=sistema, **BH,
    )


def _graus(angulo):
    return angulo["posicao_absoluta"]


@pytest.mark.parametrize("sistema", SISTEMAS)
def test_todos_os_sistemas_de_casas_calculam(sistema):
    assert _natal(sistema)["angulos"]["ascendente"]


@pytest.mark.parametrize("sistema", ["W", "M", "E"])
def test_ascendente_nao_depende_do_sistema_de_casas(sistema):
    assert _graus(_natal(sistema)["angulos"]["ascendente"]) == pytest.approx(
        _graus(_natal("P")["angulos"]["ascendente"]), abs=0.01,
    )


@pytest.mark.parametrize("sistema", ["W", "E"])
def test_meio_do_ceu_nao_depende_do_sistema_de_casas(sistema):
    assert _graus(_natal(sistema)["angulos"]["meio_do_ceu"]) == pytest.approx(
        _graus(_natal("P")["angulos"]["meio_do_ceu"]), abs=0.01,
    )


def test_sinastria_omite_casas_em_latitude_polar():
    r = calcular_sinastria(pessoa_a=POLAR, pessoa_b=ANA)
    assert r["ativacoes_de_casas"] == []
    assert r["pessoa_a"]["asc"] is None
    assert "66°" in r["aviso"]


def test_sinastria_fora_da_faixa_polar_mantem_casas():
    r = calcular_sinastria(pessoa_a=BRUNO, pessoa_b=ANA)
    assert r["ativacoes_de_casas"]
    assert "aviso" not in r


def test_composto_omite_angulos_em_latitude_polar():
    r = calcular_mapa_composto(pessoa_a=POLAR, pessoa_b=ANA)
    assert r["angulos_compostos"] == {}
    assert "66°" in r["aviso"]


def _ceu():
    from app.server import app

    return app.state.ceu


def test_texto_grande_demais_e_recusado_antes_do_calculo(monkeypatch):
    ceu = _ceu()
    monkeypatch.setattr(ceu, "dispatch", lambda *a: pytest.fail("não devia calcular"))
    args = {"pessoa_a": {**ANA, "nome": "x" * 201}, "pessoa_b": BRUNO}
    r = asyncio.run(ceu.call_tool("calcular_sinastria", args))
    assert r.isError is True
    assert "200" in json.loads(r.content[0].text)["erro"]


def test_texto_no_limite_passa(monkeypatch):
    ceu = _ceu()
    monkeypatch.setattr(ceu, "dispatch", lambda *a: {"ok": True})
    _, estruturado = asyncio.run(
        ceu.call_tool("calcular_mapa_natal", {"data": "01/01/2000", "local": "x" * 200})
    )
    assert estruturado == {"ok": True}


def test_transporte_sse_foi_removido():
    from starlette.testclient import TestClient

    from app.server import create_app

    client = TestClient(create_app())
    assert client.get("/sse").status_code == 404
    assert client.post("/messages/", json={}).status_code == 404


def test_post_mcp_sem_barra_nao_redireciona():
    from starlette.testclient import TestClient

    from app.server import create_app

    with TestClient(create_app(), follow_redirects=False) as client:
        assert client.post("/mcp", json={}).status_code != 307


def test_initialize_informa_a_versao_do_servidor():
    ceu = _ceu()
    assert ceu.server.version == ceu.settings.server_version


def test_nodo_sul_anda_com_o_nodo_norte():
    pontos = _natal("P")["pontos_sensiveis"]
    norte, sul = pontos["nodo_norte_verdadeiro"], pontos["nodo_sul_verdadeiro"]
    assert sul["velocidade"] == norte["velocidade"]
    assert sul["retrogrado"] == norte["retrogrado"]


@pytest.mark.parametrize("extra", [
    {"lat": 10.0, "lng": 20.0},
    {"lat": 91.0, "lng": 0.0, "tz_str": "UTC"},
    {"lat": 0.0, "lng": 1e300, "tz_str": "UTC"},
    {"lat": 0.0, "lng": 0.0, "tz_str": "Marte/Base"},
])
def test_coordenadas_invalidas_sao_recusadas(extra):
    with pytest.raises(ValueError):
        calcular_mapa_natal(data="12/03/1990", hora="14:30", **extra)


def test_logs_nao_registram_sessao():
    import logging

    from app.server import configurar_logging

    configurar_logging()
    assert logging.getLogger("mcp.server.streamable_http_manager").getEffectiveLevel() == logging.WARNING


RIO = {"lat": -22.91, "lng": -43.17}


def test_data_antiga_usa_a_hora_media_da_propria_cidade():
    tz = "America/Sao_Paulo"
    r = calcular_mapa_natal(data="15/06/1900", hora="12:00", local="Rio", tz_str=tz, **RIO)
    # 12:00 no meridiano de 43,17° O são 14:52:41 UTC.
    ref = calcular_mapa_natal(data="15/06/1900", hora="14:53", local="Rio", tz_str="UTC", **RIO)
    assert r["angulos"]["ascendente"]["posicao_absoluta"] == pytest.approx(
        ref["angulos"]["ascendente"]["posicao_absoluta"], abs=0.3,
    )


def test_data_com_hora_legal_nao_muda():
    from datetime import datetime

    from app.core.kerykeion import hora_media_local_utc

    assert hora_media_local_utc(datetime(1990, 3, 12, 14, 30), -43.17, "America/Sao_Paulo") is None
    assert hora_media_local_utc(datetime(1900, 6, 15, 12, 0), 0.0, "UTC") is None


def test_progressoes_usam_o_mesmo_instante_natal():
    from datetime import datetime, timezone

    from app.core.entrada import EntradaNascimento
    from app.tools.progressoes import _datetime_natal_utc

    e = EntradaNascimento.de_dict({
        "data": "15/06/1900", "hora": "12:00", "local": "Rio",
        "tz_str": "America/Sao_Paulo", **RIO,
    })
    assert _datetime_natal_utc(e) == datetime(1900, 6, 15, 14, 52, 40, 800000, tzinfo=timezone.utc)


def test_schemas_declaram_limite_nos_textos():
    from app.server import TOOLS

    props = next(t for t in TOOLS if t.name == "calcular_sinastria").inputSchema["properties"]
    assert props["pessoa_a"]["properties"]["nome"]["maxLength"] == 200
    assert props["pessoa_a"]["properties"]["local"]["maxLength"] == 200
