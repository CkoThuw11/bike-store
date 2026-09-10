from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.order_item import OrderItem
from src.domain.repositories.orderitem_repository import IOrderItemRepository
from src.infrastructure.database.models import OrderItemModel


class OrderItemRepository(IOrderItemRepository):
    """SQLAlchemy implementation of IOrderItemRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: OrderItemModel) -> OrderItem:
        return OrderItem(
            item_id=model.item_id,
            order_id=model.order_id,
            product_id=model.product_id,
            quantity=model.quantity,
            list_price=model.list_price,
            discount=model.discount,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: OrderItem) -> OrderItemModel:
        return OrderItemModel(
            item_id=entity.item_id,
            order_id=entity.order_id,
            product_id=entity.product_id,
            quantity=entity.quantity,
            list_price=entity.list_price,
            discount=entity.discount,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, order_item: OrderItem) -> OrderItem:
        """Persist a new order item and return the DB-assigned entity."""
        model = self._to_model(order_item)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_order_item_by_order_product_id(self, order_id: int, product_id: int) -> OrderItem | None:
        """Return the item for the given (order_id, product_id) pair, or None."""
        result = await self._session.execute(
            select(OrderItemModel).where(
                OrderItemModel.order_id == order_id,
                OrderItemModel.product_id == product_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_order_items_by_order_id(self, order_id: int) -> list[OrderItem]:
        """Return all line items belonging to the given order."""
        result = await self._session.execute(
            select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[OrderItem]:
        """Return a paginated list of all order items."""
        result = await self._session.execute(
            select(OrderItemModel).offset(skip).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, order_item: OrderItem) -> OrderItem:
        """Flush order item changes to the DB and return the refreshed entity."""
        result = await self._session.execute(
            select(OrderItemModel).where(OrderItemModel.item_id == order_item.item_id)
        )
        model = result.scalar_one()
        model.quantity = order_item.quantity
        model.list_price = order_item.list_price
        model.discount = order_item.discount
        model.updated_at = order_item.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, item_id: int) -> bool:
        """Delete the order item row by item_id. Returns True if a row was removed."""
        result = await self._session.execute(
            select(OrderItemModel).where(OrderItemModel.item_id == item_id)
        )
        model = result.scalar_one_or_none()
        if model: 
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
