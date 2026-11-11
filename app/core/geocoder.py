# SPDX-License-Identifier: AGPL-3.0-or-later
"""Geocodificação de cidades: GeoNames, com Nominatim de reserva, e cache persistente."""

import functools
import json
import logging
import os
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Optional, Tuple

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

logger = logging.getLogger(__name__)

# Vazio: o GeoNames sai da cadeia e só o Nominatim (1 req/s) é usado.
GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "")
NOMINATIM_USER_AGENT = os.getenv("NOMINATIM_USER_AGENT", "ceu-natal-mcp/2.0")
HTTP_TIMEOUT = 8
GEONAMES_URL = "https://secure.geonames.org/searchJSON"
# Teto de chamadas simultâneas aos provedores: cada uma prende um worker do
# threadpool por até HTTP_TIMEOUT s; sem teto, /mapa-rapido vira vetor de DoS.
GEOCODER_MAX_CONCORRENTES = int(os.getenv("GEOCODER_MAX_CONCORRENTES", "4"))
GEOCODER_ESPERA_MAX_S = float(os.getenv("GEOCODER_ESPERA_MAX_S", "3.0"))
# "Não encontrado" (um provedor respondeu sem resultado) fica no cache por 1 h:
# evita martelar provedor com cidade inexistente.
TTL_FALHA_S = 3600
# Provedor indisponível (rede, quota, resposta inválida) fica no máximo 5 min:
# uma queda curta não pode bloquear uma cidade válida por 1 h.
TTL_INDISPONIVEL_S = 300
# Teto de entradas do cache; ao exceder, descarta primeiro falhas expiradas,
# depois falhas vigentes e só então coordenadas (sempre da mais antiga).
CACHE_MAX = 10_000
# Nominatim/OSM exige no máximo 1 req/s. Serializamos as chamadas.
_NOMINATIM_MIN_INTERVAL = float(os.getenv("NOMINATIM_MIN_INTERVAL_S", "1.0"))

CACHE_PATH = os.getenv(
    "GEOCODER_CACHE_PATH",
    os.path.join(tempfile.gettempdir(), "ceu-natal-geocode-cache.json"),
)

_ESTADOS_BR = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}

# UFs que também são siglas de estados dos EUA ("Boston, MA"): sem filtro de país.
_UFS_AMBIGUAS = {"AL", "MA", "MS", "MT", "PA", "SC"}

# Mapeamento conservador de nomes comuns → ISO 3166-1 alpha-2.
# GeoNames exige código alpha-2 no parâmetro `country`. Para nomes não
# mapeados, deixamos o GeoNames buscar livre (sem filtro) e o Nominatim
# resolve via texto.
_PAIS_PARA_ISO = {
    "BRASIL": "BR", "BRAZIL": "BR",
    "USA": "US", "EUA": "US", "ESTADOS UNIDOS": "US", "UNITED STATES": "US",
    "PORTUGAL": "PT",
    "ARGENTINA": "AR",
    "URUGUAI": "UY", "URUGUAY": "UY",
    "PARAGUAI": "PY", "PARAGUAY": "PY",
    "CHILE": "CL",
    "MEXICO": "MX", "MÉXICO": "MX",
    "ESPANHA": "ES", "SPAIN": "ES",
    "FRANÇA": "FR", "FRANCE": "FR",
    "ALEMANHA": "DE", "GERMANY": "DE",
    "ITALIA": "IT", "ITÁLIA": "IT", "ITALY": "IT",
    "REINO UNIDO": "GB", "UK": "GB", "UNITED KINGDOM": "GB",
    "JAPAO": "JP", "JAPÃO": "JP", "JAPAN": "JP",
}


class GeocodingError(Exception):
    """Falha resolvendo cidade/coordenadas em todos os provedores."""


class ProvedorIndisponivel(Exception):
    """O provedor não respondeu (rede, quota, resposta fora do formato).

    Diferente de "não encontrado", que o provedor devolve como `None`.
    """


_SEMAFORO = threading.BoundedSemaphore(GEOCODER_MAX_CONCORRENTES)
_cache_lock = threading.Lock()
_cache: dict = {}
_cache_loaded = False

