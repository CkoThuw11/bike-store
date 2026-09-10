from dataclasses import dataclass, field
from decimal import Decimal

from .base_entity import BaseEntity


@dataclass(kw_only=True)
class OrderItem(BaseEntity):
    """Order item domain entity."""

    order_id: int
    product_id: int
    quantity: int
    list_price: Decimal

    discount: Decimal = Decimal("0")

    item_id: int | None = field(default=None)

    def update_information(
        self,
        quantity: int | None = None,
        list_price: Decimal | None = None,
        discount: Decimal | None = None,
    ) -> None:
        self.apply_updates(
            quantity=quantity,
            list_price=list_price,
            discount=discount,
        )

    def upsert_information(
        self,
        quantity: int,
        list_price: Decimal | None = None,
        discount: Decimal | None = None,
    ) -> None:
        self.quantity += quantity

        self.apply_updates(
            list_price=list_price,
            discount=discount,
        )