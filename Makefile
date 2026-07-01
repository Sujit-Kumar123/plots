.PHONY: dev dev-build dev-down dev-clean \
        prod prod-build prod-down \
        cqrs cqrs-build cqrs-down cqrs-clean \
        status cqrs-status health \
        logs logs-app logs-gateway logs-auth logs-chat logs-plot \
        logs-payment logs-notification logs-kafka logs-db logs-migrate \
        cqrs-logs cqrs-logs-gateway cqrs-logs-chat cqrs-logs-plot \
        migrate migrate-new \
        shell shell-gateway shell-auth shell-chat shell-plot shell-payment shell-notification shell-db \
        restart-gateway restart-auth restart-chat restart-plot \
        help

MSG ?= migration

# ── Full Dev Stack ─────────────────────────────────────────────────────────────
# All 6 microservices + frontend/nginx + postgres + redis + kafka + dev tools.
# Source code volume-mounted for hot-reload. All service ports exposed.
# Dev tools: pgAdmin (:5050), Kafka UI (:8090), Redis Commander (:8081)

dev:
	docker compose -f docker-compose.dev.yml up -d

dev-build:
	docker compose -f docker-compose.dev.yml up --build -d

dev-down:
	docker compose -f docker-compose.dev.yml down

dev-clean:
	docker compose -f docker-compose.dev.yml down -v

# ── Production ─────────────────────────────────────────────────────────────────

prod:
	docker compose up -d

prod-build:
	docker compose up --build -d

prod-down:
	docker compose down

# ── CQRS-only Stack ────────────────────────────────────────────────────────────
# Lightweight: api-gateway + chat-service + plot-service + kafka + postgres.
# No auth/payment/notification. Good for isolated CQRS domain development.

cqrs:
	docker compose -f docker-compose.cqrs.yml up -d

cqrs-build:
	docker compose -f docker-compose.cqrs.yml up --build -d

cqrs-down:
	docker compose -f docker-compose.cqrs.yml down

cqrs-clean:
	docker compose -f docker-compose.cqrs.yml down -v

# ── Status ─────────────────────────────────────────────────────────────────────

status:
	docker compose -f docker-compose.dev.yml ps

cqrs-status:
	docker compose -f docker-compose.cqrs.yml ps

health:
	@for port in 8000 8010 8001 8003 8011 8012; do \
	  printf "  port $$port: "; \
	  curl -sf http://localhost:$$port/health/ready | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','?'))" 2>/dev/null || echo "error"; \
	done

# ── Logs (dev stack) ──────────────────────────────────────────────────────────

logs:
	docker compose -f docker-compose.dev.yml logs -f --tail=100

logs-app:
	docker compose -f docker-compose.dev.yml logs -f --tail=100 app

logs-gateway:
	docker compose -f docker-compose.dev.yml logs -f --tail=100 api-gateway

logs-auth:
	docker compose -f docker-compose.dev.yml logs -f --tail=100 auth-service

logs-chat:
	docker compose -f docker-compose.dev.yml logs -f --tail=100 chat-service

logs-plot:
	docker compose -f docker-compose.dev.yml logs -f --tail=100 plot-service

logs-payment:
	docker compose -f docker-compose.dev.yml logs -f --tail=100 payment-service

logs-notification:
	docker compose -f docker-compose.dev.yml logs -f --tail=100 notification-service

logs-kafka:
	docker compose -f docker-compose.dev.yml logs -f --tail=100 kafka

logs-db:
	docker compose -f docker-compose.dev.yml logs -f --tail=100 postgres

logs-migrate:
	docker compose -f docker-compose.dev.yml logs db-migrate

# ── Logs (CQRS stack) ─────────────────────────────────────────────────────────

cqrs-logs:
	docker compose -f docker-compose.cqrs.yml logs -f --tail=100

cqrs-logs-gateway:
	docker compose -f docker-compose.cqrs.yml logs -f --tail=100 api-gateway

cqrs-logs-chat:
	docker compose -f docker-compose.cqrs.yml logs -f --tail=100 chat-service

cqrs-logs-plot:
	docker compose -f docker-compose.cqrs.yml logs -f --tail=100 plot-service

# ── Database Migrations ────────────────────────────────────────────────────────
# auth-service owns the public schema (users, sessions, roles, permissions).
# chat-service and plot-service auto-run their own migrations at startup.

migrate:
	docker compose -f docker-compose.dev.yml exec auth-service uv run alembic upgrade head

migrate-new:
	docker compose -f docker-compose.dev.yml exec auth-service \
	  uv run alembic revision --autogenerate -m '$(MSG)'

# ── Shell Access ───────────────────────────────────────────────────────────────

shell:
	docker compose -f docker-compose.dev.yml exec api-gateway bash

shell-gateway:
	docker compose -f docker-compose.dev.yml exec api-gateway bash

shell-auth:
	docker compose -f docker-compose.dev.yml exec auth-service bash

shell-chat:
	docker compose -f docker-compose.dev.yml exec chat-service bash

shell-plot:
	docker compose -f docker-compose.dev.yml exec plot-service bash

