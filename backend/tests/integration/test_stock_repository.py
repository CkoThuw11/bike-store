from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.domain.entities.product import Product
from src.domain.entities.stock import Stock
from src.infrastructure.database.models import StockModel
from src.infrastructure.repositories.product_repository import ProductRepository
from src.infrastructure.repositories.stock_repository import StockRepository

pytestmark = [pytest.mark.integration]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _seed_product(db_session, seeded_catalog, name: str = "Stock Bike") -> Product:
    repo = ProductRepository(db_session)
    return await repo.create(
        Product(
            product_name=name,
            brand_id=seeded_catalog["brand_id"],
            category_id=seeded_catalog["category_id"],
            model_year=2025,
            list_price=Decimal("799.00"),
        )
    )


async def _create_stock(db_session, store_id: int, product_id: int, qty: int = 10) -> Stock:
    repo = StockRepository(db_session)
    return await repo.create(Stock(store_id=store_id, product_id=product_id, quantity=qty))


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_stock_persists_record(db_session, seeded_catalog):
    product = await _seed_product(db_session, seeded_catalog)
    stock = await _create_stock(db_session, seeded_catalog["store_id"], product.product_id, qty=25)

    assert stock.stock_id is not None
    assert stock.quantity == 25

    row = (
        await db_session.execute(select(StockModel).where(StockModel.stock_id == stock.stock_id))
    ).scalar_one()
    assert row.quantity == 25
    assert row.store_id == seeded_catalog["store_id"]
    assert row.product_id == product.product_id


@pytest.mark.asyncio
async def test_create_duplicate_store_product_pair_raises_integrity_error(
    db_session, seeded_catalog
):
    """DB enforces unique (store_id, product_id) via uq_stocks_store_product."""
    product = await _seed_product(db_session, seeded_catalog)
    await _create_stock(db_session, seeded_catalog["store_id"], product.product_id)

    with pytest.raises(IntegrityError):
        await _create_stock(db_session, seeded_catalog["store_id"], product.product_id)


# ---------------------------------------------------------------------------
# get_stock_by_id (composite key)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_stock_by_id_returns_record(db_session, seeded_catalog):
    product = await _seed_product(db_session, seeded_catalog)
    await _create_stock(db_session, seeded_catalog["store_id"], product.product_id, qty=5)
    repo = StockRepository(db_session)

    found = await repo.get_stock_by_id(seeded_catalog["store_id"], product.product_id)

    assert found is not None
    assert found.quantity == 5


@pytest.mark.asyncio
async def test_get_stock_by_id_returns_none_when_missing(db_session, seeded_catalog):
    repo = StockRepository(db_session)

    assert await repo.get_stock_by_id(99999, 99999) is None


# ---------------------------------------------------------------------------
# get_stock_by_store_id / get_stock_by_product_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_stock_by_store_id_returns_all_store_records(db_session, seeded_catalog):
    p1 = await _seed_product(db_session, seeded_catalog, "Bike X")
    p2 = await _seed_product(db_session, seeded_catalog, "Bike Y")
    await _create_stock(db_session, seeded_catalog["store_id"], p1.product_id, qty=3)
    await _create_stock(db_session, seeded_catalog["store_id"], p2.product_id, qty=7)
    repo = StockRepository(db_session)

    records = await repo.get_stock_by_store_id(seeded_catalog["store_id"])

    assert len(records) == 2
    assert {r.product_id for r in records} == {p1.product_id, p2.product_id}


@pytest.mark.asyncio
async def test_get_stock_by_product_id_returns_all_store_records(db_session, seeded_catalog):
    product = await _seed_product(db_session, seeded_catalog)
    await _create_stock(db_session, seeded_catalog["store_id"], product.product_id, qty=4)
    repo = StockRepository(db_session)

    records = await repo.get_stock_by_product_id(product.product_id)

    assert len(records) == 1
    assert records[0].store_id == seeded_catalog["store_id"]


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_stock_quantity(db_session, seeded_catalog):
    product = await _seed_product(db_session, seeded_catalog)
    stock = await _create_stock(db_session, seeded_catalog["store_id"], product.product_id, qty=10)
    repo = StockRepository(db_session)

    stock.update_information(quantity=42)
    updated = await repo.update(stock)

    assert updated.quantity == 42

    row = (
        await db_session.execute(select(StockModel).where(StockModel.stock_id == stock.stock_id))
    ).scalar_one()
    assert row.quantity == 42
