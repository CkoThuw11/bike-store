from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateStaffCommand(BaseModel):
    """Command for creating a new staff member."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    email: EmailStr = Field(..., description="Work email address")
    phone: str = Field(..., description="Phone number")
    store_id: int = Field(..., description="Assigned store ID")
    manager_id: int | None = Field(None, description="Manager's staff ID (None = top-level)")


class UpdateStaffCommand(BaseModel):
    """Command for partially updating an existing staff member."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    first_name: str | None = Field(None, min_length=1, max_length=100, description="First name")
    last_name: str | None = Field(None, min_length=1, max_length=100, description="Last name")
    email: EmailStr | None = Field(None, description="Work email address")
    phone: str | None = Field(None, description="Phone number")
    store_id: int | None = Field(None, description="Assigned store ID")
    manager_id: int | None = Field(None, description="Manager's staff ID")


class StaffDto(BaseModel):
    """Staff response DTO — minimal, for list views."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    staff_id: int = Field(..., description="Staff ID")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: EmailStr = Field(..., description="Work email address")
    phone: str | None = Field(None, description="Phone number")
    store_id: int = Field(..., description="Assigned store ID")
    manager_id: int | None = Field(None, description="Manager's staff ID")
    is_active: bool = Field(..., description="Staff status")


class StaffDetailDto(StaffDto):
    """Staff detail response DTO — extends StaffDto with audit timestamps."""

    created_at: datetime = Field(..., description="Record created at")
    updated_at: datetime = Field(..., description="Record last updated at")


class StaffListDto(BaseModel):
    """DTO for paginated staff list responses."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    staffs: list[StaffDto] = Field(..., description="List of staff members")
    total: int = Field(..., description="Total number of staff members")
    skip: int = Field(..., description="Number of staff members skipped")
    limit: int = Field(..., description="Number of staff members returned")
