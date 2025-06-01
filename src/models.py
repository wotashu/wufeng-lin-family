from typing import List, Optional, Union

from pydantic import BaseModel


class Name(BaseModel):
    hanzi: str
    kanji: Optional[str] = None
    pinyin: Optional[str] = None
    wade_giles: Optional[str] = None
    english: Optional[str] = None


class FamilyMember(BaseModel):
    name: Name
    generation: Optional[int] = None
    gender: Optional[str] = None
    historical_significance: Optional[str] = None
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    note: Optional[str] = None
    relation: Optional[str] = None
    children: List[Union["FamilyMember", str]] = []  # Allow string or FamilyMember

    class Config:
        orm_mode = True


FamilyMember.model_rebuild()
