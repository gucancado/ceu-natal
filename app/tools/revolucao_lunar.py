"""
Revolução lunar — o mapa do instante em que a Lua volta à sua longitude natal.

Ocorre a cada ~27,32 dias (mês sideral) e rege o período até o retorno seguinte.
Usada para leitura de ciclo mensal, com ênfase na Lua e na casa que ela ocupa.
"""
from datetime import datetime
from typing import Optional

from app.core.periodos import vigencia_lunar
from app.core.revolucoes import (
    build_subject_natal,
    criar_factory,
    destaques_comuns,
    executar_retorno,
    instante_utc,
    montar_resultado,
    resolver_local_revolucao,
    resumo_planeta,
)
from app.core.validators import parse_data, validar_sistema_casas

NOTA_METODO = (
    "Mapa levantado para o primeiro instante, a partir da data de referencia, em "
    "que a Lua em transito retorna a longitude ecliptica que ocupava no "
    "nascimento. O local informado nao altera nenhuma posicao planetaria — define "
    "apenas ascendente, meio do ceu e cuspides. Ciclo de aproximadamente 27,32 dias."
)

FONTE = "swisseph mooncross_ut via kerykeion PlanetaryReturnFactory"


def calcular_revolucao_lunar(
    *,
    natal: dict,
    data_referencia: str,
    local_revolucao: str,
    sistema_casas: Optional[str] = None,
) -> dict:
    """Primeiro retorno lunar a partir de `data_referencia`, no local informado."""
    sistema_id = validar_sistema_casas(sistema_casas)

    dia_r, mes_r, ano_r = parse_data(data_referencia)
    inicio_busca = datetime(ano_r, mes_r, dia_r)

    subject_natal, _ = build_subject_natal(natal, sistema_id)
    coords = resolver_local_revolucao(local_revolucao)

    factory = criar_factory(subject_natal, coords)
    retorno = executar_retorno(
        lambda: factory.next_return_from_date(
            inicio_busca.year, inicio_busca.month, inicio_busca.day,
            return_type="Lunar",
        )
    )

    dt_utc = instante_utc(retorno)

    resultado = montar_resultado(
        tipo="lunar",
        natal=natal,
        subject_natal=subject_natal,
        retorno=retorno,
        coords=coords,
        sistema_id=sistema_id,
        vigencia=vigencia_lunar(dt_utc),
        fonte=FONTE,
        nota_metodo=NOTA_METODO,
    )
    resultado["data_referencia"] = data_referencia

    destaques = destaques_comuns(resultado, retorno, subject_natal)
    destaques["lua_na_casa"] = resultado["planetas"].get("lua", {}).get("casa")
    destaques["lua_revolucao"] = resumo_planeta(resultado, "lua")
    destaques["sol_revolucao"] = resumo_planeta(resultado, "sol")
    resultado["destaques"] = destaques

    return resultado
