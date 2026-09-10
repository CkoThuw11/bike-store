from dataclasses import dataclass, field

from .base_entity import BaseEntity


@dataclass(kw_only=True)
class Customer(BaseEntity):
    """Customer domain entity."""

    first_name: str
    last_name: str
    phone: str | None = None
    email: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    customer_id: int | None = field(default=None)

    def activate(self) -> None:
        self.is_active = True
        self.touch()

    def deactivate(self) -> None:
        self.is_active = False
        self.touch()

    def update_information(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        street: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
    ) -> None:
        self.apply_updates(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
        )