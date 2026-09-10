import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.domain.entities.brand import Brand
from src.infrastructure.database.models import BrandModel
from src.infrastructure.repositories.brand_repository import BrandRepository

pytestmark = [pytest.mark.integration]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create(db_session, name: str = "Trek") -> Brand:
    repo = BrandRepository(db_session)
    return await repo.create(Brand(brand_name=name))


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_persists_brand(db_session):
    created = await _create(db_session)

    assert created.brand_id is not None
    assert created.brand_name == "Trek"
    assert created.is_active is True

    result = await db_session.execute(
        select(BrandModel).where(BrandModel.brand_id == created.brand_id)
    )
    row = result.scalar_one()
    assert row.brand_name == "Trek"
    assert row.is_active is True


@pytest.mark.asyncio
async def test_create_duplicate_name_raises_integrity_error(db_session):
    await _create(db_session, "Specialized")

    with pytest.raises(IntegrityError):
        await _create(db_session, "Specialized")


# ---------------------------------------------------------------------------
# get_brand_by_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_by_id_returns_brand(db_session):
    created = await _create(db_session)
    repo = BrandRepository(db_session)

    found = await repo.get_brand_by_id(created.brand_id)

    assert found is not None
    assert found.brand_id == created.brand_id
    assert found.brand_name == "Trek"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_unknown_id(db_session):
    repo = BrandRepository(db_session)

    assert await repo.get_brand_by_id(99999) is None


# ---------------------------------------------------------------------------
# get_brand_by_name
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_by_name_returns_brand(db_session):
    await _create(db_session, "Giant")
    repo = BrandRepository(db_session)

    found = await repo.get_brand_by_name("Giant")

    assert found is not None
    assert found.brand_name == "Giant"


@pytest.mark.asyncio
async def test_get_by_name_returns_none_for_unknown_name(db_session):
    repo = BrandRepository(db_session)

    assert await repo.get_brand_by_name("NoSuchBrand") is None


# ---------------------------------------------------------------------------
# list_all
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_all_returns_all_brands(db_session):
    await _create(db_session, "Trek")
    await _create(db_session, "Giant")
    await _create(db_session, "Cannondale")
    repo = BrandRepository(db_session)

    brands = await repo.list_all(skip=0, limit=100)

    names = {b.brand_name for b in brands}
    assert {"Trek", "Giant", "Cannondale"}.issubset(names)


@pytest.mark.asyncio
async def test_list_all_respects_pagination(db_session):
    for name in ["A", "B", "C", "D"]:
        await _create(db_session, name)
    repo = BrandRepository(db_session)

    first_page = await repo.list_all(skip=0, limit=2)
    second_page = await repo.list_all(skip=2, limit=2)

    assert len(first_page) == 2
    assert len(second_page) == 2
    assert {b.brand_name for b in first_page}.isdisjoint(
        {b.brand_name for b in second_page}
    )


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_brand_name(db_session):
    created = await _create(db_session, "OldName")
    repo = BrandRepository(db_session)

    created.update_information(brand_name="NewName")
    updated = await repo.update(created)

    assert updated.brand_name == "NewName"

    row = (
        await db_session.execute(
            select(BrandModel).where(BrandModel.brand_id == created.brand_id)
        )
    ).scalar_one()
    assert row.brand_name == "NewName"


@pytest.mark.asyncio
async def test_update_deactivates_brand(db_session):
    created = await _create(db_session)
    repo = BrandRepository(db_session)

    created.deactivate()
    updated = await repo.update(created)

    assert updated.is_active is False

    row = (
        await db_session.execute(
            select(BrandModel).where(BrandModel.brand_id == created.brand_id)
        )
    ).scalar_one()
    assert row.is_active is False


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_removes_brand_row(db_session):
    created = await _create(db_session)
    repo = BrandRepository(db_session)

    result = await repo.delete(created.brand_id)

    assert result is True
    row = (
        await db_session.execute(
            select(BrandModel).where(BrandModel.brand_id == created.brand_id)
        )
    ).scalar_one_or_none()
    assert row is None


@pytest.mark.asyncio
async def test_delete_returns_false_for_nonexistent_id(db_session):
    repo = BrandRepository(db_session)

    assert await repo.delete(99999) is False
