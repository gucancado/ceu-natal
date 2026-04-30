"""
Testes do geocoder. Mocka os helpers privados `_try_geonames` e
`_try_nominatim` (em vez de mockar urllib/requests/httpx) — assim os
testes ficam independentes da biblioteca HTTP usada.
"""
import importlib
import json
import os

import pytest


@pytest.fixture
def geocoder(tmp_path, monkeypatch):
    """
    Recarrega o módulo do geocoder com cache apontando para um arquivo
    temporário do pytest. Garante isolamento entre testes.
    """
    cache_path = tmp_path / "geocode-cache.json"
    monkeypatch.setenv("GEOCODER_CACHE_PATH", str(cache_path))
    from app.core import geocoder as mod
    importlib.reload(mod)
    yield mod
    # Cleanup do estado global do módulo após o teste
    importlib.reload(mod)


# ─────────────────────────────────────────────────────────────
# GeocodingError nos três cenários do spec
# ─────────────────────────────────────────────────────────────
def test_cidade_nao_encontrada_em_nenhum_provedor(geocoder, monkeypatch):
    monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: None)
    monkeypatch.setattr(geocoder, "_try_nominatim", lambda c, n: None)
    with pytest.raises(geocoder.GeocodingError, match="Não foi possível geocodificar"):
        geocoder.geocode("Cidade Que Nao Existe", "BR")


def test_todos_provedores_indisponiveis(geocoder, monkeypatch):
    """Simula timeout/erro de rede: helpers retornam None silenciosamente."""
    def boom(c, n):
        return None
    monkeypatch.setattr(geocoder, "_try_geonames", boom)
    monkeypatch.setattr(geocoder, "_try_nominatim", boom)
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Belo Horizonte", "MG")


def test_resposta_sem_coordenadas_validas(geocoder, monkeypatch):
    """Helper retorna (None, None) — geocode deve levantar GeocodingError."""
    monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: (None, None))
    monkeypatch.setattr(geocoder, "_try_nominatim", lambda c, n: None)
    monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "UTC")
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Belo Horizonte", "MG")


def test_cidade_vazia_levanta_geocoding_error(geocoder):
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("", "BR")


# ─────────────────────────────────────────────────────────────
# Caminho feliz e cache
# ─────────────────────────────────────────────────────────────
def test_geocode_sucesso_via_geonames(geocoder, monkeypatch):
    monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: (-19.92, -43.94))
    monkeypatch.setattr(geocoder, "_try_nominatim", lambda c, n: pytest.fail("nominatim não devia ser chamado"))
    monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "America/Sao_Paulo")

    res = geocoder.geocode("Belo Horizonte", "MG")
    assert res == {"lat": -19.92, "lng": -43.94, "tz_str": "America/Sao_Paulo"}


def test_fallback_para_nominatim(geocoder, monkeypatch):
    monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: None)
    monkeypatch.setattr(geocoder, "_try_nominatim", lambda c, n: (38.72, -9.13))
    monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "Europe/Lisbon")

    res = geocoder.geocode("Lisboa", "Portugal")
    assert res["lat"] == 38.72
    assert res["lng"] == -9.13


def test_cache_persistido_em_arquivo(geocoder, monkeypatch):
    monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: (-23.55, -46.63))
    monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "America/Sao_Paulo")

    geocoder.geocode("São Paulo", "SP")

    # O arquivo deve existir e conter a entrada
    assert os.path.exists(geocoder.CACHE_PATH)
    with open(geocoder.CACHE_PATH, "r", encoding="utf-8") as f:
        salvo = json.load(f)
    assert "são paulo|sp" in salvo


def test_segunda_chamada_vem_do_cache_sem_bater_em_provedores(geocoder, monkeypatch):
    chamadas = {"geonames": 0, "nominatim": 0}

    def fake_geonames(c, n):
        chamadas["geonames"] += 1
        return (-19.92, -43.94)

    def fake_nominatim(c, n):
        chamadas["nominatim"] += 1
        return None

    monkeypatch.setattr(geocoder, "_try_geonames", fake_geonames)
    monkeypatch.setattr(geocoder, "_try_nominatim", fake_nominatim)
    monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "America/Sao_Paulo")

    geocoder.geocode("Belo Horizonte", "MG")
    geocoder.geocode("Belo Horizonte", "MG")
    geocoder.geocode("Belo Horizonte", "MG")

    assert chamadas["geonames"] == 1, "deveria ter caído no cache da 2ª em diante"
    assert chamadas["nominatim"] == 0


# ─────────────────────────────────────────────────────────────
# Inferência de country code (ISO alpha-2)
# ─────────────────────────────────────────────────────────────
class TestCountryISO:
    def test_uf_brasileira_vira_br(self, geocoder):
        assert geocoder._country_iso("MG") == "BR"
        assert geocoder._country_iso("SP") == "BR"
        assert geocoder._country_iso("rj") == "BR"  # case-insensitive

    def test_iso_alpha2_passa_direto(self, geocoder):
        assert geocoder._country_iso("PT") == "PT"
        assert geocoder._country_iso("FR") == "FR"

    def test_nome_por_extenso(self, geocoder):
        assert geocoder._country_iso("USA") == "US"
        assert geocoder._country_iso("Brasil") == "BR"
        assert geocoder._country_iso("Portugal") == "PT"

    def test_desconhecido_retorna_none(self, geocoder):
        assert geocoder._country_iso("Vulcano") is None
        assert geocoder._country_iso("") is None
