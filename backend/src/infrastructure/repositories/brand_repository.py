from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.brand import Brand
from src.domain.repositories.brand_repository import IBrandRepository
from src.infrastructure.database.models import BrandModel


class BrandRepository(IBrandRepository):
    """SQLAlchemy implementation of IBrandRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: BrandModel) -> Brand:
        return Brand(
            brand_id=model.brand_id,
            brand_name=model.brand_name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Brand) -> BrandModel:
        return BrandModel(
            brand_id=entity.brand_id,
            brand_name=entity.brand_name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, brand: Brand) -> Brand:
        """Persist a new brand and return the DB-assigned entity."""
        model = self._to_model(brand)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_brand_by_id(self, brand_id: int) -> Brand | None:
        """Return the brand with the given ID, or None."""
        result = await self._session.execute(
            select(BrandModel).where(BrandModel.brand_id == brand_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_brand_by_name(self, brand_name: str) -> Brand | None:
        """Return the brand with the given name, or None."""
        result = await self._session.execute(
            select(BrandModel).where(BrandModel.brand_name == brand_name)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Brand]:
        """Return a paginated list of all brands."""
        result = await self._session.execute(select(BrandModel).offset(skip).limit(limit))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, brand: Brand) -> Brand:
        """Flush brand changes to the DB and return the refreshed entity."""
        result = await self._session.execute(
            select(BrandModel).where(BrandModel.brand_id == brand.brand_id)
        )
        model = result.scalar_one()
        model.brand_name = brand.brand_name
        model.is_active = brand.is_active
        model.updated_at = brand.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, brand_id: int) -> bool:
        """Delete the brand row. Returns True if a row was actually removed."""
        result = await self._session.execute(
            select(BrandModel).where(BrandModel.brand_id == brand_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
