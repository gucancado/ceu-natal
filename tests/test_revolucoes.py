"""
Testes das revoluções solar e lunar.

Importam Kerykeion, portanto só rodam em Linux (pyswisseph não compila no
Windows). O geocoder é monkeypatchado para não depender de rede.
"""
import pytest

from app.core import revolucoes as core_revolucoes
from app.tools.revolucao_lunar import calcular_revolucao_lunar
from app.tools.revolucao_solar import calcular_revolucao_solar
from tests.conftest import BH


GUSTAVO = {
    "data": "24/07/1989",
    "hora": "09:20",
    "local": "Belo Horizonte, MG",
    "nome": "Gustavo",
    "lat": BH["lat"],
    "lng": BH["lng"],
    "tz_str": BH["tz_str"],
}

LISBOA = {"lat": 38.7223, "lng": -9.1393, "tz_str": "Europe/Lisbon"}


@pytest.fixture
def geocode_fake(monkeypatch):
    """Resolve 'Lisboa, ...' para Lisboa e qualquer outro local para BH."""
    def _fake(cidade, nacao):
        if "lisboa" in cidade.lower():
            return dict(LISBOA)
        return dict(BH)

    monkeypatch.setattr(core_revolucoes, "geocode", _fake)
    return _fake


# ─────────────────────────────────────────────────────────────
# Validações de entrada
# ─────────────────────────────────────────────────────────────
class TestValidacoes:
    def test_sem_hora_natal_falha(self, geocode_fake):
        natal = {k: v for k, v in GUSTAVO.items() if k != "hora"}
        with pytest.raises(ValueError, match="hora de nascimento"):
            calcular_revolucao_solar(
                natal=natal, ano=2026, local_revolucao="Belo Horizonte, MG"
            )

    def test_sem_local_natal_falha(self, geocode_fake):
        natal = {"data": "24/07/1989", "hora": "09:20", "nome": "Gustavo"}
        with pytest.raises(ValueError, match="local de nascimento"):
            calcular_revolucao_solar(
                natal=natal, ano=2026, local_revolucao="Belo Horizonte, MG"
            )

    def test_local_revolucao_vazio_falha(self, geocode_fake):
        with pytest.raises(ValueError, match="local_revolucao"):
            calcular_revolucao_solar(natal=GUSTAVO, ano=2026, local_revolucao="  ")

    def test_ano_fora_da_faixa_falha(self, geocode_fake):
        with pytest.raises(ValueError, match="fora da faixa"):
            calcular_revolucao_solar(
                natal=GUSTAVO, ano=1500, local_revolucao="Belo Horizonte, MG"
            )

    def test_sistema_casas_invalido_falha(self, geocode_fake):
        with pytest.raises(ValueError, match="sistema_casas"):
            calcular_revolucao_solar(
                natal=GUSTAVO, ano=2026,
                local_revolucao="Belo Horizonte, MG", sistema_casas="Z",
            )

    def test_data_referencia_invalida_falha(self, geocode_fake):
        with pytest.raises(ValueError, match="Data inválida"):
            calcular_revolucao_lunar(
                natal=GUSTAVO, data_referencia="2026-07-24",
                local_revolucao="Belo Horizonte, MG",
            )


# ─────────────────────────────────────────────────────────────
# Revolução solar
# ─────────────────────────────────────────────────────────────
class TestRevolucaoSolar:
    @pytest.fixture
    def rs(self, geocode_fake):
        return calcular_revolucao_solar(
            natal=GUSTAVO, ano=2026, local_revolucao="Belo Horizonte, MG"
        )

    def test_instante_cai_perto_do_aniversario(self, rs):
        # O retorno solar nunca se afasta mais de ~1 dia da data de nascimento.
        instante = rs["revolucao"]["instante_utc"]
        assert instante.startswith("2026-07-2")
        dia = int(instante[8:10])
        assert 23 <= dia <= 25

    def test_sol_da_revolucao_bate_com_o_sol_natal(self, rs, geocode_fake):
        from app.core.kerykeion import criar_subject

        natal = criar_subject(
            nome="Gustavo", ano=1989, mes=7, dia=24, hora=9, minuto=20,
            cidade="Belo Horizonte", nacao="MG",
            lat=BH["lat"], lng=BH["lng"], tz_str=BH["tz_str"],
        )
        # É a definição da técnica: mesma longitude, com folga de segundos de arco.
        assert abs(rs["planetas"]["sol"]["posicao_absoluta"] - natal.sun.abs_pos) < 0.01

    def test_estrutura_do_payload(self, rs):
        for chave in (
            "natal", "revolucao", "metodo", "planetas", "casas", "angulos",
            "pontos_sensiveis", "aspectos_internos", "aspectos_revolucao_natal",
            "sobreposicao", "sintese", "destaques", "ano",
        ):
            assert chave in rs, f"chave ausente: {chave}"

    def test_metodo_declara_ausencia_de_precessao(self, rs):
        assert rs["metodo"]["precessao"] == "nao_aplicada"
        assert rs["metodo"]["tecnica"] == "revolucao_solar"

    def test_vigencia_cobre_cerca_de_um_ano(self, rs):
        from datetime import datetime

        v = rs["revolucao"]["vigencia"]
        dias = (
            datetime.fromisoformat(v["fim_aproximado"])
            - datetime.fromisoformat(v["inicio"])
        ).days
        assert 364 <= dias <= 366

    def test_destaques_trazem_ascendente_e_regentes(self, rs):
        asc = rs["destaques"]["ascendente_revolucao"]
        assert asc["signo"]
        assert asc["regente_moderno"]
        assert asc["regente_tradicional"]
        assert 1 <= asc["casa_natal_onde_cai"] <= 12

    def test_sol_na_casa_e_valido(self, rs):
        assert 1 <= rs["destaques"]["sol_na_casa"] <= 12

    def test_sobreposicao_cobre_os_dois_sentidos(self, rs):
        s = rs["sobreposicao"]
        assert s["planetas_revolucao_em_casas_natais"]["sol"] in range(1, 13)
        assert s["planetas_natais_em_casas_revolucao"]["sol"] in range(1, 13)

    def test_aspectos_cruzados_usam_nomes_de_revolucao(self, rs):
        if rs["aspectos_revolucao_natal"]:
            a = rs["aspectos_revolucao_natal"][0]
            assert "planeta_revolucao" in a
            assert "planeta_natal" in a


