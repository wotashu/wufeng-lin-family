import json
from pathlib import Path

from unidecode import unidecode


def update_english_names(data):
    """
    For each record in the data list, if the nested "name" does not have an "english" value
    but has a "pinyin", set "english" to an ASCII-only version of the "pinyin".
    """
    for record in data:
        if "name" in record:
            name_dict = record["name"]
            if not name_dict.get("english") and name_dict.get("pinyin"):
                name_dict["english"] = unidecode(name_dict["pinyin"])
    return data


def main():
    input_path = Path("data/lists/historic_family.json")
    output_path = Path("data/lists/historic_family.json")

    # Load existing JSON data
    with open(input_path, "r", encoding="utf-8") as infile:
        data = json.load(infile)

    # Update the records
    updated_data = update_english_names(data)

    # Save the updated data to a new file
    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(updated_data, outfile, ensure_ascii=False, indent=4)

    print(f"Updated JSON saved to {output_path}")


if __name__ == "__main__":
    main()
