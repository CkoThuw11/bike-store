from abc import ABC, abstractmethod
from src.domain.entities.brand import Brand
from typing import List, Optional

class IBrandRepository(ABC):
    """Contract for Brand persistence operations."""

    @abstractmethod
    async def create(self, brand: Brand) -> Brand:
        """Persist a new brand and return it with its assigned ID."""
        pass

    @abstractmethod
    async def get_brand_by_id(self, brand_id: int) -> Optional[Brand]:
        """Return the brand with the given ID, or None if not found."""
        pass

    @abstractmethod
    async def get_brand_by_name(self, brand_name: str) -> Optional[Brand]:
        """Return the brand with the given name, or None if not found."""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Brand]:
        """Return a paginated list of all brands."""
        pass

    @abstractmethod
    async def update(self, brand: Brand) -> Brand:
        """Persist changes to an existing brand and return the updated entity."""
        pass

    @abstractmethod
    async def delete(self, brand_id: int) -> bool:
        """Delete the brand with the given ID. Returns True if a row was removed."""
        pass
