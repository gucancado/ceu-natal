"""
Testes do geocoder. Mocka os helpers privados `_try_geonames` e
`_try_nominatim` (em vez de mockar urllib/requests/httpx) — assim os
testes ficam independentes da biblioteca HTTP usada.
"""
import json
import os

import pytest


@pytest.fixture
def geocoder(tmp_path, monkeypatch):
    """
    Geocoder com estado zerado e cache apontando para um arquivo temporário do
    pytest (`configurar`, sem recarregar o módulo). Restaura o caminho no fim.
    Usa um usuário GeoNames fictício para que o GeoNames entre na cadeia.
    """
    from app.core import geocoder as mod
    monkeypatch.setattr(mod, "GEONAMES_USERNAME", "usuario-de-teste")
    original = (mod.CACHE_PATH, mod.GEOCODER_MAX_CONCORRENTES, mod.GEOCODER_ESPERA_MAX_S)
    mod.configurar(cache_path=str(tmp_path / "geocode-cache.json"))
    yield mod
    caminho, maximo, espera = original
    mod.configurar(cache_path=caminho, max_concorrentes=maximo, espera_max_s=espera)


# ─────────────────────────────────────────────────────────────
# GeocodingError nos três cenários do spec
# ─────────────────────────────────────────────────────────────
def test_cidade_nao_encontrada_em_nenhum_provedor(geocoder, monkeypatch):
    monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: None)
    monkeypatch.setattr(geocoder, "_try_nominatim", lambda c, n: None)
    with pytest.raises(geocoder.GeocodingError, match="Não foi possível geocodificar"):
        geocoder.geocode("Cidade Que Nao Existe", "BR")


def test_todos_provedores_indisponiveis(geocoder, monkeypatch):
    """Simula timeout/erro de rede: helpers levantam ProvedorIndisponivel."""
    def boom(c, n):
        raise geocoder.ProvedorIndisponivel("timeout")
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


# ─────────────────────────────────────────────────────────────
# Rate-limit do Nominatim (≤ 1 req/s por padrão)
# ─────────────────────────────────────────────────────────────
class TestThrottleNominatim:
    def test_segunda_chamada_imediata_dorme(self, geocoder, monkeypatch):
        dormidas = []
        monkeypatch.setattr(geocoder.time, "sleep", lambda s: dormidas.append(s))
        # relógio que avança 0.0s entre leituras → segunda chamada precisa esperar
        monkeypatch.setattr(geocoder.time, "monotonic", lambda: 100.0)
        geocoder._last_nominatim = 0.0

        geocoder._throttle_nominatim()  # primeira: marca o relógio, não dorme
        geocoder._throttle_nominatim()  # segunda: gap = 0 → dorme ~intervalo

        assert len(dormidas) == 1
        assert dormidas[0] == pytest.approx(geocoder._NOMINATIM_MIN_INTERVAL)

    def test_apos_intervalo_nao_dorme(self, geocoder, monkeypatch):
        dormidas = []
        monkeypatch.setattr(geocoder.time, "sleep", lambda s: dormidas.append(s))
        relogio = {"t": 100.0}
        monkeypatch.setattr(geocoder.time, "monotonic", lambda: relogio["t"])
        geocoder._last_nominatim = 0.0

        geocoder._throttle_nominatim()      # marca t=100
        relogio["t"] = 100.0 + geocoder._NOMINATIM_MIN_INTERVAL + 0.1
        geocoder._throttle_nominatim()      # já passou o intervalo → não dorme

        assert dormidas == []


# ─────────────────────────────────────────────────────────────
# Log estruturado de resolução (telemetria)
# ─────────────────────────────────────────────────────────────

