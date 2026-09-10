import pytest
from sqlalchemy import select

from src.infrastructure.database.models import BrandModel

pytestmark = [pytest.mark.e2e]


# ---------------------------------------------------------------------------
# create  POST /brands/
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_brand_returns_201_and_persists(client, db_session):
    response = await client.post("/brands/", json={"brand_name": "Trek"})

    assert response.status_code == 201
    data = response.json()
    assert data["brand_id"] is not None
    assert data["brand_name"] == "Trek"
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data

    row = (
        await db_session.execute(select(BrandModel).where(BrandModel.brand_id == data["brand_id"]))
    ).scalar_one()
    assert row.brand_name == "Trek"


@pytest.mark.asyncio
async def test_create_brand_duplicate_name_returns_409(client):
    await client.post("/brands/", json={"brand_name": "Specialized"})

    response = await client.post("/brands/", json={"brand_name": "Specialized"})

    assert response.status_code == 409


# ---------------------------------------------------------------------------
# list  GET /brands/
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_brands_returns_200_and_list(client):
    await client.post("/brands/", json={"brand_name": "Giant"})
    await client.post("/brands/", json={"brand_name": "Cannondale"})

    response = await client.get("/brands/")

    assert response.status_code == 200
    names = [b["brand_name"] for b in response.json()]
    assert "Giant" in names
    assert "Cannondale" in names


@pytest.mark.asyncio
async def test_list_brands_empty_returns_empty_list(client):
    response = await client.get("/brands/")

    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# get single  GET /brands/{brand_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_brand_by_id_returns_200(client):
    create_resp = await client.post("/brands/", json={"brand_name": "Scott"})
    brand_id = create_resp.json()["brand_id"]

    response = await client.get(f"/brands/{brand_id}")

    assert response.status_code == 200
    assert response.json()["brand_id"] == brand_id
    assert response.json()["brand_name"] == "Scott"


@pytest.mark.asyncio
async def test_get_brand_nonexistent_returns_404(client):
    response = await client.get("/brands/99999")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "ENTITY_NOT_FOUND"


# ---------------------------------------------------------------------------
# update  PUT /brands/{brand_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_brand_name_returns_200(client):
    create_resp = await client.post("/brands/", json={"brand_name": "OldName"})
    brand_id = create_resp.json()["brand_id"]

    response = await client.put(f"/brands/{brand_id}", json={"brand_name": "NewName"})

    assert response.status_code == 200
    assert response.json()["brand_name"] == "NewName"


@pytest.mark.asyncio
async def test_update_brand_to_duplicate_name_returns_409(client):
    await client.post("/brands/", json={"brand_name": "BrandA"})
    resp = await client.post("/brands/", json={"brand_name": "BrandB"})
    brand_b_id = resp.json()["brand_id"]

    response = await client.put(f"/brands/{brand_b_id}", json={"brand_name": "BrandA"})

    assert response.status_code == 409


# ---------------------------------------------------------------------------
# activate / deactivate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deactivate_brand_returns_200_and_is_active_false(client):
    resp = await client.post("/brands/", json={"brand_name": "ToDeactivate"})
    brand_id = resp.json()["brand_id"]

    response = await client.post(f"/brands/{brand_id}/deactivate")

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_activate_previously_deactivated_brand(client):
    resp = await client.post("/brands/", json={"brand_name": "ToReactivate"})
    brand_id = resp.json()["brand_id"]
    await client.post(f"/brands/{brand_id}/deactivate")

    response = await client.post(f"/brands/{brand_id}/activate")

    assert response.status_code == 200
    assert response.json()["is_active"] is True


# ---------------------------------------------------------------------------
# delete  DELETE /brands/{brand_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_inactive_brand_returns_200(client, db_session):
    resp = await client.post("/brands/", json={"brand_name": "ToDelete"})
    brand_id = resp.json()["brand_id"]
    await client.post(f"/brands/{brand_id}/deactivate")

    response = await client.delete(f"/brands/{brand_id}")

    assert response.status_code == 200

    row = (
        await db_session.execute(select(BrandModel).where(BrandModel.brand_id == brand_id))
    ).scalar_one_or_none()
    assert row is None


@pytest.mark.asyncio
async def test_delete_active_brand_returns_422(client):
    resp = await client.post("/brands/", json={"brand_name": "ActiveBrand"})
    brand_id = resp.json()["brand_id"]

    response = await client.delete(f"/brands/{brand_id}")

    assert response.status_code == 422
    assert response.json()["error"] == "BUSINESS_RULE_VIOLATION"
