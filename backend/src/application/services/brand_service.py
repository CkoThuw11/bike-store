from src.application.dtos.brand_dto import (
    BrandDto,
    BrandListDto,
    CreateBrandCommand,
    UpdateBrandCommand,
)
from src.domain.entities.brand import Brand
from src.domain.exceptions import (
    BusinessRuleViolationError,
    EntityAlreadyExistsException,
    EntityNotFoundError,
)
from src.domain.repositories.brand_repository import IBrandRepository


class BrandService:
    """Orchestrates all business logic related to brands."""

    def __init__(self, brand_repo: IBrandRepository) -> None:
        self._brand_repo = brand_repo

    async def create_brand(self, command: CreateBrandCommand) -> BrandDto:
        """Create a new brand, enforcing uniqueness on brand_name."""
        if await self._brand_repo.get_brand_by_name(command.brand_name):
            raise EntityAlreadyExistsException("Brand", command.brand_name)
        brand = Brand(brand_name=command.brand_name)
        created_brand = await self._brand_repo.create(brand)
        return BrandDto.model_validate(created_brand)

    async def get_brand_by_id(self, brand_id: int) -> BrandDto:
        """Return a brand by its ID, raising 404 if not found."""
        brand = await self._brand_repo.get_brand_by_id(brand_id)
        if not brand:
            raise EntityNotFoundError("Brand", brand_id)
        return BrandDto.model_validate(brand)

    async def get_brand_by_name(self, brand_name: str) -> BrandDto:
        """Return a brand by its name, raising 404 if not found."""
        brand = await self._brand_repo.get_brand_by_name(brand_name)
        if not brand:
            raise EntityNotFoundError("Brand", brand_name)
        return BrandDto.model_validate(brand)

    async def list_brands(self, skip: int = 0, limit: int = 100) -> BrandListDto:
        """Return a paginated list of all brands."""
        result = await self._brand_repo.list_all(skip, limit)
        brands, total = result if isinstance(result, tuple) else (result, len(result))
        return BrandListDto(
            brands=[BrandDto.model_validate(b) for b in brands],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def list_all_brands(self, skip: int = 0, limit: int = 100) -> list[BrandDto]:
        """Return a paginated list of brand DTOs."""
        result = await self.list_brands(skip, limit)
        return result.brands

    async def update_brand(self, brand_id: int, command: UpdateBrandCommand) -> BrandDto:
        """Apply partial updates to an existing brand, enforcing name uniqueness."""
        brand = await self._brand_repo.get_brand_by_id(brand_id)
        if not brand:
            raise EntityNotFoundError("Brand", brand_id)

        if (
            command.brand_name
            and command.brand_name != brand.brand_name
            and await self._brand_repo.get_brand_by_name(command.brand_name)
        ):
            raise EntityAlreadyExistsException("Brand", command.brand_name)

        brand.update_information(brand_name=command.brand_name)
        updated = await self._brand_repo.update(brand)
        return BrandDto.model_validate(updated)

    async def activate_brand(self, brand_id: int) -> BrandDto:
        """Activate a brand."""
        brand = await self._brand_repo.get_brand_by_id(brand_id)
        if not brand:
            raise EntityNotFoundError("Brand", brand_id)

        brand.activate()
        updated = await self._brand_repo.update(brand)
        return BrandDto.model_validate(updated)

    async def deactivate_brand(self, brand_id: int) -> BrandDto:
        """Deactivate a brand."""
        brand = await self._brand_repo.get_brand_by_id(brand_id)
        if not brand:
            raise EntityNotFoundError("Brand", brand_id)

        brand.deactivate()
        updated = await self._brand_repo.update(brand)
        return BrandDto.model_validate(updated)

    async def delete_brand(self, brand_id: int) -> BrandDto:
        """Hard-delete a brand; raises 422 if it is still active."""
        brand = await self._brand_repo.get_brand_by_id(brand_id)
        if not brand:
            raise EntityNotFoundError("Brand", brand_id)

        if brand.is_active:
            raise BusinessRuleViolationError(
                f"Brand '{brand.brand_name}' is active and cannot be deleted. "
                "Deactivate it first or reassign its products."
            )

        await self._brand_repo.delete(brand_id)
        return BrandDto.model_validate(brand)

    async def check_brand_exists(self, brand_id: int) -> None:
        """Raises EntityNotFoundError if the brand does not exist."""
        if not await self._brand_repo.get_brand_by_id(brand_id):
            raise EntityNotFoundError("Brand", brand_id)

    async def check_brand_exist(self, brand_id: int) -> bool:
        """Return True when the brand exists; raise EntityNotFoundError otherwise."""
        await self.check_brand_exists(brand_id)
        return True
