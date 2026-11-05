from typing import Optional

from app.core.aspectos import calcular_aspectos
from app.core.entrada import EntradaNascimento
from app.core.formatter import (
    formatar_angulo,
    formatar_casas,
    formatar_planeta,
    nome_sistema_casas,
)
from app.core.kerykeion import (
    MOTIVO_LATITUDE_SEM_CASAS,
    coletar_pontos,
    latitude_suporta_casas,
    planetas_iter,
    pontos_sensiveis_iter,
)
from app.core.sintese import calcular_sintese
from app.core.validators import validar_sistema_casas

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
    entrada = EntradaNascimento.de_campos(
        data=data, hora=hora, local=local, nome=nome,
        lat=lat, lng=lng, tz_str=tz_str, is_dst=is_dst,
    )
    sistema_id = validar_sistema_casas(sistema_casas)

    tem_hora = entrada.tem_hora
    tem_local = entrada.tem_local

    # Latitude resolvida antes do subject: o Kerykeion corta |lat| > 66° e
    # sobrescreve subject.lat, então depois não dá mais para saber.
    entrada = entrada.resolvida()
    # Resolvida com local sempre tem `lat`; o teste de None só estreita o tipo.
    latitude_ok = not tem_local or entrada.lat is None or latitude_suporta_casas(entrada.lat)

    subject = entrada.subject(sistema_id)

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

    if tem_local:
        # Valores resolvidos antes do subject: o Kerykeion corta |lat| > 66°.
        resultado["local_resolvido"] = {
            "lat": entrada.lat, "lng": entrada.lng, "fuso": entrada.tz_str,
        }

    if not incluir_casas:
        avisos = []
        if not tem_hora:
            avisos.append("hora de nascimento não informada")
        if not tem_local:
            avisos.append("local de nascimento não informado")
        if not latitude_ok:
            avisos.append(MOTIVO_LATITUDE_SEM_CASAS)
        aviso = f"Casas e ângulos omitidos: {' e '.join(avisos)}."
        if not tem_hora:
            aviso += (
                " Posição da Lua incerta: sem a hora, a Lua pode variar até 6,5° "
                "para cada lado, e os aspectos dela vêm marcados como incertos."
            )
        resultado["aviso"] = aviso

    return resultado
