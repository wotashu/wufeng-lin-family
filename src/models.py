from typing import List, Optional, Union

from pydantic import BaseModel


class Name(BaseModel):
    hanzi: Optional[str] = None
    kanji: Optional[str] = None
    pinyin: Optional[str] = None
    wade_giles: Optional[str] = None
    english: Optional[str] = None


class FamilyMember(BaseModel):
    name: Name
    house: Optional[str] = "Overseas House"
    generation: Optional[int] = None
    gender: Optional[str] = None
    historical_significance: Optional[str] = None
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    note: Optional[str] = None
    relation: Optional[str] = None
    parents: List[Union["FamilyMember", str]] = []  # Allow string or FamilyMember
    children: List[Union["FamilyMember", str]] = []  # Allow string or FamilyMember
    spouse: Optional[Union["FamilyMember", str]] = None  # Allow string or FamilyMember
    former_spouses: List[
        Union["FamilyMember", str]
    ] = []  # Allow string or FamilyMember
    concubines: List[Union["FamilyMember", str]] = []  # Allow string or FamilyMember,
    concubine_of: Optional[Union["FamilyMember", str]] = (
        None  # Allow string or FamilyMember
    )
    image: Optional[str] = None  # URL or path to image

    class Config:
        orm_mode = True


FamilyMember.model_rebuild()
