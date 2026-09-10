from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.domain.entities.product import Product
from src.infrastructure.database.models import ProductModel
from src.infrastructure.repositories.product_repository import ProductRepository

pytestmark = [pytest.mark.integration]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _product(
    brand_id: int,
    category_id: int,
    name: str = "Trail Bike",
    price: str = "999.99",
) -> Product:
    return Product(
        product_name=name,
        brand_id=brand_id,
        category_id=category_id,
        model_year=2025,
        list_price=Decimal(price),
    )


async def _create(db_session, seeded_catalog, name="Trail Bike") -> Product:
    repo = ProductRepository(db_session)
    return await repo.create(
        _product(seeded_catalog["brand_id"], seeded_catalog["category_id"], name=name)
    )


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_persists_product(db_session, seeded_catalog):
    created = await _create(db_session, seeded_catalog)

    assert created.product_id is not None
    assert created.product_name == "Trail Bike"
    assert created.is_active is True
    assert created.list_price == Decimal("999.99")

    row = (
        await db_session.execute(
            select(ProductModel).where(ProductModel.product_id == created.product_id)
        )
    ).scalar_one()
    assert row.product_name == "Trail Bike"
    assert row.brand_id == seeded_catalog["brand_id"]


@pytest.mark.asyncio
async def test_create_duplicate_name_raises_integrity_error(db_session, seeded_catalog):
    await _create(db_session, seeded_catalog, name="Duplicate Bike")

    with pytest.raises(IntegrityError):
        await _create(db_session, seeded_catalog, name="Duplicate Bike")


# ---------------------------------------------------------------------------
# get_product_by_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_by_id_returns_product(db_session, seeded_catalog):
    created = await _create(db_session, seeded_catalog)
    repo = ProductRepository(db_session)

    found = await repo.get_product_by_id(created.product_id)

    assert found is not None
    assert found.product_id == created.product_id
    assert found.product_name == "Trail Bike"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_unknown_id(db_session, seeded_catalog):
    repo = ProductRepository(db_session)

    assert await repo.get_product_by_id(99999) is None


# ---------------------------------------------------------------------------
# get_product_by_name
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_by_name_returns_product(db_session, seeded_catalog):
    await _create(db_session, seeded_catalog, name="Road Racer")
    repo = ProductRepository(db_session)

    found = await repo.get_product_by_name("Road Racer")

    assert found is not None
    assert found.product_name == "Road Racer"


@pytest.mark.asyncio
async def test_get_by_name_returns_none_for_unknown_name(db_session, seeded_catalog):
    repo = ProductRepository(db_session)

    assert await repo.get_product_by_name("Ghost Bike") is None


# ---------------------------------------------------------------------------
# list_all
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_all_returns_paginated_products(db_session, seeded_catalog):
    for name in ["Bike A", "Bike B", "Bike C"]:
        await _create(db_session, seeded_catalog, name=name)
    repo = ProductRepository(db_session)

    first = await repo.list_all(skip=0, limit=2)
    second = await repo.list_all(skip=2, limit=2)

    assert len(first) == 2
    assert len(second) == 1


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_product_name_and_price(db_session, seeded_catalog):
    created = await _create(db_session, seeded_catalog)
    repo = ProductRepository(db_session)

    created.update_information(product_name="Updated Bike", list_price=Decimal("1299.00"))
    updated = await repo.update(created)

    assert updated.product_name == "Updated Bike"
    assert updated.list_price == Decimal("1299.00")

    row = (
        await db_session.execute(
            select(ProductModel).where(ProductModel.product_id == created.product_id)
        )
    ).scalar_one()
    assert row.product_name == "Updated Bike"


@pytest.mark.asyncio
async def test_update_deactivates_product(db_session, seeded_catalog):
    created = await _create(db_session, seeded_catalog)
    repo = ProductRepository(db_session)

    created.deactivate()
    updated = await repo.update(created)

    assert updated.is_active is False


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_removes_product_row(db_session, seeded_catalog):
    created = await _create(db_session, seeded_catalog)
    repo = ProductRepository(db_session)

    result = await repo.delete(created.product_id)

    assert result is True
    row = (
        await db_session.execute(
            select(ProductModel).where(ProductModel.product_id == created.product_id)
        )
    ).scalar_one_or_none()
    assert row is None


@pytest.mark.asyncio
async def test_delete_returns_false_for_nonexistent_id(db_session, seeded_catalog):
    repo = ProductRepository(db_session)

    assert await repo.delete(99999) is False
