import json
import sys


def convert_record(record):
    relationships = []
    # Process spouse (single value or list)
    if "spouse" in record and record["spouse"]:
        # Allow for string or list
        if isinstance(record["spouse"], list):
            for sp in record["spouse"]:
                relationships.append(
                    {
                        "type": "spouse",
                        "target": sp,
                        "start_date": None,
                        "end_date": None,
                    }
                )
        else:
            relationships.append(
                {
                    "type": "spouse",
                    "target": record["spouse"],
                    "start_date": None,
                    "end_date": None,
                }
            )

    # Process former_spouses
    if "former_spouses" in record and record["former_spouses"]:
        if isinstance(record["former_spouses"], list):
            for fs in record["former_spouses"]:
                relationships.append(
                    {
                        "type": "former_spouse",
                        "target": fs,
                        "start_date": None,
                        "end_date": None,
                    }
                )
        else:
            relationships.append(
                {
                    "type": "former_spouse",
                    "target": record["former_spouses"],
                    "start_date": None,
                    "end_date": None,
                }
            )

    # Process parents
    if "parents" in record and record["parents"]:
        if isinstance(record["parents"], list):
            for parent in record["parents"]:
                relationships.append(
                    {
                        "type": "parent",
                        "target": parent,
                        "start_date": None,
                        "end_date": None,
                    }
                )
        else:
            relationships.append(
                {
                    "type": "parent",
                    "target": record["parents"],
                    "start_date": None,
                    "end_date": None,
                }
            )

    # Process children
    if "children" in record and record["children"]:
        if isinstance(record["children"], list):
            for child in record["children"]:
                relationships.append(
                    {
                        "type": "child",
                        "target": child,
                        "start_date": None,
                        "end_date": None,
                    }
                )
        else:
            relationships.append(
                {
                    "type": "child",
                    "target": record["children"],
                    "start_date": None,
                    "end_date": None,
                }
            )

    # Process concubines
    if "concubines" in record and record["concubines"]:
        if isinstance(record["concubines"], list):
            for con in record["concubines"]:
                relationships.append(
                    {
                        "type": "concubine",
                        "target": con,
                        "start_date": None,
                        "end_date": None,
                    }
                )
        else:
            relationships.append(
                {
                    "type": "concubine",
                    "target": record["concubines"],
                    "start_date": None,
                    "end_date": None,
                }
            )

    # Process concubine_of
    if "concubine_of" in record and record["concubine_of"]:
        if isinstance(record["concubine_of"], list):
            for co in record["concubine_of"]:
                relationships.append(
                    {
                        "type": "concubine_of",
                        "target": co,
                        "start_date": None,
                        "end_date": None,
                    }
                )
        else:
            relationships.append(
                {
                    "type": "concubine_of",
                    "target": record["concubine_of"],
                    "start_date": None,
                    "end_date": None,
                }
            )

    # Add or replace the relationships field
    record["relationships"] = relationships

    # Optionally remove the legacy fields
    for field in [
        "spouse",
        "former_spouses",
        "parents",
        "children",
        "concubines",
        "concubine_of",
    ]:
        record.pop(field, None)

    return record


def main(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as infile:
        records = json.load(infile)

    # Process each record in the JSON array
    new_records = [convert_record(record) for record in records]

    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(new_records, outfile, indent=2, ensure_ascii=False)
    print(f"Converted {len(new_records)} records saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_to_relationships.py input.json output.json")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