class TestLogResolucao:
    def _eventos(self, caplog):
        eventos = []
        for rec in caplog.records:
            try:
                obj = json.loads(rec.getMessage())
            except (ValueError, TypeError):
                continue
            if obj.get("event") == "geocode":
                eventos.append(obj)
        return eventos

    def test_loga_fonte_geonames(self, geocoder, monkeypatch, caplog):
        monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: (-19.92, -43.94))
        monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "America/Sao_Paulo")
        with caplog.at_level("INFO", logger="app.core.geocoder"):
            geocoder.geocode("Belo Horizonte", "MG")
        eventos = self._eventos(caplog)
        assert eventos and eventos[-1]["source"] == "geonames"
        assert eventos[-1]["cache_hit"] is False

    def test_loga_cache_hit_na_segunda(self, geocoder, monkeypatch, caplog):
        monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: (-19.92, -43.94))
        monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "America/Sao_Paulo")
        geocoder.geocode("Belo Horizonte", "MG")
        with caplog.at_level("INFO", logger="app.core.geocoder"):
            geocoder.geocode("Belo Horizonte", "MG")
        eventos = self._eventos(caplog)
        assert eventos and eventos[-1]["cache_hit"] is True
        assert eventos[-1]["source"] == "cache"

    def test_loga_fonte_nominatim_no_fallback(self, geocoder, monkeypatch, caplog):
        monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: None)
        monkeypatch.setattr(geocoder, "_try_nominatim", lambda c, n: (38.72, -9.13))
        monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "Europe/Lisbon")
        with caplog.at_level("INFO", logger="app.core.geocoder"):
            geocoder.geocode("Lisboa", "Portugal")
        eventos = self._eventos(caplog)
        assert eventos and eventos[-1]["source"] == "nominatim"
        assert eventos[-1]["cache_hit"] is False


# ─────────────────────────────────────────────────────────────
# UF ambígua (também é estado dos EUA) e URL do GeoNames
# ─────────────────────────────────────────────────────────────
class TestUFAmbigua:
    def test_uf_ambigua_sem_filtro_de_pais(self, geocoder):
        assert geocoder._country_iso("MA") is None

    def test_uf_nao_ambigua_vira_br(self, geocoder):
        assert geocoder._country_iso("MG") == "BR"

    def test_iso_fora_das_ufs_passa_direto(self, geocoder):
        assert geocoder._country_iso("CA") == "CA"


class _RespostaFalsa:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return b'{"geonames": []}'


def test_geonames_https_so_cidades_por_populacao(geocoder, monkeypatch):
    urls = []

    def fake_urlopen(url, timeout=None):
        urls.append(url)
        return _RespostaFalsa()

    monkeypatch.setattr(geocoder.urllib.request, "urlopen", fake_urlopen)
    assert geocoder._try_geonames("Boston", "MA") is None
    assert len(urls) == 1
    url = urls[0]
    assert url.startswith("https://secure.geonames.org/searchJSON?")
    assert "featureClass=P" in url
    assert "orderby=population" in url
    assert "maxRows=1" in url
    assert "country=" not in url


# ─────────────────────────────────────────────────────────────
# Cache de falhas (TTL) e teto de entradas
# ─────────────────────────────────────────────────────────────
def _provedores_contados(geocoder, monkeypatch, coords=None):
    chamadas = {"geonames": 0, "nominatim": 0}

    def fake_geonames(c, n):
        chamadas["geonames"] += 1
        return coords

    def fake_nominatim(c, n):
        chamadas["nominatim"] += 1
        return None

    monkeypatch.setattr(geocoder, "_try_geonames", fake_geonames)
    monkeypatch.setattr(geocoder, "_try_nominatim", fake_nominatim)
    monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "UTC")
    return chamadas


def test_falha_cacheada_nao_chama_provedor(geocoder, monkeypatch, caplog):
    chamadas = _provedores_contados(geocoder, monkeypatch)
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Cidade Inexistente", "BR")
    with caplog.at_level("INFO", logger="app.core.geocoder"):
        with pytest.raises(geocoder.GeocodingError):
            geocoder.geocode("Cidade Inexistente", "BR")
    assert chamadas == {"geonames": 1, "nominatim": 1}
    eventos = [json.loads(r.getMessage()) for r in caplog.records
               if r.getMessage().startswith("{")]
    assert eventos and eventos[-1]["source"] == "cache_falha"


def test_falha_cacheada_expira_apos_ttl(geocoder, monkeypatch):
    chamadas = _provedores_contados(geocoder, monkeypatch)
    relogio = {"t": 1_000_000.0}
    monkeypatch.setattr(geocoder.time, "time", lambda: relogio["t"])
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Cidade Inexistente", "BR")
    relogio["t"] += geocoder.TTL_FALHA_S + 1
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Cidade Inexistente", "BR")
    assert chamadas["geonames"] == 2


def test_falha_persistida_em_arquivo(geocoder, monkeypatch):
    _provedores_contados(geocoder, monkeypatch)
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Cidade Inexistente", "BR")
    with open(geocoder.CACHE_PATH, "r", encoding="utf-8") as f:
        salvo = json.load(f)
    assert salvo["cidade inexistente|br"]["erro"] is True


