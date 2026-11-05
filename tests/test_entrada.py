"""
Entrada de nascimento única (`EntradaNascimento`), comum a todas as tools.

A parte de parsing e validação não importa Kerykeion e roda no Windows; os
testes que criam subject ou resolvem coordenadas pulam sem Kerykeion.
"""
import pytest

from app.core.entrada import EntradaNascimento
from tests.conftest import ANA, BH


# ─────────────────────────────────────────────────────────────
# de_dict / de_campos
# ─────────────────────────────────────────────────────────────
def test_de_dict_sem_hora():
    entrada = EntradaNascimento.de_dict({"data": "12/03/1990"})
    assert entrada.tem_hora is False
    assert entrada.hora is None and entrada.minuto is None
    assert (entrada.dia, entrada.mes, entrada.ano) == (12, 3, 1990)


def test_de_dict_sem_data_nomeia_o_rotulo():
    with pytest.raises(ValueError, match="natal") as exc:
        EntradaNascimento.de_dict({}, rotulo="natal")
    assert str(exc.value) == "Campo 'data' obrigatório em natal."


def test_de_dict_rotulo_padrao():
    with pytest.raises(ValueError, match=r"^Campo 'data' obrigatório em pessoa\.$"):
        EntradaNascimento.de_dict({"hora": "10:00"})


def test_de_dict_completo():
    entrada = EntradaNascimento.de_dict(ANA, rotulo="pessoa_a")
    assert entrada.nome == "Ana"
    assert (entrada.hora, entrada.minuto) == (14, 30)
    assert (entrada.cidade, entrada.nacao) == ("Belo Horizonte", "MG")
    assert (entrada.lat, entrada.lng, entrada.tz_str) == (BH["lat"], BH["lng"], BH["tz_str"])
    assert entrada.is_dst is None
    assert entrada.tem_hora and entrada.tem_local


def test_nome_ausente_vira_anonimo():
    assert EntradaNascimento.de_dict({"data": "12/03/1990", "nome": None}).nome == "Anônimo"


def test_is_dst_lido_do_dict():
    assert EntradaNascimento.de_dict({"data": "16/02/2019", "is_dst": False}).is_dst is False


def test_tem_local_por_cidade_ou_por_lat_lng():
    assert EntradaNascimento.de_dict({"data": "12/03/1990", "local": "Recife, PE"}).tem_local
    assert EntradaNascimento.de_dict({"data": "12/03/1990", "lat": 1.0, "lng": 2.0}).tem_local
    assert not EntradaNascimento.de_dict({"data": "12/03/1990", "lat": 1.0}).tem_local
    assert not EntradaNascimento.de_dict({"data": "12/03/1990"}).tem_local


def test_erros_de_formato_vem_dos_validators():
    with pytest.raises(ValueError, match="Data inválida"):
        EntradaNascimento.de_dict({"data": "1990-03-12"})
    with pytest.raises(ValueError, match="Hora inválida"):
        EntradaNascimento.de_dict({"data": "12/03/1990", "hora": "25h"})


def test_de_campos_equivale_a_de_dict():
    campos = EntradaNascimento.de_campos(
        data=ANA["data"], hora=ANA["hora"], local=ANA["local"], nome=ANA["nome"],
        lat=BH["lat"], lng=BH["lng"], tz_str=BH["tz_str"],
    )
    assert campos == EntradaNascimento.de_dict(ANA)


# ─────────────────────────────────────────────────────────────
# Exigências por técnica
# ─────────────────────────────────────────────────────────────
def test_exigir_hora_e_local_sem_hora_levanta():
    entrada = EntradaNascimento.de_dict({"data": "12/03/1990", "local": "Recife, PE"})
    with pytest.raises(ValueError, match=r"^Trânsitos exigem hora e local de nascimento"):
        entrada.exigir_hora_e_local("Trânsitos")


def test_exigir_hora_e_local_sem_local_levanta():
    entrada = EntradaNascimento.de_dict({"data": "12/03/1990", "hora": "10:00"})
    with pytest.raises(ValueError, match=r"^Progressões exigem hora e local"):
        entrada.exigir_hora_e_local("Progressões")


def test_exigir_hora_e_local_completo_passa():
    EntradaNascimento.de_dict(ANA).exigir_hora_e_local("Trânsitos")


# ─────────────────────────────────────────────────────────────
# Coordenadas e subject (Kerykeion)
# ─────────────────────────────────────────────────────────────
def test_resolvida_sem_local_nao_inventa_coordenadas():
    pytest.importorskip("kerykeion")
    entrada = EntradaNascimento.de_dict({"data": "12/03/1990"})
    assert entrada.resolvida() is entrada
    assert entrada.resolvida().tem_local is False


def test_resolvida_geocodifica_uma_vez(monkeypatch):
    pytest.importorskip("kerykeion")
    from app.core import kerykeion as ky

    chamadas = []

    def fake(cidade, nacao):
        chamadas.append((cidade, nacao))
        return dict(BH)

    monkeypatch.setattr(ky, "geocode", fake)
    entrada = EntradaNascimento.de_dict({"data": "12/03/1990", "hora": "14:30", "local": "Belo Horizonte, MG"})
    resolvida = entrada.resolvida()
    assert (resolvida.lat, resolvida.lng, resolvida.tz_str) == (BH["lat"], BH["lng"], BH["tz_str"])
    resolvida.subject("P")
    assert chamadas == [("Belo Horizonte", "MG")]


def test_exigir_casas_recusa_latitude_polar():
    pytest.importorskip("kerykeion")
    polar = EntradaNascimento.de_dict(
        {"data": "01/06/1990", "hora": "12:00", "lat": 69.65, "lng": 18.96, "tz_str": "Europe/Oslo"},
    )
    with pytest.raises(ValueError, match="66°"):
        polar.exigir_casas()


def test_subject_sem_hora_usa_meio_dia():
    pytest.importorskip("kerykeion")
    subject = EntradaNascimento.de_dict({"data": "12/03/1990", **BH}).subject("P")
    assert (subject.hour, subject.minute) == (12, 0)
