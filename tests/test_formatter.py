"""Formatação de graus (sem Kerykeion)."""
from app.core.formatter import formatar_grau


def test_formatar_grau_trunca_e_nunca_vira_30_graus():
    assert formatar_grau(29.9917) == "29°59'"


def test_formatar_grau_zero():
    assert formatar_grau(0.0) == "0°00'"


def test_formatar_grau_meio_grau():
    assert formatar_grau(15.5) == "15°30'"
