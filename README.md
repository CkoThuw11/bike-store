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
| Migrations | Alembic (auto-applied on backend startup) |
| Containers | Docker, Docker Compose |

## ⚙️ Configuration

Docker Compose reads `${DATABASE_HOST}`, `${DATABASE_NAME}`, `${DATABASE_USER}`, `${DATABASE_PASSWORD}`, `${DATABASE_PORT}` directly in `docker-compose.yml` (for the Postgres service and port mapping). It resolves these from a **root-level `.env`** — not `backend/.env`. Both files are needed:

```bash
cp backend/.env.example backend/.env
cp backend/.env .env
```

Keep the two files in sync — `backend/.env` is injected into the backend/db containers via `env_file`, while the root `.env` drives variable substitution inside `docker-compose.yml` itself.

## 🚀 Run

### Docker Compose (recommended)

```bash
docker compose up --build
```

Starts:

- Frontend: `http://localhost:4200`
- Backend API: `http://localhost:8000` (docs: `/docs`, health: `/health`)
- PostgreSQL: `${DATABASE_PORT}:5432`

On first start (empty `pgdata` volume), Postgres automatically runs `backend/db/init.sql`, creating the schema and seeding all data. To re-seed, remove the volume first (`docker compose down -v`).

### Run services individually

For local (non-Docker) setup of each service, see [`backend/README.md`](./backend/README.md) and [`frontend/README.md`](./frontend/README.md).

## ⚠️ Known Notes

- The backend container runs Alembic migrations in-process at startup, inside the same `uvicorn --reload` worker. On Docker Desktop with WSL2 bind mounts, the reloader's fork can race with that startup thread and hang the container. `WATCHFILES_FORCE_POLLING=true` is set on the backend service to avoid it — don't remove it without testing a full `docker compose up` first.
- The frontend container serves a static production build via Nginx — there is no live reload inside Docker. Use `ng serve` locally (see `frontend/README.md`) for frontend development with hot reload.
- Seeded demo accounts (password `123456789`): `admin@gmail.com` (ADMIN), `customer@gmail.com` (CUSTOMER).

## 🔗 Related Docs

- [`backend/README.md`](./backend/README.md) — backend architecture, API routes, auth, seed data
- [`frontend/README.md`](./frontend/README.md) — Angular CLI commands
- [`AGENT.md`](./AGENT.md) — architecture rules, coding style, CI/CD, dev workflow
claude --resume 419bb3c7-aaf8-4dd8-807c-ea0a95cbdbec


