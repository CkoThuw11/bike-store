from abc import ABC, abstractmethod
from src.domain.entities.category import Category
from typing import List, Optional

class ICategoryRepository(ABC):
    """Contract for Category persistence operations."""

    @abstractmethod
    async def create(self, category: Category) -> Category:
        """Persist a new category and return it with its assigned ID."""
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Return the category with the given ID, or None if not found."""
        pass

    @abstractmethod
    async def get_category_by_name(self, category_name: str) -> Optional[Category]:
        """Return the category with the given name, or None if not found."""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """Return a paginated list of all categories."""
        pass

    @abstractmethod
    async def update(self, category: Category) -> Category:
        """Persist changes to an existing category and return the updated entity."""
        pass

    @abstractmethod
    async def delete(self, category_id: int) -> bool:
        """Delete the category with the given ID. Returns True if a row was removed."""
        pass
