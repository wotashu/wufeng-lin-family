import json
from pathlib import Path

with Path("data/cleaned_data.json").open("r") as file:
    data = json.load(file)

upper_house = []
lower_house = []
early_house = []
diaspora = []
before_house = []
no_house = []
other_house = []
for item in data:
    house = item.get("house", None)
    if house is None:
        no_house.append(item)
    elif "upper" in house.lower():
        upper_house.append(item)
    elif "lower" in house.lower():
        lower_house.append(item)
    elif "wu-feng" in house.lower():
        early_house.append(item)
    elif "whole" in house.lower():
        before_house.append(item)
    elif "overseas" in house.lower():
        diaspora.append(item)
    else:
        other_house.append(item)

houses = {
    "upper_house": upper_house,
    "lower_house": lower_house,
    "early_house": early_house,
    "diaspora": diaspora,
    "before_house": before_house,
    "no_house": no_house,
    "other_house": other_house,
}

for house in [
    "upper_house",
    "lower_house",
    "early_house",
    "diaspora",
    "before_house",
    "no_house",
    "other_house",
]:
    with Path(f"data/{house}.json").open("w") as file:
        json.dump(houses[house], file, indent=2, ensure_ascii=False)
