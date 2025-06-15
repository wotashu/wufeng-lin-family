from typing import List, Optional

from pydantic import BaseModel


class Name(BaseModel):
    hanzi: Optional[str] = None
    kanji: Optional[str] = None
    pinyin: Optional[str] = None
    wade_giles: Optional[str] = None
    english: Optional[str] = None
    katakana: Optional[str] = None


class Relationships(BaseModel):
    type: str
    target: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class FamilyMember(BaseModel):
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
    relationships: List[Relationships] = []
    image: Optional[str] = None  # URL or path to image
    links: Optional[List[str]] = None  # List of URLs or paths to additional resources

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


FamilyMember.model_rebuild()
