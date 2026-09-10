from fastapi import APIRouter, Depends, status

from src.api.dependencies.auth import get_current_user, require_role
from src.api.dependencies.services import get_store_service
from src.application.dtos.store_dto import CreateStoreCommand, StoreDto, UpdateStoreCommand
from src.application.services.store_service import StoreService
from src.domain.entities.user import Role

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post(
    "/",
    response_model=StoreDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def create_store(
    command: CreateStoreCommand,
    store_service: StoreService = Depends(get_store_service),
) -> StoreDto:
    return await store_service.create_store(command)


@router.get(
    "/",
    response_model=list[StoreDto],
    dependencies=[Depends(get_current_user)],
)
async def list_stores(
    skip: int = 0,
    limit: int = 100,
    store_service: StoreService = Depends(get_store_service),
) -> list[StoreDto]:
    return await store_service.get_all_stores(skip, limit)


@router.get(
    "/{store_id}",
    response_model=StoreDto,
    dependencies=[Depends(get_current_user)],
)
async def get_store(
    store_id: int,
    store_service: StoreService = Depends(get_store_service),
) -> StoreDto:
    return await store_service.get_store_by_id(store_id)


@router.put(
    "/{store_id}",
    response_model=StoreDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def update_store(
    store_id: int,
    command: UpdateStoreCommand,
    store_service: StoreService = Depends(get_store_service),
) -> StoreDto:
    return await store_service.update_store(store_id, command)

@router.post(
    "/{store_id}/activate",
    response_model=StoreDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def activate_store(
    store_id: int,
    store_service: StoreService = Depends(get_store_service),
) -> StoreDto:
    return await store_service.activate_store(store_id)


@router.post(
    "/{store_id}/deactivate",
    response_model=StoreDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def deactivate_store(
    store_id: int,
    store_service: StoreService = Depends(get_store_service),
) -> StoreDto:
    return await store_service.deactivate_store(store_id)

@router.delete(
    "/{store_id}",
    response_model=StoreDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_store(
    store_id: int,
    store_service: StoreService = Depends(get_store_service),
) -> StoreDto:
    return await store_service.delete_store(store_id)
