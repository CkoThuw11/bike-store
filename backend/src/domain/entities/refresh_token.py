from dataclasses import dataclass, field
from datetime import datetime

from .base_entity import BaseEntity, utc_now


@dataclass(kw_only=True)
class RefreshToken(BaseEntity):
    """Refresh token domain entity."""

    user_id: int
    token_hash: str
    expires_at: datetime

    is_revoked: bool = False

    token_id: int | None = field(default=None)

    def revoke(self) -> None:
        self.is_revoked = True
        self.touch()

    def is_expired(self) -> bool:
        return utc_now() >= self.expires_at

    def is_valid(self) -> bool:
        return (
            not self.is_revoked
            and not self.is_expired()
            and self.is_active
        )