import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from jose import jwt

from src.infrastructure.configs import settings


def create_access_token(user_id: int, role: str) -> str:
    """Create a signed JWT access token."""
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "exp": datetime.now(UTC).replace(tzinfo=None)
        + timedelta(minutes=settings.auth.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.auth.secret_key, algorithm=settings.auth.algorithm)


def create_refresh_token(user_id: int) -> str:
    """Create a signed JWT refresh token."""
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": datetime.now(UTC).replace(tzinfo=None)
        + timedelta(days=settings.auth.refresh_token_expire_days),
    }
    return jwt.encode(payload, settings.auth.secret_key, algorithm=settings.auth.algorithm)


def decode_token(token: str) -> dict | None:
    """Decode and verify a JWT token; returns None on any error."""
    if not token:
        return None
    try:
        return jwt.decode(token, settings.auth.secret_key, algorithms=[settings.auth.algorithm])
    except Exception:
        return None


def hash_token(token: str) -> str:
    """Return the SHA-256 hex digest of a token string."""
    return hashlib.sha256(token.encode()).hexdigest()
