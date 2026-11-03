from app.core.ratelimit import BaldeTokens, LimitadorTaxa


class Relogio:
    def __init__(self, t: float = 0.0):
        self.t = t

    def __call__(self) -> float:
        return self.t


def test_balde_permite_ate_capacidade_e_bloqueia_a_seguinte():
    b = BaldeTokens(capacidade=3, recarga_por_min=3)
    assert [b.tentar(0.0)[0] for _ in range(3)] == [True, True, True]
    permitido, espera = b.tentar(0.0)
    assert permitido is False and 0 < espera <= 20.0


def test_balde_recarrega_com_o_tempo():
    b = BaldeTokens(capacidade=3, recarga_por_min=3)
    for _ in range(3):
        b.tentar(0.0)
    assert b.tentar(20.0)[0] is True   # 20 s a 3/min = 1 token
    assert b.tentar(20.0)[0] is False


def test_sessao_bloqueia_so_a_propria_chave():
    rel = Relogio()
    lim = LimitadorTaxa(por_sessao_por_min=2, global_por_min=0, relogio=rel)
    assert lim.tentar("a")[0] and lim.tentar("a")[0]
    assert lim.tentar("a")[0] is False
    assert lim.tentar("b")[0] is True


def test_global_bloqueia_mesmo_com_sessoes_diferentes():
    lim = LimitadorTaxa(por_sessao_por_min=0, global_por_min=2, relogio=Relogio())
    assert lim.tentar("a")[0] and lim.tentar("b")[0]
    assert lim.tentar("c")[0] is False


def test_chave_none_conta_so_no_global():
    lim = LimitadorTaxa(por_sessao_por_min=1, global_por_min=3, relogio=Relogio())
    assert [lim.tentar(None)[0] for _ in range(3)] == [True, True, True]
    assert lim.tentar(None)[0] is False
    assert lim.sessoes_ativas == 0


def test_zero_nas_duas_camadas_desliga():
    lim = LimitadorTaxa(por_sessao_por_min=0, global_por_min=0, relogio=Relogio())
    assert all(lim.tentar("x")[0] for _ in range(1000))


def test_bloqueio_na_sessao_nao_consome_token_global():
    lim = LimitadorTaxa(por_sessao_por_min=1, global_por_min=2, relogio=Relogio())
    assert lim.tentar("a")[0] is True
    assert lim.tentar("a")[0] is False   # barrado na sessão
    assert lim.tentar("b")[0] is True    # global ainda tinha 1


def test_evicao_mantem_no_maximo_max_sessoes():
    lim = LimitadorTaxa(por_sessao_por_min=5, global_por_min=0, max_sessoes=2, relogio=Relogio())
    for chave in ("a", "b", "c"):
        lim.tentar(chave)
    assert lim.sessoes_ativas == 2
    assert lim.tentar("a")[0] is True    # "a" foi descartada e volta com balde cheio
