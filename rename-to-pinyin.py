import json

from unidecode import unidecode


def update_names(obj):
    """
    Recursively walk through the object.
    If a dictionary contains a "name" key and a nested "pinyin" field,
    then set its "english" field to the ASCII version of the pinyin using unidecode.
    """
    if isinstance(obj, dict):
        if "name" in obj and isinstance(obj["name"], dict):
            if "pinyin" in obj["name"]:
                # Set english to the ASCII conversion of the pinyin value.
                obj["name"]["english"] = unidecode(obj["name"]["pinyin"])
        for value in obj.values():
            update_names(value)
    elif isinstance(obj, list):
        for item in obj:
            update_names(item)


if __name__ == "__main__":
    filepaths = [
        "data/combined_houses.json",
    ]
    for filepath in filepaths:
        with open(filepath, "r", encoding="utf-8") as infile:
            data = json.load(infile)

        # First, update the nested "english" fields based on "pinyin"
        update_names(data)

        # Create a mapping from original key to new key (based on name.english)
        mapping = {}
        for original_key, record in data.items():
            # Use record "name.english" if exists; otherwise, fall back to the original key.
            new_key = record.get("name", {}).get("english", original_key)
            mapping[original_key] = new_key

        # Build a new dictionary with keys replaced by the new english ascii name.
        new_data = {}
        for original_key, record in data.items():
            new_key = mapping[original_key]
            new_data[new_key] = record

        # Update any children arrays to reference the new english keys.
        for record in new_data.values():
            if "children" in record:
                updated_children = []
                for child in record["children"]:
                    # Replace with new key if available; else, leave as is.
                    updated_children.append(mapping.get(child, child))
                record["children"] = updated_children

        new_filepath = filepath.replace(".json", "_updated.json")
        with open(new_filepath, "w", encoding="utf-8") as outfile:
            json.dump(new_data, outfile, ensure_ascii=False, indent=4)

        print(f"Updated file with keys replaced written to {new_filepath}")
