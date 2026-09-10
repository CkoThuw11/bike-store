from abc import ABC, abstractmethod

from src.domain.entities.store import Store


class IStoreRepository(ABC):
    """Abstract interface for Store repository.

    This interface defines the contract for store data access operations.
    Implementations must be provided in the Infrastructure layer.
    """

    @abstractmethod
    async def create(self, store: Store) -> Store:
        """
        Adds a new store to the repository.

        Args:
            store (Store): The store to add.

        Returns:
            Store: The added store.
        """
        pass

    @abstractmethod
    async def get_store_by_id(self, store_id: int) -> Store | None:
        """
        Retrieves a store by its ID.

        Args:
            store_id (int): The ID of the store to retrieve.

        Returns:
            Store: The retrieved store.
        """
        pass

    @abstractmethod
    async def get_store_by_name(self, store_name: str) -> Store | None:
        """
        Retrieves a store by its name.

        Args:
            store_name (str): The name of the store to retrieve.

        Returns:
            Store: The retrieved store.
        """
        pass

    @abstractmethod
    async def get_store_by_email(self, email: str) -> Store | None:
        """
        Retrieves a store by its email.

        Args:
            email (str): The email of the store to retrieve.

        Returns:
            Store: The retrieved store.
        """
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Store]:
        """
        Retrieves all stores from the repository.

        Args:
            skip (int): The number of stores to skip.
            limit (int): The maximum number of stores to retrieve.

        Returns:
            list[Store]: A list of all stores.
        """
        pass

    @abstractmethod
    async def update(self, store: Store) -> Store:
        """
        Updates an existing store in the repository.

        Args:
            store (Store): The store to update.

        Returns:
            Store: The updated store.
        """
        pass

    @abstractmethod
    async def delete(self, store_id: int) -> bool:
        """
        Deletes a store from the repository.

        Args:
            store_id (int): The ID of the store to delete.

        Returns:
            bool: True if the store was deleted successfully, False otherwise.
        """
        pass
