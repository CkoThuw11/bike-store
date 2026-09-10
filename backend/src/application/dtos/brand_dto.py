from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateBrandCommand(BaseModel):
    """Command for creating a new brand."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    brand_name: str = Field(..., min_length=1, max_length=100, description="Brand name")


class UpdateBrandCommand(BaseModel):
    """Command for partially updating an existing brand."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    brand_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Brand name"
    )


class ActivateBrandCommand(BaseModel):
    """Command for activating a brand."""

    brand_id: int


class DeactivateBrandCommand(BaseModel):
    """Command for deactivating a brand."""

    brand_id: int

class BrandDto(BaseModel):
    """Brand response DTO."""

    model_config = ConfigDict(from_attributes=True, strict=True)
    brand_id: int = Field(..., description="Brand ID")
    brand_name: str = Field(..., description="Brand name")
    is_active: bool = Field(..., description="Brand status")
    created_at: datetime = Field(..., description="Record created at")
    updated_at: datetime = Field(..., description="Record last updated at")


class BrandListDto(BaseModel):
    """DTO for paginated brand list responses."""

    model_config = ConfigDict(strict=True)
    brands: List[BrandDto] = Field(..., description="List of brands")
    total: int = Field(..., description="Total number of brands")
    skip: int = Field(..., ge=0, description="Number of records skipped")
    limit: int = Field(..., ge=1, description="Maximum number of records returned")