def test_cache_descarta_entradas_invalidas_ao_carregar(geocoder):
    with open(geocoder.CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "ok|br": {"lat": 1.0, "lng": 2.0, "tz_str": "UTC"},
            "falha|br": {"erro": True, "ts": 123.0},
            "lixo|br": "qualquer coisa",
            "meio|br": {"lat": 1.0},
        }, f)
    cache = geocoder._load_cache()
    assert set(cache) == {"ok|br", "falha|br"}


def test_cache_cheio_expulsa_a_mais_antiga(geocoder, monkeypatch):
    _provedores_contados(geocoder, monkeypatch, coords=(1.0, 2.0))
    monkeypatch.setattr(geocoder, "CACHE_MAX", 2)
    geocoder.geocode("Cidade A", "BR")
    geocoder.geocode("Cidade B", "BR")
    geocoder.geocode("Cidade C", "BR")
    cache = geocoder._load_cache()
    assert list(cache) == ["cidade b|br", "cidade c|br"]


# ─────────────────────────────────────────────────────────────
# Semáforo: limita chamadas concorrentes aos provedores
# ─────────────────────────────────────────────────────────────
def test_semaforo_esgotado_levanta_ocupado(geocoder, monkeypatch):
    import threading
    chamadas = _provedores_contados(geocoder, monkeypatch, coords=(1.0, 2.0))
    sem = threading.BoundedSemaphore(1)
    sem.acquire()
    monkeypatch.setattr(geocoder, "_SEMAFORO", sem)
    monkeypatch.setattr(geocoder, "GEOCODER_ESPERA_MAX_S", 0.01)
    with pytest.raises(geocoder.GeocodingError, match="ocupado"):
        geocoder.geocode("Belo Horizonte", "MG")
    assert chamadas == {"geonames": 0, "nominatim": 0}


def test_semaforo_liberado_apos_falha_do_provedor(geocoder, monkeypatch):
    import threading
    _provedores_contados(geocoder, monkeypatch)
    sem = threading.BoundedSemaphore(1)
    monkeypatch.setattr(geocoder, "_SEMAFORO", sem)
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Cidade Inexistente", "BR")
    assert sem.acquire(timeout=0.01)


def test_resolve_timezone_cai_para_terra(geocoder, monkeypatch):
    class FinderFalso:
        def timezone_at(self, lat, lng):
            return None

        def timezone_at_land(self, lat, lng):
            return "Europe/Lisbon"

    monkeypatch.setattr(geocoder, "_timezone_finder", lambda: FinderFalso())
    assert geocoder._resolve_timezone(38.7, -9.1) == "Europe/Lisbon"


# ─────────────────────────────────────────────────────────────
# "Não encontrado" x "provedor indisponível"
# ─────────────────────────────────────────────────────────────
def _fora_do_ar(c, n):
    from app.core.geocoder import ProvedorIndisponivel
    raise ProvedorIndisponivel("timeout")


def _contar(chamadas, chave, resultado):
    def fake(c, n):
        chamadas[chave] += 1
        if callable(resultado):
            return resultado(c, n)
        return resultado
    return fake


def test_nao_encontrado_fica_ttl_falha(geocoder, monkeypatch):
    chamadas = {"geonames": 0, "nominatim": 0}
    monkeypatch.setattr(geocoder, "_try_geonames", _contar(chamadas, "geonames", None))
    monkeypatch.setattr(geocoder, "_try_nominatim", _contar(chamadas, "nominatim", None))
    relogio = {"t": 1_000_000.0}
    monkeypatch.setattr(geocoder.time, "time", lambda: relogio["t"])
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Cidade Inexistente", "BR")
    assert geocoder._load_cache()["cidade inexistente|br"]["indisponivel"] is False
    relogio["t"] += geocoder.TTL_INDISPONIVEL_S + 1
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Cidade Inexistente", "BR")
    assert chamadas["geonames"] == 1  # ainda no cache: vale TTL_FALHA_S
    relogio["t"] += geocoder.TTL_FALHA_S
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Cidade Inexistente", "BR")
    assert chamadas["geonames"] == 2


