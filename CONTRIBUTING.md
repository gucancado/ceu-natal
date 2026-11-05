# Como contribuir

Obrigado pelo interesse. Issues com bug, dúvida de cálculo ou ideia são bem-vindas;
para PRs, leia abaixo antes.

## Ambiente

O cálculo usa o pyswisseph (Swiss Ephemeris), que não compila no Windows.

- **Linux ou macOS:**

  ```bash
  python3.11 -m venv .venv && source .venv/bin/activate
  pip install -r requirements-dev.txt
  ruff check .
  mypy app
  python -m pytest -q
  ```

- **Windows:** use o WSL e siga os passos acima. Sem WSL, dá para rodar só a parte
  que não importa o Kerykeion:

  ```bash
  python -m pytest tests/test_server.py tests/test_ratelimit.py tests/test_server_json.py tests/test_deploy_script.py tests/test_periodos.py tests/test_validators.py -q
  ```

- **CI:** todo push e PR roda `ruff`, `mypy`, a suíte completa do `pytest`, o
  `pip-audit` e o build do site. O PR só entra com o CI verde.

O site fica em `web/`: `cd web && pnpm install && pnpm typecheck && pnpm test && pnpm build`.

Dependências de runtime ficam em `requirements.in`, com teto de major; o
`requirements.txt` é um lock gerado por
`uv pip compile requirements.in -o requirements.txt --python-version 3.11`.
Não edite o lock à mão.

## Convenções

- **Português** em código (nomes, comentários, docstrings), mensagens de erro e
  commits.
- **Commits** no formato [Conventional Commits](https://www.conventionalcommits.org/pt-br/):
  `fix(core): ...`, `feat(server): ...`, `docs: ...`, `test: ...`, `chore: ...`.
- Todo `.py` novo em `app/` ou `scripts/` começa com
  `# SPDX-License-Identifier: AGPL-3.0-or-later` e uma docstring.
- Testes com Kerykeion passam `lat`, `lng` e `tz_str` direto, sem rede. Use dados
  de nascimento fictícios (veja `tests/conftest.py`).
- Lógica de cálculo vai em `app/core/`; o handler de cada tool em `app/tools/`.
  `app/server.py` só registra e despacha.

## Pull requests

- Um assunto por PR, pequeno o bastante para revisar de uma vez.
- Todo comportamento novo ou bug corrigido vem com teste.
- Atualize o `CHANGELOG.md` (seção da próxima versão) e a documentação afetada.
- Mudança de cálculo: diga no PR como conferiu o resultado (outro software,
  efeméride publicada).

Ao contribuir, você concorda que seu código é licenciado sob a
[AGPL-3.0-or-later](LICENSE) e segue o [código de conduta](CODE_OF_CONDUCT.md).
