from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.stock import Stock
from src.domain.repositories.stock_repository import IStockRepository
from src.infrastructure.database.models import StockModel


class StockRepository(IStockRepository):
    """SQLAlchemy implementation of IStockRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: StockModel) -> Stock:
        return Stock(
            stock_id=model.stock_id,
            store_id=model.store_id,
            product_id=model.product_id,
            quantity=model.quantity,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Stock) -> StockModel:
        return StockModel(
            stock_id=entity.stock_id,
            store_id=entity.store_id,
            product_id=entity.product_id,
            quantity=entity.quantity,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, stock: Stock) -> Stock:
        """Persist a new stock record and return the DB-assigned entity."""
        model = self._to_model(stock)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_stock_by_id(self, store_id: int, product_id: int) -> Stock | None:
        """Return the stock record for the given (store_id, product_id) pair, or None."""
        result = await self._session.execute(
            select(StockModel).where(
                StockModel.store_id == store_id,
                StockModel.product_id == product_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_stock_by_product_id(self, product_id: int) -> list[Stock]:
        """Return all stock records for the given product across all stores."""
        result = await self._session.execute(
            select(StockModel).where(StockModel.product_id == product_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_stock_by_store_id(self, store_id: int) -> list[Stock]:
        """Return all stock records for the given store across all products."""
        result = await self._session.execute(
            select(StockModel).where(StockModel.store_id == store_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Stock]:
        """Return a paginated list of all stock records."""
        result = await self._session.execute(
            select(StockModel).offset(skip).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, stock: Stock) -> Stock:
        """Flush stock quantity change to the DB and return the refreshed entity."""
        result = await self._session.execute(
            select(StockModel).where(
                StockModel.store_id == stock.store_id,
                StockModel.product_id == stock.product_id,
            )
        )
        model = result.scalar_one()
        model.quantity = stock.quantity
        model.updated_at = stock.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, store_id: int, product_id: int) -> bool:
        """Delete the stock row. Returns True if a row was actually removed."""
        result = await self._session.execute(
            select(StockModel).where(
                StockModel.store_id == store_id,
                StockModel.product_id == product_id,
            )
        )
        model = result.scalar_one_or_none()
        if model: 
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
