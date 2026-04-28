from collections import Counter

SIGNOS_PT = {
    "Ari": "Aries", "Tau": "Touro", "Gem": "Gemeos",
    "Can": "Cancer", "Leo": "Leao", "Vir": "Virgem",
    "Lib": "Libra", "Sco": "Escorpiao", "Sag": "Sagitario",
    "Cap": "Capricornio", "Aqu": "Aquario", "Pis": "Peixes",
}

ELEMENTOS_PT = {
    "Fire": "Fogo", "Earth": "Terra", "Air": "Ar", "Water": "Agua",
}

QUALIDADES_PT = {
    "Cardinal": "Cardinal", "Fixed": "Fixo", "Mutable": "Mutavel",
}

CASAS_NUM = {
    "First_House": 1, "Second_House": 2, "Third_House": 3,
    "Fourth_House": 4, "Fifth_House": 5, "Sixth_House": 6,
    "Seventh_House": 7, "Eighth_House": 8, "Ninth_House": 9,
    "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12,
}

ASPECTOS_PT = {
    "conjunction": "conjuncao",
    "opposition": "oposicao",
    "trine": "trigono",
    "square": "quadratura",
    "sextile": "sextil",
    "quincunx": "quincuncio",
    "semisquare": "semiquadratura",
    "semisextile": "semissextil",
    "sesquiquadrate": "sesquiquadratura",
    "biquintile": "biquintil",
    "quintile": "quintil",
}

PLANETAS_NOMES = {
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
    "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth"
]


def signo_pt(s):
    return SIGNOS_PT.get(s, s)


def elemento_pt(e):
    return ELEMENTOS_PT.get(e, e)


def qualidade_pt(q):
    return QUALIDADES_PT.get(q, q)


def formatar_grau(pos: float) -> str:
    graus = int(pos)
    minutos = round((pos - graus) * 60)
    if minutos == 60:
        graus += 1
        minutos = 0
    return f"{graus}\u00b0{minutos:02d}'"


def extrair_casa(ponto) -> int | None:
    house_val = getattr(ponto, "house", None)
    if house_val is None:
        return None
    return CASAS_NUM.get(str(house_val), None)


def formatar_planeta(ponto) -> dict:
    return {
        "signo": signo_pt(ponto.sign),
        "casa": extrair_casa(ponto),
        "grau": formatar_grau(ponto.position),
        "grau_decimal": round(ponto.position, 4),
        "posicao_absoluta": round(ponto.abs_pos, 4),
        "retrogrado": bool(ponto.retrograde),
        "velocidade": round(ponto.speed, 4) if ponto.speed is not None else None,
        "declinacao": round(ponto.declination, 4) if ponto.declination is not None else None,
        "elemento": elemento_pt(ponto.element),
        "qualidade": qualidade_pt(ponto.quality),
    }


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
        casas[f"casa_{i}"] = {
            "signo": signo_pt(h.sign),
            "grau": formatar_grau(h.position),
            "grau_decimal": round(h.position, 4),
            "posicao_absoluta": round(h.abs_pos, 4),
        }
    return casas


def formatar_aspectos(chart_data) -> list:
    resultado = []
    for a in chart_data.aspects:
        tipo_en = a.aspect.lower()
        tipo_pt = ASPECTOS_PT.get(tipo_en, tipo_en)
        p1 = PLANETAS_NOMES.get(a.p1_name, a.p1_name.lower())
        p2 = PLANETAS_NOMES.get(a.p2_name, a.p2_name.lower())
        orbe = round(abs(a.orbit), 4)
        aplicando = a.aspect_movement == "Applying" if hasattr(a, "aspect_movement") else None
        resultado.append({
            "planeta_a": p1,
            "planeta_b": p2,
            "tipo": tipo_pt,
            "orbe": orbe,
            "aplicando": aplicando,
            "exato": orbe < 1.0,
        })
    return sorted(resultado, key=lambda x: x["orbe"])


def formatar_pontos_sensiveis(subject) -> dict:
    tn = subject.true_north_lunar_node
    ts = subject.true_south_lunar_node
    ch = subject.chiron
    return {
        "nodo_norte_verdadeiro": formatar_planeta(tn),
        "nodo_sul_verdadeiro": formatar_planeta(ts),
        "chiron": formatar_planeta(ch),
    }


