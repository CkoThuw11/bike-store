from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.auth import (
    get_current_user,
    require_role,
)
from src.api.dependencies.services import (
    get_product_service,
)
from src.application.dtos.product_dto import (
    CreateProductCommand,
    ProductDto,
    UpdateProductCommand,
)
from src.application.services.product_service import (
    ProductService,
)
from src.domain.entities.user import Role

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.post(
    "/",
    response_model=ProductDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def create_product(
    command: CreateProductCommand,
    product_service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductDto:
    """Create product."""

    return await product_service.create_product(
        command
    )


@router.get(
    "/",
    response_model=list[ProductDto],
    dependencies=[Depends(get_current_user)],
)
async def list_products(
    skip: int = 0,
    limit: int = 100,
    product_service: ProductService = Depends(
        get_product_service,
    ),
) -> list[ProductDto]:
    """List products."""

    return await product_service.get_all_products(
        skip,
        limit,
    )


@router.get(
    "/search/by-name",
    response_model=list[ProductDto],
    dependencies=[Depends(get_current_user)],
)
async def search_products_by_name(
    product_name: str = Query(...),
    product_service: ProductService = Depends(
        get_product_service,
    ),
) -> list[ProductDto]:
    """Search products whose name contains the given term."""

    return await product_service.search_products_by_name(
        product_name
    )


@router.get(
    "/{product_id}",
    response_model=ProductDto,
    dependencies=[Depends(get_current_user)],
)
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductDto:
    """Get product by id."""

    return await product_service.get_product_by_id(
        product_id
    )


@router.put(
    "/{product_id}",
    response_model=ProductDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def update_product(
    product_id: int,
    command: UpdateProductCommand,
    product_service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductDto:
    """Update product."""

    return await product_service.update_product(
        product_id,
        command,
    )


@router.post(
    "/{product_id}/activate",
    response_model=ProductDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def activate_product(
    product_id: int,
    product_service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductDto:
    """Activate product."""

    return await product_service.activate_product(
        product_id
    )


@router.post(
    "/{product_id}/deactivate",
    response_model=ProductDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def deactivate_product(
    product_id: int,
    product_service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductDto:
    """Soft delete product."""

    return await product_service.deactivate_product(
        product_id
    )


@router.delete(
    "/{product_id}",
    response_model=ProductDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductDto:
    """Hard delete product."""

    return await product_service.delete_product(
        product_id
    )