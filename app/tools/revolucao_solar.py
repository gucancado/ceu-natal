"""
Revolução solar — o mapa do instante em que o Sol volta à sua longitude natal.

Ocorre uma vez por ano e rege o período até o retorno seguinte. Como o ano
trópico tem 365,2422 dias, o retorno cai na véspera, no dia ou no dia seguinte
ao aniversário, com a hora variando bastante de ano para ano.
"""
from typing import Optional

from app.core.periodos import (
    ancora_revolucao_solar,
    validar_ano_revolucao,
    vigencia_solar,
)
from app.core.revolucoes import (
    build_subject_natal,
    criar_factory,
    executar_retorno,
    instante_utc,
    montar_destaques,
    montar_resultado,
    resolver_local_revolucao,
)
from app.core.validators import validar_sistema_casas

NOTA_METODO = (
    "Mapa levantado para o instante exato em que o Sol em trânsito retorna à "
    "longitude eclíptica que ocupava no nascimento. O local informado não altera "
    "nenhuma posição planetária — define apenas ascendente, meio do céu e "
    "cúspides. Revolução trópica, sem correção de precessão: a variante "
    "precessionada somaria ~50,3\"/ano à longitude alvo e deslocaria o instante "
    "em cerca de 20 minutos por ano de idade."
)

FONTE = "swisseph solcross_ut via kerykeion PlanetaryReturnFactory"


def calcular_revolucao_solar(
    *,
    natal: dict,
    ano: int,
    local_revolucao: str,
    sistema_casas: Optional[str] = None,
) -> dict:
    """Revolução solar do ano pedido, levantada no local informado."""
    sistema_id = validar_sistema_casas(sistema_casas)
    validar_ano_revolucao(ano)  # faixa de efemérides, antes de qualquer geocoding

    subject_natal, (dia_n, mes_n, ano_n) = build_subject_natal(natal, sistema_id)
    validar_ano_revolucao(ano, ano_nascimento=ano_n)

    coords = resolver_local_revolucao(local_revolucao)

    factory = criar_factory(subject_natal, coords)
    ancora = ancora_revolucao_solar(dia_n, mes_n, ano)
    retorno = executar_retorno(
        lambda: factory.next_return_from_date(
            ancora.year, ancora.month, ancora.day, return_type="Solar"
        )
    )

    resultado = montar_resultado(
        tipo="solar",
        natal=natal,
        subject_natal=subject_natal,
        retorno=retorno,
        coords=coords,
        sistema_id=sistema_id,
        vigencia=vigencia_solar(instante_utc(retorno)),
        fonte=FONTE,
        nota_metodo=NOTA_METODO,
        luminar_definicional="sol",
    )
    resultado["ano"] = ano
    resultado["destaques"] = montar_destaques(resultado, subject_natal, "sol")

    return resultado
