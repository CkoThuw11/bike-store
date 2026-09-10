from decimal import Decimal
from types import SimpleNamespace

import pytest

from src.application.dtos.product_dto import CreateProductCommand
from src.application.services.product_service import ProductService
from src.domain.entities.product import Product
from src.domain.exceptions import EntityAlreadyExistsException


class InMemoryProductRepository:
    def __init__(self) -> None:
        self.products: list[Product] = []
        self._next_id = 1

    async def create(self, product: Product) -> Product:
        product.product_id = self._next_id
        self._next_id += 1
        self.products.append(product)
        return product

    async def get_product_by_id(self, product_id: int) -> Product | None:
        return next((p for p in self.products if p.product_id == product_id), None)

    async def get_product_by_name(self, product_name: str) -> Product | None:
        return next((p for p in self.products if p.product_name == product_name), None)

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Product]:
        return self.products[skip : skip + limit]

    async def update(self, product: Product) -> Product:
        return product

    async def delete(self, product_id: int) -> bool:
        return True


class InMemoryStockRepository:
    def __init__(self) -> None:
        self.stocks = []

    async def create(self, stock):
        self.stocks.append(stock)
        return stock


class InMemoryStoreRepository:
    async def list_all(self, skip: int = 0, limit: int = 100):
        return [
            SimpleNamespace(store_id=1),
            SimpleNamespace(store_id=2),
        ]


class ExistingBrandService:
    async def check_brand_exist(self, brand_id: int) -> bool:
        return True


class ExistingCategoryService:
    async def check_category_exist(self, category_id: int) -> bool:
        return True


def make_service(
    product_repo: InMemoryProductRepository | None = None,
    stock_repo: InMemoryStockRepository | None = None,
) -> tuple[ProductService, InMemoryProductRepository, InMemoryStockRepository]:
    product_repo = product_repo or InMemoryProductRepository()
    stock_repo = stock_repo or InMemoryStockRepository()

    service = ProductService(
        product_repo=product_repo,
        stock_repo=stock_repo,
        store_repo=InMemoryStoreRepository(),
        brand_service=ExistingBrandService(),
        category_service=ExistingCategoryService(),
    )

    return service, product_repo, stock_repo


pytestmark = [pytest.mark.unit]


@pytest.mark.asyncio
async def test_create_product_assigns_id_and_initializes_stock_for_each_store():
    service, product_repo, stock_repo = make_service()
    command = CreateProductCommand(
        product_name="Trail Bike",
        brand_id=1,
        category_id=1,
        model_year=2024,
        list_price=Decimal("999.99"),
    )

    result = await service.create_product(command)

    assert result.product_id == 1
    assert result.product_name == "Trail Bike"
    assert result.brand_id == 1
    assert result.category_id == 1
    assert result.model_year == 2024
    assert result.list_price == Decimal("999.99")
    assert result.is_active is True
    assert len(product_repo.products) == 1
    assert len(stock_repo.stocks) == 2
    assert {stock.store_id for stock in stock_repo.stocks} == {1, 2}
    assert all(stock.product_id == 1 for stock in stock_repo.stocks)
    assert all(stock.quantity == 0 for stock in stock_repo.stocks)


@pytest.mark.asyncio
async def test_create_product_rejects_duplicate_product_name():
    product_repo = InMemoryProductRepository()
    await product_repo.create(
        Product(
            product_name="Trail Bike",
            brand_id=1,
            category_id=1,
            model_year=2024,
            list_price=Decimal("999.99"),
        )
    )
    service, _, _ = make_service(product_repo=product_repo)

    command = CreateProductCommand(
        product_name="Trail Bike",
        brand_id=1,
        category_id=1,
        model_year=2024,
        list_price=Decimal("1099.99"),
    )

    with pytest.raises(EntityAlreadyExistsException):
        await service.create_product(command)
