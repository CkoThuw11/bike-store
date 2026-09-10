from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.customer import Customer
from src.domain.repositories.customer_repository import ICustomerRepository
from src.infrastructure.database.models import CustomerModel


class CustomerRepository(ICustomerRepository):
    """SQLAlchemy implementation of ICustomerRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: CustomerModel) -> Customer:
        return Customer(
            customer_id=model.customer_id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            phone=model.phone,
            street=model.street,
            city=model.city,
            state=model.state,
            zip_code=model.zip_code,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Customer) -> CustomerModel:
        return CustomerModel(
            customer_id=entity.customer_id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            phone=entity.phone,
            street=entity.street,
            city=entity.city,
            state=entity.state,
            zip_code=entity.zip_code,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, customer: Customer) -> Customer:
        """Persist a new customer and return the DB-assigned entity."""
        model = self._to_model(customer)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_customer_by_id(self, customer_id: int) -> Customer | None:
        """Return the customer with the given ID, or None."""
        result = await self._session.execute(
            select(CustomerModel).where(CustomerModel.customer_id == customer_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_customer_by_email(self, email: str) -> Customer | None:
        """Return the customer with the given email, or None."""
        result = await self._session.execute(
            select(CustomerModel).where(CustomerModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_customer_by_name(self, first_name: str) -> Customer | None:
        """Return a single customer matching the exact first name, or None."""
        result = await self._session.execute(
            select(CustomerModel).where(CustomerModel.first_name == first_name)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def search_by_name(self, name: str) -> list[Customer]:
        """Return customers whose first or last name contains the search term (case-insensitive)."""
        term = f"%{name}%"
        result = await self._session.execute(
            select(CustomerModel).where(
                or_(
                    CustomerModel.first_name.ilike(term),
                    CustomerModel.last_name.ilike(term),
                )
            )
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Customer]:
        """Return a paginated list of all customers."""
        result = await self._session.execute(select(CustomerModel).offset(skip).limit(limit))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, customer: Customer) -> Customer:
        """Flush customer changes to the DB and return the refreshed entity."""
        result = await self._session.execute(
            select(CustomerModel).where(CustomerModel.customer_id == customer.customer_id)
        )
        model = result.scalar_one()
        model.first_name = customer.first_name
        model.last_name = customer.last_name
        model.email = customer.email
        model.phone = customer.phone
        model.street = customer.street
        model.city = customer.city
        model.state = customer.state
        model.zip_code = customer.zip_code
        model.is_active = customer.is_active
        model.updated_at = customer.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, customer_id: int) -> bool:
        """Delete the customer row. Returns True if a row was actually removed."""
        result = await self._session.execute(
            select(CustomerModel).where(CustomerModel.customer_id == customer_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
