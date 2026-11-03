"""Limitador de taxa em memória para as chamadas de ferramentas MCP.

A chave de limitação é o id da sessão MCP, nunca o IP de origem. O claude.ai e
o ChatGPT chegam ao servidor a partir de IPs de saída compartilhados da
Anthropic e da OpenAI; um limite por IP bloquearia todos os usuários do
diretório de uma só vez. Cada sessão tem o seu próprio balde de tokens, e um
balde global funciona como teto de segurança para o servidor inteiro.

Sem threads nem locks: o limitador é chamado só do event loop (o cálculo é que
vai para o threadpool), então é tocado por uma única thread.
"""

import time
from collections import OrderedDict
from collections.abc import Callable


class BaldeTokens:
    """Balde de tokens: `capacidade` tokens, reabastecido a `recarga_por_min`."""

    def __init__(self, capacidade: int, recarga_por_min: float) -> None:
        self.capacidade = float(capacidade)
        self._por_segundo = recarga_por_min / 60.0
        self._tokens = float(capacidade)
        self._ultimo: float | None = None

    def _recarregar(self, agora: float) -> None:
        if self._ultimo is not None and agora > self._ultimo:
            self._tokens = min(
                self.capacidade, self._tokens + (agora - self._ultimo) * self._por_segundo
            )
        self._ultimo = agora

    def verificar(self, agora: float) -> tuple[bool, float]:
        """Como `tentar`, mas sem consumir o token."""
        self._recarregar(agora)
        if self._tokens >= 1.0:
            return True, 0.0
        return False, (1.0 - self._tokens) / self._por_segundo

    def tentar(self, agora: float) -> tuple[bool, float]:
        """Consome um token se houver. Retorna (permitido, segundos até o próximo)."""
        permitido, espera = self.verificar(agora)
        if permitido:
            self._tokens -= 1.0
        return permitido, espera


class LimitadorTaxa:
    """Limite por sessão MCP mais teto global. Taxa 0 desliga a camada."""

    def __init__(
        self,
        por_sessao_por_min: int,
        global_por_min: int,
        max_sessoes: int = 10_000,
        relogio: Callable[[], float] = time.monotonic,
    ) -> None:
        self._por_sessao = por_sessao_por_min
        self._max_sessoes = max_sessoes
        self._relogio = relogio
        self._sessoes: OrderedDict[str, BaldeTokens] = OrderedDict()
        self._global = (
            BaldeTokens(global_por_min, global_por_min) if global_por_min > 0 else None
        )

    @property
    def sessoes_ativas(self) -> int:
        return len(self._sessoes)

    def _balde_da_sessao(self, chave: str) -> BaldeTokens:
        balde = self._sessoes.get(chave)
        if balde is None:
            balde = BaldeTokens(self._por_sessao, self._por_sessao)
            self._sessoes[chave] = balde
            while len(self._sessoes) > self._max_sessoes:
                self._sessoes.popitem(last=False)  # descarta a mais antiga
        else:
            self._sessoes.move_to_end(chave)
        return balde

    def tentar(self, chave: str | None) -> tuple[bool, float]:
        """Retorna (permitido, segundos até o próximo token).

        Duas fases: verifica sessão e global sem consumir e só então consome nos
        dois, para que um bloqueio na sessão não gaste token global.
        """
        agora = self._relogio()
        baldes: list[BaldeTokens] = []
        if chave is not None and self._por_sessao > 0:
            baldes.append(self._balde_da_sessao(chave))
        if self._global is not None:
            baldes.append(self._global)
        for balde in baldes:
            permitido, espera = balde.verificar(agora)
            if not permitido:
                return False, espera
        for balde in baldes:
            balde.tentar(agora)
        return True, 0.0
