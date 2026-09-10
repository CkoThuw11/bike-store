from fastapi import APIRouter, Depends, status, Query

from src.api.dependencies.auth import get_current_user, require_role
from src.api.dependencies.services import get_brand_service
from src.application.dtos.brand_dto import BrandDto, CreateBrandCommand, UpdateBrandCommand
from src.application.services.brand_service import BrandService
from src.domain.entities.user import Role

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post(
    "/",
    response_model=BrandDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def create_brand(
    command: CreateBrandCommand,
    brand_service: BrandService = Depends(get_brand_service),
) -> BrandDto:
    return await brand_service.create_brand(command)


@router.get(
    "/",
    response_model=list[BrandDto],
    dependencies=[Depends(get_current_user)],
)
async def list_brands(
    skip: int = Query(default=0, ge=0),   
    limit: int = Query(default=100, ge=1, le=500),
    brand_service: BrandService = Depends(get_brand_service),
) -> list[BrandDto]:
    return await brand_service.list_all_brands(skip, limit)


@router.get(
    "/{brand_id}",
    response_model=BrandDto,
    dependencies=[Depends(get_current_user)],
)
async def get_brand(
    brand_id: int,
    brand_service: BrandService = Depends(get_brand_service),
) -> BrandDto:
    return await brand_service.get_brand_by_id(brand_id)


@router.put(
    "/{brand_id}",
    response_model=BrandDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def update_brand(
    brand_id: int,
    command: UpdateBrandCommand,
    brand_service: BrandService = Depends(get_brand_service),
) -> BrandDto:
    return await brand_service.update_brand(brand_id, command)

@router.post(
    "/{brand_id}/activate",
    response_model=BrandDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def activate_brand(
    brand_id: int,
    brand_service: BrandService = Depends(get_brand_service),
) -> BrandDto:
    return await brand_service.activate_brand(brand_id)



@router.post(
    "/{brand_id}/deactivate",
    response_model=BrandDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def deactivate_brand(
    brand_id: int,
    brand_service: BrandService = Depends(get_brand_service),
) -> BrandDto:
    return await brand_service.deactivate_brand(brand_id)


@router.delete(
    "/{brand_id}",
    response_model=BrandDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_brand(
    brand_id: int,
    brand_service: BrandService = Depends(get_brand_service),
) -> BrandDto:
    return await brand_service.delete_brand(brand_id)


