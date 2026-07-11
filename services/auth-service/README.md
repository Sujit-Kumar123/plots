# auth-service

FastAPI authentication microservice — handles registration, login, JWT issuance, token refresh, password reset, SSO (Google + Azure), roles, and permissions.

Runs on port **8010** internally; exposed through the API gateway at `/api/auth/*`.

---

## Running locally (via Docker Compose)

```powershell
# From the repo root
docker compose -f docker-compose.dev.yml up -d auth-service
```

---

## Database migrations

Migrations run automatically via the `db-migrate` service before `auth-service` starts.

To run manually:

```powershell
docker compose -f docker-compose.dev.yml exec auth-service uv run alembic upgrade head
```

---

## Seeding roles, permissions, and sample users

The `scripts/seed.py` directory is not volume-mounted into the container, so copy it in first:

```powershell
docker cp services/auth-service/scripts/seed.py plots-auth-service-1:/app/seed.py
docker compose -f docker-compose.dev.yml exec auth-service uv run python seed.py
```

The script is **idempotent** — safe to run multiple times. Existing records are skipped.

### What gets seeded

| Type | Details |
|---|---|
| Roles | `superadmin`, `admin`, `member` |
| Permissions | 23 `resource:action` codes (e.g. `profile:read`, `sheets:write`) |
| Sample users | 21 users across all three roles |

### Sample user credentials

| Email | Password | Role |
|---|---|---|
| `superadmin@example.com` | `superadmin123` | superadmin |
| `admin@example.com` | `admin1234` | admin |
| `member@example.com` | `member123` | member |

All other sample users use `Password@123`.

---

## Project structure

```
auth-service/
├── app/
│   ├── auth/
│   │   ├── models/          # SQLAlchemy models (User, Session, Role, Permission)
│   │   ├── routers/         # Route handlers (auth, google, azure, internal)
│   │   └── service/         # Business logic (register, login, refresh, etc.)
│   ├── common/              # Shared dependencies, permissions, responses
│   └── database.py          # Async SQLAlchemy engine + session factory
├── alembic/                 # Database migrations
├── scripts/
│   └── seed.py              # Seed script (roles, permissions, users)
├── main.py
└── pyproject.toml
```
