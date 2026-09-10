from dataclasses import dataclass, field
from enum import Enum

from .base_entity import BaseEntity


class Role(str, Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"


@dataclass(kw_only=True)
class User(BaseEntity):
    """User domain entity."""

    email: str
    password_hash: str
    username: str
    fullname: str

    role: Role = Role.CUSTOMER

    user_id: int | None = field(default=None)

    def activate(self) -> None:
        self.is_active = True
        self.touch()

    def deactivate(self) -> None:
        self.is_active = False
        self.touch()

    def update_password(
        self,
        new_password_hash: str,
    ) -> None:
        self.password_hash = new_password_hash
        self.touch()

    def update_information(
        self,
        email: str | None = None,
        username: str | None = None,
        fullname: str | None = None,
        role: Role | None = None,
    ) -> None:
        self.apply_updates(
            email=email,
            username=username,
            fullname=fullname,
            role=role,
        )

    def is_valid_for_login(self) -> bool:
        return self.is_active

    def has_role(self, role: Role) -> bool:
        return self.role == role