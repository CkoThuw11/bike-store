from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.product import Product
from src.domain.repositories.product_repository import IProductRepository
from src.infrastructure.database.models import ProductModel


class ProductRepository(IProductRepository):
    """SQLAlchemy implementation of IProductRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: ProductModel) -> Product:
        return Product(
            product_id=model.product_id,
            product_name=model.product_name,
            brand_id=model.brand_id,
            category_id=model.category_id,
            model_year=model.model_year,
            list_price=model.list_price,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Product) -> ProductModel:
        return ProductModel(
            product_id=entity.product_id,
            product_name=entity.product_name,
            brand_id=entity.brand_id,
            category_id=entity.category_id,
            model_year=entity.model_year,
            list_price=entity.list_price,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, product: Product) -> Product:
        """Persist a new product and return the DB-assigned entity."""
        model = self._to_model(product)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_product_by_id(self, product_id: int) -> Product | None:
        """Return the product with the given ID, or None."""
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.product_id == product_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_product_by_name(self, product_name: str) -> Product | None:
        """Return the product with the given name, or None."""
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.product_name == product_name)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def search_by_name(self, name: str) -> list[Product]:
        """Return products whose name contains the search term (case-insensitive)."""
        term = f"%{name}%"
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.product_name.ilike(term))
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Product]:
        """Return a paginated list of all products."""
        result = await self._session.execute(
            select(ProductModel).offset(skip).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, product: Product) -> Product:
        """Flush product changes to the DB and return the refreshed entity."""
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.product_id == product.product_id)
        )
        model = result.scalar_one()
        model.product_name = product.product_name
        model.brand_id = product.brand_id
        model.category_id = product.category_id
        model.model_year = product.model_year
        model.list_price = product.list_price
        model.updated_at = product.updated_at
        model.is_active = product.is_active
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, product_id: int) -> bool:
        """Delete the product row. Returns True if a row was actually removed."""
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.product_id == product_id)
        )
        model = result.scalar_one_or_none()
        if model: 
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
