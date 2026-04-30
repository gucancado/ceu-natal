"""
Testes do cálculo de aspectos. Usa pontos sintéticos com abs_pos conhecidos
para isolar a lógica do módulo (sem depender de Kerykeion).
"""
import pytest

from app.core.aspectos import (
    ASPECTOS_DEF,
    calcular_aspectos,
    calcular_aspectos_sinastria,
    casa_de_longitude,
    listar_tipos_aspectos,
    orbe_para,
)


def _ponto(nome: str, abs_pos: float, speed: float = 1.0) -> dict:
    return {"nome": nome, "abs_pos": abs_pos, "speed": speed}


# ─────────────────────────────────────────────────────────────
# listar_tipos_aspectos / ASPECTOS_DEF
# ─────────────────────────────────────────────────────────────
def test_listar_tipos_retorna_oito_aspectos():
    tipos = listar_tipos_aspectos()
    assert len(tipos) == 8
    nomes = {t["tipo"] for t in tipos}
    assert nomes == {
        "conjuncao", "oposicao", "trigono", "quadratura",
        "sextil", "quintil", "inconjuncao", "semi_sextil",
    }


def test_listar_tipos_traz_natureza():
    naturezas = {t["tipo"]: t["natureza"] for t in listar_tipos_aspectos()}
    assert naturezas["conjuncao"] == "neutro"
    assert naturezas["oposicao"] == "tensao"
    assert naturezas["trigono"] == "harmonico"
    assert naturezas["quadratura"] == "tensao"
    assert naturezas["sextil"] == "harmonico"


def test_aspectos_def_angulos_corretos():
    angulos = {tipo: ang for tipo, ang, _ in ASPECTOS_DEF}
    assert angulos["conjuncao"] == 0.0
    assert angulos["oposicao"] == 180.0
    assert angulos["trigono"] == 120.0
    assert angulos["quadratura"] == 90.0
    assert angulos["sextil"] == 60.0


# ─────────────────────────────────────────────────────────────
# orbe_para
# ─────────────────────────────────────────────────────────────
class TestOrbe:
    def test_conjuncao_com_luminar_8_graus(self):
        assert orbe_para("conjuncao", "sol", "marte") == 8.0

    def test_conjuncao_sem_luminar_6_graus(self):
        assert orbe_para("conjuncao", "marte", "venus") == 6.0

    def test_oposicao_com_luminar(self):
        assert orbe_para("oposicao", "lua", "saturno") == 8.0

    def test_quadratura_sempre_6(self):
        assert orbe_para("quadratura", "sol", "marte") == 6.0
        assert orbe_para("quadratura", "marte", "venus") == 6.0

    def test_trigono_sextil_4_graus(self):
        assert orbe_para("trigono", "sol", "marte") == 4.0
        assert orbe_para("sextil", "marte", "venus") == 4.0

    def test_aspectos_menores_2_graus(self):
        assert orbe_para("quintil", "sol", "marte") == 2.0
        assert orbe_para("inconjuncao", "marte", "venus") == 2.0
        assert orbe_para("semi_sextil", "sol", "lua") == 2.0


