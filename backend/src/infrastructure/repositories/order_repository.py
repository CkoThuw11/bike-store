from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.order import Order, OrderStatus
from src.domain.repositories.order_repository import IOrderRepository
from src.infrastructure.database.models import OrderModel


class OrderRepository(IOrderRepository):
    """SQLAlchemy implementation of IOrderRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: OrderModel) -> Order:
        return Order(
            order_id=model.order_id,
            customer_id=model.customer_id,
            order_status=OrderStatus(model.order_status),
            order_date=model.order_date,
            required_date=model.required_date,
            shipped_date=model.shipped_date,
            store_id=model.store_id,
            staff_id=model.staff_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Order) -> OrderModel:
        return OrderModel(
            order_id=entity.order_id,
            customer_id=entity.customer_id,
            order_status=entity.order_status,
            order_date=entity.order_date,
            required_date=entity.required_date,
            shipped_date=entity.shipped_date,
            store_id=entity.store_id,
            staff_id=entity.staff_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, order: Order) -> Order:
        """Persist a new order and return the DB-assigned entity."""
        model = self._to_model(order)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_order_by_id(self, order_id: int) -> Order | None:
        """Return the order with the given ID, or None."""
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.order_id == order_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_orders_by_customer_id(self, customer_id: int) -> list[Order]:
        """Return all orders placed by the given customer."""
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.customer_id == customer_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Order]:
        """Return a paginated list of all orders."""
        result = await self._session.execute(
            select(OrderModel).offset(skip).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, order: Order) -> Order:
        """Flush order changes to the DB and return the refreshed entity."""
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.order_id == order.order_id)
        )
        model = result.scalar_one()
        model.order_status = order.order_status
        model.order_date = order.order_date
        model.required_date = order.required_date
        model.shipped_date = order.shipped_date
        model.store_id = order.store_id
        model.staff_id = order.staff_id
        model.updated_at = order.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, order_id: int) -> bool:
        """Delete the order row. Returns True if a row was actually removed."""
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.order_id == order_id)
        )
        model = result.scalar_one_or_none()
        if model: 
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
