# MVP in 4 Weeks

A full-stack monorepo for shipping production-ready MVPs fast.

- **Backend** — FastAPI (Python 3.12), async SQLAlchemy, JWT + OAuth, Celery workers
- **Frontend** — Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui
- **Infra** — Single Docker container (Nginx → FastAPI + Next.js), PostgreSQL 16, Redis 7

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Starting the Container](#starting-the-container)
- [Database Migrations](#database-migrations)
- [Seeding the Database](#seeding-the-database)
- [Running Scripts](#running-scripts)
- [Makefile Reference](#makefile-reference)
- [Local Development (without Docker)](#local-development-without-docker)
- [Production Deployment](#production-deployment)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Adding a New Backend Module](#adding-a-new-backend-module)
- [Google OAuth2 Token Setup](#google-oauth2-token-setup)
- [CI/CD](#cicd)

---

## Tech Stack

### Backend (`backend/`)

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115+ |
| Language | Python 3.12 |
| Package manager | uv |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 + pgVector |
| Migrations | Alembic |
| Cache / Queue | Redis 7 + Celery |
| Auth | JWT (httpOnly cookies) + Google OAuth + Azure AD OAuth |
| Email | SendGrid |
| SMS | Twilio |
| File storage | Azure Blob Storage |
| Validation | Pydantic v2 |
| Production server | Gunicorn + UvicornWorker |

### Frontend (`frontend/`)

| Layer | Technology |
|---|---|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript 5 |
| Package manager | Bun |
| UI components | shadcn/ui (Radix UI) |
| Styling | Tailwind CSS v4 |
| Charts | Recharts |
| Icons | Lucide React |

### Infrastructure

| Component | Technology |
|---|---|
| Container | Single Docker image — Nginx + FastAPI + Next.js |
| Process manager | Supervisord |
| Reverse proxy | Nginx (`:80`) |
| Dev hot-reload | uvicorn `--reload` + Next.js HMR |
| CI | GitHub Actions |

---

## Project Structure

```
MVP_in_4_weeks/
├── backend/                        # FastAPI application
│   ├── app/
│   │   ├── auth/                   # JWT, sessions, OAuth (Google & Azure)
│   │   ├── admin/                  # Admin user management
│   │   ├── audit/                  # Audit log
│   │   ├── common/                 # Middleware, exceptions, pagination
│   │   ├── config/                 # Pydantic settings (reads root .env)
│   │   ├── notifications/          # SendGrid email + Twilio SMS
│   │   ├── payments/               # Stripe (placeholder)
│   │   ├── uploads/                # Azure Blob Storage
│   │   ├── worker/                 # Celery app + tasks
│   │   ├── database.py             # Async SQLAlchemy engine
│   │   └── main.py                 # FastAPI app factory
│   ├── alembic/                    # Migration scripts
│   ├── scripts/
│   │   └── seed.py                 # DB seeder (roles, permissions, users)
│   ├── tests/                      # pytest test suite
│   ├── pyproject.toml
│   └── uv.lock
│
├── frontend/                       # Next.js application
│   └── src/
│       ├── app/                    # App Router pages
│       │   ├── dashboard/          # Protected dashboard
│       │   ├── login/
│       │   ├── signup/
│       │   ├── forgot-password/
│       │   ├── reset-password/
│       │   ├── unauthorized/       # 403 page
│       │   └── not-found.tsx       # 404 page
│       ├── components/             # React components + shadcn/ui
│       ├── hooks/
│       └── lib/
│
├── docker/                         # All Docker configuration
│   ├── prod/
│   │   ├── Dockerfile              # Multi-stage: Next.js build → Python deps → runtime
│   │   └── Dockerfile.worker       # Celery worker image
│   ├── dev/
│   │   └── Dockerfile              # Dev image (hot-reload, volume-mounted)
│   ├── nginx/
│   │   └── nginx.conf              # /api/* → FastAPI :8000, /* → Next.js :3000
│   ├── supervisord.prod.conf       # Gunicorn + Next.js standalone + Nginx
│   └── supervisord.dev.conf        # uvicorn --reload + bun next dev + Nginx
│
├── .env                            # Shared secrets (git-ignored)
├── .env.example                    # Template — copy to .env
├── docker-compose.yml              # Production stack
├── docker-compose.dev.yml          # Dev stack (+ pgAdmin, Redis Commander)
├── Makefile                        # Shortcut commands
└── .github/workflows/ci.yml        # GitHub Actions
```

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Docker + Docker Compose | Latest | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Python | 3.12+ | [python.org](https://www.python.org/) *(local dev only)* |
| uv | Latest | `pip install uv` *(local dev only)* |
| Bun | Latest | [bun.sh](https://bun.sh/) *(local dev only)* |

---

## Quick Start

```bash
# 1. Clone
git clone <repo-url>
cd MVP_in_4_weeks

# 2. Configure environment
cp .env.example .env        # Linux / Mac
copy .env.example .env      # Windows
# Edit .env — fill in SECRET_KEY and any OAuth / API keys you need

# 3. Build and start dev stack
make dev-build              # Linux / Mac
.\dev.ps1 dev-build         # Windows PowerShell

# 4. Run database migrations (first time only)
make migrate                # Linux / Mac
.\dev.ps1 migrate           # Windows PowerShell

# 5. Seed the database with roles, permissions and sample users (optional)
make seed                   # Linux / Mac
.\dev.ps1 seed              # Windows PowerShell
```

The app is now running at **http://localhost**.

---

## Environment Variables

All variables live in a single root `.env` shared by both backend and frontend. Copy `.env.example` and fill in your values — the table below explains every key.

| Variable | Description | Default |
|---|---|---|
| `APP_ENV` | `development` / `production` / `testing` | `development` |
| `SECRET_KEY` | JWT signing key — **change this** | *(required)* |
| `DEBUG` | Enable debug mode | `true` |
| `DATABASE_URL` | Async PostgreSQL connection URL | `postgresql+asyncpg://...` |
| `DB_POOL_SIZE` | SQLAlchemy connection pool size | `20` |
| `POSTGRES_USER` | PostgreSQL username (Docker) | `mvp_user` |
| `POSTGRES_PASSWORD` | PostgreSQL password (Docker) | `mvp_pass` |
| `POSTGRES_DB` | PostgreSQL database name (Docker) | `mvp_db` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `REDIS_PASSWORD` | Redis password (leave empty to disable) | *(empty)* |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token lifetime | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | JWT refresh token lifetime | `7` |
| `CORS_ORIGINS` | Allowed origins (JSON array) | `["http://localhost:3000","http://localhost"]` |
| `FRONTEND_URL` | Used in email links and OAuth redirects | `http://localhost:3000` |
| `SENDGRID_API_KEY` | SendGrid API key | — |
| `FROM_EMAIL` | Sender address for emails | `noreply@example.com` |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | — |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | — |
| `TWILIO_FROM_NUMBER` | Twilio phone number | — |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | — |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | — |
| `GOOGLE_OAUTH_REDIRECT_URI` | Google OAuth callback URL | `http://localhost:8000/api/auth/google/callback` |
| `AZURE_CLIENT_ID` | Azure AD application (client) ID | — |
| `AZURE_CLIENT_SECRET` | Azure AD client secret | — |
| `AZURE_TENANT_ID` | Azure AD tenant ID | `common` |
| `AZURE_OAUTH_REDIRECT_URI` | Azure OAuth callback URL | `http://localhost:8000/api/auth/azure/callback` |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob Storage connection string | — |
| `AZURE_STORAGE_CONTAINER` | Blob container name | `uploads` |
| `RATE_LIMIT_LOGIN` | Login rate limit | `5/minute` |
| `RATE_LIMIT_REGISTER` | Register rate limit | `3/minute` |
| `NEXT_PUBLIC_API_URL` | API base URL exposed to the browser | `http://localhost/api` |

> **`NEXT_PUBLIC_*` variables** are inlined into the browser JS bundle at Next.js build time. Change them and rebuild the image for the new value to take effect.

Generate a strong `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Starting the Container

### Development (hot-reload for both backend and frontend)

```bash
make dev-build   # first run — builds the dev image (~3–5 min)
make dev         # subsequent starts (image already built)
```

| Service | URL | Credentials |
|---|---|---|
| App (Nginx) | http://localhost | — |
| FastAPI Swagger | http://localhost/docs | — |
| FastAPI ReDoc | http://localhost/redoc | — |
| pgAdmin | http://localhost:5050 | `admin@mvp.dev` / `admin` |
| Redis Commander | http://localhost:8081 | `admin` / `admin` |

Inside the dev container:

- **FastAPI** runs on `127.0.0.1:8000` with `uvicorn --reload` — saves to `backend/` trigger instant reload.
- **Next.js** runs on `127.0.0.1:3000` with HMR — saves to `frontend/src/` hot-swap in the browser.
- **Nginx** on `:80` reverse-proxies both.

### Stop the dev stack

```bash
make dev-down
```

### Production

```bash
make prod-build  # build the optimised single-container image
make prod        # start production stack
make prod-down   # stop production stack
```

The production image is a three-stage build:

| Stage | What happens |
|---|---|
| `frontend-builder` | `bun build` → Next.js standalone output |
| `backend-builder` | `uv sync --no-dev` → Python venv |
| `final` | Node.js + Nginx + Supervisord + both app dirs |

---

## Database Migrations

Migrations use **Alembic** and run inside the running `app` container.

### Apply all pending migrations

```bash
# Linux / Mac
make migrate

# Windows PowerShell
.\dev.ps1 migrate
```

Equivalent to `alembic upgrade head`.

### Generate a new migration after changing models

After you edit SQLAlchemy models, autogenerate a migration file and immediately apply it:

```bash
# Linux / Mac
make migrate-new MSG="add users table"

# Windows PowerShell
.\dev.ps1 migrate-new -Msg "add users table"
```

This runs `alembic revision --autogenerate -m "<MSG>"` inside the container and writes a new file to `backend/alembic/versions/`. The file is created on the host volume automatically — review it, then run `make migrate` / `.\dev.ps1 migrate` to apply.

### Other Alembic commands (run inside `make shell` / `.\dev.ps1 shell`)

```bash
# Check current revision
.venv/bin/alembic current

# View migration history
.venv/bin/alembic history --verbose

# Roll back one migration
.venv/bin/alembic downgrade -1

# Roll back to a specific revision
.venv/bin/alembic downgrade <revision-id>

# Roll back all migrations
.venv/bin/alembic downgrade base
```

---

## Seeding the Database

The seeder creates roles, permissions, and starter user accounts. It is safe to run multiple times (idempotent).

```bash
make seed
```

### Default seed accounts

| Role | Email | Password |
|---|---|---|
| Superadmin | superadmin@example.com | `superadmin123` |
| Admin | admin@example.com | `admin1234` |
| Member | member@example.com | `member123` |

> **Change these credentials before sharing the environment with anyone.**

---

## Running Scripts

All scripts run inside the running `app` container. Open a shell first:

```bash
make shell   # opens bash in mvp-app-dev
```

Then run any script:

```bash
# Seed
cd /app/backend && .venv/bin/python scripts/seed.py

# Custom one-off script
cd /app/backend && .venv/bin/python scripts/your_script.py
```

Or run a one-off command without entering the shell:

```bash
docker compose -f docker-compose.dev.yml exec app \
  sh -c "cd /app/backend && .venv/bin/python scripts/seed.py"
```

---

## Makefile Reference

> **Windows users** — `make` is not available by default. Use `.\dev.ps1 <task>` instead (included in the repo), or install `make` via [Chocolatey](https://chocolatey.org/): `choco install make`.

| Task | Linux / Mac | Windows (PowerShell) |
|---|---|---|
| Start dev stack | `make dev` | `.\dev.ps1 dev` |
| Rebuild dev image | `make dev-build` | `.\dev.ps1 dev-build` |
| Stop dev stack | `make dev-down` | `.\dev.ps1 dev-down` |
| Start prod stack | `make prod` | `.\dev.ps1 prod` |
| Rebuild prod image | `make prod-build` | `.\dev.ps1 prod-build` |
| Stop prod stack | `make prod-down` | `.\dev.ps1 prod-down` |
| Follow app logs | `make logs` | `.\dev.ps1 logs` |
| Follow worker logs | `make logs-worker` | `.\dev.ps1 logs-worker` |
| Apply migrations | `make migrate` | `.\dev.ps1 migrate` |
| New migration | `make migrate-new MSG="..."` | `.\dev.ps1 migrate-new -Msg "..."` |
| Seed database | `make seed` | `.\dev.ps1 seed` |
| Open shell in container | `make shell` | `.\dev.ps1 shell` |

---

## Local Development (without Docker)

Requires PostgreSQL 16 and Redis 7 running locally.

### Backend

```bash
cd backend

# Install dependencies
uv sync

# Set DATABASE_URL and REDIS_URL in root .env to point at localhost
# e.g. DATABASE_URL=postgresql+asyncpg://mvp_user:mvp_pass@localhost:5432/mvp_db

# Run migrations
uv run alembic upgrade head

# Seed (optional)
uv run python scripts/seed.py

# Start the API server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start the Celery worker (separate terminal)
uv run celery -A app.worker.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend

bun install

# Set NEXT_PUBLIC_API_URL=http://localhost:8000/api in root .env

bun dev   # starts Next.js on http://localhost:3000
```

---

## Production Deployment

### 1. Configure production values in `.env`

```env
APP_ENV=production
DEBUG=false
SECRET_KEY=<strong-random-secret>
POSTGRES_PASSWORD=<strong-db-password>
REDIS_PASSWORD=<strong-redis-password>
CORS_ORIGINS=["https://yourdomain.com"]
FRONTEND_URL=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
```

### 2. Build and start

```bash
make prod-build
```

### 3. Run migrations

```bash
docker compose exec app \
  sh -c "cd /app/backend && .venv/bin/alembic upgrade head"
```

### 4. (Optional) Seed production database

```bash
docker compose exec app \
  sh -c "cd /app/backend && .venv/bin/python scripts/seed.py"
```

> For HTTPS, place a reverse proxy (Caddy, Nginx, cloud LB) in front of the container and forward to port 80.

---

## Testing

Tests use **pytest** and require PostgreSQL. The CI pipeline runs them automatically; to run locally:

### With Docker (recommended)

```bash
make shell
cd /app/backend
.venv/bin/pytest tests/ -v
```

### Without Docker

```bash
cd backend
# Ensure DATABASE_URL points at a running Postgres instance
uv run pytest tests/ -v

# With coverage report
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## API Reference

Interactive docs (Swagger UI) are always available while the stack is running:

| Interface | URL |
|---|---|
| Swagger UI | http://localhost/docs |
| ReDoc | http://localhost/redoc |

### Endpoint groups

| Tag | Base path | Description |
|---|---|---|
| `auth` | `/api/v1/auth` | Register, login, logout, password reset, token refresh |
| `google-auth` | `/api/v1/auth/google` | Google OAuth2 sign-in |
| `azure-auth` | `/api/v1/auth/azure` | Azure AD OAuth2 sign-in |
| `profile` | `/api/v1/profile` | User profile read & update |
| `roles` | `/api/v1/roles` | Role CRUD + user–role assignment |
| `permissions` | `/api/v1/permissions` | Permission CRUD + role–permission assignment |
| `admin` | `/api/v1/admin` | Admin-only user management |
| `audit` | `/api/v1/audit` | Audit log access |
| `notifications` | `/api/v1/notifications` | In-app notifications |
| `uploads` | `/api/v1/uploads` | File upload via Azure Blob Storage |
| `payments` | `/api/v1/payments` | Payment processing (Stripe placeholder) |
| `health` | `/health` | Service health check |

### Authentication

The API issues **httpOnly JWT cookies** on login — the browser sends them automatically. For programmatic clients, use the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

## Adding a New Backend Module

1. **Create the module directory:**

```
backend/app/your_module/
├── __init__.py
├── models.py          # SQLAlchemy models
├── schemas/
│   ├── request/       # Pydantic input schemas
│   └── response/      # Pydantic output schemas
├── service.py         # Business logic
└── router.py          # FastAPI router
```

2. **Register models for Alembic** — import them in `alembic/env.py`.

3. **Register the router** — add `app.include_router(your_router)` in `backend/app/main.py → create_app()`.

4. **Generate and apply a migration:**

```bash
# Linux / Mac
make migrate-new MSG="add your_module"
make migrate

# Windows PowerShell
.\dev.ps1 migrate-new -Msg "add your_module"
.\dev.ps1 migrate
```

5. **Write tests** in `backend/tests/test_your_module/`.

---

## Google OAuth2 Token Setup

This section documents how to manually obtain OAuth2 credentials for Google APIs (e.g. Gmail, Drive).

### Step 1 — Get an authorization code

Open the following URL in a browser (replace placeholders with your values):

```
https://accounts.google.com/o/oauth2/auth
  ?client_id=<GOOGLE_CLIENT_ID>
  &redirect_uri=<REDIRECT_URI>
  &response_type=code
  &scope=https://www.googleapis.com/auth/gmail.send
  &access_type=offline
```

After the user consents, Google redirects to `<REDIRECT_URI>?code=<AUTH_CODE>`.

**Example (Drive scope):**

```
https://accounts.google.com/o/oauth2/auth?client_id=<GOOGLE_CLIENT_ID>&redirect_uri=https://yourapp.com/api/v1/google/callback&response_type=code&scope=https://www.googleapis.com/auth/drive&access_type=offline
```

Redirect received:

```
https://yourapp.com/api/v1/google/callback?code=<AUTH_CODE>&scope=https://www.googleapis.com/auth/drive
```

### Step 2 — Exchange the code for a refresh token

```bash
curl --request POST \
  --data "code=<AUTH_CODE>\
&client_id=<GOOGLE_CLIENT_ID>\
&client_secret=<GOOGLE_CLIENT_SECRET>\
&redirect_uri=<REDIRECT_URI>\
&grant_type=authorization_code" \
  https://oauth2.googleapis.com/token
```

> The `refresh_token` is only returned on the **first** authorization. Store it securely — it does not expire unless revoked.

**Example:**

```bash
curl --request POST \
  --data "code=<AUTH_CODE>&client_id=<GOOGLE_CLIENT_ID>&client_secret=<GOOGLE_CLIENT_SECRET>&redirect_uri=https://yourapp.com/api/v1/google/callback&grant_type=authorization_code" \
  https://oauth2.googleapis.com/token
```

### Step 3 — Generate a new access token from the refresh token

Access tokens expire after ~1 hour. Use the refresh token to get a new one without user interaction:

```bash
curl --request POST \
  --data "client_id=<GOOGLE_CLIENT_ID>\
&client_secret=<GOOGLE_CLIENT_SECRET>\
&refresh_token=<REFRESH_TOKEN>\
&grant_type=refresh_token" \
  https://oauth2.googleapis.com/token
```

Store `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `REFRESH_TOKEN` in your root `.env` file.

---

## CI/CD

GitHub Actions runs on every push and pull request to `main`.

| Job | Steps |
|---|---|
| `backend` | `uv sync` → `ruff check` → `ruff format --check` → `pytest` |
| `frontend` | `bun install` → `eslint` → `tsc --noEmit` |

Configuration: [.github/workflows/ci.yml](.github/workflows/ci.yml)
