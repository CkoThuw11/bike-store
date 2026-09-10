from dataclasses import dataclass, field
from decimal import Decimal

from .base_entity import BaseEntity


@dataclass(kw_only=True)
class Product(BaseEntity):
    """Product domain entity representing a catalog item."""

    product_name: str
    brand_id: int
    category_id: int
    model_year: int
    list_price: Decimal
    is_active: bool = True
    product_id: int | None = field(default=None)

    def activate(self) -> None:
        """Mark the product as active."""
        self.is_active = True
        self.touch()

    def deactivate(self) -> None:
        """Mark the product as inactive."""
        self.is_active = False
        self.touch()

    def update_information(
        self,
        product_name: str | None = None,
        brand_id: int | None = None,
        category_id: int | None = None,
        model_year: int | None = None,
        list_price: Decimal | None = None,
        is_active: bool | None = None,
    ) -> None:
        """Apply partial product information updates."""
        self.apply_updates(
            product_name=product_name,
            brand_id=brand_id,
            category_id=category_id,
            model_year=model_year,
            list_price=list_price,
            is_active=is_active,
        )
