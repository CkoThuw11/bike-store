from fastapi import APIRouter, Depends, Query

from src.api.dependencies.auth import (
    get_current_user,
    require_role,
)
from src.api.dependencies.services import (
    get_stock_service,
)
from src.application.dtos.stock_dto import (
    StockDto,
    UpdateStockCommand,
)
from src.application.services.stock_service import (
    StockService,
)
from src.domain.entities.user import Role

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
)


@router.get(
    "/",
    response_model=list[StockDto],
    dependencies=[Depends(get_current_user)],
)
async def list_stocks(
    skip: int = 0,
    limit: int = 100,
    stock_service: StockService = Depends(
        get_stock_service,
    ),
) -> list[StockDto]:
    """List all stock records."""

    return await stock_service.get_all_stock(
        skip,
        limit,
    )


@router.get(
    "/store/{store_id}",
    response_model=list[StockDto],
    dependencies=[Depends(get_current_user)],
)
async def list_stocks_by_store(
    store_id: int,
    stock_service: StockService = Depends(
        get_stock_service,
    ),
) -> list[StockDto]:
    """Get stocks by store."""

    return await stock_service.get_stock_by_store_id(
        store_id
    )


@router.get(
    "/product/{product_id}",
    response_model=list[StockDto],
    dependencies=[Depends(get_current_user)],
)
async def list_stocks_by_product(
    product_id: int,
    stock_service: StockService = Depends(
        get_stock_service,
    ),
) -> list[StockDto]:
    """Get stocks by product."""

    return await stock_service.get_stock_by_product_id(
        product_id
    )


@router.get(
    "/{store_id}/{product_id}",
    response_model=StockDto,
    dependencies=[Depends(get_current_user)],
)
async def get_stock(
    store_id: int,
    product_id: int,
    stock_service: StockService = Depends(
        get_stock_service,
    ),
) -> StockDto:
    """Get stock by composite key."""

    return await stock_service.get_stock_by_id(
        store_id,
        product_id,
    )


@router.put(
    "/{store_id}/{product_id}",
    response_model=StockDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def update_stock(
    store_id: int,
    product_id: int,
    command: UpdateStockCommand,
    stock_service: StockService = Depends(
        get_stock_service,
    ),
) -> StockDto:
    """Replace stock quantity."""

    return await stock_service.update_stock(
        store_id,
        product_id,
        command,
    )


@router.patch(
    "/{store_id}/{product_id}/adjust",
    response_model=StockDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def adjust_stock(
    store_id: int,
    product_id: int,
    delta: int = Query(...),
    stock_service: StockService = Depends(
        get_stock_service,
    ),
) -> StockDto:
    """
    Adjust stock incrementally.

    Examples:
    - delta=10
    - delta=-5
    """

    return await stock_service.adjust_stock(
        store_id,
        product_id,
        delta,
    )