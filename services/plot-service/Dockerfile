FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

ENV UV_NO_CACHE=1

COPY pyproject.toml .
RUN uv sync --no-dev

COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --no-create-home appuser && \
    chown -R appuser:appgroup /app
USER appuser

EXPOSE 8003

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8003/health')" || exit 1

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
