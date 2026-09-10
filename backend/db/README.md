# Database

This folder contains `seed_dev_data.sql`, an optional script that loads sample/demo data for local development. The schema itself is owned by Alembic migrations (see `../alembic/`) — this folder no longer creates any tables.

## Source

The base schema and sample data are derived from the **BikeStore sample database**, provided by [SQL Server Tutorial](https://www.sqlservertutorial.net/getting-started/sql-server-sample-database/).

The original `init.sql` combined the following three original files into a single script (schema creation has since moved to Alembic; `seed_dev_data.sql` now holds only the data portion):

- Table creation script
- Table population (seed data) script
- Constraints / foreign keys script

The original BikeStore schema includes the following tables:

| Table | Description |
|---|---|
| `categories` | Product categories |
| `brands` | Product brands |
| `products` | Bike products for sale |
| `stores` | Store locations |
| `staffs` | Store staff members |
| `customers` | Customer records |
| `orders` | Customer orders |
| `order_items` | Line items belonging to each order |
| `stocks` | Product stock per store |

All credit for the original schema design and sample data goes to the SQL Server Tutorial team. The script has been adapted here for use with this project's database engine and application requirements.

## Additions for this project

Two tables were added on top of the original BikeStore schema to support authentication in this backend:

| Table | Description |
|---|---|
| `users` | Application user accounts (used for authentication/authorization) |
| `refresh_tokens` | Refresh tokens issued to users for maintaining authenticated sessions |

These tables are **not part of the original BikeStore dataset** — they were added specifically to support this backend's auth flow and are maintained independently of the upstream source.

## Usage

Schema is created by running Alembic migrations (`alembic upgrade head`) — see `../alembic/`. All schema changes must go through a new Alembic revision, never by editing SQL in this folder directly.

`seed_dev_data.sql` is optional and for local development only — it is **not** run automatically and must never be applied against staging/production (it contains ~9k rows of fake demo data plus 2 demo login accounts). Apply it manually after migrations have run:

```bash
docker exec -i -e PGPASSWORD=postgres bike-store-db psql -U postgres -d bike_store < db/seed_dev_data.sql
```

(values above match `backend/.env.example`'s defaults — adjust if your `.env` differs)