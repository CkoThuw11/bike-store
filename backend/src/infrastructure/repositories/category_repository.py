from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.category import Category
from src.domain.repositories.category_repository import ICategoryRepository
from src.infrastructure.database.models import CategoryModel


class CategoryRepository(ICategoryRepository):
    """SQLAlchemy implementation of ICategoryRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: CategoryModel) -> Category:
        return Category(
            category_id=model.category_id,
            category_name=model.category_name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Category) -> CategoryModel:
        return CategoryModel(
            category_id=entity.category_id,
            category_name=entity.category_name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, category: Category) -> Category:
        """Persist a new category and return the DB-assigned entity."""
        model = self._to_model(category)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_category_by_id(self, category_id: int) -> Category | None:
        """Return the category with the given ID, or None."""
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.category_id == category_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_category_by_name(self, category_name: str) -> Category | None:
        """Return the category with the given name, or None."""
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.category_name == category_name)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Category]:
        """Return a paginated list of all categories."""
        result = await self._session.execute(select(CategoryModel).offset(skip).limit(limit))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, category: Category) -> Category:
        """Flush category changes to the DB and return the refreshed entity."""
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.category_id == category.category_id)
        )
        model = result.scalar_one()
        model.category_name = category.category_name
        model.is_active = category.is_active
        model.updated_at = category.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, category_id: int) -> bool:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.category_id == category_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