def calcular_sintese(subject, planetas_dict: dict, aspectos: list) -> dict:
    planetas_principais = ["sol","lua","mercurio","venus","marte","jupiter","saturno","urano","netuno","plutao"]

    elementos = Counter()
    qualidades = Counter()
    for nome in planetas_principais:
        p = planetas_dict.get(nome, {})
        if p.get("elemento"):
            elementos[p["elemento"]] += 1
        if p.get("qualidade"):
            qualidades[p["qualidade"]] += 1

    norte = sum(1 for nome in planetas_principais
                if planetas_dict.get(nome, {}).get("casa") and planetas_dict[nome]["casa"] in range(1, 7))
    sul = sum(1 for nome in planetas_principais
              if planetas_dict.get(nome, {}).get("casa") and planetas_dict[nome]["casa"] in range(7, 13))
    hemisferio_vertical = "Norte" if norte >= sul else "Sul"

    leste = sum(1 for nome in planetas_principais
                if planetas_dict.get(nome, {}).get("casa") and planetas_dict[nome]["casa"] in [10,11,12,1,2,3])
    oeste = sum(1 for nome in planetas_principais
                if planetas_dict.get(nome, {}).get("casa") and planetas_dict[nome]["casa"] in [4,5,6,7,8,9])
    hemisferio_horizontal = "Leste" if leste >= oeste else "Oeste"

    contagem = Counter()
    for asp in aspectos:
        contagem[asp["planeta_a"]] += 1
        contagem[asp["planeta_b"]] += 1
    planeta_mais_aspectado = contagem.most_common(1)[0][0] if contagem else None

    stelliums = []
    por_signo = Counter()
    por_casa = Counter()
    planetas_por_signo = {}
    planetas_por_casa = {}

    for nome in planetas_principais:
        p = planetas_dict.get(nome, {})
        signo = p.get("signo")
        casa = p.get("casa")
        if signo:
            por_signo[signo] += 1
            planetas_por_signo.setdefault(signo, []).append(nome)
        if casa:
            por_casa[casa] += 1
            planetas_por_casa.setdefault(casa, []).append(nome)

    for signo, count in por_signo.items():
        if count >= 3:
            stelliums.append({"tipo": "signo", "valor": signo, "planetas": planetas_por_signo[signo]})
    for casa, count in por_casa.items():
        if count >= 3:
            stelliums.append({"tipo": "casa", "valor": casa, "planetas": planetas_por_casa[casa]})

    return {
        "distribuicao_elementos": dict(elementos),
        "distribuicao_qualidades": dict(qualidades),
        "hemisferio_vertical": hemisferio_vertical,
        "hemisferio_horizontal": hemisferio_horizontal,
        "planeta_mais_aspectado": planeta_mais_aspectado,
        "stelliums": stelliums,
    }


def formatar_mapa(subject, chart_data, data: str, hora, local, tem_local: bool,
                  sistema_casas: str, incluir_aspectos: bool) -> dict:
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

    aspectos = formatar_aspectos(chart_data) if incluir_aspectos else []

    resultado = {
        "nome": subject.name,
        "nascimento": {"data": data, "hora": hora, "local": local},
        "sistema_casas": sistema_casas,
        "planetas": planetas,
        "pontos_sensiveis": formatar_pontos_sensiveis(subject),
    }

    if hora and tem_local:
        resultado["angulos"] = {
            "ascendente":   formatar_angulo(subject.first_house),
            "meio_do_ceu":  formatar_angulo(subject.tenth_house),
            "descendente":  formatar_angulo(subject.seventh_house),
            "fundo_do_ceu": formatar_angulo(subject.fourth_house),
        }
        resultado["casas"] = formatar_casas(subject)
    else:
        avisos = []
        if not hora:
            avisos.append("hora de nascimento nao informada")
        if not tem_local:
            avisos.append("local de nascimento nao informado")
        resultado["angulos"] = None
        resultado["casas"] = None
        resultado["aviso"] = f"Angulos e casas omitidos: {' e '.join(avisos)}."

    if incluir_aspectos:
        resultado["aspectos"] = aspectos

    resultado["sintese"] = calcular_sintese(subject, planetas, aspectos)

    return resultado
