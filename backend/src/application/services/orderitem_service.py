from src.application.dtos.order_item_dto import (
    CreateOrderItemCommand,
    OrderItemDto,
    UpdateOrderItemCommand,
)
from src.application.services.order_service import OrderService
from src.application.services.product_service import ProductService
from src.domain.entities.order_item import OrderItem
from src.domain.exceptions import (
    DomainValidationException,
    EntityNotFoundError,
)
from src.domain.repositories.orderitem_repository import IOrderItemRepository


class OrderItemService:
    """Application service responsible for order items."""

    def __init__(
        self,
        order_item_repo: IOrderItemRepository,
        order_service: OrderService,
        product_service: ProductService,
    ) -> None:
        self._order_item_repo = order_item_repo
        self._order_service = order_service
        self._product_service = product_service

    async def create_order_item(
        self,
        command: CreateOrderItemCommand,
    ) -> OrderItemDto:
        """Create order item."""

        await self._order_service.check_order_exist(command.order_id)

        product = await self._product_service.get_product_by_id(command.product_id)

        order_item = OrderItem(
            order_id=command.order_id,
            product_id=command.product_id,
            quantity=command.quantity,
            list_price=product.list_price,
            discount=command.discount,
        )

        created = await self._order_item_repo.create(order_item)

        return OrderItemDto.model_validate(created)

    async def get_item_by_order_product_id(
        self,
        order_id: int,
        product_id: int,
    ) -> OrderItemDto:
        """Return order item by composite key."""

        item = await self._order_item_repo.get_order_item_by_order_product_id(
            order_id,
            product_id,
        )

        if not item:
            raise EntityNotFoundError(
                "OrderItem",
                {
                    "order_id": order_id,
                    "product_id": product_id,
                },
            )

        return OrderItemDto.model_validate(item)

    async def list_items_by_order_id(
        self,
        order_id: int,
    ) -> list[OrderItemDto]:
        """Return all order items for order."""

        await self._order_service.check_order_exist(order_id)

        items = await self._order_item_repo.get_order_items_by_order_id(order_id)

        return [OrderItemDto.model_validate(item) for item in items]

    async def list_all_order_items(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[OrderItemDto]:
        """Return paginated order items."""

        items = await self._order_item_repo.list_all(
            skip,
            limit,
        )

        return [OrderItemDto.model_validate(item) for item in items]

    async def update_order_item(
        self,
        order_id: int,
        product_id: int,
        command: UpdateOrderItemCommand,
    ) -> OrderItemDto:
        """Update existing order item."""

        item = await self._order_item_repo.get_order_item_by_order_product_id(
            order_id,
            product_id,
        )

        if not item:
            raise EntityNotFoundError(
                "OrderItem",
                {
                    "order_id": order_id,
                    "product_id": product_id,
                },
            )

        if not command.model_fields_set:
            raise DomainValidationException("At least one field must be provided for update")

        item.update_information(
            quantity=command.quantity,
        )

        updated = await self._order_item_repo.update(item)

        return OrderItemDto.model_validate(updated)

    async def delete_order_item(
        self,
        order_id: int,
        product_id: int,
    ) -> OrderItemDto:
        """Hard delete order item."""

        item = await self._order_item_repo.get_order_item_by_order_product_id(
            order_id,
            product_id,
        )

        if not item:
            raise EntityNotFoundError(
                "OrderItem",
                {
                    "order_id": order_id,
                    "product_id": product_id,
                },
            )
        if item.item_id is None:
            raise EntityNotFoundError("OrderItem", {"order_id": order_id, "product_id": product_id})

        await self._order_item_repo.delete(item.item_id)

        return OrderItemDto.model_validate(item)
