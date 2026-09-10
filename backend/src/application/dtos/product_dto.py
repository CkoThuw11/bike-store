from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateProductCommand(BaseModel):
    """Command for creating a product."""
    model_config = ConfigDict(str_strip_whitespace=True, strict=True, protected_namespaces=())

    product_name: str = Field(..., min_length=1, max_length=100, description="Product name")
    brand_id: int = Field(..., description="Brand ID")
    category_id: int = Field(..., description="Category ID")
    model_year: int = Field(..., ge=1900, le=2100, description="Model year")
    list_price: Decimal = Field(..., gt=0, description="List price")

    @field_validator("list_price", mode="before")
    @classmethod
    def parse_decimal(cls, v: object) -> Decimal:
        try:
            return Decimal(str(v))
        except Exception:
            raise ValueError(f"Invalid decimal value: {v}")


class UpdateProductCommand(BaseModel):
    """Command for updating a product."""
    model_config = ConfigDict(str_strip_whitespace=True, strict=True, protected_namespaces=())

    product_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Product name")
    brand_id: Optional[int] = Field(None, description="Brand ID")
    category_id: Optional[int] = Field(None, description="Category ID")
    model_year: Optional[int] = Field(None, ge=1900, le=2100, description="Model year")
    list_price: Optional[Decimal] = Field(None, gt=0, description="List price")

    @field_validator("list_price", mode="before")
    @classmethod
    def parse_decimal(cls, v: object) -> Decimal | None:
        if v is None:
            return None
        try:
            return Decimal(str(v))
        except Exception:
            raise ValueError(f"Invalid decimal value: {v}")


class ProductDto(BaseModel):
    """Product response DTO — minimal, for list views."""
    model_config = ConfigDict(from_attributes=True, strict=True, protected_namespaces=())

    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    brand_id: int = Field(..., description="Brand ID")
    category_id: int = Field(..., description="Category ID")
    model_year: int = Field(..., description="Model year")
    list_price: Decimal = Field(..., description="List price")
    is_active: bool = Field(..., description="Product status")


class ProductDetailDto(ProductDto):
    """Product detail response DTO — extends ProductDto with audit timestamps."""

    created_at: datetime = Field(..., description="Product created at")
    updated_at: datetime = Field(..., description="Product updated at")


class ProductListDto(BaseModel):
    """DTO for paginated product list response."""
    model_config = ConfigDict(from_attributes=True, strict=True, protected_namespaces=())

    products: List[ProductDto] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")