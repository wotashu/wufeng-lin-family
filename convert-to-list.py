import json
from pathlib import Path


def convert_object_to_list(data):
    """
    Convert a JSON object (dict) into a list of objects.
    Each object gets a new field "id" which is set to its original key.
    """
    result = []
    for _, record in data.items():
        if isinstance(record, dict):
            result.append(record)
        else:
            result.append(record)
    return result


def main():
    input_path = Path("data/lists/overseas_house.json")
    output_path = Path("data/lists/overseas_house_list.json")

    with open(input_path, "r", encoding="utf-8") as infile:
        # Load the JSON object (dictionary)
        data = json.load(infile)

    # Convert the object to a list.
    list_data = convert_object_to_list(data)

    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(list_data, outfile, ensure_ascii=False, indent=4)

    print(f"Converted JSON list written to {output_path}")


if __name__ == "__main__":
    main()