class TestLocalMudaSoOsAngulos:
    """
    A garantia astrológica central: trocar o local da revolução não pode mexer
    em nenhuma longitude planetária, só nos ângulos e casas.
    """

    @pytest.fixture
    def par(self, geocode_fake):
        bh = calcular_revolucao_solar(
            natal=GUSTAVO, ano=2026, local_revolucao="Belo Horizonte, MG"
        )
        lisboa = calcular_revolucao_solar(
            natal=GUSTAVO, ano=2026, local_revolucao="Lisboa, Portugal"
        )
        return bh, lisboa

    def test_mesmo_instante(self, par):
        bh, lisboa = par
        assert bh["revolucao"]["instante_utc"] == lisboa["revolucao"]["instante_utc"]

    def test_longitudes_identicas(self, par):
        bh, lisboa = par
        for nome, dados in bh["planetas"].items():
            assert dados["posicao_absoluta"] == pytest.approx(
                lisboa["planetas"][nome]["posicao_absoluta"]
            ), f"longitude de {nome} mudou com o local"

    def test_ascendente_diferente(self, par):
        bh, lisboa = par
        assert (
            bh["angulos"]["ascendente"]["posicao_absoluta"]
            != lisboa["angulos"]["ascendente"]["posicao_absoluta"]
        )


# ─────────────────────────────────────────────────────────────
# Revolução lunar
# ─────────────────────────────────────────────────────────────
class TestRevolucaoLunar:
    @pytest.fixture
    def rl(self, geocode_fake):
        return calcular_revolucao_lunar(
            natal=GUSTAVO, data_referencia="01/07/2026",
            local_revolucao="Belo Horizonte, MG",
        )

    def test_retorno_ocorre_dentro_de_um_mes_sideral(self, rl):
        from datetime import datetime

        instante = datetime.fromisoformat(rl["revolucao"]["instante_utc"].replace("Z", "+00:00"))
        referencia = datetime(2026, 7, 1, tzinfo=instante.tzinfo)
        dias = (instante - referencia).total_seconds() / 86400.0
        assert 0 <= dias <= 28

    def test_lua_da_revolucao_bate_com_a_lua_natal(self, rl):
        from app.core.kerykeion import criar_subject

        natal = criar_subject(
            nome="Gustavo", ano=1989, mes=7, dia=24, hora=9, minuto=20,
            cidade="Belo Horizonte", nacao="MG",
            lat=BH["lat"], lng=BH["lng"], tz_str=BH["tz_str"],
        )
        assert abs(rl["planetas"]["lua"]["posicao_absoluta"] - natal.moon.abs_pos) < 0.05

    def test_vigencia_cobre_cerca_de_um_mes(self, rl):
        from datetime import datetime

        v = rl["revolucao"]["vigencia"]
        dias = (
            datetime.fromisoformat(v["fim_aproximado"])
            - datetime.fromisoformat(v["inicio"])
        ).days
        assert dias == 27

    def test_destaques_centrados_na_lua(self, rl):
        assert 1 <= rl["destaques"]["lua_na_casa"] <= 12
        assert rl["destaques"]["lua_revolucao"]["signo"]
        assert rl["destaques"]["sol_revolucao"]["signo"]

    def test_metodo_declara_a_tecnica(self, rl):
        assert rl["metodo"]["tecnica"] == "revolucao_lunar"
        assert "mooncross_ut" in rl["metodo"]["fonte"]
