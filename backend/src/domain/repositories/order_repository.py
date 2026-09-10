from abc import ABC, abstractmethod

from src.domain.entities.order import Order


class IOrderRepository(ABC):
    """Contract for Order persistence operations."""

    @abstractmethod
    async def create(self, order: Order) -> Order:
        """Persist a new order and return it with its assigned ID."""
        pass

    @abstractmethod
    async def get_order_by_id(self, order_id: int) -> Order | None:
        """Return the order with the given ID, or None if not found."""
        pass

    @abstractmethod
    async def get_orders_by_customer_id(self, customer_id: int) -> list[Order]:
        """Return all orders placed by the given customer."""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Order]:
        """Return a paginated list of all orders."""
        pass

    @abstractmethod
    async def update(self, order: Order) -> Order:
        """Persist changes to an existing order and return the updated entity."""
        pass

    @abstractmethod
    async def delete(self, order_id: int) -> bool:
        """Delete the order with the given ID. Returns True if a row was removed."""
        pass
