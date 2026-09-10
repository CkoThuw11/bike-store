from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.store import Store
from src.domain.repositories.store_repository import IStoreRepository
from src.infrastructure.database.models import StoreModel


class StoreRepository(IStoreRepository):
    """SQLAlchemy implementation of IStoreRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: StoreModel) -> Store:
        return Store(
            store_id=model.store_id,
            store_name=model.store_name,
            phone=model.phone,
            email=model.email,
            street=model.street,
            city=model.city,
            state=model.state,
            zip_code=model.zip_code,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Store) -> StoreModel:
        return StoreModel(
            store_id=entity.store_id,
            store_name=entity.store_name,
            phone=entity.phone,
            email=entity.email,
            street=entity.street,
            city=entity.city,
            state=entity.state,
            zip_code=entity.zip_code,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, store: Store) -> Store:
        """Persist a new store and return the DB-assigned entity."""
        model = self._to_model(store)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_store_by_id(self, store_id: int) -> Store | None:
        """Return the store with the given ID, or None."""
        result = await self._session.execute(
            select(StoreModel).where(StoreModel.store_id == store_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_store_by_name(self, store_name: str) -> Store | None:
        """Return the store with the given name, or None."""
        result = await self._session.execute(
            select(StoreModel).where(StoreModel.store_name == store_name)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_store_by_email(self, email: str) -> Store | None:
        """Return the store with the given email, or None."""
        result = await self._session.execute(select(StoreModel).where(StoreModel.email == email))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Store]:
        """Return a paginated list of all stores."""
        result = await self._session.execute(select(StoreModel).offset(skip).limit(limit))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, store: Store) -> Store:
        """Flush store changes to the DB and return the refreshed entity."""
        result = await self._session.execute(
            select(StoreModel).where(StoreModel.store_id == store.store_id)
        )
        model = result.scalar_one()
        model.store_name = store.store_name
        model.phone = store.phone
        model.email = store.email
        model.street = store.street
        model.city = store.city
        model.state = store.state
        model.zip_code = store.zip_code
        model.updated_at = store.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, store_id: int) -> bool:
        """Delete the store row. Returns True if a row was actually removed."""
        result = await self._session.execute(
            select(StoreModel).where(StoreModel.store_id == store_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
