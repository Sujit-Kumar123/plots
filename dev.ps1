<#
.SYNOPSIS
  Windows dev helper — run Docker Compose tasks for the full microservices stack.

.DESCRIPTION
  Six backend microservices (api-gateway, auth-service, chat-service, plot-service,
  payment-service, notification-service) + Next.js frontend served via Nginx.
  Migrations are handled automatically: auth-service runs Alembic on startup;
  chat-service and plot-service each run their own migrations at startup.

.EXAMPLE
  .\dev.ps1 dev-build       # First run / after Dockerfile changes
  .\dev.ps1 dev             # Subsequent runs (images already built)
  .\dev.ps1 dev-down        # Stop and remove containers
  .\dev.ps1 dev-clean       # Stop and remove containers + all volumes (wipes DB)
  .\dev.ps1 logs            # Follow all logs
  .\dev.ps1 logs-chat       # Follow chat-service logs
  .\dev.ps1 status          # Show container health
  .\dev.ps1 help            # Show this help
#>

param(
    [string]$Task    = "help",
    [string]$Msg     = "migration",
    [string]$Service = ""
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$DEV  = "docker compose -f docker-compose.dev.yml"
$PROD = "docker compose"
$CQRS = "docker compose -f docker-compose.cqrs.yml"

function Run([string]$cmd) {
    Write-Host "> $cmd" -ForegroundColor Cyan
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Command failed (exit $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

switch ($Task) {

    # ── Full Dev Stack (docker-compose.dev.yml) ──────────────────────────────
    # All 6 microservices + frontend/nginx + postgres + redis + kafka + dev tools
    # Source volumes mounted for hot-reload. All ports exposed.

    "dev" {
        Run "$DEV up -d"
        Write-Host ""
        Write-Host "  Stack started. Access points:" -ForegroundColor Green
        Write-Host "  App         http://localhost"
        Write-Host "  API Gateway http://localhost:8000"
        Write-Host "  Swagger     http://localhost:8000/docs"
        Write-Host ""
        Write-Host "  Use '.\dev.ps1 status' to watch service health."
    }
    "dev-build" {
        Run "$DEV up --build -d"
        Write-Host ""
        Write-Host "  Stack rebuilt and started. Access points:" -ForegroundColor Green
        Write-Host "  App         http://localhost"
        Write-Host "  API Gateway http://localhost:8000"
        Write-Host "  Swagger     http://localhost:8000/docs"
        Write-Host ""
        Write-Host "  Use '.\dev.ps1 status' to watch service health."
    }
    "dev-down" {
        Run "$DEV down"
    }
    "dev-clean" {
        Write-Host "WARNING: This will delete all Docker volumes (database data, etc.)" -ForegroundColor Yellow
        $confirm = Read-Host "Type 'yes' to continue"
        if ($confirm -eq "yes") {
            Run "$DEV down -v"
        } else {
            Write-Host "Aborted." -ForegroundColor Yellow
        }
    }

    # ── Production (docker-compose.yml) ──────────────────────────────────────

    "prod" {
        Run "$PROD up -d"
    }
    "prod-build" {
        Run "$PROD up --build -d"
    }
    "prod-down" {
        Run "$PROD down"
    }

    # ── CQRS-only Stack (docker-compose.cqrs.yml) ─────────────────────────────
    # Lightweight: api-gateway + chat-service + plot-service + kafka + postgres
    # No auth/payment/notification. Good for isolated CQRS domain development.

    "cqrs" {
        Run "$CQRS up -d"
    }
    "cqrs-build" {
        Run "$CQRS up --build -d"
    }
    "cqrs-down" {
        Run "$CQRS down"
    }
    "cqrs-clean" {
        Write-Host "WARNING: This will delete all CQRS Docker volumes." -ForegroundColor Yellow
        $confirm = Read-Host "Type 'yes' to continue"
        if ($confirm -eq "yes") {
            Run "$CQRS down -v"
        } else {
            Write-Host "Aborted." -ForegroundColor Yellow
        }
    }

    # ── Container Status ──────────────────────────────────────────────────────

    "status" {
        Run "$DEV ps"
    }
    "cqrs-status" {
        Run "$CQRS ps"
    }

    # ── Logs (dev stack) ──────────────────────────────────────────────────────

    "logs" {
        Run "$DEV logs -f --tail=100"
    }
    "logs-app" {
        Run "$DEV logs -f --tail=100 app"
    }
    "logs-gateway" {
        Run "$DEV logs -f --tail=100 api-gateway"
    }
    "logs-auth" {
        Run "$DEV logs -f --tail=100 auth-service"
    }
    "logs-chat" {
        Run "$DEV logs -f --tail=100 chat-service"
    }
    "logs-plot" {
        Run "$DEV logs -f --tail=100 plot-service"
    }
    "logs-payment" {
        Run "$DEV logs -f --tail=100 payment-service"
    }
    "logs-notification" {
        Run "$DEV logs -f --tail=100 notification-service"
    }
    "logs-kafka" {
        Run "$DEV logs -f --tail=100 kafka"
    }
    "logs-db" {
        Run "$DEV logs -f --tail=100 postgres"
    }
    "logs-migrate" {
        Run "$DEV logs db-migrate"
    }

    # ── Logs (CQRS stack) ─────────────────────────────────────────────────────

    "cqrs-logs" {
        Run "$CQRS logs -f --tail=100"
    }
    "cqrs-logs-gateway" {
        Run "$CQRS logs -f --tail=100 api-gateway"
    }
    "cqrs-logs-chat" {
        Run "$CQRS logs -f --tail=100 chat-service"
    }
    "cqrs-logs-plot" {
        Run "$CQRS logs -f --tail=100 plot-service"
    }

    # ── Database Migrations ───────────────────────────────────────────────────
    # Migrations run automatically on startup via the db-migrate init container.
    # Use these commands only if you need to run them manually.

    "migrate" {
        Run "$DEV exec auth-service uv run alembic upgrade head"
    }
    "migrate-new" {
        Run "$DEV exec auth-service uv run alembic revision --autogenerate -m '$Msg'"
    }

    # ── Shell Access ──────────────────────────────────────────────────────────

    "shell" {
        if ($Service -ne "") {
            Run "$DEV exec $Service bash"
        } else {
            Run "$DEV exec api-gateway bash"
        }
    }
    "shell-gateway" {
        Run "$DEV exec api-gateway bash"
    }
    "shell-auth" {
        Run "$DEV exec auth-service bash"
    }
    "shell-chat" {
        Run "$DEV exec chat-service bash"
    }
    "shell-plot" {
        Run "$DEV exec plot-service bash"
    }
    "shell-payment" {
        Run "$DEV exec payment-service bash"
    }
    "shell-notification" {
        Run "$DEV exec notification-service bash"
    }
    "shell-db" {
        Run "$DEV exec postgres psql -U `${POSTGRES_USER:-mvp_user} -d `${POSTGRES_DB:-mvp_db}"
    }

    # ── Restart Individual Services ───────────────────────────────────────────

    "restart-gateway" {
        Run "$DEV restart api-gateway"
    }
    "restart-auth" {
        Run "$DEV restart auth-service"
    }
    "restart-chat" {
        Run "$DEV restart chat-service"
    }
    "restart-plot" {
        Run "$DEV restart plot-service"
    }

    # ── Health Check ──────────────────────────────────────────────────────────
    # Polls /health/ready on all 6 microservices and prints a summary.

    "health" {
        $services = @(
            @{ name = "api-gateway";        port = 8000 },
            @{ name = "auth-service";       port = 8010 },
            @{ name = "chat-service";       port = 8001 },
            @{ name = "plot-service";       port = 8003 },
            @{ name = "payment-service";    port = 8011 },
            @{ name = "notification-svc";   port = 8012 }
        )
        Write-Host ""
        Write-Host "  Service Health Check" -ForegroundColor Cyan
        Write-Host "  ──────────────────────────────────────────────"
        foreach ($svc in $services) {
            try {
                $resp = Invoke-WebRequest -Uri "http://localhost:$($svc.port)/health/ready" `
                    -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
                $color = if ($resp.StatusCode -eq 200) { "Green" } else { "Yellow" }
                $label = if ($resp.StatusCode -eq 200) { "ready  " } else { "degraded" }
                Write-Host "  $label  $($svc.name):$($svc.port)" -ForegroundColor $color
            } catch {
                Write-Host "  error    $($svc.name):$($svc.port)" -ForegroundColor Red
            }
        }
        Write-Host ""
    }

    # ── Help ──────────────────────────────────────────────────────────────────

    default {
        Write-Host ""
        Write-Host "  Usage: .\dev.ps1 <task> [-Msg '<text>'] [-Service '<name>']" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  Full Dev Stack  (docker-compose.dev.yml)" -ForegroundColor Yellow
        Write-Host "  ──────────────────────────────────────────────────────────────"
        Write-Host "  dev-build        Rebuild all images and start (first run)"
        Write-Host "  dev              Start stack with existing images"
        Write-Host "  dev-down         Stop containers (keep volumes)"
        Write-Host "  dev-clean        Stop containers + delete all volumes (wipes DB)"
        Write-Host "  status           Show container health status"
        Write-Host "  health           Poll /health/ready on all 6 microservices"
        Write-Host ""
        Write-Host "  CQRS-only Stack  (docker-compose.cqrs.yml)" -ForegroundColor Yellow
        Write-Host "  ──────────────────────────────────────────────────────────────"
        Write-Host "  cqrs-build       Rebuild and start CQRS-only stack"
        Write-Host "  cqrs             Start CQRS stack"
        Write-Host "  cqrs-down        Stop CQRS stack"
        Write-Host "  cqrs-clean       Stop + delete CQRS volumes"
        Write-Host "  cqrs-status      Show CQRS container health"
        Write-Host ""
        Write-Host "  Production  (docker-compose.yml)" -ForegroundColor Yellow
        Write-Host "  ──────────────────────────────────────────────────────────────"
        Write-Host "  prod-build       Rebuild and start production stack"
        Write-Host "  prod             Start production stack"
        Write-Host "  prod-down        Stop production stack"
        Write-Host ""
        Write-Host "  Logs  (dev stack)" -ForegroundColor Yellow
        Write-Host "  ──────────────────────────────────────────────────────────────"
        Write-Host "  logs             Follow all service logs"
        Write-Host "  logs-app         Follow frontend / nginx logs"
        Write-Host "  logs-gateway     Follow api-gateway logs"
        Write-Host "  logs-auth        Follow auth-service logs"
        Write-Host "  logs-chat        Follow chat-service logs (producer + consumer)"
        Write-Host "  logs-plot        Follow plot-service logs (producer + consumer)"
        Write-Host "  logs-payment     Follow payment-service logs"
        Write-Host "  logs-notification Follow notification-service logs"
        Write-Host "  logs-kafka       Follow Kafka broker logs"
        Write-Host "  logs-db          Follow PostgreSQL logs"
        Write-Host "  logs-migrate     Show db-migrate init container output"
        Write-Host ""
        Write-Host "  Logs  (CQRS stack)" -ForegroundColor Yellow
        Write-Host "  ──────────────────────────────────────────────────────────────"
        Write-Host "  cqrs-logs        Follow all CQRS logs"
        Write-Host "  cqrs-logs-gateway"
        Write-Host "  cqrs-logs-chat"
        Write-Host "  cqrs-logs-plot"
        Write-Host ""
        Write-Host "  Database" -ForegroundColor Yellow
        Write-Host "  ──────────────────────────────────────────────────────────────"
        Write-Host "  migrate                     Apply pending Alembic migrations"
        Write-Host "  migrate-new -Msg 'desc'     Generate a new migration file"
        Write-Host ""
        Write-Host "  Shell" -ForegroundColor Yellow
        Write-Host "  ──────────────────────────────────────────────────────────────"
        Write-Host "  shell-gateway    bash in api-gateway"
        Write-Host "  shell-auth       bash in auth-service"
        Write-Host "  shell-chat       bash in chat-service"
        Write-Host "  shell-plot       bash in plot-service"
        Write-Host "  shell-payment    bash in payment-service"
        Write-Host "  shell-notification bash in notification-service"
        Write-Host "  shell -Service <name>  bash in any named container"
        Write-Host ""
        Write-Host "  Restart" -ForegroundColor Yellow
        Write-Host "  ──────────────────────────────────────────────────────────────"
        Write-Host "  restart-gateway / restart-auth / restart-chat / restart-plot"
        Write-Host ""
        Write-Host "  Swagger (dev stack, DEBUG=true)" -ForegroundColor Yellow
        Write-Host "  ──────────────────────────────────────────────────────────────"
        Write-Host "  http://localhost:8000/docs    api-gateway  (all routes)"
        Write-Host "  http://localhost:8010/docs    auth-service"
        Write-Host "  http://localhost:8001/docs    chat-service"
        Write-Host "  http://localhost:8003/docs    plot-service"
        Write-Host "  http://localhost:8011/docs    payment-service"
        Write-Host "  http://localhost:8012/docs    notification-service"
        Write-Host ""
        Write-Host "  Dev Tools" -ForegroundColor Yellow
        Write-Host "  ──────────────────────────────────────────────────────────────"
        Write-Host "  http://localhost:5050    pgAdmin  (admin@local.dev / admin)"
        Write-Host "  http://localhost:8090    Kafka UI"
        Write-Host "  http://localhost:8081    Redis Commander  (admin / admin)"
        Write-Host ""
    }
}