# ─────────────────────────────────────────────────────────────
# calcular_aspectos: pares sintéticos
# ─────────────────────────────────────────────────────────────
class TestCalcularAspectos:
    def test_conjuncao_exata(self):
        pontos = [_ponto("a", 100.0), _ponto("b", 100.0)]
        aspectos = calcular_aspectos(pontos)
        assert len(aspectos) == 1
        assert aspectos[0]["tipo"] == "conjuncao"
        assert aspectos[0]["orbe"] == 0.0
        assert aspectos[0]["exato"] is True

    def test_trigono_exato_120(self):
        pontos = [_ponto("a", 0.0), _ponto("b", 120.0)]
        aspectos = calcular_aspectos(pontos)
        assert len(aspectos) == 1
        assert aspectos[0]["tipo"] == "trigono"
        assert aspectos[0]["orbe"] == 0.0

    def test_quadratura_exata_90(self):
        pontos = [_ponto("a", 0.0), _ponto("b", 90.0)]
        aspectos = calcular_aspectos(pontos)
        assert len(aspectos) == 1
        assert aspectos[0]["tipo"] == "quadratura"

    def test_quadratura_92_dentro_orbe(self):
        """92° é quadratura: |92-90|=2, dentro do orbe de 6°."""
        pontos = [_ponto("a", 0.0), _ponto("b", 92.0)]
        aspectos = calcular_aspectos(pontos)
        assert len(aspectos) == 1
        assert aspectos[0]["tipo"] == "quadratura"
        assert aspectos[0]["orbe"] == pytest.approx(2.0)
        assert aspectos[0]["exato"] is False

    def test_100_graus_sem_aspecto(self):
        """100° está a 10° de quadratura (>6) e a 20° de trígono (>4) — nada."""
        pontos = [_ponto("a", 0.0), _ponto("b", 100.0)]
        aspectos = calcular_aspectos(pontos)
        assert aspectos == []

    def test_oposicao_180(self):
        pontos = [_ponto("a", 0.0), _ponto("b", 180.0)]
        aspectos = calcular_aspectos(pontos)
        assert len(aspectos) == 1
        assert aspectos[0]["tipo"] == "oposicao"

    def test_sextil_60(self):
        pontos = [_ponto("a", 0.0), _ponto("b", 60.0)]
        aspectos = calcular_aspectos(pontos)
        assert len(aspectos) == 1
        assert aspectos[0]["tipo"] == "sextil"

    def test_exato_quando_orbe_menor_que_meio_grau(self):
        pontos = [_ponto("a", 0.0), _ponto("b", 0.4)]
        aspectos = calcular_aspectos(pontos)
        assert aspectos[0]["exato"] is True
        pontos2 = [_ponto("a", 0.0), _ponto("b", 0.6)]
        assert calcular_aspectos(pontos2)[0]["exato"] is False

    def test_aplicando_quando_planetas_se_aproximam(self):
        # a parado em 0, b em 119° avançando para 120° → aplicando=True
        pontos = [_ponto("a", 0.0, speed=0.0), _ponto("b", 119.0, speed=1.0)]
        aspectos = calcular_aspectos(pontos)
        assert aspectos[0]["tipo"] == "trigono"
        assert aspectos[0]["aplicando"] is True

    def test_separando_quando_planetas_se_afastam(self):
        # a parado, b em 121° já passou de 120° e segue em frente → separando
        pontos = [_ponto("a", 0.0, speed=0.0), _ponto("b", 121.0, speed=1.0)]
        aspectos = calcular_aspectos(pontos)
        assert aspectos[0]["tipo"] == "trigono"
        assert aspectos[0]["aplicando"] is False

    def test_aplicando_none_quando_speed_ausente(self):
        pontos = [_ponto("a", 0.0, speed=None), _ponto("b", 120.0, speed=1.0)]
        aspectos = calcular_aspectos(pontos)
        assert aspectos[0]["aplicando"] is None

    def test_resultado_ordenado_por_orbe_crescente(self):
        pontos = [
            _ponto("a", 0.0),
            _ponto("b", 91.0),    # quadratura, orbe 1
            _ponto("c", 119.5),   # trigono, orbe 0.5
        ]
        aspectos = calcular_aspectos(pontos)
        orbes = [a["orbe"] for a in aspectos]
        assert orbes == sorted(orbes)


# ─────────────────────────────────────────────────────────────
# calcular_aspectos_sinastria
# ─────────────────────────────────────────────────────────────
def test_sinastria_marca_pessoas_corretas():
    pontos_a = [_ponto("sol", 0.0)]
    pontos_b = [_ponto("lua", 90.0)]
    aspectos = calcular_aspectos_sinastria(pontos_a, pontos_b, "Gustavo", "Naiara")
    assert len(aspectos) == 1
    a = aspectos[0]
    assert a["pessoa_a"] == "Gustavo"
    assert a["pessoa_b"] == "Naiara"
    assert a["tipo"] == "quadratura"
    assert a["natureza"] == "tensao"


# ─────────────────────────────────────────────────────────────
# casa_de_longitude
# ─────────────────────────────────────────────────────────────
class TestCasaDeLongitude:
    def test_casa_simples_iguais_30(self):
        cuspides = [i * 30.0 for i in range(12)]  # 0, 30, 60, ..., 330
        assert casa_de_longitude(15.0, cuspides) == 1
        assert casa_de_longitude(45.0, cuspides) == 2
        assert casa_de_longitude(330.5, cuspides) == 12

    def test_cruza_zero_grau(self):
        # Cuspide 1 em 350°, cuspide 2 em 20° — 5° está na casa 1
        cuspides = [350.0, 20.0, 50.0, 80.0, 110.0, 140.0,
                    170.0, 200.0, 230.0, 260.0, 290.0, 320.0]
        assert casa_de_longitude(5.0, cuspides) == 1
        assert casa_de_longitude(355.0, cuspides) == 1
        assert casa_de_longitude(25.0, cuspides) == 2
