"""
Wrapper sobre Kerykeion 5.x: cria AstrologicalSubject com lat/lng/tz explícitos
(online=False) e expõe utilitários para extrair planetas e casas.
"""
from typing import Optional

from kerykeion import AstrologicalSubjectFactory

from app.core.formatter import CASAS_NOMES, PLANETAS_NOMES_PT
from app.core.geocoder import geocode

PLANETAS_PRINCIPAIS = [
    "sun", "moon", "mercury", "venus", "mars",
    "jupiter", "saturn", "uranus", "neptune", "pluto",
]

PONTOS_SENSIVEIS_ATTRS = [
    "true_north_lunar_node",
    "true_south_lunar_node",
    "chiron",
]


def _coords_from_local(cidade: Optional[str], nacao: Optional[str]) -> Optional[dict]:
    if not cidade:
        return None
    return geocode(cidade, nacao or "")


def criar_subject(
    *,
    nome: str,
    ano: int,
    mes: int,
    dia: int,
    hora: int,
    minuto: int,
    cidade: Optional[str] = None,
    nacao: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    tz_str: Optional[str] = None,
    sistema_casas: str = "P",
):
    """
    Cria AstrologicalSubject sem rede.
    Coordenadas: ou via (lat, lng, tz_str) explícitos, ou resolvidas por geocode(cidade, nacao).
    Quando nada é fornecido, usa (0,0,UTC) — apenas posições por signo serão úteis.
    """
    if lat is None or lng is None or tz_str is None:
        if cidade:
            coords = _coords_from_local(cidade, nacao)
            lat, lng, tz_str = coords["lat"], coords["lng"], coords["tz_str"]
        else:
            lat, lng, tz_str = 0.0, 0.0, "UTC"

    return AstrologicalSubjectFactory.from_birth_data(
        name=nome,
        year=ano, month=mes, day=dia,
        hour=hora, minute=minuto,
        city=cidade or "Unknown",
        nation=nacao or "XX",
        lat=lat, lng=lng, tz_str=tz_str,
        houses_system_identifier=sistema_casas,
        online=False,
    )


def planetas_iter(subject):
    """Itera (nome_pt, ponto) para os 10 planetas principais."""
    for attr in PLANETAS_PRINCIPAIS:
        ponto = getattr(subject, attr)
        nome_pt = PLANETAS_NOMES_PT.get(ponto.name, attr)
        yield nome_pt, ponto


def pontos_sensiveis_iter(subject):
    """Itera (nome_pt, ponto) para nodos verdadeiros e Quíron."""
    for attr in PONTOS_SENSIVEIS_ATTRS:
        ponto = getattr(subject, attr)
        nome_pt = PLANETAS_NOMES_PT.get(ponto.name, attr)
        yield nome_pt, ponto


def casas_iter(subject):
    """Itera (numero_casa, ponto_cuspide) para as 12 casas."""
    for i, nome in enumerate(CASAS_NOMES, 1):
        yield i, getattr(subject, f"{nome}_house")
