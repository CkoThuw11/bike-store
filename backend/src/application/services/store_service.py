from src.application.dtos.store_dto import CreateStoreCommand, StoreDto, UpdateStoreCommand
from src.domain.entities.store import Store
from src.domain.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundError,
)
from src.domain.repositories.store_repository import IStoreRepository


class StoreService:
    """Orchestrates all business logic related to physical store locations."""

    def __init__(self, store_repo: IStoreRepository) -> None:
        self._store_repo = store_repo

    async def create_store(self, command: CreateStoreCommand) -> StoreDto:
        """Create a new store, enforcing uniqueness on both name and email."""
        if await self._store_repo.get_store_by_email(command.email):
            raise EntityAlreadyExistsException("Store", command.email)
        if await self._store_repo.get_store_by_name(command.store_name):
            raise EntityAlreadyExistsException("Store", command.store_name)

        store = Store(
            store_name=command.store_name,
            phone=command.phone,
            email=command.email,
            street=command.street,
            city=command.city,
            state=command.state,
            zip_code=command.zip_code,
        )
        created = await self._store_repo.create(store)
        return StoreDto.model_validate(created)

    async def get_store_by_id(self, store_id: int) -> StoreDto:
        """Return a store by its ID, raising 404 if not found."""
        store = await self._store_repo.get_store_by_id(store_id)
        if not store:
            raise EntityNotFoundError("Store", store_id)
        return StoreDto.model_validate(store)

    async def get_store_by_name(self, store_name: str) -> StoreDto:
        """Return a store by its name, raising 404 if not found."""
        store = await self._store_repo.get_store_by_name(store_name)
        if not store:
            raise EntityNotFoundError("Store", store_name)
        return StoreDto.model_validate(store)

    async def get_all_stores(self, skip: int = 0, limit: int = 100) -> list[StoreDto]:
        """Return a paginated list of all stores."""
        stores = await self._store_repo.list_all(skip, limit)
        return [StoreDto.model_validate(s) for s in stores]

    async def update_store(self, store_id: int, command: UpdateStoreCommand) -> StoreDto:
        """Apply partial updates to an existing store, enforcing email/name uniqueness."""
        store = await self._store_repo.get_store_by_id(store_id)
        if not store:
            raise EntityNotFoundError("Store", store_id)

        if (
            command.email
            and command.email != store.email
            and await self._store_repo.get_store_by_email(command.email)
        ):
            raise EntityAlreadyExistsException("Store", command.email)

        if (
            command.store_name
            and command.store_name != store.store_name
            and await self._store_repo.get_store_by_name(command.store_name)
        ):
            raise EntityAlreadyExistsException("Store", command.store_name)

        store.update_information(
            store_name=command.store_name,
            phone=command.phone,
            email=command.email,
            street=command.street,
            city=command.city,
            state=command.state,
            zip_code=command.zip_code,
        )
        updated = await self._store_repo.update(store)
        return StoreDto.model_validate(updated)

    async def activate_store(self, store_id: int) -> StoreDto:
        """Activate a store location."""
        store = await self._store_repo.get_store_by_id(store_id)
        if not store:
            raise EntityNotFoundError("Store", store_id)

        store.activate()
        updated = await self._store_repo.update(store)
        return StoreDto.model_validate(updated)

    async def deactivate_store(self, store_id: int) -> StoreDto:
        """Deactivate a store location."""
        store = await self._store_repo.get_store_by_id(store_id)
        if not store:
            raise EntityNotFoundError("Store", store_id)

        store.deactivate()
        updated = await self._store_repo.update(store)
        return StoreDto.model_validate(updated)

    async def delete_store(self, store_id: int) -> StoreDto:
        """Hard-delete a store; raises 404 if not found."""
        store = await self._store_repo.get_store_by_id(store_id)
        if not store:
            raise EntityNotFoundError("Store", store_id)

        await self._store_repo.delete(store_id)
        return StoreDto.model_validate(store)

    async def check_store_exist(self, store_id: int) -> bool:
        """Assert the store exists; raises EntityNotFoundError otherwise."""
        store = await self._store_repo.get_store_by_id(store_id)
        if not store:
            raise EntityNotFoundError("Store", store_id)
        return True
