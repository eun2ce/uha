from typing import TypeVar

EntityType = TypeVar("EntityType", bound="Entity")


class Entity:
    """Base entity class for domain entities."""

    pass


class AggregateRoot(Entity):
    """Base aggregate root class for domain aggregates."""

    pass
