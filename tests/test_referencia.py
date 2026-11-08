"""
Testes de referência astronômica: posições conhecidas por efemérides públicas
(USNO/IMCCE), não por sites de astrologia. O subject usa `lat=0, lng=0,
tz_str="UTC"`, então a hora de parede É o instante UTC da efeméride.

Também cobre consistência interna do mapa, o lado natal fixo nos trânsitos e
as leituras de `is_dst` na transição do horário de verão.
"""
import re

import pytest

from app.core.entrada import EntradaNascimento
from app.tools import transitos as transitos_mod
from app.tools.mapa_natal import calcular_mapa_natal
from app.tools.progressoes import _datetime_natal_utc
from app.tools.transitos import calcular_transitos
from tests.conftest import ANA, BH, BRUNO

UTC = {"lat": 0.0, "lng": 0.0, "tz_str": "UTC"}
TOL_SOL = 0.02


def _distancia_circular(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


# ─────────────────────────────────────────────────────────────
# Equinócios e solstícios: Sol em 0°, 90°, 180°, 270°
# ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize("data, hora, longitude", [
    ("20/03/2024", "03:06", 0.0),    # equinócio de março de 2024
    ("20/06/2024", "20:51", 90.0),   # solstício de junho de 2024
    ("23/09/2023", "06:50", 180.0),  # equinócio de setembro de 2023
    ("21/12/2022", "21:48", 270.0),  # solstício de dezembro de 2022
])
def test_sol_nos_equinocios_e_solsticios(data, hora, longitude):
    mapa = calcular_mapa_natal(data, hora, **UTC)
    sol = mapa["planetas"]["sol"]["posicao_absoluta"]
    assert _distancia_circular(sol, longitude) <= TOL_SOL, sol


# ─────────────────────────────────────────────────────────────
# Eclipse lunar total de 08/11/2022, máximo às 10:59 UTC
# ─────────────────────────────────────────────────────────────
def test_eclipse_lunar_total_sol_lua_em_oposicao_exata():
    mapa = calcular_mapa_natal("08/11/2022", "10:59", **UTC)
    sol_lua = [a for a in mapa["aspectos"]
               if {a["planeta_a"], a["planeta_b"]} == {"sol", "lua"}]
    assert len(sol_lua) == 1
    aspecto = sol_lua[0]
    assert aspecto["tipo"] == "oposicao"
    assert aspecto["orbe"] < 0.1
    assert aspecto["exato"] is True


# ─────────────────────────────────────────────────────────────
# Retrogradação conhecida: Mercúrio retrógrado em 01/09/2023
# ─────────────────────────────────────────────────────────────
def test_mercurio_retrogrado_em_setembro_de_2023():
    mapa = calcular_mapa_natal("01/09/2023", "12:00", **UTC)
    mercurio = mapa["planetas"]["mercurio"]
    assert mercurio["retrogrado"] is True
    assert mercurio["velocidade"] < 0


# ─────────────────────────────────────────────────────────────
# Consistência interna do mapa
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def mapa_ana():
    return calcular_mapa_natal(**ANA)


def test_descendente_oposto_ao_ascendente(mapa_ana):
    asc = mapa_ana["angulos"]["ascendente"]["posicao_absoluta"]
    desc = mapa_ana["angulos"]["descendente"]["posicao_absoluta"]
    assert _distancia_circular(desc, (asc + 180.0) % 360.0) <= 0.01


def test_cuspide_da_casa_1_igual_ao_ascendente(mapa_ana):
    asc = mapa_ana["angulos"]["ascendente"]["posicao_absoluta"]
    assert _distancia_circular(mapa_ana["casas"]["casa_1"]["posicao_absoluta"], asc) <= 0.01


def _graus_do_mapa(mapa: dict) -> list[str]:
    graus = [p["grau"] for p in mapa["planetas"].values()]
    graus += [a["grau"] for a in mapa["angulos"].values()]
    graus += [c["grau"] for c in mapa["casas"].values()]
    return graus


@pytest.mark.parametrize("pessoa", [ANA, BRUNO], ids=["ana", "bruno"])
def test_nenhum_grau_do_mapa_chega_a_30(pessoa):
    mapa = calcular_mapa_natal(**pessoa)
    graus = _graus_do_mapa(mapa)
    assert graus
    for grau in graus:
        casado = re.fullmatch(r"(\d+)°(\d{2})'", grau)
        assert casado, grau
        assert int(casado.group(1)) < 30, grau
        assert int(casado.group(2)) < 60, grau


# ─────────────────────────────────────────────────────────────
# Trânsitos: o lado natal fica parado no cálculo de `aplicando`
# ─────────────────────────────────────────────────────────────
def test_transitos_coleta_natal_fixo_e_transito_movel(monkeypatch):
    original = transitos_mod.coletar_pontos
    chamadas = []

    def espiao(subject, *, fixo=False):
        chamadas.append((subject.name, fixo))
        return original(subject, fixo=fixo)

    monkeypatch.setattr(transitos_mod, "coletar_pontos", espiao)
    calcular_transitos(natal=ANA, data_transito="26/03/2026")
    assert sorted(chamadas) == sorted([("Transito", False), (ANA["nome"], True)])


def test_saturno_em_oposicao_a_lua_natal_aplica_so_pelo_movimento_de_saturno():
    """Em 26/03/2026 12:00 UTC Saturno (direto, ~4°52' de Áries, +0,125°/dia)
    se aproxima da oposição à Lua natal da Ana (~6°20' de Libra), orbe ~1,47°.

    Só Saturno se movendo: aplicando. Se a Lua natal andasse (~12°/dia), ela
    se afastaria da oposição e o aspecto sairia separando (o bug antigo).
    """
    resultado = calcular_transitos(natal=ANA, data_transito="26/03/2026")
    saturno_lua = [a for a in resultado["aspectos_transito_natal"]
                   if a["planeta_transito"] == "saturno" and a["planeta_natal"] == "lua"]
    assert len(saturno_lua) == 1
    aspecto = saturno_lua[0]
    assert aspecto["tipo"] == "oposicao"
    assert aspecto["orbe"] == pytest.approx(1.467, abs=0.01)
    assert aspecto["aplicando"] is True


# ─────────────────────────────────────────────────────────────
# Instante natal em UTC na transição do horário de verão (BH)
# ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize("data, hora, is_dst, esperado", [
    # Início do horário de verão: 00:00 vira 01:00, 00:30 não existe.
    ("21/10/1990", "00:30", True, "1990-10-21T02:30:00+00:00"),
    # Fim do horário de verão: 23:00–23:59 de 16/02/1991 acontece duas vezes.
    ("16/02/1991", "23:30", False, "1991-02-17T02:30:00+00:00"),
    ("16/02/1991", "23:30", True, "1991-02-17T01:30:00+00:00"),
], ids=["hora-pulada-com-verao", "hora-repetida-sem-verao", "hora-repetida-com-verao"])
def test_datetime_natal_utc_na_transicao_do_horario_de_verao(data, hora, is_dst, esperado):
    entrada = EntradaNascimento.de_campos(
        data=data, hora=hora,
        lat=BH["lat"], lng=BH["lng"], tz_str=BH["tz_str"], is_dst=is_dst,
    )
    assert _datetime_natal_utc(entrada).isoformat() == esperado
