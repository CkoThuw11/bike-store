from abc import ABC, abstractmethod

from src.domain.entities.refresh_token import RefreshToken


class IRefreshTokenRepository(ABC):
    @abstractmethod
    async def save(self, entity: RefreshToken) -> RefreshToken:
        pass

    @abstractmethod
    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        pass

    @abstractmethod
    async def revoke_by_hash(self, token_hash: str) -> None:
        """Set is_revoked = True — for logout"""
        pass

    @abstractmethod
    async def revoke_all_by_user(self, user_id: int) -> None:
        """Revoke all tokens — for logout all devices / password change"""
        pass
