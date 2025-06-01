import json

from src.models import FamilyMember, Name

with open("data/family_data.json", "r", encoding="utf-8") as file:
    family_data = json.load(file)

FamilyMember.model_rebuild()
# Convert the family data to FamilyMember instances
family_members = []
for person_id, details in family_data.items():
    name_details = details.get("name", {})
    name = Name(
        hanzi=name_details.get("hanzi", ""),
        kanji=name_details.get("kanji"),
        pinyin=name_details.get("pinyin"),
        wade_giles=name_details.get("wade_giles"),
        english=name_details.get("english"),
    )
    member = FamilyMember(
        name=name,
        generation=details.get("generation", 0),  # Default to 0 if not specified
        gender=details.get("gender", None),
        historical_significance=details.get("historical_significance", None),
        birth_year=details.get("birth_year", None),
        death_year=details.get("death_year", None),
        note=details.get("note", None),
        relation=details.get("relation", None),
        children=details.get("children", []),
    )
    family_members.append(member)

# Example usage
for member in family_members:
    print(
        f"Name: {member.name.english or member.name.hanzi}, "
        f"Note: {member.note or 'No note available'}",
    )
