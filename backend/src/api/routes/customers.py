from fastapi import APIRouter, Depends, status

from src.api.dependencies.auth import get_current_user, require_role
from src.api.dependencies.services import get_customer_service
from src.application.dtos.customer_dto import CreateCustomerCommand, CustomerDto, UpdateCustomerCommand
from src.application.services.customer_service import CustomerService
from src.domain.entities.user import Role

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post(
    "/",
    response_model=CustomerDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_customer(
    command: CreateCustomerCommand,
    customer_service: CustomerService = Depends(get_customer_service),
) -> CustomerDto:
    return await customer_service.create_customer(command)


@router.get(
    "/",
    response_model=list[CustomerDto],
    dependencies=[Depends(get_current_user)],
)
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    customer_service: CustomerService = Depends(get_customer_service),
) -> list[CustomerDto]:
    return await customer_service.list_all_customers(skip, limit)


@router.get(
    "/search",
    response_model=list[CustomerDto],
    dependencies=[Depends(get_current_user)],
)
async def search_customers(
    name: str,
    customer_service: CustomerService = Depends(get_customer_service),
) -> list[CustomerDto]:
    return await customer_service.search_customers_by_name(name)


@router.get(
    "/{customer_id}",
    response_model=CustomerDto,
    dependencies=[Depends(get_current_user)],
)
async def get_customer(
    customer_id: int,
    customer_service: CustomerService = Depends(get_customer_service),
) -> CustomerDto:
    return await customer_service.get_customer_by_id(customer_id)


@router.put(
    "/{customer_id}",
    response_model=CustomerDto,
    dependencies=[Depends(get_current_user)],
)
async def update_customer(
    customer_id: int,
    command: UpdateCustomerCommand,
    customer_service: CustomerService = Depends(get_customer_service),
) -> CustomerDto:
    return await customer_service.update_customer(customer_id, command)


@router.post(
    "/{customer_id}/activate",
    response_model=CustomerDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def activate_customer(
    customer_id: int,
    customer_service: CustomerService = Depends(get_customer_service),
) -> CustomerDto:
    return await customer_service.activate_customer(customer_id)


@router.post(
    "/{customer_id}/deactivate",
    response_model=CustomerDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def deactivate_customer(
    customer_id: int,
    customer_service: CustomerService = Depends(get_customer_service),
) -> CustomerDto:
    return await customer_service.deactivate_customer(customer_id)


@router.delete(
    "/{customer_id}",
    response_model=CustomerDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_customer(
    customer_id: int,
    customer_service: CustomerService = Depends(get_customer_service),
) -> CustomerDto:
    return await customer_service.delete_customer(customer_id)
