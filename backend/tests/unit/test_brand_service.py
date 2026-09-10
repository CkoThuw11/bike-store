import pytest

from src.application.dtos.brand_dto import CreateBrandCommand, UpdateBrandCommand
from src.application.services.brand_service import BrandService
from src.domain.entities.brand import Brand
from src.domain.exceptions import BusinessRuleViolationError, EntityAlreadyExistsException

pytestmark = [pytest.mark.unit]


class InMemoryBrandRepository:
    def __init__(self) -> None:
        self.brands: list[Brand] = []
        self._next_id = 1

    async def create(self, brand: Brand) -> Brand:
        brand.brand_id = self._next_id
        self._next_id += 1
        self.brands.append(brand)
        return brand

    async def get_brand_by_id(self, brand_id: int) -> Brand | None:
        return next((b for b in self.brands if b.brand_id == brand_id), None)

    async def get_brand_by_name(self, brand_name: str) -> Brand | None:
        return next((b for b in self.brands if b.brand_name == brand_name), None)

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Brand]:
        return self.brands[skip : skip + limit]

    async def update(self, brand: Brand) -> Brand:
        return brand

    async def delete(self, brand_id: int) -> bool:
        self.brands = [brand for brand in self.brands if brand.brand_id != brand_id]
        return True


@pytest.mark.asyncio
async def test_create_brand_assigns_id_and_defaults_to_active():
    repo = InMemoryBrandRepository()
    service = BrandService(repo)

    result = await service.create_brand(CreateBrandCommand(brand_name="Trek"))

    assert result.brand_id == 1
    assert result.brand_name == "Trek"
    assert result.is_active is True
    assert len(repo.brands) == 1


@pytest.mark.asyncio
async def test_update_brand_rejects_duplicate_name():
    repo = InMemoryBrandRepository()
    await repo.create(Brand(brand_name="Trek"))
    await repo.create(Brand(brand_name="Giant"))
    service = BrandService(repo)

    with pytest.raises(EntityAlreadyExistsException):
        await service.update_brand(
            1,
            UpdateBrandCommand(brand_name="Giant"),
        )


@pytest.mark.asyncio
async def test_delete_brand_requires_brand_to_be_inactive():
    repo = InMemoryBrandRepository()
    created = await repo.create(Brand(brand_name="Trek"))
    service = BrandService(repo)

    with pytest.raises(BusinessRuleViolationError):
        await service.delete_brand(created.brand_id)