def test_provedor_indisponivel_fica_no_maximo_ttl_indisponivel(geocoder, monkeypatch):
    assert geocoder.TTL_INDISPONIVEL_S == 300
    chamadas = {"geonames": 0, "nominatim": 0}
    monkeypatch.setattr(geocoder, "_try_geonames", _contar(chamadas, "geonames", _fora_do_ar))
    monkeypatch.setattr(geocoder, "_try_nominatim", _contar(chamadas, "nominatim", _fora_do_ar))
    relogio = {"t": 1_000_000.0}
    monkeypatch.setattr(geocoder.time, "time", lambda: relogio["t"])
    with pytest.raises(geocoder.GeocodingError, match="Não foi possível geocodificar"):
        geocoder.geocode("Belo Horizonte", "MG")
    assert geocoder._load_cache()["belo horizonte|mg"]["indisponivel"] is True
    relogio["t"] += geocoder.TTL_INDISPONIVEL_S - 1
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Belo Horizonte", "MG")
    assert chamadas == {"geonames": 1, "nominatim": 1}  # ainda no cache
    relogio["t"] += 2
    monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: (-19.92, -43.94))
    monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "America/Sao_Paulo")
    assert geocoder.geocode("Belo Horizonte", "MG")["lat"] == -19.92


def test_um_provedor_fora_e_outro_sem_resultado_conta_como_indisponivel(geocoder, monkeypatch):
    monkeypatch.setattr(geocoder, "_try_geonames", _fora_do_ar)
    monkeypatch.setattr(geocoder, "_try_nominatim", lambda c, n: None)
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Belo Horizonte", "MG")
    assert geocoder._load_cache()["belo horizonte|mg"]["indisponivel"] is True


def test_geonames_fora_cai_no_nominatim(geocoder, monkeypatch):
    monkeypatch.setattr(geocoder, "_try_geonames", _fora_do_ar)
    monkeypatch.setattr(geocoder, "_try_nominatim", lambda c, n: (38.72, -9.13))
    monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "Europe/Lisbon")
    assert geocoder.geocode("Lisboa", "Portugal")["tz_str"] == "Europe/Lisbon"


def test_geonames_erro_de_rede_levanta_indisponivel(geocoder, monkeypatch):
    def falha(url, timeout=None):
        raise OSError("rede")
    monkeypatch.setattr(geocoder.urllib.request, "urlopen", falha)
    with pytest.raises(geocoder.ProvedorIndisponivel):
        geocoder._try_geonames("Recife", "PE")


def test_geonames_quota_levanta_indisponivel(geocoder, monkeypatch):
    class Quota(_RespostaFalsa):
        def read(self):
            return b'{"status": {"message": "limite diario excedido", "value": 18}}'
    monkeypatch.setattr(geocoder.urllib.request, "urlopen", lambda url, timeout=None: Quota())
    with pytest.raises(geocoder.ProvedorIndisponivel, match="limite"):
        geocoder._try_geonames("Recife", "PE")


def test_nominatim_erro_levanta_indisponivel(geocoder, monkeypatch):
    class Quebrado:
        def __init__(self, *a, **k):
            pass

        def geocode(self, *a, **k):
            raise OSError("rede")
    monkeypatch.setattr(geocoder, "Nominatim", Quebrado)
    monkeypatch.setattr(geocoder, "_throttle_nominatim", lambda: None)
    with pytest.raises(geocoder.ProvedorIndisponivel):
        geocoder._try_nominatim("Recife", "PE")


def test_evicao_tira_falha_expirada_antes_da_mais_antiga(geocoder, monkeypatch):
    """A falha expirada sai mesmo sendo mais nova que a falha vigente."""
    t0 = 1_000_000.0
    relogio = {"t": t0}
    monkeypatch.setattr(geocoder.time, "time", lambda: relogio["t"])
    monkeypatch.setattr(geocoder, "CACHE_MAX", 2)
    geocoder._load_cache()
    geocoder._guardar("vigente|br", {"erro": True, "ts": t0, "indisponivel": False})
    geocoder._guardar("expirada|br", {"erro": True, "ts": t0 + 1, "indisponivel": True})
    relogio["t"] = t0 + 1 + geocoder.TTL_INDISPONIVEL_S
    geocoder._guardar("coord|br", {"lat": 3.0, "lng": 4.0, "tz_str": "UTC"})
    assert list(geocoder._load_cache()) == ["vigente|br", "coord|br"]


