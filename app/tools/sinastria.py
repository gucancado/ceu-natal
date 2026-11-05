from typing import Optional

from app.core.aspectos import calcular_aspectos_sinastria, casa_de_longitude
from app.core.formatter import signo_pt
from app.core.kerykeion import (
    casas_iter,
    coletar_pontos,
    criar_subject,
)
from app.core.sintese import sintese_sinastria
from app.core.validators import (
    parse_data,
    parse_hora,
    parse_local,
    validar_sistema_casas,
)


def _build_subject(pessoa: dict, sistema_id: str = "P"):
    data = pessoa.get("data")
    if not data:
        raise ValueError("Campo 'data' obrigatório em cada pessoa.")

    hora = pessoa.get("hora")
    local = pessoa.get("local")
    nome = pessoa.get("nome") or "Anônimo"

    dia, mes, ano = parse_data(data)
    h, m = parse_hora(hora)
    cidade, nacao = parse_local(local)

    tem_hora = h is not None
    tem_local = cidade is not None or (
        pessoa.get("lat") is not None and pessoa.get("lng") is not None
    )

    subject = criar_subject(
        nome=nome,
        ano=ano, mes=mes, dia=dia,
        hora=h if tem_hora else 12,
        minuto=m if tem_hora else 0,
        cidade=cidade, nacao=nacao,
        lat=pessoa.get("lat"),
        lng=pessoa.get("lng"),
        tz_str=pessoa.get("tz_str"),
        sistema_casas=sistema_id,
        is_dst=pessoa.get("is_dst"),
    )
    return subject, nome, tem_hora, tem_local


def _resumo_pessoa(subject, nome: str, tem_local: bool, tem_hora: bool) -> dict:
    asc = subject.first_house
    # Asc só é confiável quando a pessoa tem hora E local — sem hora, o
    # cálculo cai num default de 12:00 que produz um Asc arbitrário.
    asc_confiavel = tem_local and tem_hora
    return {
        "nome": nome,
        "sol": signo_pt(subject.sun.sign),
        "lua": signo_pt(subject.moon.sign),
        "asc": signo_pt(asc.sign) if asc_confiavel else None,
    }


def _ativacoes(planetas_da_pessoa: list[dict], subject_outro,
               nome_pessoa: str, nome_outro: str) -> list[dict]:
    """Cada planeta de uma pessoa cai em qual casa do mapa do outro."""
    casas_lista = list(casas_iter(subject_outro))
    cuspides = [c.abs_pos for _, c in casas_lista]
    saida = []
    for p in planetas_da_pessoa:
        casa = casa_de_longitude(p["abs_pos"], cuspides)
        cuspide_obj = casas_lista[casa - 1][1]
        saida.append({
            "planeta": p["nome"],
            "pessoa": nome_pessoa,
            "cai_na_casa": casa,
            "da_pessoa": nome_outro,
            "signo_da_cuspide": signo_pt(cuspide_obj.sign),
        })
    return saida


def calcular_sinastria(
    pessoa_a: dict,
    pessoa_b: dict,
    sistema_casas: Optional[str] = None,
) -> dict:
    sistema_id = validar_sistema_casas(sistema_casas)
    subject_a, nome_a, tem_hora_a, tem_local_a = _build_subject(pessoa_a, sistema_id)
    subject_b, nome_b, tem_hora_b, tem_local_b = _build_subject(pessoa_b, sistema_id)

    pontos_a = coletar_pontos(subject_a)
    pontos_b = coletar_pontos(subject_b)

    aspectos = calcular_aspectos_sinastria(pontos_a, pontos_b, nome_a, nome_b)

    # Casas só existem com hora E local: sem hora, o cálculo usa 12:00 e as
    # cúspides saem arbitrárias.
    completo_a = tem_hora_a and tem_local_a
    completo_b = tem_hora_b and tem_local_b
    ativacoes: list[dict] = []
    if completo_a and completo_b:
        # planetas de A nas casas de B, e vice-versa
        ativacoes.extend(_ativacoes(pontos_a, subject_b, nome_a, nome_b))
        ativacoes.extend(_ativacoes(pontos_b, subject_a, nome_b, nome_a))

    resultado = {
        "pessoa_a": _resumo_pessoa(subject_a, nome_a, tem_local_a, tem_hora_a),
        "pessoa_b": _resumo_pessoa(subject_b, nome_b, tem_local_b, tem_hora_b),
        "aspectos_sinastria": aspectos,
        "ativacoes_de_casas": ativacoes,
        "sintese_sinastria": sintese_sinastria(aspectos),
    }
    incompletos = [n for n, ok in ((nome_a, completo_a), (nome_b, completo_b)) if not ok]
    if incompletos:
        resultado["aviso"] = (
            "Ativações de casas omitidas: hora de nascimento ausente em "
            f"{' e '.join(incompletos)}."
        )
    return resultado
