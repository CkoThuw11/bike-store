from pydantic import BaseModel, EmailStr, field_validator
from src.domain.entities.user import Role

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.CUSTOMER

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com",
                "password": "Secret123",
            }
        }
    }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com",
                "password": "Secret123",
            }
        }
    }


class UserResponse(BaseModel):
    user_id: int
    email: str
    role: Role
    is_active: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "email": "john@example.com",
                "role": "CUSTOMER",
                "is_active": True,
            }
        }
    }


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Registration successful",
                "user": {
                    "user_id": 1,
                    "email": "john@example.com",
                    "role": "CUSTOMER",
                    "is_active": True,
                }
            }
        }
    }


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
            }
        }
    }


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
            }
        }
    }


class MessageResponse(BaseModel):
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {"message": "Logged out successfully"}
        }
    }


class ErrorResponse(BaseModel):
    error: str
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "TOKEN_EXPIRED",
                "message": "Access token has expired",
            }
        }
    }