from dataclasses import dataclass, field

from .base_entity import BaseEntity


@dataclass(kw_only=True)
class Staff(BaseEntity):
    """Staff domain entity representing a store employee."""

    first_name: str
    last_name: str
    email: str
    store_id: int
    phone: str
    manager_id: int | None = None
    is_active: bool = True
    staff_id: int | None = field(default=None)

    def activate(self) -> None:
        """Mark the staff member as active."""
        self.is_active = True
        self.touch()

    def deactivate(self) -> None:
        """Mark the staff member as inactive."""
        self.is_active = False
        self.touch()

    def update_information(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        store_id: int | None = None,
        manager_id: int | None = None,
    ) -> None:
        """Apply partial staff information updates."""
        self.apply_updates(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            store_id=store_id,
            manager_id=manager_id,
        )
