from fastapi import APIRouter, Depends, status

from src.api.dependencies.auth import get_current_user, require_role
from src.api.dependencies.services import get_category_service
from src.application.dtos.category_dto import CategoryDto, CreateCategoryCommand, UpdateCategoryCommand
from src.application.services.category_service import CategoryService
from src.domain.entities.user import Role

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "/",
    response_model=CategoryDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def create_category(
    command: CreateCategoryCommand,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryDto:
    return await category_service.create_category(command)


@router.get(
    "/",
    response_model=list[CategoryDto],
    dependencies=[Depends(get_current_user)],
)
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    category_service: CategoryService = Depends(get_category_service),
) -> list[CategoryDto]:
    return await category_service.list_all_categories(skip, limit)


@router.get(
    "/{category_id}",
    response_model=CategoryDto,
    dependencies=[Depends(get_current_user)],
)
async def get_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryDto:
    return await category_service.get_category_by_id(category_id)


@router.put(
    "/{category_id}",
    response_model=CategoryDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def update_category(
    category_id: int,
    command: UpdateCategoryCommand,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryDto:
    return await category_service.update_category(category_id, command)


@router.post(
    "/{category_id}/activate",
    response_model=CategoryDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def activate_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryDto:
    return await category_service.activate_category(category_id)


@router.post(
    "/{category_id}/deactivate",
    response_model=CategoryDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def deactivate_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryDto:
    return await category_service.deactivate_category(category_id)


@router.delete(
    "/{category_id}",
    response_model=CategoryDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryDto:
    return await category_service.delete_category(category_id)


