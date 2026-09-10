from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AddressCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    street: Optional[str] = Field(None, max_length=255, description="Street")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State")
    zip_code: Optional[str] = Field(None, max_length=10, description="Zip code")


class CreateCustomerCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    phone: Optional[str] = Field(None, max_length=15, description="Phone number")
    email: Optional[str] = Field(None, max_length=100, description="Email address")
    address: Optional[AddressCommand] = None


class UpdateCustomerCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[AddressCommand] = None


class CustomerDto(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)
    customer_id: int = Field(..., description="Customer ID")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    street: Optional[str] = Field(None, description="Street")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    zip_code: Optional[str] = Field(None, description="Zip code")
    is_active: bool = Field(..., description="Is active")
    created_at: datetime = Field(..., description="Record created at")
    updated_at: datetime = Field(..., description="Record last updated at")


class CustomerListDto(BaseModel):
    model_config = ConfigDict(strict=True)
    customers: List[CustomerDto] = Field(..., description="List of customers")
    total: int = Field(..., description="Total number of customers")
    skip: int = Field(..., ge=0, description="Number of records skipped")
    limit: int = Field(..., ge=1, description="Maximum number of records returned")
