from fastapi import Depends

from src.api.dependencies.repositories import (
    get_brand_repository,
    get_category_repository,
    get_customer_repository,
    get_order_item_repository,
    get_order_repository,
    get_product_repository,
    get_refresh_token_repository,
    get_staff_repository,
    get_stock_repository,
    get_store_repository,
    get_user_repository,
)
from src.application.services.auth_service import AuthService
from src.application.services.brand_service import BrandService
from src.application.services.category_service import CategoryService
from src.application.services.customer_service import CustomerService
from src.application.services.order_service import OrderService
from src.application.services.orderitem_service import OrderItemService
from src.application.services.product_service import ProductService
from src.application.services.staff_service import StaffService
from src.application.services.stock_service import StockService
from src.application.services.store_service import StoreService
from src.domain.repositories.brand_repository import IBrandRepository
from src.domain.repositories.category_repository import ICategoryRepository
from src.domain.repositories.customer_repository import ICustomerRepository
from src.domain.repositories.order_repository import IOrderRepository
from src.domain.repositories.orderitem_repository import IOrderItemRepository
from src.domain.repositories.product_repository import IProductRepository
from src.domain.repositories.refresh_token_repository import IRefreshTokenRepository
from src.domain.repositories.staff_repository import IStaffRepository
from src.domain.repositories.stock_repository import IStockRepository
from src.domain.repositories.store_repository import IStoreRepository
from src.domain.repositories.user_repository import IUserRepository


def get_auth_service(
    user_repo: IUserRepository = Depends(get_user_repository),
    token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repository),
) -> AuthService:
    return AuthService(user_repo, token_repo)


def get_brand_service(repo: IBrandRepository = Depends(get_brand_repository)) -> BrandService:
    return BrandService(repo)


def get_category_service(
    repo: ICategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    return CategoryService(repo)


def get_store_service(repo: IStoreRepository = Depends(get_store_repository)) -> StoreService:
    return StoreService(repo)


def get_customer_service(
    repo: ICustomerRepository = Depends(get_customer_repository),
) -> CustomerService:
    return CustomerService(repo)


def get_staff_service(
    repo: IStaffRepository = Depends(get_staff_repository),
    store_service: StoreService = Depends(get_store_service),
) -> StaffService:
    return StaffService(repo, store_service)


def get_product_service(
    product_repo: IProductRepository = Depends(get_product_repository),
    stock_repo: IStockRepository = Depends(get_stock_repository),
    store_repo: IStoreRepository = Depends(get_store_repository),
    brand_service: BrandService = Depends(get_brand_service),
    category_service: CategoryService = Depends(get_category_service),
) -> ProductService:
    return ProductService(
        product_repo=product_repo,
        stock_repo=stock_repo,
        store_repo=store_repo,
        brand_service=brand_service,
        category_service=category_service,
    )


def get_stock_service(
    repo: IStockRepository = Depends(get_stock_repository),
    store_service: StoreService = Depends(get_store_service),
    product_service: ProductService = Depends(get_product_service),
) -> StockService:
    return StockService(repo, store_service, product_service)


def get_order_service(
    repo: IOrderRepository = Depends(get_order_repository),
    order_item_repo: IOrderItemRepository = Depends(get_order_item_repository),
    customer_service: CustomerService = Depends(get_customer_service),
    store_service: StoreService = Depends(get_store_service),
    staff_service: StaffService = Depends(get_staff_service),
    stock_service: StockService = Depends(get_stock_service),
) -> OrderService:
    return OrderService(
        repo, order_item_repo, customer_service, store_service, staff_service, stock_service
    )


def get_order_item_service(
    repo: IOrderItemRepository = Depends(get_order_item_repository),
    order_service: OrderService = Depends(get_order_service),
    product_service: ProductService = Depends(get_product_service),
) -> OrderItemService:
    return OrderItemService(repo, order_service, product_service)
