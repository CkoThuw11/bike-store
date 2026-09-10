from src.application.dtos.product_dto import (
    CreateProductCommand,
    ProductDto,
    UpdateProductCommand,
)
from src.application.services.brand_service import BrandService
from src.application.services.category_service import CategoryService
from src.domain.entities.product import Product
from src.domain.entities.stock import Stock
from src.domain.exceptions import (
    BusinessRuleViolationError,
    EntityAlreadyExistsException,
    EntityNotFoundError,
)
from src.domain.repositories.product_repository import IProductRepository
from src.domain.repositories.stock_repository import IStockRepository
from src.domain.repositories.store_repository import IStoreRepository


class ProductService:
    """Orchestrates product business workflows."""

    def __init__(
        self,
        product_repo: IProductRepository,
        stock_repo: IStockRepository,
        store_repo: IStoreRepository,
        brand_service: BrandService,
        category_service: CategoryService,
    ) -> None:
        self._product_repo = product_repo
        self._stock_repo = stock_repo
        self._store_repo = store_repo
        self._brand_service = brand_service
        self._category_service = category_service

    async def create_product(
        self,
        command: CreateProductCommand,
    ) -> ProductDto:
        """
        Create product workflow.

        Flow:
        1. Validate brand/category existence
        2. Validate uniqueness
        3. Create product
        4. Initialize stock for all stores
        """

        await self._brand_service.check_brand_exist(command.brand_id)
        await self._category_service.check_category_exist(command.category_id)

        existing = await self._product_repo.get_product_by_name(command.product_name)

        if existing:
            raise EntityAlreadyExistsException(
                "Product",
                command.product_name,
            )

        if command.list_price <= 0:
            raise BusinessRuleViolationError("Product price must be greater than 0.")

        product = Product(
            product_name=command.product_name,
            brand_id=command.brand_id,
            category_id=command.category_id,
            model_year=command.model_year,
            list_price=command.list_price,
        )

        created = await self._product_repo.create(product)

        stores = await self._store_repo.list_all()

        for store in stores:
            stock = Stock(
                store_id=store.store_id,
                product_id=created.product_id,
                quantity=0,
            )

            await self._stock_repo.create(stock)

        return ProductDto.model_validate(created)

    async def get_product_by_id(
        self,
        product_id: int,
    ) -> ProductDto:
        """Return product by ID."""

        product = await self._product_repo.get_product_by_id(product_id)

        if not product:
            raise EntityNotFoundError("Product", product_id)

        return ProductDto.model_validate(product)

    async def get_product_by_name(
        self,
        product_name: str,
    ) -> ProductDto:
        """Return product by name."""

        product = await self._product_repo.get_product_by_name(product_name)

        if not product:
            raise EntityNotFoundError("Product", product_name)

        return ProductDto.model_validate(product)

    async def search_products_by_name(self, name: str) -> list[ProductDto]:
        """Return products whose name contains the search term."""
        products = await self._product_repo.search_by_name(name)
        return [ProductDto.model_validate(p) for p in products]

    async def get_all_products(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProductDto]:
        """Return paginated products."""

        products = await self._product_repo.list_all(skip, limit)

        return [ProductDto.model_validate(product) for product in products]

    async def update_product(
        self,
        product_id: int,
        command: UpdateProductCommand,
    ) -> ProductDto:
        """
        Update product workflow.
        """

        product = await self._product_repo.get_product_by_id(product_id)

        if not product:
            raise EntityNotFoundError("Product", product_id)

        if command.product_name and command.product_name != product.product_name:
            conflicting = await self._product_repo.get_product_by_name(command.product_name)

            if conflicting:
                raise EntityAlreadyExistsException(
                    "Product",
                    command.product_name,
                )

        if command.brand_id and command.brand_id != product.brand_id:
            await self._brand_service.check_brand_exist(command.brand_id)

        if command.category_id and command.category_id != product.category_id:
            await self._category_service.check_category_exist(command.category_id)

        if command.list_price is not None and command.list_price <= 0:
            raise BusinessRuleViolationError("Product price must be greater than 0.")

        product.update_information(
            product_name=command.product_name,
            brand_id=command.brand_id,
            category_id=command.category_id,
            model_year=command.model_year,
            list_price=command.list_price,
        )

        updated = await self._product_repo.update(product)
        return ProductDto.model_validate(updated)

    async def deactivate_product(
        self,
        product_id: int,
    ) -> ProductDto:
        """
        Soft-delete product.
        """

        product = await self._product_repo.get_product_by_id(product_id)

        if not product:
            raise EntityNotFoundError("Product", product_id)

        if not product.is_active:
            raise BusinessRuleViolationError(f"Product '{product_id}' is already deactivated.")

        product.deactivate()

        updated = await self._product_repo.update(product)

        return ProductDto.model_validate(updated)

    async def activate_product(
        self,
        product_id: int,
    ) -> ProductDto:
        """
        Activate product.
        """

        product = await self._product_repo.get_product_by_id(product_id)

        if not product:
            raise EntityNotFoundError("Product", product_id)

        product.activate()

        updated = await self._product_repo.update(product)

        return ProductDto.model_validate(updated)

    async def delete_product(
        self,
        product_id: int,
    ) -> ProductDto:
        """Hard-delete a product; raises 422 if it is still active."""

        product = await self._product_repo.get_product_by_id(product_id)

        if not product:
            raise EntityNotFoundError("Product", product_id)

        if product.is_active:
            raise BusinessRuleViolationError(
                f"Product '{product.product_name}' is active and cannot be deleted. "
                "Deactivate it first."
            )

        for stock in await self._stock_repo.get_stock_by_product_id(product_id):
            if stock.store_id is not None:
                await self._stock_repo.delete(stock.store_id, product_id)

        await self._product_repo.delete(product_id)

        return ProductDto.model_validate(product)
