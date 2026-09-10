import pytest

pytestmark = [pytest.mark.e2e]

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
REFRESH_URL = "/auth/refresh"
LOGOUT_URL = "/auth/logout"


def _register_payload(
    email="test@example.com",
    password="Secret123",
    username="testuser",
    fullname="Test User",
) -> dict:
    return {
        "email": email,
        "password": password,
        "username": username,
        "fullname": fullname,
    }


@pytest.mark.asyncio
async def test_register_creates_customer_by_default(client):
    response = await client.post(REGISTER_URL, json=_register_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["role"] == "CUSTOMER"


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(client):
    payload = _register_payload()
    await client.post(REGISTER_URL, json=payload)

    response = await client.post(
        REGISTER_URL,
        json={**payload, "username": "other", "fullname": "Other User"},
    )

    assert response.status_code == 409
    assert response.json()["error"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_login_returns_access_and_refresh_tokens(client):
    await client.post(REGISTER_URL, json=_register_payload())

    response = await client.post(
        LOGIN_URL,
        json={"email": "test@example.com", "password": "Secret123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_pair"]["access_token"]
    assert data["token_pair"]["refresh_token"]
    assert "refreshToken" in response.cookies


@pytest.mark.asyncio
async def test_login_rejects_wrong_password(client):
    await client.post(REGISTER_URL, json=_register_payload())

    response = await client.post(
        LOGIN_URL,
        json={"email": "test@example.com", "password": "WrongPass"},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_refresh_without_cookie_returns_401(client):
    """Regression: was raising ValueError (500) — must return 401 TOKEN_MISSING."""
    response = await client.post(REFRESH_URL)

    assert response.status_code == 401
    assert response.json()["error"] == "TOKEN_MISSING"


@pytest.mark.asyncio
async def test_refresh_with_valid_cookie_rotates_token(client):
    await client.post(REGISTER_URL, json=_register_payload())
    login_resp = await client.post(
        LOGIN_URL,
        json={"email": "test@example.com", "password": "Secret123"},
    )
    old_refresh = login_resp.json()["token_pair"]["refresh_token"]

    response = await client.post(
        REFRESH_URL,
        cookies={"refreshToken": old_refresh},
    )

    assert response.status_code == 200
    new_pair = response.json()["token_pair"]
    assert new_pair["access_token"]
    assert new_pair["refresh_token"] != old_refresh


@pytest.mark.asyncio
async def test_logout_clears_cookie(client):
    await client.post(REGISTER_URL, json=_register_payload())
    login_resp = await client.post(
        LOGIN_URL,
        json={"email": "test@example.com", "password": "Secret123"},
    )
    refresh_token = login_resp.json()["token_pair"]["refresh_token"]

    response = await client.post(
        LOGOUT_URL,
        cookies={"refreshToken": refresh_token},
    )

    assert response.status_code == 204
