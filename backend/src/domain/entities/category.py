from dataclasses import dataclass, field

from .base_entity import BaseEntity


@dataclass(kw_only=True)
class Category(BaseEntity):
    """Category domain entity."""

    category_name: str
    category_id: int | None = field(default=None)

    def activate(self) -> None:
        self.is_active = True
        self.touch()

    def deactivate(self) -> None:
        self.is_active = False
        self.touch()

    def update_information(
        self,
        category_name: str | None = None,
    ) -> None:
        self.apply_updates(
            category_name=category_name,
        )
