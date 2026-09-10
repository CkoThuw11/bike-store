from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class CreateStoreCommand(BaseModel):
    """Command for creating a store."""
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    store_name: str = Field(..., min_length=1, max_length=100, description="Store name")
    phone: str = Field(..., description="Phone")
    email: str = Field(..., description="Email")
    street: str = Field(..., description="Street")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    zip_code: str = Field(..., description="Zip code")

class UpdateStoreCommand(BaseModel):
    """Command for updating a store."""
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    store_name:  Optional[str]  = Field(None, min_length=1, max_length=100, description="Store name")
    phone:  Optional[str]  = Field(None, description="Phone")
    email:  Optional[str]  = Field(None, description="Email")
    street:  Optional[str]  = Field(None, description="Street")
    city:  Optional[str] = Field(None, description="City")
    state:  Optional[str]  = Field(None, description="State")
    zip_code:  Optional[str]  = Field(None, description="Zip code")


class StoreDto(BaseModel):
    """Store response DTO."""
    model_config = ConfigDict(from_attributes=True, strict = True)
    store_id: int = Field(..., description="Store ID")
    store_name: str = Field(..., description="Store name")
    phone: str = Field(..., description="Phone")
    email: str = Field(..., description="Email")
    street: str = Field(..., description="Street")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    zip_code: str = Field(..., description="Zip code")
    is_active: bool = Field(..., description="Store status")
    created_at: datetime = Field(..., description="Store create at")
    updated_at: datetime = Field(..., description="Store update at")

class StoreListDto(BaseModel):
    """DTO for paginated store list response."""
    model_config = ConfigDict(strict = True)
    stores: List[StoreDto] = Field(..., description="List of stores")
    total: int = Field(..., description="Total number of stores")
    skip: int = Field(..., description="Number of stores to skip")
    limit: int = Field(..., description="Number of stores to limit")
