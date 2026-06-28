<#
.SYNOPSIS
  Windows equivalent of the Makefile — run dev/prod/CQRS Docker tasks.

.EXAMPLE
  .\dev.ps1 dev-build
  .\dev.ps1 migrate
  .\dev.ps1 cqrs-build
  .\dev.ps1 help
#>

param(
    [string]$Task = "help",
    [string]$Msg  = "migration"
)

$DEV  = "docker compose -f docker-compose.dev.yml"
$PROD = "docker compose"
$CQRS = "docker compose -f docker-compose.cqrs.yml"

switch ($Task) {

    # ── Development (Monolith) ──────────────────────────────────────────────────

    "dev" {
        Invoke-Expression "$DEV up -d"
    }
    "dev-build" {
        Invoke-Expression "$DEV up --build -d"
    }
    "dev-down" {
        Invoke-Expression "$DEV down"
    }

    # ── Production (Monolith) ───────────────────────────────────────────────────

    "prod" {
        Invoke-Expression "$PROD up -d"
    }
    "prod-build" {
        Invoke-Expression "$PROD up --build -d"
    }
    "prod-down" {
        Invoke-Expression "$PROD down"
    }

    # ── CQRS Microservices ──────────────────────────────────────────────────────

    "cqrs" {
        Invoke-Expression "$CQRS up -d"
    }
    "cqrs-build" {
        Invoke-Expression "$CQRS up --build -d"
    }
    "cqrs-down" {
        Invoke-Expression "$CQRS down"
    }

    # ── Logs ─────────────────────────────────────────────────────────────────────

    "logs" {
        Invoke-Expression "$DEV logs -f app"
    }
    "logs-worker" {
        Invoke-Expression "$DEV logs -f worker"
    }
    "logs-gateway" {
        Invoke-Expression "$CQRS logs -f api-gateway"
    }
    "logs-chat-cmd" {
        Invoke-Expression "$CQRS logs -f chat-command"
    }
    "logs-chat-qry" {
        Invoke-Expression "$CQRS logs -f chat-query"
    }
    "logs-plot-cmd" {
        Invoke-Expression "$CQRS logs -f plot-command"
    }
    "logs-plot-qry" {
        Invoke-Expression "$CQRS logs -f plot-query"
    }

    # ── Database ──────────────────────────────────────────────────────────────────

    "migrate" {
        Invoke-Expression "$DEV exec app sh -c 'cd /app/backend && .venv/bin/alembic upgrade head'"
    }
    "migrate-new" {
        Invoke-Expression "$DEV exec app sh -c 'cd /app/backend && .venv/bin/alembic revision --autogenerate -m ""$Msg""'"
    }
    "seed" {
        Invoke-Expression "$DEV exec app sh -c 'cd /app/backend && .venv/bin/python scripts/seed.py'"
    }

    # ── Shell ─────────────────────────────────────────────────────────────────────

    "shell" {
        Invoke-Expression "$DEV exec app bash"
    }
    "shell-gateway" {
        Invoke-Expression "$CQRS exec api-gateway bash"
    }

    # ── Help ──────────────────────────────────────────────────────────────────────

    default {
        Write-Host ""
        Write-Host "  Usage: .\dev.ps1 <task> [-Msg '<description>']"
        Write-Host ""
        Write-Host "  Monolith — Development  (docker-compose.dev.yml)"
        Write-Host "  ──────────────────────────────────────────────────────────"
        Write-Host "  dev              Start monolith dev stack (hot-reload)"
        Write-Host "  dev-build        Rebuild image and start dev stack"
        Write-Host "  dev-down         Stop dev stack"
        Write-Host ""
        Write-Host "  Monolith — Production  (docker-compose.yml)"
        Write-Host "  ──────────────────────────────────────────────────────────"
        Write-Host "  prod             Start monolith production stack"
        Write-Host "  prod-build       Rebuild image and start production stack"
        Write-Host "  prod-down        Stop production stack"
        Write-Host ""
        Write-Host "  CQRS Microservices  (docker-compose.cqrs.yml)"
        Write-Host "  ──────────────────────────────────────────────────────────"
        Write-Host "  cqrs             Start CQRS stack"
        Write-Host "  cqrs-build       Rebuild all 5 service images and start"
        Write-Host "  cqrs-down        Stop CQRS stack"
        Write-Host ""
        Write-Host "  Logs"
        Write-Host "  ──────────────────────────────────────────────────────────"
        Write-Host "  logs             Follow app logs            (monolith dev)"
        Write-Host "  logs-worker      Follow Celery worker logs  (monolith dev)"
        Write-Host "  logs-gateway     Follow api-gateway logs    (CQRS)"
        Write-Host "  logs-chat-cmd    Follow chat-command logs   (CQRS)"
        Write-Host "  logs-chat-qry    Follow chat-query logs     (CQRS)"
        Write-Host "  logs-plot-cmd    Follow plot-command logs   (CQRS)"
        Write-Host "  logs-plot-qry    Follow plot-query logs     (CQRS)"
        Write-Host ""
        Write-Host "  Database  (monolith dev)"
        Write-Host "  ──────────────────────────────────────────────────────────"
        Write-Host "  migrate          Apply all pending Alembic migrations"
        Write-Host "  migrate-new      Generate a new migration (-Msg 'description')"
        Write-Host "  seed             Run the database seeder"
        Write-Host ""
        Write-Host "  Shell"
        Write-Host "  ──────────────────────────────────────────────────────────"
        Write-Host "  shell            Open bash in app container  (monolith dev)"
        Write-Host "  shell-gateway    Open bash in api-gateway    (CQRS)"
        Write-Host ""
    }
}