shell-payment:
	docker compose -f docker-compose.dev.yml exec payment-service bash

shell-notification:
	docker compose -f docker-compose.dev.yml exec notification-service bash

shell-db:
	docker compose -f docker-compose.dev.yml exec postgres psql -U $${POSTGRES_USER:-mvp_user} -d $${POSTGRES_DB:-mvp_db}

# ── Restart Individual Services ───────────────────────────────────────────────

restart-gateway:
	docker compose -f docker-compose.dev.yml restart api-gateway

restart-auth:
	docker compose -f docker-compose.dev.yml restart auth-service

restart-chat:
	docker compose -f docker-compose.dev.yml restart chat-service

restart-plot:
	docker compose -f docker-compose.dev.yml restart plot-service

# ── Help ───────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "  Full Dev Stack  (docker-compose.dev.yml)"
	@echo "  ──────────────────────────────────────────────────────────────────"
	@echo "  make dev-build        Rebuild all images and start  (first run)"
	@echo "  make dev              Start stack with existing images"
	@echo "  make dev-down         Stop containers (keep volumes)"
	@echo "  make dev-clean        Stop containers + delete all volumes (wipes DB)"
	@echo "  make status           Show container health status"
	@echo "  make health           Poll /health/ready on all 6 microservices"
	@echo ""
	@echo "  CQRS-only Stack  (docker-compose.cqrs.yml)"
	@echo "  ──────────────────────────────────────────────────────────────────"
	@echo "  make cqrs-build       Rebuild and start CQRS-only stack"
	@echo "  make cqrs             Start CQRS stack"
	@echo "  make cqrs-down        Stop CQRS stack (keep volumes)"
	@echo "  make cqrs-clean       Stop + delete CQRS volumes"
	@echo "  make cqrs-status      Show CQRS container health"
	@echo ""
	@echo "  Production  (docker-compose.yml)"
	@echo "  ──────────────────────────────────────────────────────────────────"
	@echo "  make prod-build       Rebuild and start production stack"
	@echo "  make prod             Start production stack"
	@echo "  make prod-down        Stop production stack"
	@echo ""
	@echo "  Logs  (dev stack)"
	@echo "  ──────────────────────────────────────────────────────────────────"
	@echo "  make logs             Follow all service logs"
	@echo "  make logs-app         Follow frontend / nginx logs"
	@echo "  make logs-gateway     Follow api-gateway logs"
	@echo "  make logs-auth        Follow auth-service logs"
	@echo "  make logs-chat        Follow chat-service logs (producer + consumer)"
	@echo "  make logs-plot        Follow plot-service logs (producer + consumer)"
	@echo "  make logs-payment     Follow payment-service logs"
	@echo "  make logs-notification Follow notification-service logs"
	@echo "  make logs-kafka       Follow Kafka broker logs"
	@echo "  make logs-db          Follow PostgreSQL logs"
	@echo "  make logs-migrate     Show db-migrate init container output"
	@echo ""
	@echo "  Logs  (CQRS stack)"
	@echo "  ──────────────────────────────────────────────────────────────────"
	@echo "  make cqrs-logs        Follow all CQRS logs"
	@echo "  make cqrs-logs-gateway / cqrs-logs-chat / cqrs-logs-plot"
	@echo ""
	@echo "  Database"
	@echo "  ──────────────────────────────────────────────────────────────────"
	@echo "  make migrate               Apply pending auth-service Alembic migrations"
	@echo "  make migrate-new MSG='...' Generate a new autogenerated migration"
	@echo ""
	@echo "  Shell"
	@echo "  ──────────────────────────────────────────────────────────────────"
	@echo "  make shell-gateway    bash in api-gateway"
	@echo "  make shell-auth       bash in auth-service"
	@echo "  make shell-chat       bash in chat-service"
	@echo "  make shell-plot       bash in plot-service"
	@echo "  make shell-payment    bash in payment-service"
	@echo "  make shell-notification bash in notification-service"
	@echo "  make shell-db         psql in postgres"
	@echo ""
	@echo "  Restart"
	@echo "  ──────────────────────────────────────────────────────────────────"
	@echo "  make restart-gateway / restart-auth / restart-chat / restart-plot"
	@echo ""
	@echo "  Swagger  (dev stack, DEBUG=true)"
	@echo "  ──────────────────────────────────────────────────────────────────"
	@echo "  http://localhost:8000/docs    api-gateway  (all routes)"
	@echo "  http://localhost:8010/docs    auth-service"
	@echo "  http://localhost:8001/docs    chat-service"
	@echo "  http://localhost:8003/docs    plot-service"
	@echo "  http://localhost:8011/docs    payment-service"
	@echo "  http://localhost:8012/docs    notification-service"
	@echo ""
	@echo "  Dev Tools"
	@echo "  ──────────────────────────────────────────────────────────────────"
	@echo "  http://localhost:5050    pgAdmin  (admin@local.dev / admin)"
	@echo "  http://localhost:8090    Kafka UI"
	@echo "  http://localhost:8081    Redis Commander  (admin / admin)"
	@echo ""
