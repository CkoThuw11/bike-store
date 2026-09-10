import pytest

pytestmark = [pytest.mark.e2e]


@pytest.mark.asyncio
async def test_create_category_returns_201(client):
    response = await client.post("/categories/", json={"category_name": "Mountain Bikes"})

    assert response.status_code == 201
    data = response.json()
    assert data["category_id"] is not None
    assert data["category_name"] == "Mountain Bikes"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_list_categories_returns_200(client):
    await client.post("/categories/", json={"category_name": "Road Bikes"})

    response = await client.get("/categories/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_category_by_id_returns_200(client):
    create_resp = await client.post("/categories/", json={"category_name": "BMX"})
    category_id = create_resp.json()["category_id"]

    response = await client.get(f"/categories/{category_id}")

    assert response.status_code == 200
    assert response.json()["category_id"] == category_id


@pytest.mark.asyncio
async def test_activate_category_uses_correct_path_param(client):
    """Regression: route was /{brand_id}/activate — must be /{category_id}/activate."""
    create_resp = await client.post("/categories/", json={"category_name": "Cruisers"})
    category_id = create_resp.json()["category_id"]

    # Deactivate first
    deactivate_resp = await client.post(f"/categories/{category_id}/deactivate")
    assert deactivate_resp.status_code == 200
    assert deactivate_resp.json()["is_active"] is False

    # Activate using the correct path
    activate_resp = await client.post(f"/categories/{category_id}/activate")
    assert activate_resp.status_code == 200
    assert activate_resp.json()["is_active"] is True


@pytest.mark.asyncio
async def test_deactivate_category_uses_correct_path_param(client):
    """Regression: route was /{brand_id}/deactivate — must be /{category_id}/deactivate."""
    create_resp = await client.post("/categories/", json={"category_name": "Kids Bikes"})
    category_id = create_resp.json()["category_id"]

    response = await client.post(f"/categories/{category_id}/deactivate")

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_get_nonexistent_category_returns_404(client):
    response = await client.get("/categories/99999")

    assert response.status_code == 404
    assert response.json()["error"] == "ENTITY_NOT_FOUND"
