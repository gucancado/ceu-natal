# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Configuração do servidor: um objeto imutável no lugar de `os.getenv` espalhado
pelo import de `app.server`.

`Settings.do_ambiente()` lê as variáveis de ambiente (nomes em maiúsculas,
mesmos defaults de antes); os testes constroem `Settings(...)` direto e passam
para `create_app`.
"""
import os
from dataclasses import dataclass


def _lista(valor: str) -> tuple[str, ...]:
    return tuple(p.strip() for p in valor.split(",") if p.strip())


@dataclass(frozen=True)
class Settings:
    server_name: str = "ceu-natal"
    server_version: str = "2.2.3"
    # Vazio = sem autenticação (modo dev).
    api_key: str = ""
    # Hosts permitidos no transporte Streamable HTTP (anti-DNS rebinding).
    # Vazio = sem validação (modo dev / proxy reverso confiável).
    allowed_hosts: tuple[str, ...] = ()
    # Token do portal de plugins da OpenAI; vazio = rota de verificação responde 404.
    openai_apps_challenge: str = ""
    # Limite de taxa (chamadas de tool por minuto); 0 desliga a camada.
    rate_limit_session_per_min: int = 30
    rate_limit_global_per_min: int = 600
    # URLs públicas (a landing troca de domínio só por env), sem barra final.
    public_site_url: str = "https://github.com/gucancado/ceu-natal"
    public_mcp_url: str = "https://astrologia-mcp.gustavocancado.com.br"
    # Mapa rápido do site: limite por IP (o formulário roda no navegador da
    # pessoa, então o IP é dela; os IPs compartilhados de Anthropic/OpenAI não
    # passam aqui).
    rate_limit_mapa_rapido_ip_per_min: int = 6
    rate_limit_mapa_rapido_global_per_min: int = 120
    # Origens aceitas pelo CORS do /mapa-rapido. Vazio = só public_site_url.
    cors_origins: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # Normaliza também quando o objeto é construído à mão (testes).
        object.__setattr__(self, "api_key", self.api_key.strip())
        object.__setattr__(self, "public_site_url", self.public_site_url.rstrip("/"))
        object.__setattr__(self, "public_mcp_url", self.public_mcp_url.rstrip("/"))
        object.__setattr__(self, "allowed_hosts", tuple(h.strip() for h in self.allowed_hosts if h.strip()))
        object.__setattr__(
            self, "cors_origins",
            tuple(o.strip().rstrip("/") for o in self.cors_origins if o.strip()),
        )

    @property
    def cors_efetivos(self) -> tuple[str, ...]:
        """Origens do CORS do /mapa-rapido; padrão: só o site."""
        return self.cors_origins or (self.public_site_url,)

    @classmethod
    def do_ambiente(cls) -> "Settings":
        """Lê as variáveis de ambiente; ausentes ficam com os defaults acima."""
        p = cls()

        def env(nome: str, padrao) -> str:
            return os.getenv(nome, str(padrao))

        return cls(
            server_name=env("MCP_SERVER_NAME", p.server_name),
            server_version=env("MCP_SERVER_VERSION", p.server_version),
            api_key=env("MCP_API_KEY", p.api_key),
            allowed_hosts=_lista(env("MCP_ALLOWED_HOSTS", "")),
            openai_apps_challenge=env("OPENAI_APPS_CHALLENGE", p.openai_apps_challenge).strip(),
            rate_limit_session_per_min=int(env("RATE_LIMIT_SESSION_PER_MIN", p.rate_limit_session_per_min)),
            rate_limit_global_per_min=int(env("RATE_LIMIT_GLOBAL_PER_MIN", p.rate_limit_global_per_min)),
            public_site_url=env("PUBLIC_SITE_URL", p.public_site_url),
            public_mcp_url=env("PUBLIC_MCP_URL", p.public_mcp_url),
            rate_limit_mapa_rapido_ip_per_min=int(
                env("RATE_LIMIT_MAPA_RAPIDO_IP_PER_MIN", p.rate_limit_mapa_rapido_ip_per_min)
            ),
            rate_limit_mapa_rapido_global_per_min=int(
                env("RATE_LIMIT_MAPA_RAPIDO_GLOBAL_PER_MIN", p.rate_limit_mapa_rapido_global_per_min)
            ),
            cors_origins=_lista(env("CORS_ORIGINS", "")),
        )
