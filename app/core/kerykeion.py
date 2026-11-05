# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Wrapper sobre Kerykeion 5.x: cria AstrologicalSubject com lat/lng/tz explícitos
(online=False) e expõe utilitários para extrair planetas e casas.
"""
from typing import TYPE_CHECKING, Optional, cast

from kerykeion import AstrologicalSubjectFactory

if TYPE_CHECKING:
    from kerykeion.schemas import HousesSystemIdentifier

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

# Acima desta latitude o Kerykeion (`check_and_adjust_polar_latitude`) corta a
# latitude para 66° antes de chamar `swe_houses`: casas, ascendente e meio do
# céu sairiam calculados para outro lugar, em qualquer sistema de casas. O corte
# também sobrescreve `subject.lat`, então a checagem usa a latitude resolvida
# antes de criar o subject (`resolver_coordenadas`).
LATITUDE_MAX_CASAS = 66.0

MOTIVO_LATITUDE_SEM_CASAS = (
    "latitude acima de 66° não é suportada pelo cálculo de casas nesta versão"
)


def latitude_suporta_casas(lat: float) -> bool:
    """True quando |lat| <= 66°, faixa em que as casas saem corretas."""
    return abs(lat) <= LATITUDE_MAX_CASAS


def exigir_latitude_com_casas(lat: float) -> None:
    """Para técnicas que dependem das casas natais: recusa latitude polar."""
    if not latitude_suporta_casas(lat):
        raise ValueError(f"Casas e ângulos indisponíveis: {MOTIVO_LATITUDE_SEM_CASAS}.")


def resolver_coordenadas(
    cidade: Optional[str],
    nacao: Optional[str],
    lat: Optional[float],
    lng: Optional[float],
    tz_str: Optional[str],
) -> tuple[float, float, str]:
    """(lat, lng, tz_str) explícitos, ou via geocode(cidade, nacao), ou (0, 0, UTC)."""
    if lat is None or lng is None or tz_str is None:
        if cidade:
            coords = geocode(cidade, nacao or "")
            return coords["lat"], coords["lng"], coords["tz_str"]
        return 0.0, 0.0, "UTC"
    return lat, lng, tz_str


def _erro_de_horario_de_verao(exc: BaseException) -> bool:
    """True quando a exceção do Kerykeion nasceu de hora ambígua/inexistente (pytz)."""
    from pytz.exceptions import AmbiguousTimeError, NonExistentTimeError

    origem = exc.__cause__ or exc.__context__
    return isinstance(origem, (AmbiguousTimeError, NonExistentTimeError))


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
    is_dst: Optional[bool] = None,
):
    """
    Cria AstrologicalSubject sem rede.
    Coordenadas: ou via (lat, lng, tz_str) explícitos, ou resolvidas por geocode(cidade, nacao).
    Quando nada é fornecido, usa (0,0,UTC) — apenas posições por signo serão úteis.

    `is_dst` desambigua a hora local na transição do horário de verão (hora
    repetida ou inexistente). Sem ele, o Kerykeion levanta `KerykeionException`
    a partir do erro do pytz, que aqui vira `ValueError` com instrução para o
    chamador. Outras `KerykeionException` sobem como estão.
    """
    from kerykeion.schemas import KerykeionException

    lat, lng, tz_str = resolver_coordenadas(cidade, nacao, lat, lng, tz_str)

    try:
        return AstrologicalSubjectFactory.from_birth_data(
            name=nome,
            year=ano, month=mes, day=dia,
            hour=hora, minute=minuto,
            city=cidade or "Unknown",
            nation=nacao or "XX",
            lat=lat, lng=lng, tz_str=tz_str,
            # `sistema_casas` já passou por `validar_sistema_casas` (subconjunto do Literal).
            houses_system_identifier=cast("HousesSystemIdentifier", sistema_casas),
            is_dst=is_dst,
            online=False,
        )
    except KerykeionException as exc:
        if not _erro_de_horario_de_verao(exc):
            raise
        raise ValueError(
            f"Hora ambígua ou inexistente por causa do horário de verão em {tz_str}: "
            f"informe is_dst=true (horário de verão) ou is_dst=false. Detalhe: {exc}"
        ) from exc


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


def coletar_pontos(subject, *, fixo: bool = False) -> list[dict]:
    """Pontos no formato consumido por `aspectos`: 10 planetas + nodos + Quíron.

    `fixo=True` marca o lado que não se move na técnica (o natal em trânsitos,
    progressões e revoluções): `speed` vem 0.0 para que `aplicando` dependa só
    do movimento do outro lado.
    """
    pontos = []
    for iterador in (planetas_iter, pontos_sensiveis_iter):
        for nome_pt, ponto in iterador(subject):
            pontos.append({
                "nome": nome_pt,
                "abs_pos": ponto.abs_pos,
                "speed": 0.0 if fixo else ponto.speed,
            })
    return pontos


def casas_iter(subject):
    """Itera (numero_casa, ponto_cuspide) para as 12 casas."""
    for i, nome in enumerate(CASAS_NOMES, 1):
        yield i, getattr(subject, f"{nome}_house")
