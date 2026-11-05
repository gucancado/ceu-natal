import pytest

from app.core.validators import (
    SISTEMAS_CASAS_VALIDOS,
    parse_data,
    parse_hora,
    parse_local,
    validar_sistema_casas,
)


# ─────────────────────────────────────────────────────────────
# parse_local
# ─────────────────────────────────────────────────────────────
class TestParseLocal:
    def test_cidade_uf_brasileira(self):
        assert parse_local("Belo Horizonte, MG") == ("Belo Horizonte", "MG")

    def test_cidade_com_espaco_e_acento(self):
        assert parse_local("Poços de Caldas, MG") == ("Poços de Caldas", "MG")

    def test_cidade_com_virgula_no_nome(self):
        """rsplit pega só a última vírgula — preserva 'D.C.' no nome da cidade."""
        assert parse_local("Washington, D.C., USA") == ("Washington, D.C.", "USA")

    def test_cidade_sem_uf(self):
        assert parse_local("São Paulo") == ("São Paulo", "")

    def test_whitespace_em_ambos_lados(self):
        assert parse_local("  Belo Horizonte ,  MG  ") == ("Belo Horizonte", "MG")

    def test_string_vazia_levanta_erro(self):
        with pytest.raises(ValueError):
            parse_local("")

    def test_string_so_espacos_levanta_erro(self):
        with pytest.raises(ValueError):
            parse_local("   ")

    def test_none_retorna_tupla_neutra(self):
        assert parse_local(None) == (None, "")

    def test_so_virgula_levanta_erro(self):
        with pytest.raises(ValueError):
            parse_local(",")

    def test_pais_por_extenso(self):
        assert parse_local("Lisboa, Portugal") == ("Lisboa", "Portugal")


# ─────────────────────────────────────────────────────────────
# parse_data
# ─────────────────────────────────────────────────────────────
class TestParseData:
    def test_data_valida(self):
        assert parse_data("12/03/1990") == (12, 3, 1990)

    def test_data_com_espacos(self):
        assert parse_data("  25/07/1992  ") == (25, 7, 1992)

    def test_data_invalida_levanta_erro(self):
        with pytest.raises(ValueError):
            parse_data("32/13/2000")

    def test_formato_errado(self):
        with pytest.raises(ValueError):
            parse_data("1990-03-12")

    def test_ano_abaixo_da_faixa_levanta_erro(self):
        with pytest.raises(ValueError, match=r"Ano 999 fora da faixa suportada \(1000 a 3000\)\."):
            parse_data("01/01/0999")

    def test_ano_acima_da_faixa_levanta_erro(self):
        with pytest.raises(ValueError, match="fora da faixa suportada"):
            parse_data("01/01/3001")

    def test_limites_da_faixa_aceitos(self):
        assert parse_data("01/01/1000") == (1, 1, 1000)
        assert parse_data("31/12/3000") == (31, 12, 3000)


# ─────────────────────────────────────────────────────────────
# parse_hora
# ─────────────────────────────────────────────────────────────
class TestParseHora:
    def test_hora_valida(self):
        assert parse_hora("09:20") == (9, 20)

    def test_hora_none(self):
        assert parse_hora(None) == (None, None)

    def test_hora_vazia(self):
        assert parse_hora("") == (None, None)

    def test_hora_invalida(self):
        with pytest.raises(ValueError):
            parse_hora("25:00")


# ─────────────────────────────────────────────────────────────
# validar_sistema_casas
# ─────────────────────────────────────────────────────────────
class TestValidarSistemaCasas:
    def test_none_retorna_placidus(self):
        assert validar_sistema_casas(None) == "P"

    def test_identificador_valido_minusculo(self):
        assert validar_sistema_casas("w") == "W"

    def test_identificador_valido_maiusculo(self):
        assert validar_sistema_casas("K") == "K"

    def test_todos_os_validos_passam(self):
        for ident in SISTEMAS_CASAS_VALIDOS:
            assert validar_sistema_casas(ident) == ident

    def test_invalido_levanta_value_error(self):
        with pytest.raises(ValueError, match="sistema_casas"):
            validar_sistema_casas("Z")

    def test_mensagem_lista_opcoes_validas(self):
        with pytest.raises(ValueError) as exc_info:
            validar_sistema_casas("XYZ")
        msg = str(exc_info.value)
        for ident in SISTEMAS_CASAS_VALIDOS:
            assert ident in msg

    def test_tipo_errado_levanta_value_error(self):
        with pytest.raises(ValueError):
            validar_sistema_casas(123)  # type: ignore[arg-type]

    def test_strip_whitespace(self):
        assert validar_sistema_casas("  P  ") == "P"
