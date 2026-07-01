# Plots

Full-stack monorepo: **Next.js 16** frontend · **9 FastAPI microservices** · **CQRS** with Kafka · deployable on Docker Compose or Kubernetes.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Quick Start](#quick-start)
- [Stack 1 — Dev (9 services, hot-reload)](#stack-1--dev-9-services-hot-reload)
- [Stack 2 — Production (9 services)](#stack-2--production-9-services)
- [Stack 3 — CQRS Lightweight (5 services)](#stack-3--cqrs-lightweight-5-services)
- [Database Migrations](#database-migrations)
- [All Commands Reference](#all-commands-reference)
- [Environment Variables](#environment-variables)
- [Architecture Overview](#architecture-overview)
- [Kubernetes Deployment](#kubernetes-deployment)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · FastAPI 0.115 · SQLAlchemy 2.0 async · Alembic · Pydantic v2 |
| Frontend | Next.js 16 · React 19 · TypeScript 5 · Tailwind CSS v4 · shadcn/ui · Bun |
| Auth | JWT (httpOnly cookies) · Google OAuth 2.0 · Azure AD |
| Database | PostgreSQL 16 + pgvector · Redis 7 |
| CQRS / Events | Apache Kafka (aiokafka) · 9 independent FastAPI microservices |
| Package Manager (Python) | uv — `uv sync --no-dev` per service |
| Infrastructure | Docker Compose · Kubernetes · Nginx · Supervisord |

---

## Project Structure

```
plots/
├── frontend/                    # Next.js 16 App Router
│   └── src/
│       ├── app/                 # Pages (login, dashboard, chat, sheets…)
│       ├── components/          # shadcn/ui primitives + AI chat components
│       ├── context/             # Auth context
│       └── lib/services/        # API helpers (client + server)
├── services/                    # All 9 microservices
│   ├── api-gateway/             # JWT validation · HTTP proxy (:8000)
│   ├── chat-command/            # Chat write side — Kafka publisher (:8001)
│   │   └── alembic/             # Migrations for chat_write schema
│   ├── chat-query/              # Chat read side — Kafka consumer (:8002)
│   │   └── alembic/             # Migrations for chat_read schema
│   ├── plot-command/            # Plot write side — Kafka publisher (:8003)
│   │   └── alembic/             # Migrations for plot_write schema
│   ├── plot-query/              # Plot read side — Kafka consumer (:8004)
│   │   └── alembic/             # Migrations for plot_read schema
│   ├── auth-service/            # Auth, OAuth 2.0, RBAC, admin, audit (:8010)
│   │   └── alembic/             # Migrations for public schema (run via db-migrate)
│   ├── payment-service/         # Payments (:8011)
│   ├── notification-service/    # Notifications — calls email-service (:8012)
│   └── email-service/           # Transactional email via SendGrid (:8013)
├── docker/
│   ├── dev/Dockerfile           # Dev frontend image (bun dev + nginx, hot-reload)
│   ├── prod/Dockerfile.frontend # Prod frontend image (Next.js standalone + nginx)
│   ├── nginx/nginx.fullstack.conf  # Nginx config (proxies /api/* → api-gateway)
│   ├── supervisord.fullstack.conf  # Dev supervisord (bun dev + nginx)
│   └── supervisord.prod.frontend.conf  # Prod supervisord (node standalone + nginx)
├── scripts/
│   └── init-schemas.sql         # Creates chat_write, chat_read, plot_write, plot_read schemas
├── k8s/                         # Kubernetes manifests
├── docker-compose.yml           # Stack 2 — Production microservices (9 services)
├── docker-compose.dev.yml       # Stack 1 — Dev microservices (9 services, hot-reload)
├── docker-compose.cqrs.yml      # Stack 3 — CQRS lightweight dev (5 services)
├── Makefile                     # All make targets
└── .env.example                 # Environment template
```

---

## Prerequisites

- **Docker Desktop** ≥ 26.0 with Docker Compose v2

```bash
docker compose version   # must be v2.x
```

No local Python or Node.js installation required — everything runs inside Docker.

---

## Environment Setup

```bash
# 1. Clone the repo
git clone <repository-url>
cd plots

# 2. Create .env from the template
cp .env.example .env
```

Open `.env` and fill in at minimum:

```env
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=<long-random-string>
INTERNAL_SERVICE_SECRET=<long-random-string>

POSTGRES_USER=mvp_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=mvp_db
```

All other variables have safe defaults for local development.

---

## Quick Start

```bash
# Build all service images and start (first run)
make dev-build

# Open the app
open http://localhost
```

That's it. Migrations run automatically — the `db-migrate` init container applies auth-service Alembic migrations before any service starts, and each CQRS service runs its own `alembic upgrade head` at startup.

---

## Stack 1 — Dev (9 services, hot-reload)

**File:** `docker-compose.dev.yml`

All source code is volume-mounted. Saving a Python file restarts uvicorn immediately; saving a frontend file triggers Next.js HMR. Dev tools (pgAdmin, Kafka UI, Redis Commander) are included. Swagger is enabled on every service.

### Services

| Container | Role | Port |
|---|---|---|
| `app` | Next.js dev server + Nginx | `80` |
| `api-gateway` | JWT validation · HTTP proxy · rate limiting | `8000` |
| `auth-service` | Auth, OAuth 2.0, RBAC, admin, audit | `8010` |
| `payment-service` | Payments | `8011` |
| `notification-service` | Multi-channel notifications | `8012` |
| `email-service` | Transactional email (SendGrid) | `8013` |
| `chat-command` | Chat write side — Kafka publisher | `8001` |
| `chat-query` | Chat read side — Kafka consumer + projections | `8002` |
| `plot-command` | Plot write side — Kafka publisher | `8003` |
| `plot-query` | Plot read side — Kafka consumer + projections | `8004` |
| `db-migrate` | Runs auth-service Alembic, then exits | — |
| `postgres` | PostgreSQL 16 + pgvector | `5432` |
| `redis` | Redis 7 | `6379` |
| `kafka` | Apache Kafka | `29092` (external) |
| `zookeeper` | Kafka coordination | internal |
| `kafka-init` | Creates 4 Kafka topics, then exits | — |
| `kafka-ui` | Kafka browser UI | `8090` |
| `pgadmin` | pgAdmin 4 | `5050` |
| `redis-commander` | Redis browser UI | `8081` |

### Start

```bash
make dev-build    # first run — builds all images
make dev          # subsequent starts (no rebuild)
```

### Stop

```bash
make dev-down
```

### URLs

| Service | URL |
|---|---|
| Application | http://localhost |
| API Gateway Swagger | http://localhost:8000/docs |
| auth-service Swagger | http://localhost:8010/docs |
| chat-command Swagger | http://localhost:8001/docs |
| chat-query Swagger | http://localhost:8002/docs |
| plot-command Swagger | http://localhost:8003/docs |
| plot-query Swagger | http://localhost:8004/docs |
| payment-service Swagger | http://localhost:8011/docs |
| notification-service Swagger | http://localhost:8012/docs |
| email-service Swagger | http://localhost:8013/docs |
| pgAdmin | http://localhost:5050 — `admin@local.dev` / `admin` |
| Kafka UI | http://localhost:8090 |
| Redis Commander | http://localhost:8081 — `admin` / `admin` |
| PostgreSQL | `localhost:5432` — see `.env` |
| Kafka (external) | `localhost:29092` |

---

## Stack 2 — Production (9 services)

**File:** `docker-compose.yml`

Immutable images — no volume mounts. Next.js is compiled to a standalone server bundle. `DEBUG=false` disables Swagger on all services. Only port 80 (nginx) is exposed externally; all backend services use Docker-internal networking. CPU and memory limits are set on every service.

### Start

```bash
make prod-build   # first run — builds all images (~5–10 min)
make prod         # subsequent starts
```

### Stop

```bash
make prod-down
```

### Required env vars (no defaults in production)

```env
POSTGRES_USER=<value>
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=<value>
REDIS_PASSWORD=<strong-password>
SECRET_KEY=<long-random-string>
INTERNAL_SERVICE_SECRET=<long-random-string>
SENDGRID_API_KEY=<key>
APP_URL=https://yourapp.com
```

### URLs

| Service | URL |
|---|---|
| Application | http://localhost (or your domain on port 80) |

> All backend service ports are internal only. Swagger is disabled (`DEBUG=false`).

---

## Stack 3 — CQRS Lightweight (5 services)

**File:** `docker-compose.cqrs.yml`

A minimal stack for developing the chat/plot domain in isolation — no auth, payment, notification, or email services.

### Services

| Container | Role | Port |
|---|---|---|
| `api-gateway` | JWT validation · HTTP proxy | `8000` |
| `chat-command` | Chat write side | internal :8001 |
| `chat-query` | Chat read side | internal :8002 |
| `plot-command` | Plot write side | internal :8003 |
| `plot-query` | Plot read side | internal :8004 |
| `postgres` | PostgreSQL 16 + pgvector | `5432` |
| `kafka` | Apache Kafka | `29092` |
| `zookeeper` | Kafka coordination | internal |
| `kafka-init` | Creates topics, then exits | — |
| `kafka-ui` | Kafka browser UI | `8090` |

### Start

```bash
make cqrs-build   # first run
make cqrs         # subsequent starts
```

### Stop

```bash
make cqrs-down
```

---

## Database Migrations

### How migrations work

| Service | Schema | When applied |
|---|---|---|
| `auth-service` | `public` | `db-migrate` init container runs before auth-service starts |
| `chat-command` | `chat_write` | Auto-run at service startup |
| `chat-query` | `chat_read` | Auto-run at service startup |
| `plot-command` | `plot_write` | Auto-run at service startup |
| `plot-query` | `plot_read` | Auto-run at service startup |

### Apply migrations manually (dev stack)

```bash
# Auth-service — public schema
make migrate

# Or run directly inside the container
docker compose -f docker-compose.dev.yml exec auth-service \
  uv run alembic upgrade head

# CQRS service example
docker compose -f docker-compose.dev.yml exec chat-command \
  uv run alembic upgrade head
```

### Generate a new migration

```bash
# Auth-service
make migrate-new MSG="add avatar column to profiles"

# CQRS service
docker compose -f docker-compose.dev.yml exec chat-command \
  uv run alembic revision --autogenerate -m "add typing_status column"
```

### Check current migration state

```bash
docker compose -f docker-compose.dev.yml exec auth-service \
  uv run alembic current

docker compose -f docker-compose.dev.yml exec chat-command \
  uv run alembic current
```

### Roll back one migration

```bash
docker compose -f docker-compose.dev.yml exec auth-service \
  uv run alembic downgrade -1
```

### Migration file locations

```
services/
├── auth-service/alembic/versions/     # public schema
├── chat-command/alembic/versions/     # chat_write schema
├── chat-query/alembic/versions/       # chat_read schema
├── plot-command/alembic/versions/     # plot_write schema
└── plot-query/alembic/versions/       # plot_read schema
```

---

## All Commands Reference

### `make` targets

| Command | Description |
|---|---|
| **Dev stack** | |
| `make dev` | Start dev stack (all 9 services + tools) |
| `make dev-build` | Rebuild all images and start dev stack |
| `make dev-down` | Stop dev stack |
| **Production stack** | |
| `make prod` | Start production stack |
| `make prod-build` | Rebuild all images and start production stack |
| `make prod-down` | Stop production stack |
| **CQRS lightweight** | |
| `make cqrs` | Start 5-service CQRS stack |
| `make cqrs-build` | Rebuild CQRS images and start |
| `make cqrs-down` | Stop CQRS stack |
| **Logs (dev stack)** | |
| `make logs` | Follow all service logs |
| `make logs-app` | Follow frontend/nginx logs |
| `make logs-gateway` | Follow api-gateway logs |
| `make logs-auth` | Follow auth-service logs |
| `make logs-payment` | Follow payment-service logs |
| `make logs-notification` | Follow notification-service logs |
| `make logs-email` | Follow email-service logs |
| `make logs-chat-cmd` | Follow chat-command logs |
| `make logs-chat-qry` | Follow chat-query logs |
| `make logs-plot-cmd` | Follow plot-command logs |
| `make logs-plot-qry` | Follow plot-query logs |
| **Migrations (dev stack)** | |
| `make migrate` | Apply all pending auth-service Alembic migrations |
| `make migrate-new MSG='desc'` | Generate a new autogenerated migration |
| **Shell access (dev stack)** | |
| `make shell` | bash in frontend container |
| `make shell-gateway` | bash in api-gateway |
| `make shell-auth` | bash in auth-service |
| `make shell-chat-cmd` | bash in chat-command |
| `make shell-chat-qry` | bash in chat-query |
| `make shell-plot-cmd` | bash in plot-command |
| `make shell-plot-qry` | bash in plot-query |

---

## Environment Variables

### Required for all stacks

| Variable | Description | How to generate |
|---|---|---|
| `SECRET_KEY` | JWT signing secret | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `INTERNAL_SERVICE_SECRET` | Shared secret for service-to-service calls | Same as above |
| `POSTGRES_USER` | PostgreSQL username | — |
| `POSTGRES_PASSWORD` | PostgreSQL password | — |
| `POSTGRES_DB` | PostgreSQL database name | — |

### Additional for production

| Variable | Description |
|---|---|
| `REDIS_PASSWORD` | Redis password (required in prod; optional in dev) |
| `SENDGRID_API_KEY` | SendGrid key for transactional email |
| `APP_URL` | Your public URL (e.g. `https://yourapp.com`) — sets CORS allowed origins |

### Authentication (OAuth)

| Variable | Default | Description |
|---|---|---|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token lifetime |
| `GOOGLE_CLIENT_ID` | — | Google Cloud Console OAuth app ID |
| `GOOGLE_CLIENT_SECRET` | — | Google Cloud Console OAuth secret |
| `GOOGLE_REDIRECT_URI` | — | Must be in Google allowed redirect list |
| `AZURE_CLIENT_ID` | — | Azure AD app registration ID |
| `AZURE_CLIENT_SECRET` | — | Azure AD app secret |
| `AZURE_TENANT_ID` | `common` | Azure AD tenant |
| `NEXT_PUBLIC_AUTH_GOOGLE_ENABLED` | `false` | Show Google SSO button in frontend |
| `NEXT_PUBLIC_AUTH_AZURE_ENABLED` | `false` | Show Azure SSO button in frontend |

### Database & cache

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |
| `REDIS_DB` | `0` | Redis database index |
| `POSTGRES_PORT` | `5432` | Exposed host port for PostgreSQL |

### External services

| Variable | Description |
|---|---|
| `FROM_EMAIL` | Sender address (default: `noreply@yourapp.com`) |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob Storage (file uploads) |
| `AZURE_STORAGE_CONTAINER` | Blob container name (default: `uploads`) |

### Frontend

| Variable | Default | Description |
|---|---|---|
| `BACKEND_INTERNAL_URL` | `http://api-gateway:8000` | Next.js SSR → API Gateway (server-side, not public) |
| `NEXT_PUBLIC_API_URL` | *(relative `/api`)* | API base URL baked into browser bundle at build time |

> `NEXT_PUBLIC_*` variables are inlined at `bun build` time. Changing them requires a frontend rebuild.

---

## Architecture Overview

```
Browser
  │  HTTP
  ▼
Nginx :80
  │  /api/auth/*  → api-gateway (rate-limited)
  │  /api/*       → api-gateway
  │  /*           → Next.js SSR :3000 (loopback, same container)
  ▼
API Gateway :8000
  │
  │  Sets on every request:
  │    x-user-id, x-user-role, x-user-email  (from JWT)
  │    x-internal-secret                      (service auth)
  │
  ├─► auth-service :8010       ◄── public schema (Alembic via db-migrate)
  │     auth, OAuth, RBAC,          depends on: postgres, redis, email-service
  │     admin, audit log
  │
  ├─► payment-service :8011    (stateless — no DB)
  │
  ├─► notification-service :8012
  │     └─► email-service :8013  (x-internal-secret validated)
  │
  ├─(write)─► chat-command :8001 ──► chat_write schema
  │               │ Kafka: chat.events
  ├─(read) ──► chat-query  :8002 ──► chat_read  schema
  │               (Kafka consumer — projects events into read model)
  │
  ├─(write)─► plot-command :8003 ──► plot_write schema
  │               │ Kafka: plot.events
  └─(read) ──► plot-query  :8004 ──► plot_read  schema
                  (Kafka consumer — projects events into read model)

PostgreSQL :5432   5 schemas: public · chat_write · chat_read · plot_write · plot_read
Redis :6379        session cache (api-gateway) · rate limiting
Apache Kafka       topics: chat.events · chat.bulk.commands · plot.events · plot.bulk.commands
```

### Security model

| Concern | How it's handled |
|---|---|
| Browser → api-gateway | JWT in httpOnly cookie validated by `SessionValidationMiddleware` |
| Session validation | Redis cache fast path → auth-service HTTP fallback (graceful degradation) |
| Gateway → downstream services | `x-user-id`, `x-user-role`, `x-user-email` headers set from JWT payload |
| Service-to-service calls | `x-internal-secret` header verified by `InternalAuthMiddleware` on every internal service |
| No JWT re-validation | Downstream services trust gateway headers — zero token decoding outside api-gateway |

### Request routing

| Path prefix | Methods | Routes to |
|---|---|---|
| `/api/auth/*` | ALL | auth-service :8010 |
| `/api/profile/*` | ALL | auth-service :8010 |
| `/api/admin/*` | ALL | auth-service :8010 |
| `/api/payments/*` | ALL | payment-service :8011 |
| `/api/notifications/*` | ALL | notification-service :8012 |
| `/api/v1/chat/messages` | `POST` | chat-command :8001 |
| `/api/v1/chat/messages/bulk` | `POST` | chat-command :8001 |
| `/api/v1/chat/messages/{id}` | `DELETE` | chat-command :8001 |
| `/api/v1/chat/sessions` | `GET` | chat-query :8002 |
| `/api/v1/chat/sessions/{id}/messages` | `GET` | chat-query :8002 |
| `/api/v1/plots` | `POST` | plot-command :8003 |
| `/api/v1/plots/bulk` | `POST` | plot-command :8003 |
| `/api/v1/plots/{id}` | `PUT` / `DELETE` | plot-command :8003 |
| `/api/v1/plots` | `GET` | plot-query :8004 |
| `/api/v1/plots/{id}` | `GET` | plot-query :8004 |
| `/api/v1/plots/search` | `GET` | plot-query :8004 |

### Database schemas

| Schema | Owner | Contents |
|---|---|---|
| `public` | auth-service | users, sessions, roles, permissions, audit_logs, uploads |
| `chat_write` | chat-command | source-of-truth messages and sessions |
| `chat_read` | chat-query | denormalised projection (last_message_preview, message_count) |
| `plot_write` | plot-command | source-of-truth plots with versioning |
| `plot_read` | plot-query | denormalised projection (element_count) |

### Startup order

```
1. postgres (healthy)
      │
      ├─ db-migrate ──► alembic upgrade head (public schema) ──► exits
      │
      └─ kafka-init ──► creates 4 topics ──► exits
             │
2.    ├─ auth-service, email-service, payment-service, notification-service
      │
      ├─ chat-command, chat-query, plot-command, plot-query
      │       each auto-runs: alembic upgrade head (own schema)
      │
3.    └─ api-gateway
             │
4.           └─ app (Next.js + Nginx)
```

---

## Kubernetes Deployment

All manifests are in `k8s/`. Deploy to any cluster with `kubectl`.

```bash
# 1. Namespace and config
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml       # fill in base64-encoded values first

# 2. Infrastructure (wait for each to be ready)
kubectl apply -f k8s/infra/zookeeper.yaml
kubectl rollout status statefulset/zookeeper -n plots-system

kubectl apply -f k8s/infra/kafka.yaml
kubectl rollout status statefulset/kafka -n plots-system

kubectl apply -f k8s/infra/postgres.yaml
kubectl rollout status statefulset/postgres -n plots-system

# 3. Create Kafka topics (once)
kubectl exec -n plots-system kafka-0 -- bash < kafka/create-topics.sh

# 4. Deploy all microservices
kubectl apply -f k8s/services/
kubectl rollout status deployment -n plots-system

# 5. Ingress and autoscaling
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa/
```

### Build and push service images

```bash
REGISTRY=<your-registry>
for svc in api-gateway auth-service payment-service notification-service email-service \
           chat-command chat-query plot-command plot-query; do
  docker build -t $REGISTRY/plots/$svc:latest services/$svc/
  docker push $REGISTRY/plots/$svc:latest
done

# Frontend
docker build -t $REGISTRY/plots/frontend:latest \
  -f docker/prod/Dockerfile.frontend .
docker push $REGISTRY/plots/frontend:latest
```

### HPA targets

| Service | Min | Max | CPU trigger | Memory trigger |
|---|---|---|---|---|
| api-gateway | 2 | 10 | 70% | 80% |
| auth-service | 2 | 10 | 70% | 80% |
| chat-command | 3 | 20 | 70% | 80% |
| chat-query | 3 | 30 | 60% | 75% |
| plot-command | 3 | 20 | 70% | 80% |
| plot-query | 3 | 30 | 60% | 75% |
