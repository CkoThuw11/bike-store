# src/application/dtos/order_item_dto.py

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateOrderItemCommand(BaseModel):
    """
    Add product into pending order/cart.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        strict=True,
    )

    order_id: int

    product_id: int

    quantity: int = Field(
        ...,
        gt=0,
    )

    discount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    @field_validator("discount", mode="before")
    @classmethod
    def parse_decimal(cls, v: object) -> Decimal:
        try:
            return Decimal(str(v))
        except Exception:
            raise ValueError(f"Invalid decimal value: {v}")


class UpdateOrderItemCommand(BaseModel):
    """Update order item quantity."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        strict=True,
    )

    quantity: Optional[int] = Field(
        None,
        gt=0,
    )


class OrderItemDto(BaseModel):
    """Order item response DTO."""

    model_config = ConfigDict(
        from_attributes=True,
        strict=True,
    )

    order_id: int

    item_id: int

    product_id: int

    quantity: int

    list_price: Decimal

    discount: Decimal

    created_at: datetime

    updated_at: datetime


class OrderItemListDto(BaseModel):
    """Paginated order item list DTO."""

    model_config = ConfigDict(
        from_attributes=True,
        strict=True,
    )

    order_items: List[OrderItemDto]

    total: int

    skip: int

    limit: int