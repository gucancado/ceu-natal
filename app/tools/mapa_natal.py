from typing import Optional

from app.core.aspectos import calcular_aspectos
from app.core.formatter import (
    formatar_angulo,
    formatar_casas,
    formatar_planeta,
    nome_sistema_casas,
    planeta_pt,
)
from app.core.kerykeion import (
    casas_iter,
    criar_subject,
    planetas_iter,
    pontos_sensiveis_iter,
)
from app.core.sintese import calcular_sintese
from app.core.validators import (
    parse_data,
    parse_hora,
    parse_local,
    validar_sistema_casas,
)


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

    subject = criar_subject(
        nome=nome or "Anônimo",
        ano=ano, mes=mes, dia=dia,
        hora=hora_calc, minuto=min_calc,
        cidade=cidade, nacao=nacao,
        lat=lat, lng=lng, tz_str=tz_str,
        sistema_casas=sistema_id,
    )

    incluir_casas = tem_hora and tem_local

    planetas_dict: dict = {}
    pontos_aspectos: list[dict] = []

    for nome_pt, ponto in planetas_iter(subject):
        planetas_dict[nome_pt] = formatar_planeta(ponto, incluir_casa=incluir_casas)
        pontos_aspectos.append({
            "nome": nome_pt,
            "abs_pos": ponto.abs_pos,
            "speed": ponto.speed,
        })

    pontos_sensiveis_dict: dict = {}
    for nome_pt, ponto in pontos_sensiveis_iter(subject):
        pontos_sensiveis_dict[nome_pt] = formatar_planeta(ponto, incluir_casa=incluir_casas)
        pontos_aspectos.append({
            "nome": nome_pt,
            "abs_pos": ponto.abs_pos,
            "speed": ponto.speed,
        })

    aspectos = calcular_aspectos(pontos_aspectos)

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
        resultado["aviso"] = (
            f"Casas e ângulos omitidos: {' e '.join(avisos)}."
        )

    return resultado
