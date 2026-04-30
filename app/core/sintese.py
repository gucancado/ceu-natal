from collections import Counter

PLANETAS_PRINCIPAIS_PT = [
    "sol", "lua", "mercurio", "venus", "marte",
    "jupiter", "saturno", "urano", "netuno", "plutao",
]


def calcular_sintese(planetas_dict: dict, aspectos: list[dict]) -> dict:
    elementos = Counter()
    qualidades = Counter()
    for nome in PLANETAS_PRINCIPAIS_PT:
        p = planetas_dict.get(nome, {})
        if p.get("elemento"):
            elementos[p["elemento"]] += 1
        if p.get("qualidade"):
            qualidades[p["qualidade"]] += 1

    norte = sum(
        1 for nome in PLANETAS_PRINCIPAIS_PT
        if planetas_dict.get(nome, {}).get("casa") in range(1, 7)
    )
    sul = sum(
        1 for nome in PLANETAS_PRINCIPAIS_PT
        if planetas_dict.get(nome, {}).get("casa") in range(7, 13)
    )
    hemisferio_vertical = "Norte" if norte >= sul else "Sul"

    leste_casas = {10, 11, 12, 1, 2, 3}
    oeste_casas = {4, 5, 6, 7, 8, 9}
    leste = sum(
        1 for nome in PLANETAS_PRINCIPAIS_PT
        if planetas_dict.get(nome, {}).get("casa") in leste_casas
    )
    oeste = sum(
        1 for nome in PLANETAS_PRINCIPAIS_PT
        if planetas_dict.get(nome, {}).get("casa") in oeste_casas
    )
    hemisferio_horizontal = "Leste" if leste >= oeste else "Oeste"

    contagem = Counter()
    for asp in aspectos:
        contagem[asp["planeta_a"]] += 1
        contagem[asp["planeta_b"]] += 1
    planeta_mais_aspectado = contagem.most_common(1)[0][0] if contagem else None

    por_signo = Counter()
    por_casa = Counter()
    planetas_por_signo: dict = {}
    planetas_por_casa: dict = {}
    for nome in PLANETAS_PRINCIPAIS_PT:
        p = planetas_dict.get(nome, {})
        signo = p.get("signo")
        casa = p.get("casa")
        if signo:
            por_signo[signo] += 1
            planetas_por_signo.setdefault(signo, []).append(nome)
        if casa:
            por_casa[casa] += 1
            planetas_por_casa.setdefault(casa, []).append(nome)

    stelliums = []
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


def sintese_sinastria(aspectos: list[dict]) -> dict:
    harmonicos = sum(1 for a in aspectos if a["natureza"] == "harmonico")
    tensao = sum(1 for a in aspectos if a["natureza"] == "tensao")
    neutros = sum(1 for a in aspectos if a["natureza"] == "neutro")

    contagem_a = Counter()
    contagem_b = Counter()
    for a in aspectos:
        contagem_a[a["planeta_a"]] += 1
        contagem_b[a["planeta_b"]] += 1

    return {
        "aspectos_harmonicos": harmonicos,
        "aspectos_tensao": tensao,
        "aspectos_neutros": neutros,
        "planetas_mais_ativados_a": [n for n, _ in contagem_a.most_common(3)],
        "planetas_mais_ativados_b": [n for n, _ in contagem_b.most_common(3)],
    }