_nominatim_lock = threading.Lock()
_last_nominatim = 0.0

_avisado_sem_geonames = False


def configurar(
    *,
    cache_path: Optional[str] = None,
    max_concorrentes: Optional[int] = None,
    espera_max_s: Optional[float] = None,
) -> None:
    """Reconfigura o módulo e zera o estado: cache em memória (recarregado do
    arquivo no próximo uso), semáforo e relógio do Nominatim. Parâmetro omitido
    mantém o valor atual. Os testes usam isto no lugar de recarregar o módulo."""
    global CACHE_PATH, GEOCODER_MAX_CONCORRENTES, GEOCODER_ESPERA_MAX_S
    global _SEMAFORO, _cache, _cache_loaded, _last_nominatim, _avisado_sem_geonames
    if cache_path is not None:
        CACHE_PATH = cache_path
    if max_concorrentes is not None:
        GEOCODER_MAX_CONCORRENTES = max_concorrentes
    if espera_max_s is not None:
        GEOCODER_ESPERA_MAX_S = espera_max_s
    with _cache_lock:
        _cache = {}
        _cache_loaded = False
    _SEMAFORO = threading.BoundedSemaphore(GEOCODER_MAX_CONCORRENTES)
    _last_nominatim = 0.0
    _avisado_sem_geonames = False


def _avisar_sem_geonames() -> None:
    """Avisa uma vez por processo (ou por `configurar`) que o GeoNames está fora."""
    global _avisado_sem_geonames
    if _avisado_sem_geonames:
        return
    _avisado_sem_geonames = True
    logger.warning(
        "GEONAMES_USERNAME não definido: usando só o Nominatim (1 req/s). "
        "Crie uma conta gratuita em geonames.org e defina a env."
    )


def _provedores() -> list:
    """Cadeia de provedores na ordem de tentativa."""
    if not GEONAMES_USERNAME:
        _avisar_sem_geonames()
        return [("nominatim", _try_nominatim)]
    return [("geonames", _try_geonames), ("nominatim", _try_nominatim)]


def _throttle_nominatim() -> None:
    """Garante intervalo mínimo entre chamadas ao Nominatim (política OSM ≤ 1 req/s)."""
    global _last_nominatim
    # Serializa intencionalmente: N chamadas concorrentes ao Nominatim ficam ~interval apart (política OSM).
    with _nominatim_lock:
        espera = _NOMINATIM_MIN_INTERVAL - (time.monotonic() - _last_nominatim)
        if espera > 0:
            time.sleep(espera)
        _last_nominatim = time.monotonic()


# Chamado a cada cidade resolvida com (cidade, país ISO ou None); o servidor
# liga aqui as estatísticas. Falha no gancho nunca derruba o cálculo.
ao_resolver: Optional[Callable[[str, Optional[str]], None]] = None


def _avisar_resolvida(cidade: str, nacao: str) -> None:
    gancho = ao_resolver
    if gancho is None:
        return
    try:
        gancho(cidade, _country_iso(nacao))
    except Exception:  # noqa: BLE001
        logger.warning("falha ao registrar estatística de lugar", exc_info=True)


def _log_geocode(cidade: str, nacao: str, source: str, cache_hit: bool) -> None:
    logger.info(json.dumps({
        "event": "geocode",
        "cidade": cidade,
        "nacao": nacao,
        "source": source,
        "cache_hit": cache_hit,
    }, ensure_ascii=False))


def _entrada_sucesso(valor) -> bool:
    return isinstance(valor, dict) and {"lat", "lng", "tz_str"} <= valor.keys()


def _entrada_falha(valor) -> bool:
    return (isinstance(valor, dict) and valor.get("erro") is True
            and isinstance(valor.get("ts"), (int, float)))


def _ttl_falha(entrada: dict) -> int:
    return TTL_INDISPONIVEL_S if entrada.get("indisponivel") else TTL_FALHA_S


def _falha_expirada(entrada: dict, agora: float) -> bool:
    return agora - entrada["ts"] >= _ttl_falha(entrada)


