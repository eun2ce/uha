from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model with camelCase field aliases."""

    class Config:
        alias_generator = to_camel
        populate_by_name = True


__all__ = ["CamelModel", "Field"]
