from abc import ABC, abstractmethod
from src.domain.entities.order_item import OrderItem
from typing import List, Optional


class IOrderItemRepository(ABC):
    """Contract for OrderItem persistence operations."""

    @abstractmethod
    async def create(self, order_item: OrderItem) -> OrderItem:
        """Persist a new order item and return it with its assigned ID."""
        pass

    @abstractmethod
    async def get_order_item_by_order_product_id(self, order_id: int, product_id: int) -> Optional[OrderItem]:
        """Return the item for the given (order_id, product_id) pair, or None."""
        pass

    @abstractmethod
    async def get_order_items_by_order_id(self, order_id: int) -> List[OrderItem]:
        """Return all line items belonging to the given order."""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[OrderItem]:
        """Return a paginated list of all order items."""
        pass

    @abstractmethod
    async def update(self, order_item: OrderItem) -> OrderItem:
        """Persist changes to an existing order item and return the updated entity."""
        pass

    @abstractmethod
    async def delete(self, item_id: int) -> bool:
        """Delete the order item with the given item_id. Returns True if a row was removed."""
        pass