def _load_cache() -> dict:
    global _cache, _cache_loaded
    with _cache_lock:
        if _cache_loaded:
            return _cache
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                _cache = json.load(f)
                if not isinstance(_cache, dict):
                    raise ValueError("formato inesperado")
                _cache = {k: v for k, v in _cache.items()
                          if _entrada_sucesso(v) or _entrada_falha(v)}
        except FileNotFoundError:
            _cache = {}
        except (json.JSONDecodeError, ValueError, OSError) as exc:
            logger.warning("cache de geocoder corrompido em %s (%s) — recomeçando vazio.",
                           CACHE_PATH, exc)
            _cache = {}
        _cache_loaded = True
        return _cache


def _save_cache() -> None:
    """Persiste o cache atual em disco. Chamada deve ser feita já com o lock."""
    try:
        os.makedirs(os.path.dirname(CACHE_PATH) or ".", exist_ok=True)
        tmp_path = f"{CACHE_PATH}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(_cache, f, ensure_ascii=False)
        os.replace(tmp_path, CACHE_PATH)
    except OSError as exc:
        logger.warning("não consegui persistir cache de geocoder em %s: %s",
                       CACHE_PATH, exc)


def _evictar(preservar: str) -> None:
    """Traz o cache para CACHE_MAX: falhas expiradas, depois falhas vigentes e
    por último coordenadas, sempre da mais antiga. Nunca descarta `preservar`
    (a entrada recém-gravada). Chamada já com o lock."""
    if len(_cache) <= CACHE_MAX:
        return
    agora = time.time()
    candidatas = [k for k in _cache if k != preservar]
    for chave in [k for k in candidatas if _entrada_falha(_cache[k]) and _falha_expirada(_cache[k], agora)]:
        del _cache[chave]
    falhas = [k for k in candidatas if k in _cache and _entrada_falha(_cache[k])]
    while len(_cache) > CACHE_MAX and falhas:
        del _cache[falhas.pop(0)]
    resto = [k for k in candidatas if k in _cache]
    while len(_cache) > CACHE_MAX and resto:
        del _cache[resto.pop(0)]


def _guardar(cache_key: str, valor: dict) -> None:
    """Grava no cache (já carregado), respeita CACHE_MAX e persiste."""
    with _cache_lock:
        _cache.pop(cache_key, None)
        _cache[cache_key] = valor
        _evictar(preservar=cache_key)
        _save_cache()


@functools.lru_cache(maxsize=1)
def _timezone_finder() -> TimezoneFinder:
    """Instancia o TimezoneFinder só no primeiro uso (carregar leva segundos)."""
    return TimezoneFinder()


def _resolve_timezone(lat: float, lng: float) -> str:
    _tf = _timezone_finder()
    return (_tf.timezone_at(lat=lat, lng=lng)
            or _tf.timezone_at_land(lat=lat, lng=lng)
            or "UTC")


def _country_iso(nacao: str) -> Optional[str]:
    """Retorna o ISO alpha-2 para usar em filtro de country, ou None."""
    if not nacao:
        return None
    nacao_up = nacao.strip().upper()
    if nacao_up in _UFS_AMBIGUAS:
        return None
    if nacao_up in _ESTADOS_BR:
        return "BR"
    if len(nacao_up) == 2 and nacao_up.isalpha():
        return nacao_up
    return _PAIS_PARA_ISO.get(nacao_up)


def _build_query(cidade: str, nacao: str) -> str:
    return f"{cidade}, {nacao}".strip(", ").strip() if nacao else cidade.strip()


