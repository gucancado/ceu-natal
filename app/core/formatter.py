SIGNOS_PT = {
    "Ari": "Aries", "Tau": "Touro", "Gem": "Gemeos",
    "Can": "Cancer", "Leo": "Leao", "Vir": "Virgem",
    "Lib": "Libra", "Sco": "Escorpiao", "Sag": "Sagitario",
    "Cap": "Capricornio", "Aqu": "Aquario", "Pis": "Peixes",
}

ELEMENTOS_PT = {"Fire": "Fogo", "Earth": "Terra", "Air": "Ar", "Water": "Agua"}
QUALIDADES_PT = {"Cardinal": "Cardinal", "Fixed": "Fixo", "Mutable": "Mutavel"}

CASAS_NUM = {
    "First_House": 1, "Second_House": 2, "Third_House": 3,
    "Fourth_House": 4, "Fifth_House": 5, "Sixth_House": 6,
    "Seventh_House": 7, "Eighth_House": 8, "Ninth_House": 9,
    "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12,
}

PLANETAS_NOMES_PT = {
    "Sun": "sol", "Moon": "lua", "Mercury": "mercurio",
    "Venus": "venus", "Mars": "marte", "Jupiter": "jupiter",
    "Saturn": "saturno", "Uranus": "urano", "Neptune": "netuno",
    "Pluto": "plutao", "Chiron": "chiron",
    "True_North_Lunar_Node": "nodo_norte_verdadeiro",
    "True_South_Lunar_Node": "nodo_sul_verdadeiro",
    "Ascendant": "ascendente", "Medium_Coeli": "meio_do_ceu",
}

CASAS_NOMES = [
    "first", "second", "third", "fourth", "fifth", "sixth",
    "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
]

# Regentes por signo, chaveados pelo nome em português (saída de `signo_pt`).
# Guardamos as duas escolas porque a leitura do regente do ascendente numa
# revolução muda conforme a tradição adotada — quem lê Escorpião por Marte não
# quer receber Plutão em silêncio.
REGENTES_SIGNO = {
    "Aries":       {"moderno": "marte",   "tradicional": "marte"},
    "Touro":       {"moderno": "venus",   "tradicional": "venus"},
    "Gemeos":      {"moderno": "mercurio", "tradicional": "mercurio"},
    "Cancer":      {"moderno": "lua",     "tradicional": "lua"},
    "Leao":        {"moderno": "sol",     "tradicional": "sol"},
    "Virgem":      {"moderno": "mercurio", "tradicional": "mercurio"},
    "Libra":       {"moderno": "venus",   "tradicional": "venus"},
    "Escorpiao":   {"moderno": "plutao",  "tradicional": "marte"},
    "Sagitario":   {"moderno": "jupiter", "tradicional": "jupiter"},
    "Capricornio": {"moderno": "saturno", "tradicional": "saturno"},
    "Aquario":     {"moderno": "urano",   "tradicional": "saturno"},
    "Peixes":      {"moderno": "netuno",  "tradicional": "jupiter"},
}

SISTEMAS_CASAS_NOMES = {
    "P": "Placidus", "K": "Koch", "O": "Porphyrius", "R": "Regiomontanus",
    "C": "Campanus", "E": "Equal", "W": "Whole Sign", "B": "Alcabitus",
    "M": "Morinus", "T": "Topocentric",
}


def nome_sistema_casas(identificador: str) -> str:
    return SISTEMAS_CASAS_NOMES.get(identificador, identificador)


def signo_pt(s):
    return SIGNOS_PT.get(s, s)


def elemento_pt(e):
    return ELEMENTOS_PT.get(e, e)


def qualidade_pt(q):
    return QUALIDADES_PT.get(q, q)


def planeta_pt(nome_en: str) -> str:
    return PLANETAS_NOMES_PT.get(nome_en, nome_en.lower())


def regentes_de(signo_em_portugues: str) -> dict:
    """Regentes moderno e tradicional de um signo. Signo desconhecido → None."""
    return REGENTES_SIGNO.get(signo_em_portugues, {"moderno": None, "tradicional": None})


def formatar_grau(pos: float) -> str:
    graus = int(pos)
    minutos = round((pos - graus) * 60)
    if minutos == 60:
        graus += 1
        minutos = 0
    return f"{graus}°{minutos:02d}'"


def extrair_casa(ponto) -> int | None:
    house_val = getattr(ponto, "house", None)
    if house_val is None:
        return None
    return CASAS_NUM.get(str(house_val), None)


def formatar_planeta(ponto, incluir_casa: bool = True) -> dict:
    base = {
        "signo": signo_pt(ponto.sign),
        "grau": formatar_grau(ponto.position),
        "grau_decimal": round(ponto.position, 4),
        "posicao_absoluta": round(ponto.abs_pos, 4),
        "retrogrado": bool(ponto.retrograde),
        "velocidade": round(ponto.speed, 4) if ponto.speed is not None else None,
        "declinacao": round(ponto.declination, 4) if ponto.declination is not None else None,
        "elemento": elemento_pt(ponto.element),
        "qualidade": qualidade_pt(ponto.quality),
    }
    if incluir_casa:
        base["casa"] = extrair_casa(ponto)
    return base


def formatar_angulo(ponto) -> dict:
    return {
        "signo": signo_pt(ponto.sign),
        "grau": formatar_grau(ponto.position),
        "grau_decimal": round(ponto.position, 4),
        "posicao_absoluta": round(ponto.abs_pos, 4),
    }


def formatar_casas(subject) -> dict:
    casas = {}
    for i, nome in enumerate(CASAS_NOMES, 1):
        h = getattr(subject, f"{nome}_house")
        casas[f"casa_{i}"] = formatar_angulo(h)
    return casas
