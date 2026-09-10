from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.domain.entities.user import Role


class RegisterCommand(BaseModel):
    """Command for user registration."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        strict=True,
    )

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    username: str = Field(min_length=3, max_length=30)
    fullname: str = Field(min_length=3, max_length=60)


class LoginCommand(BaseModel):
    """Command for login."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        strict=True,
    )

    email: EmailStr
    password: str


class RefreshAccessTokenCommand(BaseModel):
    """Command for refreshing access token."""

    model_config = ConfigDict(strict=True)

    refresh_token: str


class LogoutCommand(BaseModel):
    """Command for logout."""

    model_config = ConfigDict(strict=True)

    refresh_token: str



class UserDTO(BaseModel):
    """User response DTO."""

    model_config = ConfigDict(
        from_attributes=True,
        strict=True,
    )

    user_id: int
    email: str
    username: str
    fullname: str
    role: Role

    is_active: bool

    created_at: datetime
    updated_at: datetime


class RefreshTokenDTO(BaseModel):
    """Refresh token response DTO."""

    model_config = ConfigDict(
        from_attributes=True,
        strict=True,
    )

    token_id: int
    user_id: int

    expires_at: datetime

    is_revoked: bool
    is_active: bool

    created_at: datetime
    updated_at: datetime


class TokenPairDTO(BaseModel):
    """Token pair DTO."""

    model_config = ConfigDict(strict=True)

    access_token: str
    refresh_token: str

    expires_in: int


class RegisterResponseDTO(BaseModel):
    """Registration response DTO."""

    model_config = ConfigDict(strict=True)

    user: UserDTO


class LoginResponseDTO(BaseModel):
    """Login response DTO."""

    model_config = ConfigDict(strict=True)

    user: UserDTO
    token_pair: TokenPairDTO


class RefreshTokenResponseDTO(BaseModel):
    """Refresh token response DTO."""

    model_config = ConfigDict(strict=True)

    token_pair: TokenPairDTO