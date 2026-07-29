"""
Revolução lunar — o mapa do instante em que a Lua volta à sua longitude natal.

Ocorre a cada ~27,32 dias (mês sideral) e rege o período até o retorno seguinte.
Usada para leitura de ciclo mensal, com ênfase na Lua e na casa que ela ocupa.

DECISÃO DE DESIGN: a busca devolve o *próximo* retorno a partir da data de
referência, nunca o vigente. Quando a data pedida cai no meio de um ciclo que já
estava rodando, o resultado traz `ciclo_em_curso` apontando isso e dizendo como
obter o mapa do ciclo vigente — sem esse aviso, quem pergunta "como está meu mês
agora?" receberia o mapa do mês que ainda não começou, e o mapa estaria correto
para o período errado.
"""
from datetime import datetime
from typing import Optional

from app.core.periodos import MES_SIDERAL_DIAS, ciclo_anterior, vigencia_lunar
from app.core.revolucoes import (
    build_subject_natal,
    criar_factory,
    executar_retorno,
    instante_utc,
    montar_destaques,
    montar_resultado,
    resolver_local_revolucao,
)
from app.core.validators import parse_data, validar_sistema_casas

NOTA_METODO = (
    "Mapa levantado para o primeiro instante, a partir da data de referência, em "
    "que a Lua em trânsito retorna à longitude eclíptica que ocupava no "
    "nascimento. O local informado não altera nenhuma posição planetária — define "
    "apenas ascendente, meio do céu e cúspides. Ciclo de aproximadamente 27,32 dias."
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
        luminar_definicional="lua",
    )
    resultado["data_referencia"] = data_referencia
    resultado["destaques"] = montar_destaques(resultado, subject_natal, "lua")

    em_curso = ciclo_anterior(dt_utc, inicio_busca, MES_SIDERAL_DIAS)
    if em_curso:
        resultado["ciclo_em_curso"] = em_curso

    return resultado
