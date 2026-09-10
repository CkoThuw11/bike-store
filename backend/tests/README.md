# Test Suite

The tests follow the strategy in `Testing_Strategy.md`:

- `tests/unit/`: fast service tests using in-memory fakes.
- `tests/integration/`: repository tests using PostgreSQL.
- `tests/e2e/`: FastAPI route tests with dependency overrides.

Run all tests:

```bash
pytest
```

Run by layer:

```bash
pytest -m unit
pytest -m integration
pytest -m e2e
```

Database-backed tests use `TEST_DATABASE_URL` when set:

```bash
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/test_db pytest -m "integration or e2e"
```

If `TEST_DATABASE_URL` is not set, the tests try Testcontainers with PostgreSQL. If Docker is unavailable, those tests skip cleanly.
