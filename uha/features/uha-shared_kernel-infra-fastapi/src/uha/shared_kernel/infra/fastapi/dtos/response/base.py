from typing import TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ResponseDto[DataT](BaseModel):
    """Base response DTO."""

    status: str | int
    message: str | None = None
    data: DataT | None = None
