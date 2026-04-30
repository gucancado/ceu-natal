import json
import os
import tempfile
import urllib.parse
import urllib.request
from typing import Optional

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "gucancado")
NOMINATIM_USER_AGENT = os.getenv("NOMINATIM_USER_AGENT", "ceu-natal-mcp/2.0")
HTTP_TIMEOUT = 8

CACHE_PATH = os.path.join(tempfile.gettempdir(), "geocoder_cache.json")

_tf = TimezoneFinder()


def _load_cache() -> dict:
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict) -> None:
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
    except OSError:
        pass


def _resolve_timezone(lat: float, lng: float) -> str:
    tz = _tf.timezone_at(lat=lat, lng=lng)
    if not tz:
        tz = _tf.closest_timezone_at(lat=lat, lng=lng)
    return tz or "UTC"


def _try_geonames(cidade: str, nacao: str) -> Optional[tuple[float, float]]:
    params = {
        "q": cidade,
        "country": nacao,
        "maxRows": 1,
        "username": GEONAMES_USERNAME,
    }
    url = "http://api.geonames.org/searchJSON?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

    results = data.get("geonames") or []
    if not results:
        return None
    first = results[0]
    try:
        return float(first["lat"]), float(first["lng"])
    except (KeyError, TypeError, ValueError):
        return None


def _try_nominatim(cidade: str, nacao: str) -> Optional[tuple[float, float]]:
    try:
        geolocator = Nominatim(user_agent=NOMINATIM_USER_AGENT, timeout=HTTP_TIMEOUT)
        query = f"{cidade}, {nacao}" if nacao else cidade
        location = geolocator.geocode(query, addressdetails=False, language="pt")
        if location is None:
            return None
        return float(location.latitude), float(location.longitude)
    except Exception:
        return None


def geocode(cidade: str, nacao: str) -> dict:
    """
    Resolve cidade/nação para {lat, lng, tz_str}.
    GeoNames (HTTP direto) -> Nominatim/OSM (fallback). Cache em /tmp.
    """
    if not cidade:
        raise ValueError("Cidade obrigatória para geocodificação.")

    nacao = (nacao or "").strip()
    cache_key = f"{cidade.strip().lower()}|{nacao.lower()}"

    cache = _load_cache()
    if cache_key in cache:
        return cache[cache_key]

    coords = _try_geonames(cidade, nacao) or _try_nominatim(cidade, nacao)
    if coords is None:
        raise ValueError(
            f"Não foi possível geocodificar '{cidade}, {nacao}'. "
            "Verifique o nome da cidade ou tente novamente mais tarde."
        )

    lat, lng = coords
    tz_str = _resolve_timezone(lat, lng)

    resultado = {"lat": lat, "lng": lng, "tz_str": tz_str}
    cache[cache_key] = resultado
    _save_cache(cache)
    return resultado
