from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateCategoryCommand(BaseModel):
    """Command for creating a new product category."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    category_name: str = Field(..., min_length=1, max_length=100, description="Category name")

class UpdateCategoryCommand(BaseModel):
    """Command for partially updating an existing category."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    category_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Category name"
    )


class ActivateCategoryCommand(BaseModel):
    """Command for activating a category."""

    category_id: int


class DeactivateCategoryCommand(BaseModel):
    """Command for deactivating a category."""

    category_id: int

class CategoryDto(BaseModel):
    """Category response DTO."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    category_id: int = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name")
    is_active: bool = Field(..., description="Category status")
    created_at: datetime = Field(..., description="Record created at")
    updated_at: datetime = Field(..., description="Record last updated at")


class CategoryListDto(BaseModel):
    """DTO for paginated category list responses."""

    model_config = ConfigDict(strict=True)
    categories: List[CategoryDto] = Field(..., description="List of categories")
    total: int = Field(..., description="Total number of categories")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
