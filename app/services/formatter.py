from kerykeion import AstrologicalSubjectFactory

# Mapeamento de signos em inglês para português
SIGNOS_PT = {
    "Ari": "Áries",
    "Tau": "Touro",
    "Gem": "Gêmeos",
    "Can": "Câncer",
    "Leo": "Leão",
    "Vir": "Virgem",
    "Lib": "Libra",
    "Sco": "Escorpião",
    "Sag": "Sagitário",
    "Cap": "Capricórnio",
    "Aqu": "Aquário",
    "Pis": "Peixes",
    # nomes completos também, caso venham assim
    "Aries": "Áries",
    "Taurus": "Touro",
    "Gemini": "Gêmeos",
    "Cancer": "Câncer",
    "Leo": "Leão",
    "Virgo": "Virgem",
    "Libra": "Libra",
    "Scorpio": "Escorpião",
    "Sagittarius": "Sagitário",
    "Capricorn": "Capricórnio",
    "Aquarius": "Aquário",
    "Pisces": "Peixes",
}


def signo_pt(signo: str) -> str:
    return SIGNOS_PT.get(signo, signo)


def formatar_grau(pos: float) -> str:
    """Converte posição decimal para formato grau°minuto'"""
    graus = int(pos)
    minutos = round((pos - graus) * 60)
    if minutos == 60:
        graus += 1
        minutos = 0
    return f"{graus}°{minutos:02d}'"


def formatar_planeta(ponto) -> dict:
    return {
        "signo": signo_pt(ponto.sign),
        "casa": int(ponto.house_name[0]) if ponto.house_name and ponto.house_name[0].isdigit() else None,
        "grau": formatar_grau(ponto.position),
        "retrogrado": bool(ponto.retrograde),
    }


def formatar_angulo(ponto) -> dict:
    return {
        "signo": signo_pt(ponto.sign),
        "grau": formatar_grau(ponto.position),
    }


def formatar_mapa(subject, data: str, hora: str | None, local: str | None, tem_local: bool) -> dict:
    planetas = {
        "sol":      formatar_planeta(subject.sun),
        "lua":      formatar_planeta(subject.moon),
        "mercurio": formatar_planeta(subject.mercury),
        "venus":    formatar_planeta(subject.venus),
        "marte":    formatar_planeta(subject.mars),
        "jupiter":  formatar_planeta(subject.jupiter),
        "saturno":  formatar_planeta(subject.saturn),
        "urano":    formatar_planeta(subject.uranus),
        "netuno":   formatar_planeta(subject.neptune),
        "plutao":   formatar_planeta(subject.pluto),
    }

    resultado = {
        "nome": subject.name,
        "nascimento": {
            "data": data,
            "hora": hora,
            "local": local,
        },
        "planetas": planetas,
    }

    # Ângulos e casas só são confiáveis se hora E local forem informados
    if hora and tem_local:
        resultado["angulos"] = {
            "ascendente":  formatar_angulo(subject.first_house),
            "meio_do_ceu": formatar_angulo(subject.tenth_house),
            "descendente": formatar_angulo(subject.seventh_house),
            "fundo_do_ceu": formatar_angulo(subject.fourth_house),
        }
    else:
        avisos = []
        if not hora:
            avisos.append("hora de nascimento não informada")
        if not tem_local:
            avisos.append("local de nascimento não informado")
        resultado["angulos"] = None
        resultado["aviso"] = f"Ângulos e casas omitidos: {' e '.join(avisos)}."

    return resultado
