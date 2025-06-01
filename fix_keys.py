import json

# Load the JSON with new English top-level keys
with open("data/family_data_new.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# Build a mapping from the original key (or the hanzi name) to the English name key.
# In our file, the top-level key is already the English name.
# However the children fields still contain the original keys (e.g. "林石")
# So we need a mapping from the Chinese name to the English key.
name_mapping = {}
for eng_key, person in data.items():
    # Assume person["name"]["hanzi"] holds the original Chinese name.
    hanzi = person.get("name", {}).get("hanzi")
    english = person.get("name", {}).get("english", eng_key)
    if hanzi:
        name_mapping[hanzi] = english

# Now update each person's children list: replace each child name with its English version if available.
for person in data.values():
    if "children" in person:
        updated_children = []
        for child in person["children"]:
            # Look up the child in the mapping using the Chinese name.
            new_child = name_mapping.get(child, child)
            updated_children.append(new_child)
        person["children"] = updated_children

# Write the updated data back to a new file
with open("data/family_data_new_updated.json", "w", encoding="utf-8") as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=4)

print("Updated JSON saved to data/family_data_new_updated.json")
