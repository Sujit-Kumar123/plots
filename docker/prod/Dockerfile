# ── Stage 1: Build Next.js frontend ──────────────────────────────────────────
FROM oven/bun:1-slim AS frontend-builder

WORKDIR /build/frontend

COPY frontend/package.json frontend/bun.lock* ./
RUN bun install --frozen-lockfile

COPY frontend/ ./
# Root .env → .env.local so Next.js inlines NEXT_PUBLIC_* vars at build time
COPY .env .env.local
RUN bun run build


# ── Stage 2: Install Python production dependencies ───────────────────────────
FROM python:3.12-slim AS backend-builder

WORKDIR /build/backend

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


# ── Stage 3: Production runtime ───────────────────────────────────────────────
FROM python:3.12-slim

# Node.js 22 (runs Next.js standalone server.js) + Nginx + Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl gnupg2 supervisor nginx \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Backend ───────────────────────────────────────────────────────────────────
COPY --from=backend-builder /build/backend/.venv /app/backend/.venv
COPY backend/ /app/backend/

# ── Frontend (Next.js standalone — minimal self-contained server) ─────────────
# standalone/ contains server.js + minimal node_modules
COPY --from=frontend-builder /build/frontend/.next/standalone /app/frontend/
# Static JS/CSS chunks (referenced by server.js)
COPY --from=frontend-builder /build/frontend/.next/static     /app/frontend/.next/static
# Public directory (favicon, images, etc.)
COPY --from=frontend-builder /build/frontend/public           /app/frontend/public

# ── Nginx + Supervisor configs ────────────────────────────────────────────────
RUN rm -f /etc/nginx/sites-enabled/default
COPY docker/nginx/nginx.conf         /etc/nginx/conf.d/app.conf
COPY docker/supervisord.prod.conf    /etc/supervisor/conf.d/app.conf

ENV PATH="/app/backend/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

EXPOSE 80

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/app.conf"]
