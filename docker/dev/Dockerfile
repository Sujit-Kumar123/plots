# Development image — both services run with hot-reload via supervisord.
# Source code is volume-mounted at runtime; this image only pre-installs deps.
FROM python:3.12-slim

# Node.js 22 + Nginx + Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl gnupg2 supervisor nginx \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Bun binary (for `bun run next dev`)
COPY --from=oven/bun:latest /usr/local/bin/bun /usr/local/bin/bun

# uv (Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# ── Python deps (cached layer; code volume-mounted at runtime) ────────────────
COPY backend/pyproject.toml backend/uv.lock /app/backend/
RUN cd /app/backend && uv sync --frozen --no-install-project

# ── JS deps (cached layer; node_modules preserved via named volume) ───────────
COPY frontend/package.json frontend/bun.lock* /app/frontend/
RUN cd /app/frontend && bun install

# ── Nginx + Supervisor configs ────────────────────────────────────────────────
RUN rm -f /etc/nginx/sites-enabled/default
COPY docker/nginx/nginx.conf        /etc/nginx/conf.d/app.conf
COPY docker/supervisord.dev.conf    /etc/supervisor/conf.d/app.conf

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NEXT_TELEMETRY_DISABLED=1

EXPOSE 80

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/app.conf"]
