from src.application.dtos.staff_dto import CreateStaffCommand, StaffDto, UpdateStaffCommand
from src.application.services.store_service import StoreService
from src.domain.entities.staff import Staff
from src.domain.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundError,
)
from src.domain.repositories.staff_repository import IStaffRepository

class StaffService:
    """Orchestrates all business logic related to staff members."""

    def __init__(self, staff_repo: IStaffRepository, store_service: StoreService) -> None:
        self._staff_repo = staff_repo
        self._store_service = store_service

    async def create_staff(self, command: CreateStaffCommand) -> StaffDto:
        """Create a new staff member, validating email uniqueness and referenced store/manager."""
        existing = await self._staff_repo.get_staff_by_email(command.email)
        if existing:
            raise EntityAlreadyExistsException("Staff", command.email)

        await self._store_service.check_store_exist(command.store_id)

        if command.manager_id:
            manager = await self._staff_repo.get_staff_by_id(command.manager_id)
            if not manager:
                raise EntityNotFoundError("Staff (manager)", command.manager_id)

        staff = Staff(
            first_name=command.first_name,
            last_name=command.last_name,
            email=command.email,
            store_id=command.store_id,
            phone=command.phone,
            manager_id=command.manager_id
        )
        created = await self._staff_repo.create(staff)
        return StaffDto.model_validate(created)

    async def get_staff_by_id(self, staff_id: int) -> StaffDto:
        """Return a staff member by their ID, raising 404 if not found."""
        staff = await self._staff_repo.get_staff_by_id(staff_id)
        if not staff:
            raise EntityNotFoundError("Staff", staff_id)
        return StaffDto.model_validate(staff)

    async def get_staff_by_email(self, email: str) -> StaffDto:
        """Return a staff member by their email, raising 404 if not found."""
        staff = await self._staff_repo.get_staff_by_email(email)
        if not staff:
            raise EntityNotFoundError("Staff", email)
        return StaffDto.model_validate(staff)

    async def search_staff_by_last_name(self, last_name: str) -> list[StaffDto]:
        """Return staff members whose last name contains the search term."""
        staff_list = await self._staff_repo.search_by_last_name(last_name)
        return [StaffDto.model_validate(s) for s in staff_list]

    async def get_all_staff(self, skip: int = 0, limit: int = 100) -> list[StaffDto]:
        """Return a paginated list of all staff members."""
        staff_list = await self._staff_repo.list_all(skip, limit)
        return [StaffDto.model_validate(s) for s in staff_list]

    async def update_staff(self, staff_id: int, command: UpdateStaffCommand) -> StaffDto:
        """Apply partial updates to an existing staff member."""
        staff = await self._staff_repo.get_staff_by_id(staff_id)
        if not staff:
            raise EntityNotFoundError("Staff", staff_id)

        if command.email and command.email != staff.email:
            conflicting = await self._staff_repo.get_staff_by_email(command.email)
            if conflicting:
                raise EntityAlreadyExistsException("Staff", command.email)

        if command.store_id and command.store_id != staff.store_id:
            await self._store_service.check_store_exist(command.store_id)

        if command.manager_id and command.manager_id != staff.manager_id:
            manager = await self._staff_repo.get_staff_by_id(command.manager_id)
            if not manager:
                raise EntityNotFoundError("Staff (manager)", command.manager_id)

        staff.update_information(
            first_name=command.first_name,
            last_name=command.last_name,
            email=command.email,
            phone=command.phone,
            store_id=command.store_id,
            manager_id=command.manager_id
        )
        updated = await self._staff_repo.update(staff)
        return StaffDto.model_validate(updated)
    
    async def activate_staff(self, staff_id: int) -> StaffDto:
        """Activate a staff member."""
        staff = await self._staff_repo.get_staff_by_id(staff_id)
        if not staff:
            raise EntityNotFoundError("Staff", staff_id)

        staff.activate()
        updated = await self._staff_repo.update(staff)
        return StaffDto.model_validate(updated)

    async def deactivate_staff(self, staff_id: int) -> StaffDto:
        """Deactivate a staff member."""
        staff = await self._staff_repo.get_staff_by_id(staff_id)
        if not staff:
            raise EntityNotFoundError("Staff", staff_id)

        staff.deactivate()
        updated = await self._staff_repo.update(staff)
        return StaffDto.model_validate(updated)  

    async def delete_staff(self, staff_id: int) -> StaffDto:
        """Hard-delete a staff member; raises 404 if not found."""
        staff = await self._staff_repo.get_staff_by_id(staff_id)
        if not staff:
            raise EntityNotFoundError("Staff", staff_id)

        await self._staff_repo.delete(staff_id)
        return StaffDto.model_validate(staff)

    async def check_staff_exist(self, staff_id: int) -> bool:
        """Assert the staff member exists; raises EntityNotFoundError otherwise."""
        staff = await self._staff_repo.get_staff_by_id(staff_id)
        if not staff:
            raise EntityNotFoundError("Staff", staff_id)
        return True
