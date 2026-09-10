from datetime import timedelta

from src.application.dtos.auth_dto import (
    LoginResponseDTO,
    RefreshTokenResponseDTO,
    RegisterResponseDTO,
    TokenPairDTO,
    UserDTO,
)
from src.application.utils.password import (
    hash_password,
    verify_password,
)
from src.application.utils.token import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)
from src.domain.entities.refresh_token import (
    RefreshToken,
    utc_now,
)
from src.domain.entities.user import (
    Role,
    User,
)
from src.domain.exceptions import (
    BusinessRuleViolationError,
    EmailAlreadyExistsError,
    EntityNotFoundError,
    InvalidAccountStatusException,
    InvalidCredentialsException,
    SecurityBreachException,
    TokenExpiredException,
    TokenInvalidError,
)
from src.domain.repositories.refresh_token_repository import (
    IRefreshTokenRepository,
)
from src.domain.repositories.user_repository import (
    IUserRepository,
)
from src.infrastructure.configs import settings


class AuthService:
    """Authentication application service."""

    def __init__(
        self,
        user_repo: IUserRepository,
        token_repo: IRefreshTokenRepository,
    ):
        self._user_repo = user_repo
        self._token_repo = token_repo

    async def register(
        self,
        email: str,
        password: str,
        username: str,
        fullname: str,
        role: Role = Role.CUSTOMER,
    ) -> RegisterResponseDTO:
        """Register new user."""

        existing_user = await self._user_repo.get_by_email(email)

        if existing_user:
            raise EmailAlreadyExistsError(email)

        user = User(
            email=email,
            password_hash=hash_password(password),
            username=username,
            fullname=fullname,
            role=role,
        )

        created_user = await self._user_repo.create(user)

        return RegisterResponseDTO(
            user=UserDTO.model_validate(created_user)
        )

    async def login(
        self,
        email: str,
        password: str,
    ) -> LoginResponseDTO:
        """Authenticate user and issue tokens."""

        user = await self._user_repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsException()

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise InvalidCredentialsException()

        if user.user_id is None:
            raise BusinessRuleViolationError(
                "Persisted user must have user_id"
            )

        if not user.is_valid_for_login():
            raise InvalidAccountStatusException(
                user.user_id
            )

        access_token = create_access_token(
            user.user_id,
            user.role.value,
        )

        raw_refresh_token = create_refresh_token(
            user.user_id,
        )

        refresh_token = RefreshToken(
            user_id=user.user_id,
            token_hash=hash_token(raw_refresh_token),
            expires_at=(
                utc_now()
                + timedelta(days=settings.auth.refresh_token_expire_days)
            ),
        )

        await self._token_repo.save(refresh_token)

        return LoginResponseDTO(
            user=UserDTO.model_validate(user),
            token_pair=TokenPairDTO(
                access_token=access_token,
                refresh_token=raw_refresh_token,
                expires_in=settings.auth.access_token_expire_minutes * 60,
            ),
        )

    async def refresh_access_token(
        self,
        raw_refresh_token: str,
    ) -> RefreshTokenResponseDTO:
        """Refresh access token using refresh token rotation."""

        payload = decode_token(raw_refresh_token)

        if not payload:
            raise TokenInvalidError()

        if payload.get("type") != "refresh":
            raise TokenInvalidError()

        token_hash = hash_token(raw_refresh_token)

        stored_token = await self._token_repo.get_by_hash(
            token_hash
        )

        if not stored_token:
            raise TokenInvalidError()

        if stored_token.user_id is None:
            raise BusinessRuleViolationError(
                "Persisted refresh token must have user_id"
            )

        if stored_token.is_revoked:
            raise SecurityBreachException(
                user_id=stored_token.user_id,
                reason="Revoked refresh token reuse detected",
            )

        if stored_token.is_expired():
            raise TokenExpiredException()

        user = await self._user_repo.get_by_id(
            stored_token.user_id
        )

        if not user:
            raise EntityNotFoundError(
                "User",
                stored_token.user_id,
            )

        if user.user_id is None:
            raise BusinessRuleViolationError(
                "Persisted user must have user_id"
            )

        if not user.is_valid_for_login():
            raise InvalidAccountStatusException(
                user.user_id
            )

        # Rotate old refresh token
        await self._token_repo.revoke_by_hash(
            token_hash
        )

        # Generate new refresh token
        new_raw_refresh_token = create_refresh_token(
            user.user_id
        )

        new_refresh_token = RefreshToken(
            user_id=user.user_id,
            token_hash=hash_token(
                new_raw_refresh_token
            ),
            expires_at=(
                utc_now()
                + timedelta(days=settings.auth.refresh_token_expire_days)
            ),
        )

        await self._token_repo.save(
            new_refresh_token
        )

        return RefreshTokenResponseDTO(
            token_pair=TokenPairDTO(
                access_token=create_access_token(
                    user.user_id,
                    user.role.value,
                ),
                refresh_token=new_raw_refresh_token,
                expires_in=settings.auth.access_token_expire_minutes * 60,
            ),
        )

    async def logout(
        self,
        raw_refresh_token: str,
    ) -> None:
        """Logout current device."""

        token_hash = hash_token(raw_refresh_token)

        await self._token_repo.revoke_by_hash(
            token_hash
        )

    async def logout_all_devices(
        self,
        user_id: int,
    ) -> None:
        """Logout all user devices."""

        await self._token_repo.revoke_all_by_user(
            user_id
        )