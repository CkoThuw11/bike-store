from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateStockCommand(BaseModel):
    """Command for creating a stock record for a product in a store."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    store_id: int = Field(..., description="Store ID")
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., ge=0, description="Initial quantity")


class UpdateStockCommand(BaseModel):
    """Command for updating the quantity of a stock record."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    quantity: int = Field(..., ge=0, description="New quantity")


class StockDto(BaseModel):
    """Stock response DTO."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    store_id: int = Field(..., description="Store ID")
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., description="Current quantity")
    created_at: datetime = Field(..., description="Record created at")
    updated_at: datetime = Field(..., description="Record last updated at")


class StockListDto(BaseModel):
    """DTO for paginated stock list response."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    stocks: list[StockDto] = Field(..., description="List of stock records")
    total: int = Field(..., description="Total number of stock records")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
