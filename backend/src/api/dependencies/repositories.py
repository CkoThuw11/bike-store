# src/api/dependencies/repositories.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.connection import get_db
from src.infrastructure.repositories.brand_repository import BrandRepository
from src.infrastructure.repositories.category_repository import CategoryRepository
from src.infrastructure.repositories.customer_repository import CustomerRepository
from src.infrastructure.repositories.order_repository import OrderRepository
from src.infrastructure.repositories.orderitem_repository import OrderItemRepository
from src.infrastructure.repositories.product_repository import ProductRepository
from src.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from src.infrastructure.repositories.staff_repository import StaffRepository
from src.infrastructure.repositories.stock_repository import StockRepository
from src.infrastructure.repositories.store_repository import StoreRepository
from src.infrastructure.repositories.user_repository import UserRepository


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_refresh_token_repository(session: AsyncSession = Depends(get_db)) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


def get_brand_repository(session: AsyncSession = Depends(get_db)) -> BrandRepository:
    return BrandRepository(session)


def get_category_repository(session: AsyncSession = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(session)


def get_customer_repository(session: AsyncSession = Depends(get_db)) -> CustomerRepository:
    return CustomerRepository(session)


def get_order_repository(session: AsyncSession = Depends(get_db)) -> OrderRepository:
    return OrderRepository(session)


def get_order_item_repository(session: AsyncSession = Depends(get_db)) -> OrderItemRepository:
    return OrderItemRepository(session)


def get_product_repository(session: AsyncSession = Depends(get_db)) -> ProductRepository:
    return ProductRepository(session)


def get_staff_repository(session: AsyncSession = Depends(get_db)) -> StaffRepository:
    return StaffRepository(session)


def get_stock_repository(session: AsyncSession = Depends(get_db)) -> StockRepository:
    return StockRepository(session)


def get_store_repository(session: AsyncSession = Depends(get_db)) -> StoreRepository:
    return StoreRepository(session)
