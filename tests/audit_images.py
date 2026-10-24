import json

with open("backend/data/recipes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Auditing image metadata across {len(data['recipes'])} recipes:")
for r in data["recipes"]:
    img = r.get("image", {})
    url = img.get("url", "")
    author = img.get("author", "")
    lic = img.get("license", "")
    alt = img.get("alt", "")
    src = r.get("source", {})
    print(f"[{r['id']}] Dish: {r['dish_en']} | Author: {author} | License: {lic} | Alt: {alt[:30]}...")
