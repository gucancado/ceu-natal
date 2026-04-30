import json
import logging
import os
import tempfile
import threading
import urllib.parse
import urllib.request
from typing import Optional, Tuple

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

logger = logging.getLogger(__name__)

GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "gucancado")
NOMINATIM_USER_AGENT = os.getenv("NOMINATIM_USER_AGENT", "ceu-natal-mcp/2.0")
HTTP_TIMEOUT = 8

CACHE_PATH = os.getenv(
    "GEOCODER_CACHE_PATH",
    os.path.join(tempfile.gettempdir(), "ceu-natal-geocode-cache.json"),
)

_ESTADOS_BR = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}

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


_tf = TimezoneFinder()
_cache_lock = threading.Lock()
_cache: dict = {}
_cache_loaded = False


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


def _resolve_timezone(lat: float, lng: float) -> str:
    tz = _tf.timezone_at(lat=lat, lng=lng)
    if not tz:
        tz = _tf.closest_timezone_at(lat=lat, lng=lng)
    return tz or "UTC"


def _country_iso(nacao: str) -> Optional[str]:
    """Retorna o ISO alpha-2 para usar em filtro de country, ou None."""
    if not nacao:
        return None
    nacao_up = nacao.strip().upper()
    if nacao_up in _ESTADOS_BR:
        return "BR"
    if len(nacao_up) == 2 and nacao_up.isalpha():
        return nacao_up
    return _PAIS_PARA_ISO.get(nacao_up)


def _build_query(cidade: str, nacao: str) -> str:
    return f"{cidade}, {nacao}".strip(", ").strip() if nacao else cidade.strip()


def _try_geonames(cidade: str, nacao: str) -> Optional[Tuple[float, float]]:
    params = {
        "q": _build_query(cidade, nacao),
        "maxRows": 1,
        "username": GEONAMES_USERNAME,
    }
    iso = _country_iso(nacao)
    if iso:
        params["country"] = iso

    url = "http://api.geonames.org/searchJSON?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        logger.info("GeoNames indisponível: %s", exc)
        return None

    results = data.get("geonames") or []
    if not results:
        return None
    first = results[0]
    try:
        return float(first["lat"]), float(first["lng"])
    except (KeyError, TypeError, ValueError):
        return None


def _try_nominatim(cidade: str, nacao: str) -> Optional[Tuple[float, float]]:
    try:
        geolocator = Nominatim(user_agent=NOMINATIM_USER_AGENT, timeout=HTTP_TIMEOUT)
        location = geolocator.geocode(_build_query(cidade, nacao),
                                      addressdetails=False, language="pt")
        if location is None:
            return None
        return float(location.latitude), float(location.longitude)
    except Exception as exc:
        logger.info("Nominatim indisponível: %s", exc)
        return None


def geocode(cidade: str, nacao: str) -> dict:
    """
    Resolve cidade/nação para {lat, lng, tz_str}.

    Tenta GeoNames (HTTP direto) e cai pra Nominatim/OSM como fallback.
    Cache persistente em arquivo JSON (`GEOCODER_CACHE_PATH`).

    Levanta `GeocodingError` se nenhum provedor conseguir resolver.
    """
    if not cidade:
        raise GeocodingError("Cidade obrigatória para geocodificação.")

    nacao = (nacao or "").strip()
    cache_key = f"{cidade.strip().lower()}|{nacao.lower()}"

    cache = _load_cache()
    if cache_key in cache:
        return cache[cache_key]

    geonames_result = _try_geonames(cidade, nacao)
    nominatim_result = None if geonames_result else _try_nominatim(cidade, nacao)
    coords = geonames_result or nominatim_result

    if coords is None:
        # Diferenciar "todos os provedores indisponíveis" vs "cidade não encontrada"
        # é difícil sem expor estado interno; mensagem cobre ambos os casos.
        raise GeocodingError(
            f"Não foi possível geocodificar '{cidade}"
            f"{', ' + nacao if nacao else ''}'. "
            "Verifique o nome da cidade ou tente novamente em instantes."
        )

    lat, lng = coords
    if lat is None or lng is None:
        raise GeocodingError(
            f"Resposta do geocoder sem coordenadas válidas para '{cidade}'."
        )

    tz_str = _resolve_timezone(lat, lng)

    resultado = {"lat": lat, "lng": lng, "tz_str": tz_str}
    with _cache_lock:
        cache[cache_key] = resultado
        _save_cache()
    return resultado
