from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Response,
)
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies.services import (
    get_auth_service,
)
from src.application.dtos.auth_dto import (
    LoginCommand,
    LoginResponseDTO,
    RefreshTokenResponseDTO,
    RegisterCommand,
    RegisterResponseDTO,
)
from src.application.services.auth_service import (
    AuthService,
)
from src.domain.exceptions import TokenMissingError

REFRESH_COOKIE_KEY = "refreshToken"
COOKIE_MAX_AGE = 7 * 24 * 60 * 60

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


def _set_refresh_cookie(
    response: Response,
    raw_refresh_token: str,
) -> None:
    """Attach refresh token cookie."""

    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=raw_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
    )


@router.post(
    "/register",
    response_model=RegisterResponseDTO,
    status_code=201,
)
async def register(
    command: RegisterCommand,
    service: AuthService = Depends(get_auth_service),
) -> RegisterResponseDTO:
    """Register new account."""

    return await service.register(
        email=command.email,
        password=command.password,
        username=command.username,
        fullname=command.fullname,
    )


@router.post(
    "/login",
    response_model=LoginResponseDTO,
)
async def login(
    command: LoginCommand,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> LoginResponseDTO:
    """Authenticate user."""

    result = await service.login(
        email=command.email,
        password=command.password,
    )

    _set_refresh_cookie(
        response,
        result.token_pair.refresh_token,
    )

    return result


@router.post(
    "/refresh",
    response_model=RefreshTokenResponseDTO,
)
async def refresh_access_token(
    response: Response,
    service: AuthService = Depends(get_auth_service),
    refresh_token: str | None = Cookie(
        default=None,
        alias=REFRESH_COOKIE_KEY,
    ),
) -> RefreshTokenResponseDTO:
    """Refresh access token."""

    if refresh_token is None:
        raise TokenMissingError()

    result = await service.refresh_access_token(refresh_token)

    _set_refresh_cookie(
        response,
        result.token_pair.refresh_token,
    )

    return result


@router.post(
    "/logout",
    status_code=204,
)
async def logout(
    response: Response,
    service: AuthService = Depends(get_auth_service),
    refresh_token: str | None = Cookie(
        default=None,
        alias=REFRESH_COOKIE_KEY,
    ),
) -> None:
    """Logout current device."""

    if refresh_token is None:
        return

    await service.logout(refresh_token)

    response.delete_cookie(key=REFRESH_COOKIE_KEY)


@router.post(
    "/login/swagger",
    include_in_schema=False,
)
async def login_swagger(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Swagger OAuth2 compatible login.
    """

    result = await service.login(
        email=form_data.username,
        password=form_data.password,
    )

    _set_refresh_cookie(
        response,
        result.token_pair.refresh_token,
    )

    return {
        "access_token": (result.token_pair.access_token),
        "token_type": "bearer",
    }
