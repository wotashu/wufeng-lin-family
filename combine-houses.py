import json
from pathlib import Path


def add_house_field(data, house_name):
    """
    For every top-level record in the data, add a new key "house" with value house_name.
    """
    for record in data.values():
        record["house"] = house_name
    return data


def main():
    # Path to the houses folder
    housefolder = Path("data/houses")
    # List of house file names without extension
    houses = ["early_house", "upper_house", "lower_house", "overseas_house"]

    combined_data = {}

    for house in houses:
        house_path = housefolder / f"{house}.json"
        if not house_path.exists():
            print(f"House file {house_path} does not exist.")
            continue

        with open(house_path, "r", encoding="utf-8") as infile:
            data = json.load(infile)

        # Add the 'house' field to each record
        data = add_house_field(data, house)

        # Combine into one dictionary; if there are duplicate keys across houses,
        # you might decide to namespace them or store them in a list.
        combined_data.update(data)

    # Save the combined data into a new JSON file.
    output_path = Path("data/combined_houses.json")
    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(combined_data, outfile, ensure_ascii=False, indent=4)

    print(f"Combined house data written to {output_path}")


if __name__ == "__main__":
    main()
