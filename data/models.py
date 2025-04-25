from typing import Self

from pydantic import BaseModel


class Position(BaseModel):
    title: str
    institution: str | None = None


class Person(BaseModel):
    name: str
    courtesy_name: str | None = None
    positions: list[Position] = []
    spouse: Self | None = None
    children: list[Self] = []
    associated_sites: list[str] = []

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True


Person.model_rebuild()  # Needed for recursive models in Pydantic v2
