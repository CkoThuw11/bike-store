from dataclasses import dataclass, field

from .base_entity import BaseEntity


@dataclass(kw_only=True)
class Stock(BaseEntity):
    """Stock domain entity representing product inventory at a store."""

    store_id: int | None
    product_id: int | None
    quantity: int
    stock_id: int | None = field(default=None)

    def update_information(self, quantity: int | None = None) -> None:
        """Apply partial stock information updates."""
        self.apply_updates(quantity=quantity)
