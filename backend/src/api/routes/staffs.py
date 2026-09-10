from fastapi import APIRouter, Depends, status

from src.api.dependencies.auth import get_current_user, require_role
from src.api.dependencies.services import get_staff_service
from src.application.dtos.staff_dto import CreateStaffCommand, StaffDto, UpdateStaffCommand
from src.application.services.staff_service import StaffService
from src.domain.entities.user import Role

router = APIRouter(prefix="/staffs", tags=["staffs"])


@router.post(
    "/",
    response_model=StaffDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def create_staff(
    command: CreateStaffCommand,
    staff_service: StaffService = Depends(get_staff_service),
) -> StaffDto:
    return await staff_service.create_staff(command)


@router.get(
    "/",
    response_model=list[StaffDto],
    dependencies=[Depends(get_current_user)],
)
async def list_staff(
    skip: int = 0,
    limit: int = 100,
    staff_service: StaffService = Depends(get_staff_service),
) -> list[StaffDto]:
    return await staff_service.get_all_staff(skip, limit)


@router.get(
    "/search",
    response_model=list[StaffDto],
    dependencies=[Depends(get_current_user)],
)
async def search_staff_by_last_name(
    last_name: str,
    staff_service: StaffService = Depends(get_staff_service),
) -> list[StaffDto]:
    return await staff_service.search_staff_by_last_name(last_name)


@router.get(
    "/{staff_id}",
    response_model=StaffDto,
    dependencies=[Depends(get_current_user)],
)
async def get_staff(
    staff_id: int,
    staff_service: StaffService = Depends(get_staff_service),
) -> StaffDto:
    return await staff_service.get_staff_by_id(staff_id)


@router.put(
    "/{staff_id}",
    response_model=StaffDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def update_staff(
    staff_id: int,
    command: UpdateStaffCommand,
    staff_service: StaffService = Depends(get_staff_service),
) -> StaffDto:
    return await staff_service.update_staff(staff_id, command)


@router.post(
    "/{staff_id}/activate",
    response_model=StaffDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def activate_staff(
    staff_id: int,
    staff_service: StaffService = Depends(get_staff_service),
) -> StaffDto:
    return await staff_service.activate_staff(staff_id)


@router.post(
    "/{staff_id}/deactivate",
    response_model=StaffDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def deactivate_staff(
    staff_id: int,
    staff_service: StaffService = Depends(get_staff_service),
) -> StaffDto:
    return await staff_service.deactivate_staff(staff_id)


@router.delete(
    "/{staff_id}",
    response_model=StaffDto,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_staff(
    staff_id: int,
    staff_service: StaffService = Depends(get_staff_service),
) -> StaffDto:
    return await staff_service.delete_staff(staff_id)
