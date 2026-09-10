from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.domain.entities.order import (
    OrderStatus,
)


class CreateOrderCommand(BaseModel):
    """
    Create an empty order/cart.

    Notes:
    - Acts as shopping cart initially
    - No store assignment yet
    - No staff assignment yet
    - No shipment yet
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        strict=True,
    )

    customer_id: int = Field(
        ...,
        description="Customer ID",
    )


class CheckoutOrderCommand(BaseModel):
    """
    Checkout pending order.

    Trigger actual business workflow:
    - validate stock
    - assign store
    - assign staff
    - deduct stock
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        strict=True,
    )

    required_date: datetime = Field(
        ...,
        description="Required delivery date",
    )

    @field_validator("required_date", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, datetime):
            return v.replace(tzinfo=None) if v.tzinfo else v
        if isinstance(v, str):
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            return dt.replace(tzinfo=None)
        raise ValueError(f"Invalid datetime: {v}")

class UpdateOrderCommand(BaseModel):
    """Update order information."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        strict=True,
    )

    order_status: Optional[OrderStatus] = None

    required_date: Optional[datetime] = None

    shipped_date: Optional[datetime] = None

    @field_validator("order_status", mode="before")
    @classmethod
    def parse_order_status(cls, v):
        if isinstance(v, OrderStatus):
            return v
        if isinstance(v, int):
            return OrderStatus(v)
        raise ValueError(f"Invalid order_status: {v}")

    @field_validator("required_date", "shipped_date", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, datetime):
            return v.replace(tzinfo=None) if v.tzinfo else v
        if isinstance(v, str):
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            return dt.replace(tzinfo=None)
        raise ValueError(f"Invalid datetime: {v}")


class OrderDto(BaseModel):
    """Order response DTO."""

    model_config = ConfigDict(
        from_attributes=True,
        strict=True,
    )

    order_id: int
    customer_id: int

    order_status: OrderStatus

    order_date: datetime

    required_date: Optional[datetime]

    shipped_date: Optional[datetime]

    store_id: Optional[int]

    staff_id: Optional[int]

    created_at: datetime
    updated_at: datetime


class OrderListDto(BaseModel):
    """Paginated order list DTO."""

    model_config = ConfigDict(
        from_attributes=True,
        strict=True,
    )

    orders: List[OrderDto]

    total: int

    skip: int

    limit: int