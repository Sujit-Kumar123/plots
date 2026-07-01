# Development frontend image — Next.js dev server + Nginx via supervisord.
# Source code is volume-mounted at runtime; this image only pre-installs deps.
# The compose overrides both config files with volume mounts at startup.
FROM python:3.12-slim

# Node.js 22 + Nginx + Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl gnupg2 supervisor nginx \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Bun (for `bun run next dev`)
COPY --from=oven/bun:latest /usr/local/bin/bun /usr/local/bin/bun

WORKDIR /app

# ── JS deps (cached layer; node_modules preserved via named volume) ───────────
COPY frontend/package.json frontend/bun.lock* /app/frontend/
RUN cd /app/frontend && bun install

# ── Nginx + Supervisor default configs (overridden by volume mounts in compose)
RUN rm -f /etc/nginx/sites-enabled/default
COPY docker/nginx/nginx.fullstack.conf        /etc/nginx/conf.d/app.conf
COPY docker/supervisord.fullstack.conf        /etc/supervisor/conf.d/app.conf

ENV NEXT_TELEMETRY_DISABLED=1

EXPOSE 80

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/app.conf"]
