FROM python:3.11-slim

WORKDIR /app

# Usuário sem privilégios para rodar o servidor. O diretório do cache do
# geocoder (GEOCODER_CACHE_PATH, volume no docker-compose) pertence a ele.
RUN useradd --create-home --shell /usr/sbin/nologin app \
    && mkdir -p /var/cache/ceu-natal \
    && chown app:app /var/cache/ceu-natal

# Só as dependências de runtime, pinadas pelo lockfile.
COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY --chown=app:app . .

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://localhost:8000/health',timeout=5).read(); sys.exit(0)" || exit 1

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
