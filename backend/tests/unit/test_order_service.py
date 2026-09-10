from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from src.application.dtos.order_dto import CheckoutOrderCommand, CreateOrderCommand
from src.application.services.order_service import OrderService
from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError

pytestmark = [pytest.mark.unit]

# ---------------------------------------------------------------------------
# In-memory fakes
# ---------------------------------------------------------------------------


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: list[Order] = []
        self._next_id = 1

    async def create(self, order: Order) -> Order:
        order.order_id = self._next_id
        self._next_id += 1
        self._orders.append(order)
        return order

    async def get_order_by_id(self, order_id: int) -> Order | None:
        return next((o for o in self._orders if o.order_id == order_id), None)

    async def get_orders_by_customer_id(self, customer_id: int) -> list[Order]:
        return [o for o in self._orders if o.customer_id == customer_id]

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Order]:
        return self._orders[skip : skip + limit]

    async def update(self, order: Order) -> Order:
        return order

    async def delete(self, order_id: int) -> bool:
        self._orders = [o for o in self._orders if o.order_id != order_id]
        return True


class InMemoryOrderItemRepository:
    def __init__(self, items: list[OrderItem] | None = None) -> None:
        self._items: list[OrderItem] = items or []

    async def get_order_items_by_order_id(self, order_id: int) -> list[OrderItem]:
        return [i for i in self._items if i.order_id == order_id]

    async def create(self, item: OrderItem) -> OrderItem:
        self._items.append(item)
        return item

    async def get_order_item_by_order_product_id(
        self, order_id: int, product_id: int
    ) -> OrderItem | None:
        return next(
            (i for i in self._items if i.order_id == order_id and i.product_id == product_id),
            None,
        )

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[OrderItem]:
        return self._items[skip : skip + limit]

    async def update(self, item: OrderItem) -> OrderItem:
        return item

    async def delete(self, item_id: int) -> bool:
        self._items = [i for i in self._items if i.item_id != item_id]
        return True


class FakeCustomerService:
    async def check_customer_exist(self, customer_id: int) -> bool:
        return True


class FakeStoreService:
    async def check_store_exist(self, store_id: int) -> bool:
        return True


class FakeStaffService:
    async def check_staff_exist(self, staff_id: int) -> bool:
        return True


class FakeStockService:
    def __init__(self, qty: int = 10) -> None:
        self._qty = qty
        self.adjustments: list[tuple[int, int, int]] = []

    async def get_stock_by_id(self, store_id: int, product_id: int):
        return SimpleNamespace(quantity=self._qty)

    async def adjust_stock(self, store_id: int, product_id: int, delta: int) -> None:
        self.adjustments.append((store_id, product_id, delta))


def make_service(
    order_repo=None,
    order_item_repo=None,
    stock_service=None,
):
    order_repo = order_repo or InMemoryOrderRepository()
    order_item_repo = order_item_repo or InMemoryOrderItemRepository()
    stock_service = stock_service or FakeStockService()

    service = OrderService(
        order_repo=order_repo,
        order_item_repo=order_item_repo,
        customer_service=FakeCustomerService(),
        store_service=FakeStoreService(),
        staff_service=FakeStaffService(),
        stock_service=stock_service,
    )
    return service, order_repo, order_item_repo, stock_service


# ---------------------------------------------------------------------------
# Tests — create_order
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_order_creates_pending_order():
    service, order_repo, _, _ = make_service()

    result = await service.create_order(CreateOrderCommand(customer_id=42))

    assert result.order_id == 1
    assert result.customer_id == 42
    assert result.order_status == OrderStatus.PENDING
    assert len(order_repo._orders) == 1


# ---------------------------------------------------------------------------
# Tests — checkout_order
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_checkout_order_transitions_to_processing():
    order_repo = InMemoryOrderRepository()
    item_repo = InMemoryOrderItemRepository()
    stock_service = FakeStockService(qty=5)
    service, _, _, _ = make_service(order_repo, item_repo, stock_service)

    created = await service.create_order(CreateOrderCommand(customer_id=1))

    from decimal import Decimal

    item_repo._items.append(
        OrderItem(
            item_id=1,
            order_id=created.order_id,
            product_id=10,
            quantity=2,
            list_price=Decimal("99.99"),
            discount=Decimal("0"),
        )
    )

    result = await service.checkout_order(
        created.order_id,
        CheckoutOrderCommand(
            required_date=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7)
        ),
    )

    assert result.order_status == OrderStatus.PROCESSING


@pytest.mark.asyncio
async def test_checkout_order_deducts_stock():
    order_repo = InMemoryOrderRepository()
    item_repo = InMemoryOrderItemRepository()
    stock_service = FakeStockService(qty=10)
    service, _, _, _ = make_service(order_repo, item_repo, stock_service)

    created = await service.create_order(CreateOrderCommand(customer_id=1))

    from decimal import Decimal

    item_repo._items.append(
        OrderItem(
            item_id=1,
            order_id=created.order_id,
            product_id=5,
            quantity=3,
            list_price=Decimal("100"),
            discount=Decimal("0"),
        )
    )

    await service.checkout_order(
        created.order_id,
        CheckoutOrderCommand(
            required_date=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7)
        ),
    )

    assert stock_service.adjustments == [(1, 5, -3)]


@pytest.mark.asyncio
async def test_checkout_rejects_non_pending_order():
    order_repo = InMemoryOrderRepository()
    item_repo = InMemoryOrderItemRepository()
    service, _, _, _ = make_service(order_repo, item_repo)

    created = await service.create_order(CreateOrderCommand(customer_id=1))
    order_repo._orders[0].order_status = OrderStatus.PROCESSING

    with pytest.raises(BusinessRuleViolationError):
        await service.checkout_order(
            created.order_id,
            CheckoutOrderCommand(
                required_date=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7)
            ),
        )


@pytest.mark.asyncio
async def test_checkout_rejects_empty_order():
    service, _, _, _ = make_service()

    created = await service.create_order(CreateOrderCommand(customer_id=1))

    with pytest.raises(BusinessRuleViolationError):
        await service.checkout_order(
            created.order_id,
            CheckoutOrderCommand(
                required_date=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7)
            ),
        )


@pytest.mark.asyncio
async def test_checkout_rejects_insufficient_stock():
    order_repo = InMemoryOrderRepository()
    item_repo = InMemoryOrderItemRepository()
    stock_service = FakeStockService(qty=1)
    service, _, _, _ = make_service(order_repo, item_repo, stock_service)

    created = await service.create_order(CreateOrderCommand(customer_id=1))

    from decimal import Decimal

    item_repo._items.append(
        OrderItem(
            item_id=1,
            order_id=created.order_id,
            product_id=7,
            quantity=5,
            list_price=Decimal("50"),
            discount=Decimal("0"),
        )
    )

    with pytest.raises(BusinessRuleViolationError):
        await service.checkout_order(
            created.order_id,
            CheckoutOrderCommand(
                required_date=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7)
            ),
        )


@pytest.mark.asyncio
async def test_get_order_by_id_raises_when_not_found():
    service, _, _, _ = make_service()

    with pytest.raises(EntityNotFoundError):
        await service.get_order_by_id(999)


@pytest.mark.asyncio
async def test_delete_order_removes_from_repo():
    order_repo = InMemoryOrderRepository()
    service, _, _, _ = make_service(order_repo)

    created = await service.create_order(CreateOrderCommand(customer_id=1))
    await service.delete_order(created.order_id)

    assert len(order_repo._orders) == 0
