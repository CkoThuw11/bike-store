from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


@dataclass(kw_only=True)
class BaseEntity:
    """Base entity with internal audit fields."""

    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    is_active: bool = field(default=True)

    def touch(self) -> None:
        self.updated_at = utc_now()

    def apply_updates(self, **changes: Any) -> None:
        for field_name, value in changes.items():
            if value is not None and hasattr(self, field_name):
                setattr(self, field_name, value)

        self.touch()
