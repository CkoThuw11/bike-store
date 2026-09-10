from src.application.dtos.category_dto import (
    CategoryDto,
    CategoryListDto,
    CreateCategoryCommand,
    UpdateCategoryCommand,
)
from src.domain.entities.category import Category
from src.domain.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundError,
)
from src.domain.repositories.category_repository import ICategoryRepository


class CategoryService:
    """Orchestrates all business logic related to product categories."""

    def __init__(self, category_repo: ICategoryRepository) -> None:
        self._category_repo = category_repo

    async def create_category(self, command: CreateCategoryCommand) -> CategoryDto:
        """Create a new category, enforcing uniqueness on category_name."""
        if await self._category_repo.get_category_by_name(command.category_name):
            raise EntityAlreadyExistsException("Category", command.category_name)
        category = Category(category_name=command.category_name)
        created_category = await self._category_repo.create(category)
        return CategoryDto.model_validate(created_category)

    async def get_category_by_id(self, category_id: int) -> CategoryDto:
        """Return a category by its ID, raising 404 if not found."""
        category = await self._category_repo.get_category_by_id(category_id)
        if not category:
            raise EntityNotFoundError("Category", category_id)
        return CategoryDto.model_validate(category)

    async def get_category_by_name(self, category_name: str) -> CategoryDto:
        """Return a category by its name, raising 404 if not found."""
        category = await self._category_repo.get_category_by_name(category_name)
        if not category:
            raise EntityNotFoundError("Category", category_name)
        return CategoryDto.model_validate(category)

    async def list_categories(self, skip: int = 0, limit: int = 100) -> CategoryListDto:
        """Return a paginated list of all categories."""
        result = await self._category_repo.list_all(skip, limit)
        categories, total = result if isinstance(result, tuple) else (result, len(result))
        return CategoryListDto(
            categories=[CategoryDto.model_validate(c) for c in categories],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def list_all_categories(self, skip: int = 0, limit: int = 100) -> list[CategoryDto]:
        """Return a paginated list of category DTOs."""
        result = await self.list_categories(skip, limit)
        return result.categories

    async def update_category(
        self, category_id: int, command: UpdateCategoryCommand
    ) -> CategoryDto:
        """Apply partial updates to an existing category, enforcing name uniqueness."""
        category = await self._category_repo.get_category_by_id(category_id)
        if not category:
            raise EntityNotFoundError("Category", category_id)

        if (
            command.category_name
            and command.category_name != category.category_name
            and await self._category_repo.get_category_by_name(command.category_name)
        ):
            raise EntityAlreadyExistsException("Category", command.category_name)

        category.update_information(category_name=command.category_name)
        updated = await self._category_repo.update(category)
        return CategoryDto.model_validate(updated)

    async def activate_category(self, category_id: int) -> CategoryDto:
        """Activate a category."""
        category = await self._category_repo.get_category_by_id(category_id)
        if not category:
            raise EntityNotFoundError("Category", category_id)

        category.activate()
        updated = await self._category_repo.update(category)
        return CategoryDto.model_validate(updated)

    async def deactivate_category(self, category_id: int) -> CategoryDto:
        """Deactivate a category."""
        category = await self._category_repo.get_category_by_id(category_id)
        if not category:
            raise EntityNotFoundError("Category", category_id)

        category.deactivate()
        updated = await self._category_repo.update(category)
        return CategoryDto.model_validate(updated)

    async def delete_category(self, category_id: int) -> CategoryDto:
        """Hard-delete a category."""
        category = await self._category_repo.get_category_by_id(category_id)
        if not category:
            raise EntityNotFoundError("Category", category_id)

        await self._category_repo.delete(category_id)
        return CategoryDto.model_validate(category)

    async def check_category_exists(self, category_id: int) -> None:
        """Raises EntityNotFoundError if the category does not exist."""
        if not await self._category_repo.get_category_by_id(category_id):
            raise EntityNotFoundError("Category", category_id)

    async def check_category_exist(self, category_id: int) -> bool:
        """Return True when the category exists; raise EntityNotFoundError otherwise."""
        await self.check_category_exists(category_id)
        return True
