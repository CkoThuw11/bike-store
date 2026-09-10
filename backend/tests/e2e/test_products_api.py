from decimal import Decimal

import pytest
from sqlalchemy import select

from src.infrastructure.database.models import ProductModel, StockModel

pytestmark = [pytest.mark.e2e]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_product(client, seeded_catalog, name="HTTP Bike", price="1599.95"):
    return await client.post(
        "/products/",
        json={
            "product_name": name,
            "brand_id": seeded_catalog["brand_id"],
            "category_id": seeded_catalog["category_id"],
            "model_year": 2026,
            "list_price": price,
        },
    )


# ---------------------------------------------------------------------------
# create  POST /products/
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_product_returns_201_and_initialises_stock(
    client, db_session, seeded_catalog
):
    response = await _create_product(client, seeded_catalog)

    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] is not None
    assert data["product_name"] == "HTTP Bike"
    assert Decimal(str(data["list_price"])) == Decimal("1599.95")
    assert data["is_active"] is True

    row = (
        await db_session.execute(
            select(ProductModel).where(ProductModel.product_id == data["product_id"])
        )
    ).scalar_one()
    assert row.product_name == "HTTP Bike"

    stocks = (
        await db_session.execute(
            select(StockModel).where(StockModel.product_id == data["product_id"])
        )
    ).scalars().all()
    assert len(stocks) == 1
    assert stocks[0].store_id == seeded_catalog["store_id"]
    assert stocks[0].quantity == 0


@pytest.mark.asyncio
async def test_create_product_duplicate_name_returns_409(client, seeded_catalog):
    await _create_product(client, seeded_catalog, name="Duplicate Bike")

    response = await _create_product(client, seeded_catalog, name="Duplicate Bike")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_product_invalid_price_returns_422(client, seeded_catalog):
    response = await client.post(
        "/products/",
        json={
            "product_name": "Bad Price Bike",
            "brand_id": seeded_catalog["brand_id"],
            "category_id": seeded_catalog["category_id"],
            "model_year": 2026,
            "list_price": "0.00",
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# list  GET /products/
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_products_returns_200(client, seeded_catalog):
    await _create_product(client, seeded_catalog, name="Bike A")
    await _create_product(client, seeded_catalog, name="Bike B")

    response = await client.get("/products/")

    assert response.status_code == 200
    names = [p["product_name"] for p in response.json()]
    assert "Bike A" in names
    assert "Bike B" in names


# ---------------------------------------------------------------------------
# get single  GET /products/{product_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_product_by_id_returns_200(client, seeded_catalog):
    create_resp = await _create_product(client, seeded_catalog)
    product_id = create_resp.json()["product_id"]

    response = await client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["product_id"] == product_id


@pytest.mark.asyncio
async def test_get_product_nonexistent_returns_404(client):
    response = await client.get("/products/99999")

    assert response.status_code == 404
    assert response.json()["error"] == "ENTITY_NOT_FOUND"


# ---------------------------------------------------------------------------
# search  GET /products/search/by-name
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_product_by_name_returns_200(client, seeded_catalog):
    await _create_product(client, seeded_catalog, name="Mountain Fury")

    response = await client.get(
        "/products/search/by-name", params={"product_name": "Mountain Fury"}
    )

    assert response.status_code == 200
    assert response.json()["product_name"] == "Mountain Fury"


@pytest.mark.asyncio
async def test_search_product_by_name_not_found_returns_404(client):
    response = await client.get(
        "/products/search/by-name", params={"product_name": "Ghost Bike"}
    )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# update  PUT /products/{product_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_product_name_and_price_returns_200(client, seeded_catalog):
    create_resp = await _create_product(client, seeded_catalog)
    product_id = create_resp.json()["product_id"]

    response = await client.put(
        f"/products/{product_id}",
        json={"product_name": "Updated Bike", "list_price": "2000.00"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == "Updated Bike"
    assert Decimal(str(data["list_price"])) == Decimal("2000.00")


# ---------------------------------------------------------------------------
# activate / deactivate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deactivate_product_returns_200_and_is_active_false(client, seeded_catalog):
    create_resp = await _create_product(client, seeded_catalog)
    product_id = create_resp.json()["product_id"]

    response = await client.post(f"/products/{product_id}/deactivate")

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_activate_product_returns_200_and_is_active_true(client, seeded_catalog):
    create_resp = await _create_product(client, seeded_catalog)
    product_id = create_resp.json()["product_id"]
    await client.post(f"/products/{product_id}/deactivate")

    response = await client.post(f"/products/{product_id}/activate")

    assert response.status_code == 200
    assert response.json()["is_active"] is True


# ---------------------------------------------------------------------------
# delete  DELETE /products/{product_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_product_returns_200_and_removes_row(client, db_session, seeded_catalog):
    create_resp = await _create_product(client, seeded_catalog)
    product_id = create_resp.json()["product_id"]

    response = await client.delete(f"/products/{product_id}")

    assert response.status_code == 200

    row = (
        await db_session.execute(
            select(ProductModel).where(ProductModel.product_id == product_id)
        )
    ).scalar_one_or_none()
    assert row is None
