from abc import ABC, abstractmethod
from src.domain.entities.stock import Stock
from typing import List, Optional


class IStockRepository(ABC):
    """Contract for Stock (inventory) persistence operations."""

    @abstractmethod
    async def create(self, stock: Stock) -> Stock:
        """Persist a new stock record and return it with its assigned ID."""
        pass

    @abstractmethod
    async def get_stock_by_id(self, store_id: int, product_id: int) -> Optional[Stock]:
        """Return the stock record for the given (store_id, product_id) pair, or None."""
        pass

    @abstractmethod
    async def get_stock_by_product_id(self, product_id: int) -> List[Stock]:
        """Return all stock records for the given product across all stores."""
        pass

    @abstractmethod
    async def get_stock_by_store_id(self, store_id: int) -> List[Stock]:
        """Return all stock records for the given store across all products."""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Stock]:
        """Return a paginated list of all stock records."""
        pass

    @abstractmethod
    async def update(self, stock: Stock) -> Stock:
        """Persist quantity/timestamp changes to an existing stock record."""
        pass

    @abstractmethod
    async def delete(self, store_id: int, product_id: int) -> bool:
        """Delete the stock record for the given (store_id, product_id). Returns True if removed."""
        pass
