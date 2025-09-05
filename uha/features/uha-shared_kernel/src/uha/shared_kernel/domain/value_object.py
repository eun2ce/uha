from enum import Enum, EnumMeta
from typing import Any, TypeVar

from uha.shared_kernel.domain.exception import ValueObjectEnumError

ValueObjectType = TypeVar("ValueObjectType", bound="ValueObject")


class ValueObject:
    """Base value object class."""
    
    def __composite_values__(self):
        return (self.value,)

    @classmethod
    def from_value(cls, value: Any) -> ValueObjectType:
        """Create a value object from a value."""
        if isinstance(cls, EnumMeta):
            for item in cls:
                if item.value == value:
                    return item
            raise ValueObjectEnumError

        instance = cls(value=value)
        return instance


class Status(ValueObject, str, Enum):
    """Generic status value object."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"

    @property
    def is_active(self) -> bool:
        return self == Status.ACTIVE

    @property
    def is_inactive(self) -> bool:
        return self == Status.INACTIVE

    @property
    def is_pending(self) -> bool:
        return self == Status.PENDING
