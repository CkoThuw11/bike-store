from fastapi import APIRouter, Depends, status

from src.api.dependencies.auth import (
    get_current_user,
    require_role,
)
from src.api.dependencies.services import (
    get_order_service,
)
from src.application.dtos.order_dto import (
    CheckoutOrderCommand,
    CreateOrderCommand,
    OrderDto,
    UpdateOrderCommand,
)
from src.application.services.order_service import (
    OrderService,
)
from src.domain.entities.user import Role

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.post(
    "/",
    response_model=OrderDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_order(
    command: CreateOrderCommand,
    order_service: OrderService = Depends(
        get_order_service,
    ),
) -> OrderDto:
    """Create empty pending order."""

    return await order_service.create_order(command)


@router.post(
    "/{order_id}/checkout",
    response_model=OrderDto,
    dependencies=[Depends(get_current_user)],
)
async def checkout_order(
    order_id: int,
    command: CheckoutOrderCommand,
    order_service: OrderService = Depends(
        get_order_service,
    ),
) -> OrderDto:
    """Checkout pending order."""

    return await order_service.checkout_order(
        order_id,
        command,
    )


@router.get(
    "/",
    response_model=list[OrderDto],
    dependencies=[Depends(get_current_user)],
)
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    order_service: OrderService = Depends(
        get_order_service,
    ),
) -> list[OrderDto]:
    """List all orders."""

    return await order_service.list_all_orders(
        skip,
        limit,
    )


@router.get(
    "/customer/{customer_id}",
    response_model=list[OrderDto],
    dependencies=[Depends(get_current_user)],
)
async def get_orders_by_customer(
    customer_id: int,
    order_service: OrderService = Depends(
        get_order_service,
    ),
) -> list[OrderDto]:
    """Get orders by customer."""

    return await order_service.get_orders_by_customer_id(customer_id)


@router.get(
    "/{order_id}",
    response_model=OrderDto,
    dependencies=[Depends(get_current_user)],
)
async def get_order(
    order_id: int,
    order_service: OrderService = Depends(
        get_order_service,
    ),
) -> OrderDto:
    """Get order by id."""

    return await order_service.get_order_by_id(order_id)


@router.put(
    "/{order_id}",
    response_model=OrderDto,
    dependencies=[Depends(get_current_user)],
)
async def update_order(
    order_id: int,
    command: UpdateOrderCommand,
    order_service: OrderService = Depends(
        get_order_service,
    ),
) -> OrderDto:
    """Update order."""

    return await order_service.update_order(
        order_id,
        command,
    )


@router.delete(
    "/{order_id}",
    response_model=OrderDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_order(
    order_id: int,
    order_service: OrderService = Depends(
        get_order_service,
    ),
) -> OrderDto:
    """Delete order."""

    return await order_service.delete_order(order_id)
