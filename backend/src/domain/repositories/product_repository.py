from abc import ABC, abstractmethod
from src.domain.entities.product import Product
from typing import List, Optional


class IProductRepository(ABC):
    """Abstract interface for Product repository.
    
    This interface defines the contract for product data access operations.
    Implementations must be provided in the Infrastructure layer.
    """

    @abstractmethod
    async def create(self, product: Product) -> Product:
        """
        Adds a new product to the repository.
        
        Args:
            product (Product): The product to add.
        
        Returns:
            Product: The added product.
        """
        pass

    @abstractmethod
    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Retrieves a product by its ID.
        
        Args:
            product_id (int): The ID of the product to retrieve.
        
        Returns:
            Optional[Product]: The retrieved product, or None if not found.
        """
        pass

    @abstractmethod
    async def get_product_by_name(self, product_name: str) -> Optional[Product]:
        """
        Retrieves a product by its name.
        
        Args:
            product_name (str): The name of the product to retrieve.
        
        Returns:
            Optional[Product]: The retrieved product, or None if not found.
        """
        pass

    @abstractmethod
    async def search_by_name(self, name: str) -> List[Product]:
        """
        Retrieves products whose name contains the given search term.

        Args:
            name (str): The search term to match against product names.

        Returns:
            List[Product]: Products whose name contains the search term.
        """
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Retrieves all products from the repository.
        
        Args:
            skip (int): The number of products to skip.
            limit (int): The maximum number of products to retrieve.
        
        Returns:
            list[Product]: A list of all products.
        """
        pass

    @abstractmethod
    async def update(self, product: Product) -> Product:
        """
        Updates an existing product in the repository.
        
        Args:
            product (Product): The product to update.
        
        Returns:
            Product: The updated product.
        """
        pass

    @abstractmethod
    async def delete(self, product_id: int) -> bool:
        """
        Deletes a product from the repository.
        
        Args:
            product_id (int): The ID of the product to delete.
        """
        pass