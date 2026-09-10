import pytest

from src.application.services.auth_service import AuthService
from src.domain.entities.refresh_token import RefreshToken
from src.domain.entities.user import Role, User
from src.domain.exceptions import (
    EmailAlreadyExistsError,
    InvalidAccountStatusException,
    InvalidCredentialsException,
    SecurityBreachException,
    TokenInvalidError,
)

pytestmark = [pytest.mark.unit]


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: list[User] = []
        self._next_id = 1

    async def create(self, user: User) -> User:
        user.user_id = self._next_id
        self._next_id += 1
        self._users.append(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        return next((u for u in self._users if u.user_id == user_id), None)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users if u.email == email), None)

    async def update(self, user: User) -> User:
        return user

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self._users[skip : skip + limit]

    async def delete(self, user_id: int) -> bool:
        self._users = [u for u in self._users if u.user_id != user_id]
        return True


class InMemoryTokenRepository:
    def __init__(self) -> None:
        self._tokens: list[RefreshToken] = []

    async def save(self, token: RefreshToken) -> RefreshToken:
        self._tokens.append(token)
        return token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return next((t for t in self._tokens if t.token_hash == token_hash), None)

    async def revoke_by_hash(self, token_hash: str) -> None:
        for token in self._tokens:
            if token.token_hash == token_hash:
                token.is_revoked = True

    async def revoke_all_by_user(self, user_id: int) -> None:
        for token in self._tokens:
            if token.user_id == user_id:
                token.is_revoked = True


def make_service(
    user_repo: InMemoryUserRepository | None = None,
    token_repo: InMemoryTokenRepository | None = None,
) -> tuple[AuthService, InMemoryUserRepository, InMemoryTokenRepository]:
    user_repo = user_repo or InMemoryUserRepository()
    token_repo = token_repo or InMemoryTokenRepository()
    return AuthService(user_repo, token_repo), user_repo, token_repo


@pytest.mark.asyncio
async def test_register_defaults_to_customer_role():
    service, user_repo, _ = make_service()

    result = await service.register(
        email="user@example.com",
        password="Secret123",
        username="testuser",
        fullname="Test User",
    )

    assert result.user.email == "user@example.com"
    assert result.user.role == Role.CUSTOMER
    assert len(user_repo._users) == 1


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email():
    service, _, _ = make_service()

    await service.register(
        email="dupe@example.com",
        password="Secret123",
        username="user1",
        fullname="User One",
    )

    with pytest.raises(EmailAlreadyExistsError):
        await service.register(
            email="dupe@example.com",
            password="Other456",
            username="user2",
            fullname="User Two",
        )


@pytest.mark.asyncio
async def test_login_returns_token_pair():
    service, _, token_repo = make_service()

    await service.register(
        email="login@example.com",
        password="Secret123",
        username="loginuser",
        fullname="Login User",
    )

    result = await service.login(email="login@example.com", password="Secret123")

    assert result.token_pair.access_token
    assert result.token_pair.refresh_token
    assert result.token_pair.expires_in > 0
    assert len(token_repo._tokens) == 1


@pytest.mark.asyncio
async def test_login_rejects_wrong_password():
    service, _, _ = make_service()

    await service.register(
        email="login@example.com",
        password="Secret123",
        username="loginuser",
        fullname="Login User",
    )

    with pytest.raises(InvalidCredentialsException):
        await service.login(email="login@example.com", password="WrongPass")


@pytest.mark.asyncio
async def test_login_rejects_unknown_email():
    service, _, _ = make_service()

    with pytest.raises(InvalidCredentialsException):
        await service.login(email="nobody@example.com", password="Secret123")


@pytest.mark.asyncio
async def test_login_rejects_inactive_user():
    service, user_repo, _ = make_service()

    await service.register(
        email="inactive@example.com",
        password="Secret123",
        username="inactiveuser",
        fullname="Inactive User",
    )
    user_repo._users[0].is_active = False

    with pytest.raises(InvalidAccountStatusException):
        await service.login(email="inactive@example.com", password="Secret123")


@pytest.mark.asyncio
async def test_refresh_rotates_token():
    service, _, token_repo = make_service()

    await service.register(
        email="refresh@example.com",
        password="Secret123",
        username="refreshuser",
        fullname="Refresh User",
    )
    login_result = await service.login(email="refresh@example.com", password="Secret123")
    old_refresh = login_result.token_pair.refresh_token

    result = await service.refresh_access_token(old_refresh)

    assert result.token_pair.access_token
    assert result.token_pair.refresh_token != old_refresh
    # Old token must be revoked
    old_tokens = [t for t in token_repo._tokens if t.is_revoked]
    assert len(old_tokens) == 1


@pytest.mark.asyncio
async def test_refresh_rejects_invalid_token():
    service, _, _ = make_service()

    with pytest.raises(TokenInvalidError):
        await service.refresh_access_token("not-a-valid-token")


@pytest.mark.asyncio
async def test_refresh_rejects_revoked_token():
    service, _, token_repo = make_service()

    await service.register(
        email="reuse@example.com",
        password="Secret123",
        username="reuseuser",
        fullname="Reuse User",
    )
    login_result = await service.login(email="reuse@example.com", password="Secret123")
    raw_token = login_result.token_pair.refresh_token

    # Revoke it
    await service.refresh_access_token(raw_token)

    # Try to reuse the original revoked token — should raise SecurityBreachException
    with pytest.raises(SecurityBreachException):
        await service.refresh_access_token(raw_token)


@pytest.mark.asyncio
async def test_logout_revokes_token():
    service, _, token_repo = make_service()

    await service.register(
        email="logout@example.com",
        password="Secret123",
        username="logoutuser",
        fullname="Logout User",
    )
    login_result = await service.login(email="logout@example.com", password="Secret123")
    raw_token = login_result.token_pair.refresh_token

    await service.logout(raw_token)

    assert all(t.is_revoked for t in token_repo._tokens)