def _try_geonames(cidade: str, nacao: str) -> Optional[Tuple[float, float]]:
    """(lat, lng), ou None se o GeoNames respondeu sem resultado.

    Levanta `ProvedorIndisponivel` em erro de rede, quota (o GeoNames responde
    200 com um bloco `status`) ou resposta fora do formato.
    """
    params = {
        "q": _build_query(cidade, nacao),
        "maxRows": 1,
        "featureClass": "P",
        "orderby": "population",
        "username": GEONAMES_USERNAME,
    }
    iso = _country_iso(nacao)
    if iso:
        params["country"] = iso

    url = GEONAMES_URL + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        logger.info("GeoNames indisponível: %s", exc)
        raise ProvedorIndisponivel(f"GeoNames: {exc}") from exc

    if not isinstance(data, dict) or data.get("status"):
        detalhe = data.get("status") if isinstance(data, dict) else data
        logger.info("GeoNames indisponível: %s", detalhe)
        raise ProvedorIndisponivel(f"GeoNames: {detalhe}")

    results = data.get("geonames") or []
    if not results:
        return None
    first = results[0]
    try:
        return float(first["lat"]), float(first["lng"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ProvedorIndisponivel(f"GeoNames: resposta sem coordenadas ({exc})") from exc


def _try_nominatim(cidade: str, nacao: str) -> Optional[Tuple[float, float]]:
    """(lat, lng), ou None se o Nominatim respondeu sem resultado.

    Levanta `ProvedorIndisponivel` em erro de rede, quota ou resposta inválida.
    """
    _throttle_nominatim()
    try:
        geolocator = Nominatim(user_agent=NOMINATIM_USER_AGENT, timeout=HTTP_TIMEOUT)
        location = geolocator.geocode(_build_query(cidade, nacao),
                                      addressdetails=False, language="pt")
        if location is None:
            return None
        return float(location.latitude), float(location.longitude)
    except Exception as exc:
        logger.info("Nominatim indisponível: %s", exc)
        raise ProvedorIndisponivel(f"Nominatim: {exc}") from exc


def geocode(cidade: str, nacao: str) -> dict:
    """
    Resolve cidade/nação para {lat, lng, tz_str}.

    Tenta GeoNames (HTTP direto) e cai pra Nominatim/OSM como fallback; sem
    `GEONAMES_USERNAME`, usa só o Nominatim.
    Cache persistente em arquivo JSON (`GEOCODER_CACHE_PATH`).

    Levanta `GeocodingError` se nenhum provedor conseguir resolver.
    """
    if not cidade:
        raise GeocodingError("Cidade obrigatória para geocodificação.")

    nacao = (nacao or "").strip()
    cache_key = f"{cidade.strip().lower()}|{nacao.lower()}"

    msg_falha = (
        f"Não foi possível geocodificar '{cidade}"
        f"{', ' + nacao if nacao else ''}'. "
        "Verifique o nome da cidade ou tente novamente em instantes."
    )

    cache = _load_cache()
    with _cache_lock:
        entrada = cache.get(cache_key)
    if entrada is not None:
        if not entrada.get("erro"):
            _log_geocode(cidade, nacao, source="cache", cache_hit=True)
            _avisar_resolvida(cidade, nacao)
            return entrada
        if not _falha_expirada(entrada, time.time()):
            _log_geocode(cidade, nacao, source="cache_falha", cache_hit=True)
            raise GeocodingError(msg_falha)

    semaforo = _SEMAFORO
    if not semaforo.acquire(timeout=GEOCODER_ESPERA_MAX_S):
        raise GeocodingError("Geocodificador ocupado. Tente de novo em instantes.")
    coords, source, indisponivel = None, "", False
    try:
        for nome, provedor in _provedores():
            try:
                coords = provedor(cidade, nacao)
            except ProvedorIndisponivel:
                indisponivel = True
                continue
            if coords:
                source = nome
                break
    finally:
        semaforo.release()

    if not coords:
        # Mesma mensagem nos dois casos; muda quanto a falha fica no cache:
        # "não encontrado" TTL_FALHA_S, algum provedor fora do ar
        # TTL_INDISPONIVEL_S (o outro pode ter só não achado por ser pior).
        _guardar(cache_key, {"erro": True, "ts": time.time(), "indisponivel": indisponivel})
        raise GeocodingError(msg_falha)

    lat, lng = coords
    if lat is None or lng is None:
        raise GeocodingError(
            f"Resposta do geocoder sem coordenadas válidas para '{cidade}'."
        )

    tz_str = _resolve_timezone(lat, lng)

    resultado = {"lat": lat, "lng": lng, "tz_str": tz_str}
    _guardar(cache_key, resultado)
    _log_geocode(cidade, nacao, source=source, cache_hit=False)
    _avisar_resolvida(cidade, nacao)
    return resultado
