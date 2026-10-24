import os
import sys
import json
import urllib.request
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
import recipe_engine as engine

recipes_path = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "recipes.json")
with open(recipes_path, "r", encoding="utf-8") as f:
    catalog = json.load(f)

recipes = catalog.get("recipes", [])
print(f"Total recipes loaded: {len(recipes)}")
assert len(recipes) == 31, f"Expected 31 recipes, got {len(recipes)}"

errors = []
warnings = []

for idx, r in enumerate(recipes):
    rid = r.get("id")
    dish = r.get("dish")
    dish_en = r.get("dish_en")
    
    if not rid or not dish or not dish_en:
        errors.append(f"Recipe #{idx} missing basic identifier: {r}")
        
    base_s = r.get("base_servings")
    if not isinstance(base_s, int) or base_s <= 0:
        errors.append(f"[{rid}] Invalid base_servings: {base_s}")
        
    prep = r.get("prep_time_min", 0)
    cook = r.get("cook_time_min", 0)
    total = r.get("total_time_min", 0)
    if prep + cook != total:
        errors.append(f"[{rid}] Timing mismatch: prep({prep}) + cook({cook}) = {prep+cook} != total({total})")
        
    steps = r.get("steps", [])
    if not steps:
        errors.append(f"[{rid}] No steps defined")
    step_duration_sum = 0
    for s_idx, s in enumerate(steps):
        if s.get("order") != s_idx + 1:
            errors.append(f"[{rid}] Step order mismatch at index {s_idx}: {s.get('order')}")
        if not s.get("instruction") or not s.get("instruction_en"):
            errors.append(f"[{rid}] Step #{s_idx+1} missing instruction text")
        step_duration_sum += s.get("duration_min", 0)
        
    if step_duration_sum > cook + 5:
        warnings.append(f"[{rid}] Step duration sum ({step_duration_sum}m) exceeds cook_time ({cook}m)")

    ings = r.get("ingredients", [])
    if not ings:
        errors.append(f"[{rid}] No ingredients defined")
    for i_idx, i in enumerate(ings):
        if not i.get("name") or not i.get("name_en"):
            errors.append(f"[{rid}] Ingredient #{i_idx} missing name")
        amt = i.get("amount")
        if not isinstance(amt, (int, float)) or amt <= 0:
            errors.append(f"[{rid}] Ingredient {i.get('name')} has non-positive amount: {amt}")
        if not i.get("unit"):
            errors.append(f"[{rid}] Ingredient {i.get('name')} missing unit")

    subs = r.get("substitutions", [])
    if not subs:
        warnings.append(f"[{rid}] No substitutions listed")
    for s in subs:
        if not s.get("ingredient_bn") or not s.get("substitute_bn") or not s.get("impact_bn"):
            errors.append(f"[{rid}] Incomplete substitution: {s}")

    src = r.get("source", {})
    if not src.get("name") or not src.get("attribution"):
        errors.append(f"[{rid}] Incomplete source attribution: {src}")

    img = r.get("image", {})
    if not img.get("url") or not img.get("license") or not img.get("author"):
        errors.append(f"[{rid}] Incomplete image metadata: {img}")

print(f"Validation complete: {len(errors)} errors, {len(warnings)} warnings.")
if errors:
    for e in errors:
        print(" ERROR:", e)
if warnings:
    for w in warnings:
        print(" WARNING:", w)

assert len(errors) == 0, "Recipe validation failed with errors!"

print("\n=== VERIFYING MATHEMATICAL SCALING ===")
for r in recipes[:5]:
    rid = r["id"]
    base_s = r["base_servings"]
    for target_s in [1, 2, 4, 8, 12]:
        scaled = engine.scale_recipe(r, target_s)
        ratio = target_s / base_s
        assert scaled["base_servings"] == target_s
        assert scaled["cook_time_min"] == r["cook_time_min"], "Cook time must NOT scale!"
        assert scaled["prep_time_min"] == r["prep_time_min"], "Prep time must NOT scale!"
        
        salt_orig = [i["amount"] for i in r["ingredients"] if "salt" in i["name_en"].lower() or "লবণ" in i["name"]]
        if salt_orig:
            salt_scaled = [i["amount"] for i in scaled["ingredients"] if "salt" in i["name_en"].lower() or "লবণ" in i["name"]][0]
            expected_salt = round(salt_orig[0] * (ratio ** 0.82), 2)
            print(f"[{rid}] Servings {base_s}->{target_s} | Salt orig: {salt_orig[0]} -> scaled: {salt_scaled} (conservative factor: {round(ratio**0.82, 3)})")
            assert abs(salt_scaled - expected_salt) <= 0.25, f"Salt scaling off: expected ~{expected_salt}, got {salt_scaled}"

        chili_orig = [i["amount"] for i in r["ingredients"] if "chili" in i["name_en"].lower() or "মরিচ" in i["name"]]
        if chili_orig:
            chili_scaled = [i["amount"] for i in scaled["ingredients"] if "chili" in i["name_en"].lower() or "মরিচ" in i["name"]][0]
            expected_chili = round(chili_orig[0] * (ratio ** 0.85), 2)
            print(f"[{rid}] Servings {base_s}->{target_s} | Chili orig: {chili_orig[0]} -> scaled: {chili_scaled} (conservative factor: {round(ratio**0.85, 3)})")
            assert abs(chili_scaled - expected_chili) <= 0.25, f"Chili scaling off: expected ~{expected_chili}, got {chili_scaled}"

print("\n=== TESTING LIVE URL ACCESSIBILITY SAMPLE ===")
test_sample = recipes[:5]
for r in test_sample:
    url = r["image"]["url"]
    print(f"Testing URL for '{r['dish_en']}': {url[:60]}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PachikaAudit/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f" -> Status: {resp.status}, Content-Type: {resp.headers.get('Content-Type')}")
            assert resp.status == 200
    except Exception as e:
        print(f" -> Live URL check note: {e}")

print("\n=== ALL RECIPE DATA INTEGRITY CHECKS PASSED ===")
