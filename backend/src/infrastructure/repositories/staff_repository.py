from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.staff import Staff
from src.domain.repositories.staff_repository import IStaffRepository
from src.infrastructure.database.models import StaffModel


class StaffRepository(IStaffRepository):
    """SQLAlchemy implementation of IStaffRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: StaffModel) -> Staff:
        return Staff(
            staff_id=model.staff_id,
            first_name=model.first_name,
            last_name=model.last_name,
            phone=model.phone,
            email=model.email,
            store_id=model.store_id,
            manager_id=model.manager_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Staff) -> StaffModel:
        return StaffModel(
            staff_id=entity.staff_id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            phone=entity.phone,
            store_id=entity.store_id,
            manager_id=entity.manager_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, staff: Staff) -> Staff:
        """Persist a new staff member and return the DB-assigned entity."""
        model = self._to_model(staff)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_staff_by_id(self, staff_id: int) -> Staff | None:
        """Return the staff member with the given ID, or None."""
        result = await self._session.execute(
            select(StaffModel).where(StaffModel.staff_id == staff_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_staff_by_email(self, email: str) -> Staff | None:
        """Return the staff member with the given email, or None."""
        result = await self._session.execute(
            select(StaffModel).where(StaffModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_staff_by_last_name(self, last_name: str) -> Staff | None:
        """Return all staff members with the given last name."""
        result = await self._session.execute(
            select(StaffModel).where(StaffModel.last_name == last_name)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def search_by_last_name(self, last_name: str) -> list[Staff]:
        """Return staff members whose last name contains the search term (case-insensitive)."""
        term = f"%{last_name}%"
        result = await self._session.execute(
            select(StaffModel).where(StaffModel.last_name.ilike(term))
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Staff]:
        """Return a paginated list of all staff members."""
        result = await self._session.execute(
            select(StaffModel).offset(skip).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, staff: Staff) -> Staff:
        """Flush staff changes to the DB and return the refreshed entity."""
        result = await self._session.execute(
            select(StaffModel).where(StaffModel.staff_id == staff.staff_id)
        )
        model = result.scalar_one()
        model.first_name = staff.first_name
        model.last_name = staff.last_name
        model.email = staff.email
        model.phone = staff.phone
        model.store_id = staff.store_id
        model.manager_id = staff.manager_id
        model.is_active = staff.is_active
        model.updated_at = staff.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, staff_id: int) -> bool:
        """Delete the staff row. Returns True if a row was actually removed."""
        result = await self._session.execute(
            select(StaffModel).where(StaffModel.staff_id == staff_id)
        )
        model = result.scalar_one_or_none()
        if model: 
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
