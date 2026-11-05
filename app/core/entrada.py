"""
Entrada de nascimento única: o objeto pessoa/natal que todas as tools recebem
(`data`, `hora`, `local`, `nome`, `lat`, `lng`, `tz_str`, `is_dst`), validado
uma vez e convertido em AstrologicalSubject num lugar só.

Fluxo das técnicas que dependem das casas natais (trânsitos, progressões,
revoluções):

    entrada = EntradaNascimento.de_dict(natal, rotulo="natal")
    entrada.exigir_hora_e_local("Trânsitos")   # só hora/local, sem rede
    entrada = entrada.exigir_casas()           # geocodifica e recusa |lat| > 66°
    subject = entrada.subject(sistema_id)

A checagem de latitude fica em `exigir_casas()`, separada de
`exigir_hora_e_local()`: a primeira precisa resolver coordenadas (pode ir à
rede), a segunda é validação pura e roda antes de qualquer custo.

Este módulo não importa Kerykeion no carregamento (parsing e validação rodam sem
pyswisseph); `resolvida()`, `exigir_casas()` e `subject()` importam sob demanda.
"""
from dataclasses import dataclass, replace
from typing import Optional

from app.core.validators import parse_data, parse_hora, parse_local

NOME_PADRAO = "Anônimo"


@dataclass(frozen=True)
class EntradaNascimento:
    nome: str
    dia: int
    mes: int
    ano: int
    hora: Optional[int]
    minuto: Optional[int]
    cidade: Optional[str]
    nacao: str
    lat: Optional[float]
    lng: Optional[float]
    tz_str: Optional[str]
    is_dst: Optional[bool]

    @property
    def tem_hora(self) -> bool:
        return self.hora is not None

    def hora_ou_meio_dia(self) -> tuple[int, int]:
        """(hora, minuto) informados; sem hora, 12:00."""
        if self.hora is None or self.minuto is None:
            return 12, 0
        return self.hora, self.minuto

    @property
    def tem_local(self) -> bool:
        """Local por nome de cidade ou por coordenadas explícitas (lat e lng)."""
        return self.cidade is not None or (self.lat is not None and self.lng is not None)

    @classmethod
    def de_dict(cls, pessoa: dict, *, rotulo: str = "pessoa") -> "EntradaNascimento":
        """Objeto pessoa/natal das tools. `rotulo` nomeia o objeto no erro de data ausente."""
        if not pessoa.get("data"):
            raise ValueError(f"Campo 'data' obrigatório em {rotulo}.")
        return cls.de_campos(
            data=pessoa["data"],
            hora=pessoa.get("hora"),
            local=pessoa.get("local"),
            nome=pessoa.get("nome"),
            lat=pessoa.get("lat"),
            lng=pessoa.get("lng"),
            tz_str=pessoa.get("tz_str"),
            is_dst=pessoa.get("is_dst"),
        )

    @classmethod
    def de_campos(
        cls,
        *,
        data: str,
        hora: Optional[str] = None,
        local: Optional[str] = None,
        nome: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        tz_str: Optional[str] = None,
        is_dst: Optional[bool] = None,
    ) -> "EntradaNascimento":
        dia, mes, ano = parse_data(data)
        h, m = parse_hora(hora)
        cidade, nacao = parse_local(local)
        return cls(
            nome=nome or NOME_PADRAO,
            dia=dia, mes=mes, ano=ano,
            hora=h, minuto=m,
            cidade=cidade, nacao=nacao,
            lat=lat, lng=lng, tz_str=tz_str,
            is_dst=is_dst,
        )

    def exigir_hora_e_local(self, tecnica: str) -> None:
        """Técnicas que sobrepõem algo às casas natais recusam entrada incompleta."""
        if not (self.tem_hora and self.tem_local):
            raise ValueError(
                f"{tecnica} exigem hora e local de nascimento — sem isso, casas "
                "natais não podem ser calculadas."
            )

    def resolvida(self) -> "EntradaNascimento":
        """Cópia com (lat, lng, tz_str) resolvidos — geocodifica uma vez só.

        Sem local devolve a própria entrada: o subject cai em (0, 0, UTC) e
        `tem_local` continua False.
        """
        if not self.tem_local:
            return self
        from app.core.kerykeion import resolver_coordenadas

        lat, lng, tz_str = resolver_coordenadas(
            self.cidade, self.nacao, self.lat, self.lng, self.tz_str,
        )
        return replace(self, lat=lat, lng=lng, tz_str=tz_str)

    def exigir_casas(self) -> "EntradaNascimento":
        """Entrada resolvida, recusando latitude em que as casas saem erradas.

        Chamar depois de `exigir_hora_e_local`. A latitude é checada antes do
        subject: o Kerykeion corta |lat| > 66° e sobrescreve `subject.lat`.
        """
        from app.core.kerykeion import exigir_latitude_com_casas

        resolvida = self.resolvida()
        # Resolvida com local sempre tem `lat`; o segundo teste só estreita o tipo.
        if resolvida.tem_local and resolvida.lat is not None:
            exigir_latitude_com_casas(resolvida.lat)
        return resolvida

    def subject(self, sistema_id: str):
        """AstrologicalSubject da entrada; sem hora, calcula para as 12:00."""
        from app.core.kerykeion import criar_subject

        hora, minuto = self.hora_ou_meio_dia()
        return criar_subject(
            nome=self.nome,
            ano=self.ano, mes=self.mes, dia=self.dia,
            hora=hora, minuto=minuto,
            cidade=self.cidade, nacao=self.nacao,
            lat=self.lat, lng=self.lng, tz_str=self.tz_str,
            sistema_casas=sistema_id,
            is_dst=self.is_dst,
        )
