from typing import Optional

from app.core.aspectos import calcular_aspectos_cruzados, casa_de_longitude
from app.core.entrada import EntradaNascimento
from app.core.formatter import signo_pt
from app.core.kerykeion import casas_iter, coletar_pontos
from app.core.sintese import sintese_sinastria
from app.core.validators import validar_sistema_casas


def _resumo_pessoa(subject, nome: str, asc_confiavel: bool) -> dict:
    asc = subject.first_house
    # Asc só é confiável quando a pessoa tem hora E local — sem hora, o
    # cálculo cai num default de 12:00 que produz um Asc arbitrário.
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
    entrada_a = EntradaNascimento.de_dict(pessoa_a, rotulo="pessoa_a")
    subject_a, nome_a = entrada_a.subject(sistema_id), entrada_a.nome
    entrada_b = EntradaNascimento.de_dict(pessoa_b, rotulo="pessoa_b")
    subject_b, nome_b = entrada_b.subject(sistema_id), entrada_b.nome

    pontos_a = coletar_pontos(subject_a)
    pontos_b = coletar_pontos(subject_b)

    aspectos = calcular_aspectos_cruzados(pontos_a, pontos_b, nome_a, nome_b)

    # Casas só existem com hora E local: sem hora, o cálculo usa 12:00 e as
    # cúspides saem arbitrárias.
    completo_a = entrada_a.tem_hora and entrada_a.tem_local
    completo_b = entrada_b.tem_hora and entrada_b.tem_local
    ativacoes: list[dict] = []
    if completo_a and completo_b:
        # planetas de A nas casas de B, e vice-versa
        ativacoes.extend(_ativacoes(pontos_a, subject_b, nome_a, nome_b))
        ativacoes.extend(_ativacoes(pontos_b, subject_a, nome_b, nome_a))

    resultado = {
        "pessoa_a": _resumo_pessoa(subject_a, nome_a, completo_a),
        "pessoa_b": _resumo_pessoa(subject_b, nome_b, completo_b),
        "aspectos_sinastria": aspectos,
        "ativacoes_de_casas": ativacoes,
        "sintese_sinastria": sintese_sinastria(aspectos),
    }
    incompletos = [n for n, ok in ((nome_a, completo_a), (nome_b, completo_b)) if not ok]
    if incompletos:
        resultado["aviso"] = (
            "Ativações de casas omitidas: hora ou local de nascimento ausente em "
            f"{' e '.join(incompletos)}."
        )
    return resultado
