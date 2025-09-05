from dataclasses import dataclass, field
from datetime import datetime

from pendulum import DateTime


@dataclass(init=True, kw_only=True)
class TimeStampMixin:
    """Mixin to add timestamp fields to entities."""

    created_at: datetime = field(default_factory=lambda: DateTime.now(tz="UTC"), repr=False)
    updated_at: datetime = field(default_factory=lambda: DateTime.now(tz="UTC"), repr=False)
