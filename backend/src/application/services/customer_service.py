from src.application.dtos.customer_dto import CustomerDto, CreateCustomerCommand, UpdateCustomerCommand
from src.domain.entities.customer import Customer
from src.domain.exceptions import EntityAlreadyExistsException, EntityNotFoundError
from src.domain.repositories.customer_repository import ICustomerRepository


class CustomerService:
    """Orchestrates all business logic related to customers."""

    def __init__(self, customer_repo: ICustomerRepository) -> None:
        self._customer_repo = customer_repo

    async def create_customer(self, command: CreateCustomerCommand) -> CustomerDto:
        """Create a new customer, enforcing email uniqueness when provided."""
        if command.email:
            existing = await self._customer_repo.get_customer_by_email(command.email)
            if existing:
                raise EntityAlreadyExistsException("Customer", command.email)

        address = getattr(command, "address", None)
        customer = Customer(
            first_name=command.first_name,
            last_name=command.last_name,
            phone=command.phone,
            email=command.email,
            street=getattr(address, "street", None),
            city=getattr(address, "city", None),
            state=getattr(address, "state", None),
            zip_code=getattr(address, "zip_code", None)
        )
        created = await self._customer_repo.create(customer)
        return CustomerDto.model_validate(created)

    async def get_customer_by_id(self, customer_id: int) -> CustomerDto:
        """Return a customer by their ID, raising 404 if not found."""
        customer = await self._customer_repo.get_customer_by_id(customer_id)
        if not customer:
            raise EntityNotFoundError("Customer", customer_id)
        return CustomerDto.model_validate(customer)

    async def get_customer_by_email(self, email: str) -> CustomerDto:
        """Return a customer by their email, raising 404 if not found."""
        customer = await self._customer_repo.get_customer_by_email(email)
        if not customer:
            raise EntityNotFoundError("Customer", email)
        return CustomerDto.model_validate(customer)

    async def search_customers_by_name(self, name: str) -> list[CustomerDto]:
        """Return customers whose first or last name contains the search term."""
        customers = await self._customer_repo.search_by_name(name)
        return [CustomerDto.model_validate(c) for c in customers]

    async def list_all_customers(self, skip: int = 0, limit: int = 100) -> list[CustomerDto]:
        """Return a paginated list of all customers."""
        customers = await self._customer_repo.list_all(skip, limit)
        return [CustomerDto.model_validate(c) for c in customers]

    async def update_customer(self, customer_id: int, command: UpdateCustomerCommand) -> CustomerDto:
        """Apply partial updates to an existing customer, enforcing email uniqueness."""
        customer = await self._customer_repo.get_customer_by_id(customer_id)
        if not customer:
            raise EntityNotFoundError("Customer", customer_id)

        if command.email and command.email != customer.email:
            conflicting = await self._customer_repo.get_customer_by_email(command.email)
            if conflicting:
                raise EntityAlreadyExistsException("Customer", command.email)

        address = getattr(command, "address", None)
        customer.update_information(
            first_name=command.first_name,
            last_name=command.last_name,
            phone=command.phone,
            email=command.email,
            street=getattr(address, "street", None),
            city=getattr(address, "city", None),
            state=getattr(address, "state", None),
            zip_code=getattr(address, "zip_code", None),
        )
        updated = await self._customer_repo.update(customer)
        return CustomerDto.model_validate(updated)

    async def activate_customer(self, customer_id: int) -> CustomerDto:
        """Activate a customer."""
        category = await self._customer_repo.get_customer_by_id(customer_id)
        if not category:
            raise EntityNotFoundError("Customer", customer_id)

        category.activate()
        updated = await self._customer_repo.update(category)
        return CustomerDto.model_validate(updated)

    async def deactivate_customer(self, customer_id: int) -> CustomerDto:
        """Deactivate a customer."""
        category = await self._customer_repo.get_customer_by_id(customer_id)
        if not category:
            raise EntityNotFoundError("Customer", customer_id)

        category.deactivate()
        updated = await self._customer_repo.update(category)
        return CustomerDto.model_validate(updated)
    

    async def delete_customer(self, customer_id: int) -> CustomerDto:
        """Hard-delete a customer record; raises 404 if not found."""
        customer = await self._customer_repo.get_customer_by_id(customer_id)
        if not customer:
            raise EntityNotFoundError("Customer", customer_id)

        await self._customer_repo.delete(customer_id)
        return CustomerDto.model_validate(customer)

    async def check_customer_exist(self, customer_id: int) -> bool:
        """Assert the customer exists; raises EntityNotFoundError otherwise."""
        customer = await self._customer_repo.get_customer_by_id(customer_id)
        if not customer:
            raise EntityNotFoundError("Customer", customer_id)
        return True
