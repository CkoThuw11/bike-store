from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.refresh_token import RefreshToken
from src.domain.repositories.refresh_token_repository import IRefreshTokenRepository
from src.infrastructure.database.models import RefreshTokenModel


class RefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            token_id=model.token_id,
            user_id=model.user_id,
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            is_revoked=model.is_revoked,
        )

    def _to_model(self, entity: RefreshToken) -> RefreshTokenModel:
        return RefreshTokenModel(
            token_id=entity.token_id,
            user_id=entity.user_id,
            token_hash=entity.token_hash,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
            is_revoked=entity.is_revoked,
        )

    async def save(self, entity: RefreshToken) -> RefreshToken:
        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def revoke_by_hash(self, token_hash: str) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
            .values(is_revoked=True)
        )
        await self._session.flush()

    async def revoke_all_by_user(self, user_id: int) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .values(is_revoked=True)
        )
        await self._session.flush()
