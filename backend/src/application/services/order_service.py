from src.application.dtos.order_dto import (
    CreateOrderCommand,
    CheckoutOrderCommand,
    OrderDto,
    UpdateOrderCommand,
    OrderStatus,
)
from src.application.services.customer_service import CustomerService
from src.application.services.staff_service import StaffService
from src.application.services.stock_service import StockService
from src.application.services.store_service import StoreService
from src.domain.entities.order import Order
from src.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
)
from src.domain.repositories.order_repository import IOrderRepository
from src.domain.repositories.orderitem_repository import (
    IOrderItemRepository,
)

from datetime import datetime, timezone
class OrderService:
    """
    Application service responsible for order workflows.

    Order lifecycle:
    - PENDING     -> cart
    - PROCESSING  -> paid/processing
    - SHIPPED
    - COMPLETED
    - CANCELLED
    """

    def __init__(
        self,
        order_repo: IOrderRepository,
        order_item_repo: IOrderItemRepository,
        customer_service: CustomerService,
        store_service: StoreService,
        staff_service: StaffService,
        stock_service: StockService,
    ) -> None:
        self._order_repo = order_repo
        self._order_item_repo = order_item_repo

        self._customer_service = customer_service
        self._store_service = store_service
        self._staff_service = staff_service
        self._stock_service = stock_service

    async def _get_existing_order(
        self,
        order_id: int,
    ) -> Order:
        """Get existing order or raise 404."""

        order = await self._order_repo.get_order_by_id(
            order_id
        )

        if not order:
            raise EntityNotFoundError(
                "Order",
                order_id,
            )

        return order

    async def create_order(
        self,
        command: CreateOrderCommand,
    ) -> OrderDto:
        """
        Create empty pending order.

        This acts as shopping cart.
        """

        await self._customer_service.check_customer_exist(
            command.customer_id
        )
        store_id = 1
        staff_id = 1
        order = Order(
            customer_id=command.customer_id,
            order_status=OrderStatus.PENDING,
            required_date=None,
            shipped_date=None,
            store_id=store_id,
            staff_id=staff_id,
        )

        created = await self._order_repo.create(
            order
        )
        return OrderDto.model_validate(created)

    async def checkout_order(
        self,
        order_id: int,
        command: CheckoutOrderCommand,
    ) -> OrderDto:
        """
        Checkout pending order.

        Flow:
        1. Validate order exists
        2. Validate order has items
        3. Validate stock availability
        4. Assign store
        5. Assign staff
        6. Deduct stock
        7. Update order status
        """

        order = await self._get_existing_order(
            order_id
        )

        if order.order_status != OrderStatus.PENDING:
            raise BusinessRuleViolationError(
                "Only pending orders can be checked out."
            )

        items = await self._order_item_repo.get_order_items_by_order_id(
            order_id
        )

        if not items:
            raise BusinessRuleViolationError(
                "Cannot checkout empty order."
            )

        #
        # TEMPORARY assignment strategy
        #
        assigned_store_id = 1
        assigned_staff_id = 1

        await self._store_service.check_store_exist(
            assigned_store_id
        )

        await self._staff_service.check_staff_exist(
            assigned_staff_id
        )

        #
        # Validate stock
        #
        for item in items:
            stock = await self._stock_service.get_stock_by_id(
                assigned_store_id,
                item.product_id,
            )

            if stock.quantity < item.quantity:
                raise BusinessRuleViolationError(
                    (
                        f"Insufficient stock for "
                        f"product '{item.product_id}'. "
                        f"Available: {stock.quantity}, "
                        f"requested: {item.quantity}."
                    )
                )

        #
        # Deduct stock
        #
        for item in items:
            await self._stock_service.adjust_stock(
                store_id=assigned_store_id,
                product_id=item.product_id,
                delta=-item.quantity,
            )

        #
        # Update order
        #
        order.update_information(
            order_status=OrderStatus.PROCESSING,
            order_date=datetime.now(timezone.utc).replace(tzinfo=None),
            required_date=command.required_date,
            store_id=assigned_store_id,
            staff_id=assigned_staff_id,
        )

        updated = await self._order_repo.update(
            order
        )

        return OrderDto.model_validate(updated)

    async def get_order_by_id(
        self,
        order_id: int,
    ) -> OrderDto:
        """Get order by ID."""

        order = await self._get_existing_order(
            order_id
        )

        return OrderDto.model_validate(order)

    async def get_orders_by_customer_id(
        self,
        customer_id: int,
    ) -> list[OrderDto]:
        """Get all orders by customer."""

        await self._customer_service.check_customer_exist(
            customer_id
        )

        orders = await self._order_repo.get_orders_by_customer_id(
            customer_id
        )

        return [
            OrderDto.model_validate(order)
            for order in orders
        ]

    async def list_all_orders(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[OrderDto]:
        """List paginated orders."""

        orders = await self._order_repo.list_all(
            skip,
            limit,
        )

        return [
            OrderDto.model_validate(order)
            for order in orders
        ]

    async def update_order(
        self,
        order_id: int,
        command: UpdateOrderCommand,
    ) -> OrderDto:
        """Update order."""

        order = await self._get_existing_order(
            order_id
        )

        order.update_information(
            order_status=command.order_status,
            required_date=command.required_date,
            shipped_date=command.shipped_date,
        )

        updated = await self._order_repo.update(
            order
        )

        return OrderDto.model_validate(updated)

    async def delete_order(
        self,
        order_id: int,
    ) -> OrderDto:
        """Delete order."""

        order = await self._get_existing_order(
            order_id
        )

        await self._order_repo.delete(
            order_id
        )

        return OrderDto.model_validate(order)

    async def check_order_exist(
        self,
        order_id: int,
    ) -> bool:
        """Validate order existence."""

        await self._get_existing_order(
            order_id
        )

        return True