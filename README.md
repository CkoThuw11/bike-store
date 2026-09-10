# 🚲 Bike Store

Full-stack bike store management system — Angular frontend + FastAPI backend, built as a strict Clean Architecture / MVVM reference project. Rules and conventions live in [`AGENT.md`](./AGENT.md) — read it before contributing.

## 🔎 Project Snapshot

- **Frontend:** Angular (standalone components, Signals, MVVM)
- **Backend:** FastAPI + async SQLAlchemy + PostgreSQL 16, JWT auth, Alembic migrations
- **Architecture:** Clean Architecture (backend) + MVVM (frontend) — full rules in [`AGENT.md`](./AGENT.md)
- **Orchestration:** Docker Compose at the repo root, wiring frontend + backend + Postgres together

## 📁 Structure

```text
bike-store/
├── backend/            # FastAPI service — see backend/README.md
├── frontend/           # Angular app — see frontend/README.md
├── docker-compose.yml  # Orchestrates backend + frontend + Postgres
├── AGENT.md            # Architecture rules and conventions
└── README.md
```

## 🧰 Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Angular, Signals, SCSS |
| Backend | FastAPI, Uvicorn, Python 3.11 |
| Database | PostgreSQL 16, async SQLAlchemy + asyncpg |
| Auth | JWT (access + rotating refresh tokens) |
| Migrations | Alembic (applied by a one-shot `migrate` service before backend starts) |
| Containers | Docker, Docker Compose |

## ⚙️ Configuration

Two `.env` files, two different jobs — both are needed:

```bash
cp backend/.env.example backend/.env
cp .env.example .env
```

- **`backend/.env`** — the full app config (DB, JWT secret, logging, etc.), injected into the `migrate`/`backend`/`db` containers via `env_file`. This is what the application actually reads at runtime.
- **Root `.env`** — only the 5 `DATABASE_*` values, used solely for `docker-compose.yml`'s own `${DATABASE_HOST}`/`${DATABASE_NAME}`/`${DATABASE_USER}`/`${DATABASE_PASSWORD}`/`${DATABASE_PORT}` substitution (the `db` service's `POSTGRES_*` env and its port mapping). `docker-compose.yml` never reads `backend/.env` directly — Compose's `${VAR}` substitution only looks at a `.env` in the same directory as the compose file itself, which is why this second, narrower file exists.

Keep the `DATABASE_*` values identical across both files — they must point at the same database.

## 🚀 Run

### Docker Compose (recommended)

```bash
docker compose up --build
```

Starts:

- Frontend: `http://localhost:4200`
- Backend API: `http://localhost:8000` (docs: `/docs`, health: `/health`)
- PostgreSQL: `${DATABASE_PORT}:5432`

A one-shot `migrate` service runs `alembic upgrade head` and must complete successfully before `backend` starts — this is what creates the schema. There is no automatic seeding; to load optional demo data for local dev, run it manually:

```bash
docker exec -i -e PGPASSWORD=postgres bike-store-db psql -U postgres -d bike_store < backend/db/seed_dev_data.sql
```

(values above match `.env.example`'s defaults — adjust if your `.env` differs)

### Run services individually

For local (non-Docker) setup of each service, see [`backend/README.md`](./backend/README.md) and [`frontend/README.md`](./frontend/README.md).

## ⚠️ Known Notes

- Migrations run via a separate one-shot `migrate` service (`alembic upgrade head`), gated before `backend` starts — the backend itself no longer runs migrations at boot. `WATCHFILES_FORCE_POLLING=true` remains set on the backend service for reload reliability on WSL2 bind mounts.
- The frontend container serves a static production build via Nginx — there is no live reload inside Docker. Use `ng serve` locally (see `frontend/README.md`) for frontend development with hot reload.
- Demo data (including the demo account below) is optional and not seeded automatically — see `backend/db/seed_dev_data.sql`. Never apply it against staging/production.
- Seeded demo account (password `123456789`, once `seed_dev_data.sql` is applied): `admin@gmail.com` (ADMIN). The frontend is admin-only (see `frontend/README.md`), so no `CUSTOMER` demo account is seeded.

## 🔗 Related Docs

- [`backend/README.md`](./backend/README.md) — backend architecture, API routes, auth, seed data
- [`frontend/README.md`](./frontend/README.md) — Angular CLI commands
- [`AGENT.md`](./AGENT.md) — architecture rules, coding style, CI/CD, dev workflow



