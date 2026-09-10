from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AddressCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    street: str | None = Field(None, max_length=255, description="Street")
    city: str | None = Field(None, max_length=100, description="City")
    state: str | None = Field(None, max_length=100, description="State")
    zip_code: str | None = Field(None, max_length=10, description="Zip code")


class CreateCustomerCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    phone: str | None = Field(None, max_length=15, description="Phone number")
    email: str | None = Field(None, max_length=100, description="Email address")
    address: AddressCommand | None = None


class UpdateCustomerCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=15)
    email: str | None = Field(None, max_length=100)
    address: AddressCommand | None = None


class CustomerDto(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)
    customer_id: int = Field(..., description="Customer ID")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    phone: str | None = Field(None, description="Phone number")
    email: str | None = Field(None, description="Email address")
    street: str | None = Field(None, description="Street")
    city: str | None = Field(None, description="City")
    state: str | None = Field(None, description="State")
    zip_code: str | None = Field(None, description="Zip code")
    is_active: bool = Field(..., description="Is active")
    created_at: datetime = Field(..., description="Record created at")
    updated_at: datetime = Field(..., description="Record last updated at")


class CustomerListDto(BaseModel):
    model_config = ConfigDict(strict=True)
    customers: list[CustomerDto] = Field(..., description="List of customers")
    total: int = Field(..., description="Total number of customers")
    skip: int = Field(..., ge=0, description="Number of records skipped")
    limit: int = Field(..., ge=1, description="Maximum number of records returned")
