from abc import ABC, abstractmethod

from src.domain.entities.customer import Customer


class ICustomerRepository(ABC):
    """Contract for Customer persistence operations."""

    @abstractmethod
    async def create(self, customer: Customer) -> Customer:
        """Persist a new customer and return it with its assigned ID."""
        pass

    @abstractmethod
    async def get_customer_by_id(self, customer_id: int) -> Customer | None:
        """Return the customer with the given ID, or None if not found."""
        pass

    @abstractmethod
    async def get_customer_by_email(self, email: str) -> Customer | None:
        """Return the customer with the given email, or None if not found."""
        pass

    @abstractmethod
    async def get_customer_by_name(self, first_name: str) -> Customer | None:
        """Return a single customer matching the given first name, or None."""
        pass

    @abstractmethod
    async def search_by_name(self, name: str) -> list[Customer]:
        """Return all customers whose first or last name contains the search term."""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Customer]:
        """Return a paginated list of all customers."""
        pass

    @abstractmethod
    async def update(self, customer: Customer) -> Customer:
        """Persist changes to an existing customer and return the updated entity."""
        pass

    @abstractmethod
    async def delete(self, customer_id: int) -> bool:
        """Delete the customer with the given ID. Returns True if a row was removed."""
        pass
