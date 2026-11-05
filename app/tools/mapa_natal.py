from typing import Optional

from app.core.aspectos import calcular_aspectos
from app.core.formatter import (
    formatar_angulo,
    formatar_casas,
    formatar_planeta,
    nome_sistema_casas,
)
from app.core.kerykeion import (
    MOTIVO_LATITUDE_SEM_CASAS,
    coletar_pontos,
    criar_subject,
    latitude_suporta_casas,
    planetas_iter,
    pontos_sensiveis_iter,
    resolver_coordenadas,
)
from app.core.sintese import calcular_sintese
from app.core.validators import (
    parse_data,
    parse_hora,
    parse_local,
    validar_sistema_casas,
)

# Metade do movimento diário médio da Lua (~13°): erro máximo ao usar 12:00.
MARGEM_LUA_SEM_HORA = 6.5


def calcular_mapa_natal(
    data: str,
    hora: Optional[str] = None,
    local: Optional[str] = None,
    nome: Optional[str] = None,
    sistema_casas: Optional[str] = None,
    *,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    tz_str: Optional[str] = None,
    is_dst: Optional[bool] = None,
) -> dict:
    """
    Calcula o mapa natal completo.
    Coordenadas: ou via geocoder (cidade/nação extraídos de `local`),
    ou explicitamente via lat/lng/tz_str (caminho usado em testes).
    """
    dia, mes, ano = parse_data(data)
    h, m = parse_hora(hora)
    cidade, nacao = parse_local(local)
    sistema_id = validar_sistema_casas(sistema_casas)

    tem_hora = h is not None
    tem_local = cidade is not None or (lat is not None and lng is not None)

    hora_calc = h if tem_hora else 12
    min_calc = m if tem_hora else 0

    # Latitude resolvida antes do subject: o Kerykeion corta |lat| > 66° e
    # sobrescreve subject.lat, então depois não dá mais para saber.
    lat, lng, tz_str = resolver_coordenadas(cidade, nacao, lat, lng, tz_str)
    latitude_ok = latitude_suporta_casas(lat)

    subject = criar_subject(
        nome=nome or "Anônimo",
        ano=ano, mes=mes, dia=dia,
        hora=hora_calc, minuto=min_calc,
        cidade=cidade, nacao=nacao,
        lat=lat, lng=lng, tz_str=tz_str,
        sistema_casas=sistema_id,
        is_dst=is_dst,
    )

    incluir_casas = tem_hora and tem_local and latitude_ok

    planetas_dict: dict = {}
    for nome_pt, ponto in planetas_iter(subject):
        planetas_dict[nome_pt] = formatar_planeta(ponto, incluir_casa=incluir_casas)

    pontos_sensiveis_dict: dict = {}
    for nome_pt, ponto in pontos_sensiveis_iter(subject):
        pontos_sensiveis_dict[nome_pt] = formatar_planeta(ponto, incluir_casa=incluir_casas)

    aspectos = calcular_aspectos(coletar_pontos(subject))

    if not tem_hora:
        # Sem hora o cálculo usa 12:00; a Lua anda ~13°/dia, então pode estar
        # até ~6,5° antes ou depois da posição calculada.
        lua = planetas_dict["lua"]
        lua["posicao_incerta"] = True
        lua["signo_pode_mudar"] = (
            lua["grau_decimal"] < MARGEM_LUA_SEM_HORA
            or lua["grau_decimal"] > 30.0 - MARGEM_LUA_SEM_HORA
        )
        for asp in aspectos:
            if "lua" in (asp["planeta_a"], asp["planeta_b"]):
                asp["incerto"] = True

    if incluir_casas:
        angulos = {
            "ascendente":   formatar_angulo(subject.first_house),
            "meio_do_ceu":  formatar_angulo(subject.tenth_house),
            "descendente":  formatar_angulo(subject.seventh_house),
            "fundo_do_ceu": formatar_angulo(subject.fourth_house),
        }
        casas = formatar_casas(subject)
    else:
        angulos = {}
        casas = None

    sintese = calcular_sintese(planetas_dict, aspectos)

    resultado = {
        "nome": nome,
        "nascimento": {"data": data, "hora": hora, "local": local},
        "sistema_casas": nome_sistema_casas(sistema_id),
        "planetas": planetas_dict,
        "angulos": angulos,
        "casas": casas,
        "aspectos": aspectos,
        "pontos_sensiveis": pontos_sensiveis_dict,
        "sintese": sintese,
    }

    if not incluir_casas:
        avisos = []
        if not tem_hora:
            avisos.append("hora de nascimento não informada")
        if not tem_local:
            avisos.append("local de nascimento não informado")
        if not latitude_ok:
            avisos.append(MOTIVO_LATITUDE_SEM_CASAS)
        resultado["aviso"] = (
            f"Casas e ângulos omitidos: {' e '.join(avisos)}."
        )
        if not tem_hora:
            resultado["aviso"] += (
                " Posição da Lua incerta: sem a hora, a Lua pode variar até 6,5° "
                "para cada lado, e os aspectos dela vêm marcados como incertos."
            )

    return resultado
