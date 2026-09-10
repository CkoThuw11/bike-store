from dataclasses import dataclass, field

from .base_entity import BaseEntity


@dataclass(kw_only=True)
class Brand(BaseEntity):
    """Brand domain entity."""

    brand_name: str
    brand_id: int | None = field(default=None)

    def activate(self) -> None:
        self.is_active = True
        self.touch()

    def deactivate(self) -> None:
        self.is_active = False
        self.touch()

    def update_information(
        self,
        brand_name: str | None = None,
    ) -> None:
        self.apply_updates(
            brand_name=brand_name,
        )
