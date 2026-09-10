from fastapi import APIRouter, Depends, status

from src.api.dependencies.auth import (
    get_current_user,
    require_role,
)
from src.api.dependencies.services import (
    get_order_item_service,
)
from src.application.dtos.order_item_dto import (
    CreateOrderItemCommand,
    OrderItemDto,
    UpdateOrderItemCommand,
)
from src.application.services.orderitem_service import (
    OrderItemService,
)
from src.domain.entities.user import Role

router = APIRouter(
    prefix="/order-items",
    tags=["order-items"],
)


@router.post(
    "/",
    response_model=OrderItemDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_order_item(
    command: CreateOrderItemCommand,
    order_item_service: OrderItemService = Depends(get_order_item_service),
) -> OrderItemDto:
    """Create order item."""

    return await order_item_service.create_order_item(command)


@router.get(
    "/",
    response_model=list[OrderItemDto],
    dependencies=[Depends(get_current_user)],
)
async def list_order_items(
    skip: int = 0,
    limit: int = 100,
    order_item_service: OrderItemService = Depends(get_order_item_service),
) -> list[OrderItemDto]:
    """List all order items."""

    return await order_item_service.list_all_order_items(
        skip,
        limit,
    )


@router.get(
    "/order/{order_id}",
    response_model=list[OrderItemDto],
    dependencies=[Depends(get_current_user)],
)
async def list_items_by_order(
    order_id: int,
    order_item_service: OrderItemService = Depends(get_order_item_service),
) -> list[OrderItemDto]:
    """List items by order id."""

    return await order_item_service.list_items_by_order_id(order_id)


@router.get(
    "/{order_id}/{product_id}",
    response_model=OrderItemDto,
    dependencies=[Depends(get_current_user)],
)
async def get_order_item(
    order_id: int,
    product_id: int,
    order_item_service: OrderItemService = Depends(get_order_item_service),
) -> OrderItemDto:
    """Get order item by composite key."""

    return await order_item_service.get_item_by_order_product_id(
        order_id,
        product_id,
    )


@router.put(
    "/{order_id}/{product_id}",
    response_model=OrderItemDto,
    dependencies=[Depends(get_current_user)],
)
async def update_order_item(
    order_id: int,
    product_id: int,
    command: UpdateOrderItemCommand,
    order_item_service: OrderItemService = Depends(get_order_item_service),
) -> OrderItemDto:
    """Update order item."""

    return await order_item_service.update_order_item(
        order_id,
        product_id,
        command,
    )


@router.delete(
    "/{order_id}/{product_id}",
    response_model=OrderItemDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_order_item(
    order_id: int,
    product_id: int,
    order_item_service: OrderItemService = Depends(get_order_item_service),
) -> OrderItemDto:
    """Delete order item."""

    return await order_item_service.delete_order_item(
        order_id,
        product_id,
    )
