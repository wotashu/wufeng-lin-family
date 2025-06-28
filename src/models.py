from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator


class Name(BaseModel):
    hanzi: Optional[str] = None
    kanji: Optional[str] = None
    pinyin: Optional[str] = None
    wade_giles: Optional[str] = None
    english: Optional[str] = None
    katakana: Optional[str] = None


class Relationship(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    source_id: ObjectId
    type: str
    target: ObjectId
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    @field_validator("source_id", mode="before")
    def ensure_source_id_objectid(cls, v):
        if isinstance(v, str):
            return ObjectId(v)
        return v

    @field_validator("target", mode="before")
    def ensure_target_objectid(cls, v):
        if isinstance(v, str):
            return ObjectId(v)
        return v

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FamilyMember(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    name: Name
    house: Optional[str] = None
    branch: Optional[str] = None
    generation: Optional[int] = None
    gender: Optional[str] = None
    historical_significance: Optional[str] = None
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    note: Optional[str] = None
    relation: Optional[str] = None
    image: Optional[str] = None  # URL or path to image
    links: Optional[List[str]] = None  # List of URLs or paths to additional resources

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


FamilyMember.model_rebuild()
Relationship.model_rebuild()
