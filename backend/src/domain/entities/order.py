from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

from .base_entity import BaseEntity, utc_now


class OrderStatus(IntEnum):
    """Order lifecycle status."""

    PENDING = 1
    PROCESSING = 2
    SHIPPED = 3
    COMPLETED = 4
    CANCELLED = 5


@dataclass(kw_only=True)
class Order(BaseEntity):
    """Order domain entity."""

    customer_id: int
    order_status: OrderStatus = OrderStatus.PENDING
    required_date: datetime | None = None
    store_id: int | None
    staff_id: int | None

    order_date: datetime = field(default_factory=utc_now)
    shipped_date: datetime | None = None

    order_id: int | None = field(default=None)

    def update_information(
        self,
        order_status: int | None = None,
        order_date: datetime | None = None,
        required_date: datetime | None = None,
        shipped_date: datetime | None = None,
        store_id: int | None = None,
        staff_id: int | None = None,
    ) -> None:
        self.apply_updates(
            order_status=order_status,
            order_date=order_date,
            required_date=required_date,
            shipped_date=shipped_date,
            store_id=store_id,
            staff_id=staff_id,
        )
