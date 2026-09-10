from src.application.dtos.stock_dto import (
    StockDto,
    UpdateStockCommand,
)
from src.application.services.product_service import ProductService
from src.application.services.store_service import StoreService
from src.domain.entities.stock import Stock
from src.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
)
from src.domain.repositories.stock_repository import IStockRepository


class StockService:
    """
    Application service responsible for inventory operations.

    Responsibilities:
    - Query stock
    - Update stock quantity
    - Adjust stock quantity

    Notes:
    - Stock records are initialized automatically during product creation.
    - This service does NOT create/delete stock records.
    """

    def __init__(
        self,
        stock_repo: IStockRepository,
        store_service: StoreService,
        product_service: ProductService,
    ) -> None:
        self._stock_repo = stock_repo
        self._store_service = store_service
        self._product_service = product_service

    async def _validate_store_and_product(
        self,
        store_id: int,
        product_id: int,
    ) -> None:
        """Validate store and product existence."""

        await self._store_service.check_store_exist(store_id)
        await self._product_service.get_product_by_id(product_id)

    async def _get_existing_stock(
        self,
        store_id: int,
        product_id: int,
    ) -> Stock:
        """
        Get existing stock entity.

        Raises:
            EntityNotFoundError: if stock record does not exist.
        """

        stock = await self._stock_repo.get_stock_by_id(
            store_id,
            product_id,
        )

        if not stock:
            raise EntityNotFoundError(
                "Stock",
                {
                    "store_id": store_id,
                    "product_id": product_id,
                },
            )

        return stock

    async def get_stock_by_id(
        self,
        store_id: int,
        product_id: int,
    ) -> StockDto:
        """Get stock by store and product."""

        await self._validate_store_and_product(
            store_id,
            product_id,
        )

        stock = await self._get_existing_stock(
            store_id,
            product_id,
        )

        return StockDto.model_validate(stock)

    async def get_stock_by_product_id(
        self,
        product_id: int,
    ) -> list[StockDto]:
        """Get all stock records for a product."""

        await self._product_service.get_product_by_id(product_id)

        stocks = await self._stock_repo.get_stock_by_product_id(
            product_id,
        )

        return [
            StockDto.model_validate(stock)
            for stock in stocks
        ]

    async def get_stock_by_store_id(
        self,
        store_id: int,
    ) -> list[StockDto]:
        """Get all stock records for a store."""

        await self._store_service.check_store_exist(store_id)

        stocks = await self._stock_repo.get_stock_by_store_id(
            store_id,
        )

        return [
            StockDto.model_validate(stock)
            for stock in stocks
        ]

    async def get_all_stock(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[StockDto]:
        """Get paginated stock list."""

        stocks = await self._stock_repo.list_all(
            skip,
            limit,
        )

        return [
            StockDto.model_validate(stock)
            for stock in stocks
        ]

    async def update_stock(
        self,
        store_id: int,
        product_id: int,
        command: UpdateStockCommand,
    ) -> StockDto:
        """
        Replace stock quantity directly.

        Typically used for:
        - admin correction
        - inventory recount
        """

        await self._validate_store_and_product(
            store_id,
            product_id,
        )

        stock = await self._get_existing_stock(
            store_id,
            product_id,
        )

        if command.quantity < 0:
            raise BusinessRuleViolationError(
                "Stock quantity cannot be negative."
            )

        stock.update_information(
            quantity=command.quantity,
        )

        updated_stock = await self._stock_repo.update(stock)

        return StockDto.model_validate(updated_stock)

    async def adjust_stock(
        self,
        store_id: int,
        product_id: int,
        delta: int,
    ) -> StockDto:
        """
        Adjust stock quantity incrementally.

        Examples:
        - +10 → warehouse received inventory
        - -2  → customer purchased product
        """

        await self._validate_store_and_product(
            store_id,
            product_id,
        )

        stock = await self._get_existing_stock(
            store_id,
            product_id,
        )

        new_quantity = stock.quantity + delta

        if new_quantity < 0:
            raise BusinessRuleViolationError(
                (
                    f"Insufficient stock for "
                    f"product '{product_id}' "
                    f"at store '{store_id}'. "
                    f"Available: {stock.quantity}, "
                    f"requested reduction: {abs(delta)}."
                )
            )

        stock.update_information(
            quantity=new_quantity,
        )

        updated_stock = await self._stock_repo.update(stock)

        return StockDto.model_validate(updated_stock)