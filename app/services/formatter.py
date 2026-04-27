CASAS_NUM = {
    "First_House": 1, "Second_House": 2, "Third_House": 3,
    "Fourth_House": 4, "Fifth_House": 5, "Sixth_House": 6,
    "Seventh_House": 7, "Eighth_House": 8, "Ninth_House": 9,
    "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12,
}

SIGNOS_PT = {
    "Ari": "Aries", "Aries": "Aries",
    "Tau": "Touro", "Taurus": "Touro",
    "Gem": "Gemeos", "Gemini": "Gemeos",
    "Can": "Cancer", "Cancer": "Cancer",
    "Leo": "Leao",
    "Vir": "Virgem", "Virgo": "Virgem",
    "Lib": "Libra",
    "Sco": "Escorpiao", "Scorpio": "Escorpiao",
    "Sag": "Sagitario", "Sagittarius": "Sagitario",
    "Cap": "Capricornio", "Capricorn": "Capricornio",
    "Aqu": "Aquario", "Aquarius": "Aquario",
    "Pis": "Peixes", "Pisces": "Peixes",
}


def signo_pt(signo):
    return SIGNOS_PT.get(signo, signo)


def formatar_grau(pos):
    graus = int(pos)
    minutos = round((pos - graus) * 60)
    if minutos == 60:
        graus += 1
        minutos = 0
    return f"{graus}\u00b0{minutos:02d}'"


def extrair_casa(ponto):
    house_val = getattr(ponto, "house", None)
    if house_val is None:
        return None
    return CASAS_NUM.get(str(house_val), None)


def formatar_planeta(ponto):
    return {
        "signo": signo_pt(ponto.sign),
        "casa": extrair_casa(ponto),
        "grau": formatar_grau(ponto.position),
        "retrogrado": bool(ponto.retrograde),
    }


def formatar_angulo(ponto):
    return {
        "signo": signo_pt(ponto.sign),
        "grau": formatar_grau(ponto.position),
    }


def formatar_mapa(subject, data, hora, local, tem_local):
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

    if hora and tem_local:
        resultado["angulos"] = {
            "ascendente":   formatar_angulo(subject.first_house),
            "meio_do_ceu":  formatar_angulo(subject.tenth_house),
            "descendente":  formatar_angulo(subject.seventh_house),
            "fundo_do_ceu": formatar_angulo(subject.fourth_house),
        }
    else:
        avisos = []
        if not hora:
            avisos.append("hora de nascimento nao informada")
        if not tem_local:
            avisos.append("local de nascimento nao informado")
        resultado["angulos"] = None
        resultado["aviso"] = f"Angulos e casas omitidos: {' e '.join(avisos)}."

    return resultado
