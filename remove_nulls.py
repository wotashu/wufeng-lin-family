import json
import sys


def remove_nulls(obj):
    # If it's a dict, rebuild it filtering out keys with None values.
    if isinstance(obj, dict):
        return {k: remove_nulls(v) for k, v in obj.items() if v is not None}
    # If it's a list, filter out any None items and process items.
    elif isinstance(obj, list):
        return [remove_nulls(x) for x in obj if x is not None]
    else:
        return obj


def main(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as infile:
        data = json.load(infile)
    cleaned_data = remove_nulls(data)
    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(cleaned_data, outfile, ensure_ascii=False, indent=2)
    print(f"Cleaned data written to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python remove_nulls.py input.json output.json")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
