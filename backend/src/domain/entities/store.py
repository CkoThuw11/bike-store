from dataclasses import dataclass, field

from .base_entity import BaseEntity


@dataclass(kw_only=True)
class Store(BaseEntity):
    """Store domain entity representing a physical location."""

    store_name: str
    phone: str
    email: str
    street: str
    city: str
    state: str
    zip_code: str
    is_active: bool = True
    store_id: int | None = field(default=None)

    def activate(self) -> None:
        """Mark the store as active."""
        self.is_active = True
        self.touch()

    def deactivate(self) -> None:
        """Mark the store as inactive."""
        self.is_active = False
        self.touch()

    def update_information(
        self,
        store_name: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        street: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
    ) -> None:
        """Apply partial store information updates."""
        self.apply_updates(
            store_name=store_name,
            phone=phone,
            email=email,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
        )
