# Plots

Full-stack monorepo: **FastAPI** backend · **Next.js 16** frontend · **CQRS microservices** with Kafka · deployable on Docker or Kubernetes.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Stack 1 — Monolith Development](#stack-1--monolith-development)
- [Stack 2 — Monolith Production](#stack-2--monolith-production)
- [Stack 3 — CQRS Microservices](#stack-3--cqrs-microservices)
- [Running All Services — Quick Reference](#running-all-services--quick-reference)
- [All Commands Reference](#all-commands-reference)
- [Database Migrations](#database-migrations)
- [Environment Variables](#environment-variables)
- [Architecture Overview](#architecture-overview)
- [Kubernetes Deployment](#kubernetes-deployment)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · FastAPI 0.115 · SQLAlchemy 2.0 async · Alembic · Pydantic v2 |
| Frontend | Next.js 16.2 · React 19 · TypeScript 5 · Tailwind CSS v4 · shadcn/ui · Bun |
| Auth | JWT (httpOnly cookies) · Google OAuth 2.0 · Azure AD |
| Database | PostgreSQL 16 + pgvector · Redis 7 |
| Task Queue | Celery 5 + Redis broker |
| CQRS / Events | Apache Kafka (aiokafka) · 5 independent FastAPI microservices |
| Infrastructure | Docker Compose · Kubernetes · Nginx · Supervisord |
| Package Managers | uv (Python) · Bun (JavaScript) |

---

## Project Structure

```
plots/
├── backend/                    # FastAPI monolith
│   ├── app/
│   │   ├── auth/               # Auth, OAuth, RBAC (roles + permissions)
│   │   ├── admin/              # Admin user management
│   │   ├── audit/              # Audit log
│   │   ├── plot/               # Plot sheets (monolith CRUD)
│   │   ├── notifications/      # Email (SendGrid) + SMS (Twilio)
│   │   ├── uploads/            # Azure Blob Storage
│   │   ├── payments/           # Stripe placeholder
│   │   ├── worker/             # Celery tasks
│   │   ├── config.py           # Pydantic Settings
│   │   ├── database.py         # Async SQLAlchemy engine
│   │   └── main.py             # FastAPI app factory
│   ├── alembic/                # Database migrations
│   ├── scripts/                # seed.py
│   └── pyproject.toml          # Python deps (managed by uv)
├── frontend/                   # Next.js 16 App Router
│   └── src/
│       ├── app/                # Pages (login, dashboard, chat, sheets…)
│       ├── components/         # shadcn/ui primitives + AI chat components
│       ├── context/            # Auth context
│       └── lib/services/       # API helpers
├── services/                   # CQRS microservices
│   ├── api-gateway/            # JWT validation + HTTP proxy (:8000)
│   ├── chat-command/           # Chat write side (:8001)
│   ├── chat-query/             # Chat read side + Kafka consumer (:8002)
│   ├── plot-command/           # Plot write side (:8003)
│   └── plot-query/             # Plot read side + Kafka consumer (:8004)
├── docker/
│   ├── dev/Dockerfile          # Dev image (hot-reload, Supervisord)
│   ├── prod/Dockerfile         # Prod image (Gunicorn + Next.js standalone)
│   ├── prod/Dockerfile.worker  # Celery worker image
│   ├── nginx/nginx.conf        # Nginx reverse proxy config
│   ├── supervisord.dev.conf    # Supervisord: uvicorn + bun dev + nginx
│   └── supervisord.prod.conf   # Supervisord: gunicorn + node server.js + nginx
├── k8s/                        # Kubernetes manifests
│   ├── infra/                  # StatefulSets: Kafka, Zookeeper, PostgreSQL
│   ├── services/               # Deployments for each microservice
│   └── hpa/                    # HorizontalPodAutoscaler configs
├── kafka/                      # Topic definitions + create-topics.sh
├── scripts/
│   └── init-schemas.sql        # Creates CQRS PostgreSQL schemas on first start
├── docs/
│   └── index.html              # Full technical documentation (open in browser)
├── docker-compose.yml          # Production monolith stack
├── docker-compose.dev.yml      # Development monolith stack (hot-reload)
├── docker-compose.cqrs.yml     # CQRS microservices stack (local dev)
├── Makefile                    # Make targets (Linux / macOS)
├── dev.ps1                     # PowerShell equivalent (Windows)
└── .env.example                # Environment template
```

---

## Prerequisites

- **Docker Desktop** ≥ 26.0 with Docker Compose v2 (`docker compose version`)
- **Git**

No local Python or Node.js installation required — everything runs inside Docker.

---

## Environment Setup

```bash
# 1. Clone the repo
git clone <repository-url>
cd plots

# 2. Create your .env from the template
cp .env.example .env
```

Open `.env` and set at minimum:

```env
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
POSTGRES_USER=mvp_user
POSTGRES_PASSWORD=<strong password>
POSTGRES_DB=mvp_db
```

All other variables have sensible defaults for local development.

---

## Stack 1 — Monolith Development

The development stack runs all services with **hot-reload** — source code is volume-mounted, so saving a file in `backend/` or `frontend/` takes effect immediately without rebuilding.

### Services started

| Container | Role | Port |
|---|---|---|
| `mvp-app-dev` | Nginx → FastAPI (uvicorn `--reload`) + Next.js (`bun dev`) | `80` |
| `mvp-worker-dev` | Celery worker (autoreload) | — |
| `mvp-postgres-dev` | PostgreSQL 16 + pgvector | `5432` |
| `mvp-redis-dev` | Redis 7 | `6379` |
| `mvp-pgadmin-dev` | pgAdmin 4 | `5050` |
| `mvp-redis-gui-dev` | Redis Commander | `8081` |

### Start

```bash
# Linux / macOS
make dev-build      # first run — builds the image
make dev            # subsequent starts

# Windows (PowerShell)
.\dev.ps1 dev-build
.\dev.ps1 dev
```

### Apply migrations (first run only)

```bash
make migrate        # Linux / macOS
.\dev.ps1 migrate   # Windows
```

### Stop

```bash
make dev-down
.\dev.ps1 dev-down
```

### Service URLs

| Service | URL | Default credentials |
|---|---|---|
| Application | http://localhost | — |
| FastAPI Swagger UI | http://localhost/docs | — |
| FastAPI ReDoc | http://localhost/redoc | — |
| pgAdmin | http://localhost:5050 | `admin@mvp.dev` / `admin` |
| Redis Commander | http://localhost:8081 | `admin` / `admin` |
| PostgreSQL (direct) | `localhost:5432` | see `.env` |
| Redis (direct) | `localhost:6379` | see `.env` |

---

## Stack 2 — Monolith Production

The production stack uses a **multi-stage Docker build**: Next.js is compiled to a standalone server bundle, Python dependencies are pre-installed into a venv, and Gunicorn runs the FastAPI app with uvicorn workers.

### Services started

| Container | Role | Port |
|---|---|---|
| `mvp-app` | Nginx → Gunicorn (uvicorn workers) + Next.js standalone | `80` |
| `mvp-worker` | Celery worker (4 concurrent) | — |
| `mvp-postgres` | PostgreSQL 16 + pgvector | *(internal only)* |
| `mvp-redis` | Redis 7 | *(internal only)* |

### Start

```bash
# Linux / macOS
make prod-build     # first run — builds multi-stage image (~3–5 min)
make prod           # subsequent starts

# Windows (PowerShell)
.\dev.ps1 prod-build
.\dev.ps1 prod
```

### Stop

```bash
make prod-down
.\dev.ps1 prod-down
```

### Service URLs

| Service | URL |
|---|---|
| Application | http://localhost |
| FastAPI Swagger UI | http://localhost/docs *(disabled in production — set `DEBUG=true` to enable)* |

> PostgreSQL and Redis are not exposed externally in the production stack.

---

## Stack 3 — CQRS Microservices

The CQRS stack runs **5 FastAPI microservices** behind an API Gateway, with Apache Kafka for event streaming. Write operations (POST/PUT/DELETE) go to command services; read operations (GET) go to query services.

### Services started

| Container | Role | Port |
|---|---|---|
| `api-gateway` | JWT validation · HTTP proxy to command/query services | `8000` |
| `chat-command` | Chat write side — persists messages, publishes Kafka events | *(internal :8001)* |
| `chat-query` | Chat read side — serves paginated history from projections | *(internal :8002)* |
| `plot-command` | Plot write side — persists plots, publishes Kafka events | *(internal :8003)* |
| `plot-query` | Plot read side — serves plots from denormalised read model | *(internal :8004)* |
| `kafka` | Apache Kafka broker (Confluent 7.6.0) | `9092` |
| `zookeeper` | Zookeeper (Kafka coordination) | *(internal :2181)* |
| `kafka-init` | Creates 4 Kafka topics, then exits | — |
| `kafka-ui` | Kafka UI — browse topics, messages, consumer groups | `8090` |
| `postgres` | PostgreSQL 16 + pgvector (shared with CQRS schemas) | `5432` |

### Start

```bash
# Linux / macOS
make cqrs-build     # first run — builds all 5 service images
make cqrs           # subsequent starts

# Windows (PowerShell)
.\dev.ps1 cqrs-build
.\dev.ps1 cqrs
```

### What happens on first start

1. **PostgreSQL** starts and runs `scripts/init-schemas.sql` automatically, creating:
   `chat_write`, `chat_read`, `plot_write`, `plot_read` schemas
2. **Zookeeper** starts, then **Kafka** broker connects to it
3. **kafka-init** waits for Kafka to be healthy, then creates the 4 topics:
   - `chat.events` (4 partitions) · `chat.bulk.commands` (2 partitions)
   - `plot.events` (4 partitions) · `plot.bulk.commands` (2 partitions)
   — then exits with code 0
4. **Microservices** start, each runs `Base.metadata.create_all` to create their tables
5. **chat-query** and **plot-query** start their Kafka consumer background tasks

### Stop

```bash
make cqrs-down
.\dev.ps1 cqrs-down
```

### Service URLs

| Service | URL | Notes |
|---|---|---|
| API Gateway | http://localhost:8000 | All requests enter here |
| API Gateway Swagger | http://localhost:8000/docs | Debug mode only |
| Kafka UI | http://localhost:8090 | Browse topics and messages |
| PostgreSQL | `localhost:5432` | Schemas: `chat_write`, `chat_read`, `plot_write`, `plot_read` |
| Kafka | `localhost:9092` | Direct broker access |

### Routing at the API Gateway

| Path | Method | Routes to |
|---|---|---|
| `/api/v1/chat/messages` | POST | chat-command :8001 |
| `/api/v1/chat/messages/bulk` | POST | chat-command :8001 |
| `/api/v1/chat/messages/{id}` | DELETE | chat-command :8001 |
| `/api/v1/chat/sessions` | GET | chat-query :8002 |
| `/api/v1/chat/sessions/{id}/messages` | GET | chat-query :8002 |
| `/api/v1/plots` | POST | plot-command :8003 |
| `/api/v1/plots/bulk` | POST | plot-command :8003 |
| `/api/v1/plots/{id}` | PUT / DELETE | plot-command :8003 |
| `/api/v1/plots` | GET | plot-query :8004 |
| `/api/v1/plots/search` | GET | plot-query :8004 |
| `/api/v1/plots/{id}` | GET | plot-query :8004 |

### Test a bulk write

```bash
curl -X POST http://localhost:8000/api/v1/plots/bulk \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"plots":[
    {"name":"Plot A","elements":{"blocks":[],"walls":[]}},
    {"name":"Plot B","elements":{"blocks":[],"penLines":[]}}
  ]}'
# → {"accepted":2,"ids":["<uuid>","<uuid>"]}
```

> **Port conflict note:** Both the monolith dev stack and the CQRS stack bind PostgreSQL on `:5432`. Run them one at a time, or change `POSTGRES_PORT` in `.env` before starting the second stack.

---

## Running All Services — Quick Reference

```
                      ┌──────────────────────────────────────────┐
                      │          MONOLITH DEV STACK              │
                      │  make dev-build  →  make migrate         │
                      ├──────────────┬───────────────────────────┤
                      │ localhost    │ App (FastAPI + Next.js)   │
                      │ localhost/docs│ Swagger UI               │
                      │ :5050        │ pgAdmin                   │
                      │ :8081        │ Redis Commander           │
                      └──────────────┴───────────────────────────┘

                      ┌──────────────────────────────────────────┐
                      │         CQRS MICROSERVICES STACK         │
                      │         make cqrs-build                  │
                      ├──────────────┬───────────────────────────┤
                      │ :8000        │ API Gateway               │
                      │ :8090        │ Kafka UI                  │
                      │ :9092        │ Kafka (direct)            │
                      │ :5432        │ PostgreSQL (CQRS schemas) │
                      └──────────────┴───────────────────────────┘
```

---

## All Commands Reference

### Linux / macOS (`make`)

| Command | Stack | Description |
|---|---|---|
| `make dev` | Monolith dev | Start dev stack |
| `make dev-build` | Monolith dev | Build image and start dev stack |
| `make dev-down` | Monolith dev | Stop dev stack |
| `make prod` | Monolith prod | Start production stack |
| `make prod-build` | Monolith prod | Build image and start production stack |
| `make prod-down` | Monolith prod | Stop production stack |
| `make cqrs` | CQRS | Start CQRS stack |
| `make cqrs-build` | CQRS | Build all service images and start |
| `make cqrs-down` | CQRS | Stop CQRS stack |
| `make logs` | Monolith dev | Follow app container logs |
| `make logs-worker` | Monolith dev | Follow Celery worker logs |
| `make logs-gateway` | CQRS | Follow api-gateway logs |
| `make logs-chat-cmd` | CQRS | Follow chat-command logs |
| `make logs-chat-qry` | CQRS | Follow chat-query logs |
| `make logs-plot-cmd` | CQRS | Follow plot-command logs |
| `make logs-plot-qry` | CQRS | Follow plot-query logs |
| `make migrate` | Monolith dev | Apply all Alembic migrations |
| `make migrate-new MSG='desc'` | Monolith dev | Generate a new migration |
| `make seed` | Monolith dev | Run the database seeder |
| `make shell` | Monolith dev | Open bash in app container |
| `make shell-gateway` | CQRS | Open bash in api-gateway |

### Windows (`.\dev.ps1`)

Replace `make <cmd>` with `.\dev.ps1 <cmd>`. For `migrate-new`, pass the message with `-Msg`:

```powershell
.\dev.ps1 migrate-new -Msg "add avatar column"
```

---

## Database Migrations

Alembic migrations live in `backend/alembic/`. They apply to the monolith `public` schema. CQRS microservices manage their own tables via SQLAlchemy `create_all` on startup — no separate migration step needed.

```bash
# Apply all pending migrations
make migrate

# Generate a new migration after changing a model
make migrate-new MSG="add avatar column to profiles"

# Roll back one migration
docker compose -f docker-compose.dev.yml exec app \
  sh -c "cd /app/backend && .venv/bin/alembic downgrade -1"

# Check current migration state
docker compose -f docker-compose.dev.yml exec app \
  sh -c "cd /app/backend && .venv/bin/alembic current"
```

---

## Environment Variables

Copy `.env.example` to `.env`. The table below covers the most important variables.

### Required

| Variable | Description |
|---|---|
| `SECRET_KEY` | JWT signing secret — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_DB` | PostgreSQL database name |

### Authentication

| Variable | Default | Description |
|---|---|---|
| `AUTH_EMAIL_ENABLED` | `true` | Enable email / password login |
| `AUTH_GOOGLE_ENABLED` | `false` | Enable Google OAuth 2.0 |
| `AUTH_AZURE_ENABLED` | `false` | Enable Azure AD OAuth |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token lifetime |
| `GOOGLE_CLIENT_ID` | — | Google Cloud Console app ID |
| `GOOGLE_CLIENT_SECRET` | — | Google Cloud Console app secret |
| `GOOGLE_OAUTH_REDIRECT_URI` | `.../api/auth/google/callback` | Must be in Google allowed list |
| `AZURE_CLIENT_ID` | — | Azure AD app registration ID |
| `AZURE_CLIENT_SECRET` | — | Azure AD app secret |
| `AZURE_TENANT_ID` | `common` | Azure AD tenant |

### Database & Cache

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...@localhost:5432/mvp_db` | Async PostgreSQL URL |
| `DB_POOL_SIZE` | `20` | SQLAlchemy pool size |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `REDIS_PASSWORD` | *(empty)* | Leave empty to disable Redis auth |

### External Services

| Variable | Description |
|---|---|
| `SENDGRID_API_KEY` | SendGrid key for transactional email |
| `FROM_EMAIL` | Sender address (default: `noreply@example.com`) |
| `TWILIO_ACCOUNT_SID` | Twilio account SID for SMS |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_FROM_NUMBER` | Twilio sender number |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob Storage connection string |
| `AZURE_STORAGE_CONTAINER` | Blob container name (default: `uploads`) |

### Frontend

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | *(relative `/api`)* | API base URL baked into the browser bundle at build time |
| `NEXT_PUBLIC_AUTH_GOOGLE_ENABLED` | `false` | Show Google SSO button |
| `NEXT_PUBLIC_AUTH_AZURE_ENABLED` | `false` | Show Azure SSO button |
| `BACKEND_INTERNAL_URL` | `http://localhost:8000` | Server-side Next.js → FastAPI URL (not exposed to browser) |

> `NEXT_PUBLIC_*` variables are inlined at `bun build` time. Changing them requires a frontend rebuild.

---

## Architecture Overview

The project runs as two independently deployable stacks.

### Monolith Stack

```
Browser
  │  HTTP
  ▼
Nginx :80
  ├─► FastAPI :8000   (uvicorn / gunicorn)
  │     auth · plot · admin · uploads · notifications · payments
  └─► Next.js :3000   (bun dev / node server.js)

PostgreSQL :5432 (public schema)
Redis :6379          (Celery broker + result backend)
Celery Worker        (email, async tasks)
```

### CQRS Microservices Stack

```
Browser
  │  HTTP
  ▼
API Gateway :8000
  ├─(write)─► chat-command :8001 ──► chat_write schema
  │               │ publish
  ├─(write)─► plot-command :8003 ──► plot_write schema
  │               │ publish
  │           Apache Kafka
  │               │ subscribe (projection consumers)
  ├─(read)──► chat-query  :8002 ──► chat_read  schema
  └─(read)──► plot-query  :8004 ──► plot_read  schema

PostgreSQL :5432  (4 schemas: chat_write, chat_read, plot_write, plot_read)
Kafka topics: chat.events · chat.bulk.commands · plot.events · plot.bulk.commands
```

Command services write to PostgreSQL and publish events to Kafka.
Query services project those events into optimised read models asynchronously.
Bulk operations return `202 Accepted` immediately — projection happens in the background.

### Database Schemas

| Schema | Owner | Purpose |
|---|---|---|
| `public` | Monolith | Users, sessions, roles, permissions, audit, sheets |
| `chat_write` | chat-command | Source-of-truth chat messages |
| `chat_read` | chat-query | Denormalised projection (adds `last_message_preview`, `message_count`) |
| `plot_write` | plot-command | Source-of-truth plots (with `version`) |
| `plot_read` | plot-query | Denormalised projection (adds `element_count`) |

---

## Kubernetes Deployment

All manifests are in `k8s/`. Deploy to any cluster with `kubectl`.

```bash
# 1. Create namespace and config
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml       # fill in base64 values first

# 2. Infrastructure (order matters — wait for each to be ready)
kubectl apply -f k8s/infra/zookeeper.yaml
kubectl rollout status statefulset/zookeeper -n plots-system

kubectl apply -f k8s/infra/kafka.yaml
kubectl rollout status statefulset/kafka -n plots-system

kubectl apply -f k8s/infra/postgres.yaml
kubectl rollout status statefulset/postgres -n plots-system

# 3. Create Kafka topics (once)
kubectl exec -n plots-system kafka-0 -- bash < kafka/create-topics.sh

# 4. Deploy microservices
kubectl apply -f k8s/services/
kubectl rollout status deployment -n plots-system

# 5. Ingress and autoscaling
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa/
```

### Build and push service images

```bash
REGISTRY=<your-registry>
for svc in api-gateway chat-command chat-query plot-command plot-query; do
  docker build -t $REGISTRY/plots/$svc:latest services/$svc/
  docker push $REGISTRY/plots/$svc:latest
done
```

### HPA targets

| Service | Min | Max | CPU trigger | Mem trigger |
|---|---|---|---|---|
| chat-command | 3 | 20 | 70% | 80% |
| chat-query | 3 | 30 | 60% | 75% |
| plot-command | 3 | 20 | 70% | 80% |
| plot-query | 3 | 30 | 60% | 75% |

---

## Full Technical Documentation

Open [`docs/index.html`](docs/index.html) in a browser for complete API reference, model definitions, Kafka topic details, and database schema documentation.
