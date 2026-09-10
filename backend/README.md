# 🚲 Bike Store API

FastAPI backend for a bike store management system using Clean Architecture, async SQLAlchemy, PostgreSQL, JWT authentication, Alembic-managed migrations, and Docker.

## 🔎 Project Snapshot

- **Framework:** FastAPI + Uvicorn
- **Database:** PostgreSQL 16 with async SQLAlchemy and asyncpg
- **Architecture:** API → Application → Domain ← Infrastructure
- **Auth:** JWT access tokens, refresh-token rotation, HttpOnly refresh cookie
- **Data:** Schema created by Alembic migrations; `db/seed_dev_data.sql` — optional demo data for local dev
- **Containers:** Dockerfile + Docker Compose

## 🧱 Architecture

```text
HTTP request
  -> src/api/              FastAPI routes, dependencies, middleware
  -> src/application/      DTOs and service orchestration
  -> src/domain/           Entities, enums, repository contracts, exceptions
  <- src/infrastructure/   SQLAlchemy models, DB connection, repositories
```

Core rules:

- Keep routes thin: validate, authorize, delegate.
- Keep domain code independent from FastAPI, Pydantic, and SQLAlchemy.
- Keep ORM models inside `src/infrastructure/`.
- Depend on repository interfaces from the domain layer.

Full conventions (SOLID, SRP, exception handling, layering rules) live in [`AGENT.md`](./AGENT.md) — read it before contributing.

## 🧰 Tech Stack

| Area | Technology |
| --- | --- |
| API | FastAPI |
| Runtime | Uvicorn, Python 3.11 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy async + asyncpg |
| Validation | Pydantic |
| Auth | JWT, passlib bcrypt |
| Migrations | Alembic |
| Logging | structlog, python-json-logger |
| Testing | pytest, pytest-asyncio, testcontainers, httpx |
| Code Quality | ruff (lint/format), mypy (types) |
| Containers | Docker, Docker Compose |

## 📁 Structure

```text
BackendEngineering/
├── alembic/                 # Migration environment (applied by the `migrate` service before backend starts)
├── db/
│   └── seed_dev_data.sql    # Optional demo data for local dev, applied manually
├── src/
│   ├── api/                 # Routes, dependencies, exception handlers
│   ├── application/         # DTOs, services, auth/password/token helpers
│   ├── core/                # Logging and request middleware
│   ├── domain/              # Entities, repository ABCs, exceptions
│   ├── infrastructure/      # DB config, SQLAlchemy models, repositories
│   └── main.py              # FastAPI app wiring
├── tests/
│   ├── unit/                # Fast tests, no external services
│   ├── integration/         # Repository/DB tests against PostgreSQL
│   └── e2e/                 # Full HTTP contract tests
├── .env.example
├── AGENT.md                 # Architecture rules and conventions
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## ⚙️ Configuration

Create a local env file:

```bash
cp .env.example .env
```

Important variables:

```env
DATABASE_HOST=db
DATABASE_NAME=bike_store
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_PORT=5432

AUTH_SECRET_KEY=change-this-to-a-random-secret-key
AUTH_ALGORITHM=HS256
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=15
AUTH_REFRESH_TOKEN_EXPIRE_DAYS=7

APP_DEBUG=true
LOG_LEVEL=INFO
LOG_FORMAT=text
```
## 🚀 Run

### Docker Compose

```bash
docker compose up --build
```

Starts:

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- PostgreSQL: `${DATABASE_PORT}:5432`

A one-shot `migrate` service runs `alembic upgrade head` and must complete successfully before `backend` starts — this creates the schema. To load demo data on top, apply it manually:

```bash
docker exec -i -e PGPASSWORD=postgres bike-store-db psql -U postgres -d bike_store < db/seed_dev_data.sql
```

(values above match `.env.example`'s defaults — adjust if your `.env` differs)

### Local Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
PGPASSWORD=postgres psql -h localhost -U postgres -d bike_store -f db/seed_dev_data.sql  # optional demo data
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔐 Authentication

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Register user |
| `POST` | `/auth/login` | Login and issue token pair |
| `POST` | `/auth/refresh` | Rotate refresh token |
| `POST` | `/auth/logout` | Revoke refresh token |
| `POST` | `/auth/login/swagger` | Swagger OAuth2 login |

Access tokens use `Authorization: Bearer <token>`. Refresh tokens are returned in the body and set as the `refreshToken` HttpOnly cookie.

Current roles in code: `ADMIN`, `CUSTOMER`.

Register example:

```json
{
  "email": "admin@example.com",
  "password": "Secret123",
  "username": "admin",
  "fullname": "System Admin"
}
```

## 🛣️ API Routes

Most non-auth routes require a bearer token. Admin-only routes use `require_role(Role.ADMIN)`.

| Resource | Main Routes |
| --- | --- |
| Brands | `/brands/`, `/brands/{brand_id}`, `/brands/{brand_id}/activate`, `/brands/{brand_id}/deactivate` |
| Categories | `/categories/`, `/categories/{category_id}` |
| Products | `/products/`, `/products/{product_id}`, `/products/search/by-name`, `/products/{product_id}/activate`, `/products/{product_id}/deactivate` |
| Stores | `/stores/`, `/stores/{store_id}`, `/stores/{store_id}/activate`, `/stores/{store_id}/deactivate` |
| Staff | `/staffs/`, `/staffs/{staff_id}`, `/staffs/search`, `/staffs/{staff_id}/activate`, `/staffs/{staff_id}/deactivate` |
| Stock | `/stocks/`, `/stocks/{store_id}/{product_id}`, `/stocks/store/{store_id}`, `/stocks/product/{product_id}`, `/stocks/{store_id}/{product_id}/adjust` |
| Customers | `/customers/`, `/customers/{customer_id}`, `/customers/search` |
| Orders | `/orders/`, `/orders/{order_id}`, `/orders/customer/{customer_id}`, `/orders/{order_id}/checkout` |
| Order Items | `/order-items/`, `/order-items/{order_id}/{product_id}`, `/order-items/order/{order_id}` |

Use Swagger UI at `/docs` for exact methods and request/response schemas.

## 🌱 Seed Data

Schema is created by Alembic migrations (`alembic upgrade head`), not by a SQL bootstrap script. `db/seed_dev_data.sql` is optional and dev-only — it loads sample brands, categories, customers, stores, staff, products, orders, order items, and stock, plus one demo admin user (see below). It is never run automatically; apply it manually and never against staging/production.

Seeded account (password `123456789`):

| Email | Username | Role |
| --- | --- | --- |
| `admin@gmail.com` | `admin` | ADMIN |

## ⚠️ Known Notes

- Database migrations run via a separate one-shot `migrate` service (`alembic upgrade head`), gated before `backend` starts — the API container itself does not run migrations.
- Context-aware structured logging is implemented using `structlog` (outputs console-colored text in development and JSON in production), configured via `APP_DEBUG`/`LOG_LEVEL`/`LOG_FORMAT`.
- Tests are split into three tiers (`pytest.ini` markers): `unit` (no external services), `integration` (PostgreSQL via testcontainers), `e2e` (full HTTP contract tests). Run them individually via `pytest -m unit`, `pytest -m integration`, `pytest -m e2e`.

