# Database

This folder contains `init.sql`, the SQL script used to initialize the project's database schema and seed data.

## Source

The base schema and sample data are derived from the **BikeStore sample database**, provided by [SQL Server Tutorial](https://www.sqlservertutorial.net/getting-started/sql-server-sample-database/).

`init.sql` combines the following three original files into a single script:

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

`init.sql` is intended to be run once to bootstrap the database with schema + sample data. Schema changes going forward should be made through Alembic migrations (see `alembic/`), not by editing this file directly, to keep migration history consistent.