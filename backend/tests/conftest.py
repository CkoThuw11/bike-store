import os
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.infrastructure.database.models import Base, BrandModel, CategoryModel, StoreModel


def _postgres_url_from_container() -> Generator[str, None, None]:
    testcontainers = pytest.importorskip("testcontainers.postgres")
    PostgresContainer = testcontainers.PostgresContainer

    try:
        with PostgresContainer("postgres:16-alpine") as postgres:
            raw_url = postgres.get_connection_url()
            async_url = raw_url.replace(
                "postgresql+psycopg2://",
                "postgresql+asyncpg://",
            ).replace(
                "postgresql://",
                "postgresql+asyncpg://",
            )
            yield async_url
    except Exception as exc:
        pytest.skip(f"PostgreSQL test container is unavailable: {exc}")


@pytest.fixture(scope="session")
def test_database_url() -> Generator[str, None, None]:
    configured_url = os.getenv("TEST_DATABASE_URL")
    if configured_url:
        yield configured_url
        return

    yield from _postgres_url_from_container()


@pytest_asyncio.fixture
async def db_session(test_database_url: str) -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(test_database_url, echo=False, poolclass=NullPool)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        session = session_factory()
        try:
            yield session
        finally:
            try:
                await session.rollback()
            except Exception:
                pass
            await session.close()
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def seeded_catalog(db_session: AsyncSession) -> dict[str, int]:
    brand = BrandModel(brand_name="Test Brand")
    category = CategoryModel(category_name="Test Category")
    store = StoreModel(
        store_name="Test Store",
        phone="555-0100",
        email="store@example.com",
        street="1 Test Street",
        city="Austin",
        state="TX",
        zip_code="78701",
    )

    db_session.add_all([brand, category, store])
    await db_session.flush()

    return {
        "brand_id": brand.brand_id,
        "category_id": category.category_id,
        "store_id": store.store_id,
    }


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from src.api.dependencies.auth import get_current_user
    from src.infrastructure.connection import get_db
    from src.main import app

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    async def override_current_user() -> dict[str, int | str]:
        return {"user_id": 1, "role": "ADMIN"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()