def test_evicao_tira_falha_vigente_antes_de_coordenada(geocoder, monkeypatch):
    monkeypatch.setattr(geocoder, "CACHE_MAX", 2)
    geocoder._load_cache()
    geocoder._guardar("coord antiga|br", {"lat": 1.0, "lng": 2.0, "tz_str": "UTC"})
    geocoder._guardar("falha|br", {"erro": True, "ts": geocoder.time.time(), "indisponivel": False})
    geocoder._guardar("coord nova|br", {"lat": 3.0, "lng": 4.0, "tz_str": "UTC"})
    assert list(geocoder._load_cache()) == ["coord antiga|br", "coord nova|br"]


def test_configurar_zera_cache_e_semaforo(geocoder, tmp_path):
    geocoder._load_cache()
    geocoder._guardar("x|br", {"lat": 1.0, "lng": 2.0, "tz_str": "UTC"})
    outro = tmp_path / "outro.json"
    geocoder.configurar(cache_path=str(outro), max_concorrentes=1)
    assert geocoder.CACHE_PATH == str(outro)
    assert geocoder._load_cache() == {}
    assert geocoder._SEMAFORO.acquire(timeout=0)
    assert not geocoder._SEMAFORO.acquire(timeout=0)
    geocoder._SEMAFORO.release()


def test_evicao_preserva_a_falha_recem_inserida(geocoder, monkeypatch):
    """Cache cheio de coordenadas: a falha nova fica e sai a coordenada mais antiga."""
    _provedores_contados(geocoder, monkeypatch, coords=(1.0, 2.0))
    monkeypatch.setattr(geocoder, "CACHE_MAX", 2)
    geocoder.geocode("Cidade A", "BR")
    geocoder.geocode("Cidade B", "BR")
    monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: None)
    monkeypatch.setattr(geocoder, "_try_nominatim", lambda c, n: None)
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Inexistente", "BR")
    cache = geocoder._load_cache()
    assert list(cache) == ["cidade b|br", "inexistente|br"]
    assert cache["inexistente|br"]["erro"] is True
    # A falha cacheada evita nova chamada aos provedores.
    monkeypatch.setattr(geocoder, "_try_geonames", lambda c, n: pytest.fail("devia vir do cache"))
    with pytest.raises(geocoder.GeocodingError):
        geocoder.geocode("Inexistente", "BR")


# ─────────────────────────────────────────────────────────────
# Sem GEONAMES_USERNAME: só o Nominatim, com um aviso por processo
# ─────────────────────────────────────────────────────────────
def _sem_geonames(geocoder, monkeypatch):
    """Usuário vazio; GeoNames proibido; Nominatim registra as chamadas."""
    monkeypatch.setattr(geocoder, "GEONAMES_USERNAME", "")
    monkeypatch.setattr(geocoder, "_try_geonames",
                        lambda c, n: pytest.fail("GeoNames não devia ser chamado"))
    chamadas = []

    def fake_nominatim(c, n):
        chamadas.append((c, n))
        return (38.72, -9.13)

    monkeypatch.setattr(geocoder, "_try_nominatim", fake_nominatim)
    monkeypatch.setattr(geocoder, "_resolve_timezone", lambda lat, lng: "Europe/Lisbon")
    return chamadas


def _avisos_sem_geonames(caplog):
    return [r for r in caplog.records
            if r.levelname == "WARNING" and "GEONAMES_USERNAME" in r.getMessage()]


def test_sem_usuario_geonames_usa_so_o_nominatim(geocoder, monkeypatch):
    chamadas = _sem_geonames(geocoder, monkeypatch)
    res = geocoder.geocode("Lisboa", "Portugal")
    assert res["lat"] == 38.72
    assert chamadas == [("Lisboa", "Portugal")]


def test_sem_usuario_geonames_avisa_uma_vez(geocoder, monkeypatch, caplog):
    _sem_geonames(geocoder, monkeypatch)
    with caplog.at_level("WARNING", logger="app.core.geocoder"):
        geocoder.geocode("Lisboa", "Portugal")
        geocoder.geocode("Porto", "Portugal")
    avisos = _avisos_sem_geonames(caplog)
    assert len(avisos) == 1
    assert "Nominatim" in avisos[0].getMessage()


def test_configurar_rearma_o_aviso_sem_geonames(geocoder, monkeypatch, caplog):
    _sem_geonames(geocoder, monkeypatch)
    with caplog.at_level("WARNING", logger="app.core.geocoder"):
        geocoder.geocode("Lisboa", "Portugal")
        geocoder.configurar()
        geocoder.geocode("Porto", "Portugal")
    assert len(_avisos_sem_geonames(caplog)) == 2
