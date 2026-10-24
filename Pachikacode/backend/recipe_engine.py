
import json
import os
import re
import sys
import difflib

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "recipes.json")

CATEGORY_META = {
    "bhuna": {"bn": "ভুনা", "en": "Bhuna", "icon": "🍲"},
    "curry": {"bn": "তরকারি ও কারি", "en": "Curry", "icon": "🍛"},
    "rice": {"bn": "ভাত ও বিরিয়ানি", "en": "Rice & Biryani", "icon": "🍚"},
    "bhorta": {"bn": "ভর্তা", "en": "Bhorta", "icon": "🥔"},
    "vegetable": {"bn": "সবজি", "en": "Vegetable", "icon": "🥬"},
    "dal": {"bn": "ডাল", "en": "Dal", "icon": "🥣"},
    "snack": {"bn": "নাস্তা", "en": "Snacks", "icon": "🥟"},
    "soup": {"bn": "স্যুপ", "en": "Soup", "icon": "🍲"},
    "dessert": {"bn": "মিষ্টি", "en": "Dessert", "icon": "🍮"},
    "drink": {"bn": "চা, কফি ও শরবত", "en": "Beverages", "icon": "☕"},
    "quick": {"bn": "ঝটপট রান্না", "en": "Quick Eats", "icon": "⚡"},
}

DISH_ALIASES = {
    "biriyani": "chicken_biryani",
    "biryani": "chicken_biryani",
    "murgi biriyani": "chicken_biryani",
    "chicken biriyani": "chicken_biryani",
    "polao": "pulao",
    "pulao": "pulao",
    "morog polao": "pulao",
    "khichdi": "khichuri",
    "khechuri": "khichuri",
    "khichuri": "khichuri",
    "ভুনা খিচুড়ি": "khichuri",
    "খিচুড়ী": "khichuri",
    "doodh cha": "cha",
    "dudh cha": "cha",
    "milk tea": "cha",
    "দুধ চা": "cha",
    "রং চা": "lebu_cha",
    "লেবু চা": "lebu_cha",
    "lemon tea": "lebu_cha",
    "black tea": "lebu_cha",
    "black coffee": "americano",
    "americano": "americano",
    "iced coffee": "iced_coffee",
    "cold coffee": "iced_coffee",
    "dalgona": "dalgona_coffee",
    "dalgona coffee": "dalgona_coffee",
    "alu bhorta": "aloo_bhorta",
    "alu vorta": "aloo_bhorta",
    "aloo bhorta": "aloo_bhorta",
    "potato mash": "aloo_bhorta",
    "begun bhorta": "begun_bhorta",
    "begun vorta": "begun_bhorta",
    "baingan bharta": "begun_bhorta",
    "eggplant mash": "begun_bhorta",
    "singara": "singara",
    "shingara": "singara",
    "samosa": "singara",
    "piyaju": "piyaju",
    "peyaju": "piyaju",
    "peaju": "piyaju",
    "pakora": "piyaju",
    "egg bhurji": "egg_bhurji",
    "dim bhurji": "egg_bhurji",
    "dimer bhurji": "egg_bhurji",
    "dimer dalna": "egg_bhurji",
    "dim dalna": "egg_bhurji",
    "ডিমের ডালনা": "egg_bhurji",
    "egg curry": "egg_bhurji",
    "scrambled eggs": "egg_bhurji",
    "chingri": "prawn_malai_curry",
    "prawn": "prawn_malai_curry",
    "chingri malai curry": "prawn_malai_curry",
    "prawn malai curry": "prawn_malai_curry",
    "shrimp curry": "prawn_malai_curry",
    "মাছের ঝোল": "fish_curry",
    "macher jhol": "fish_curry",
    "fish curry": "fish_curry",
    "মাছ ভুনা": "fish_bhuna",
    "fish bhuna": "fish_bhuna",
    "ilish bhuna": "fish_bhuna",
    "payesh": "payesh",
    "payas": "payesh",
    "kheer": "payesh",
    "rice pudding": "payesh",
    "mishti doi": "mishti_doi",
    "misti doi": "mishti_doi",
    "sweet curd": "mishti_doi",
    "sweet yogurt": "mishti_doi",
    "borhani": "borhani",
    "burhani": "borhani",
    "doi ghol": "doi_ghol",
    "ghol": "doi_ghol",
    "lassi": "doi_ghol",
    "buttermilk": "doi_ghol",
    "chocolate milk": "chocolate_milk",
    "choco milk": "chocolate_milk",
    "daal": "dal",
    "dal": "dal",
    "dhal": "dal",
    "lentil soup": "dal",
    "ডাল রান্না": "dal",
    "chicken soup": "chicken_soup",
    "veg soup": "veg_soup",
    "vegetable soup": "veg_soup",
    "chicken curry": "chicken_curry",
    "মুরগির কারি": "chicken_curry",
    "chicken bhuna": "chicken_bhuna",
    "মুরগির মাংস ভুনা": "chicken_bhuna",
    "beef curry": "beef_curry",
    "গরুর মাংস কারি": "beef_curry",
    "beef bhuna": "beef_bhuna",
    "গরুর মাংস ভুনা": "beef_bhuna",
    "mutton bhuna": "mutton_bhuna",
    "খাসির মাংস ভুনা": "mutton_bhuna",
    "mutton": "mutton_bhuna",
    "খাসি": "mutton_bhuna",
    "duck bhuna": "duck_bhuna",
    "হাঁসের মাংস ভুনা": "duck_bhuna",
    "duck": "duck_bhuna",
    "হাঁস": "duck_bhuna",
    "veg curry": "veg_curry",
    "sobji": "veg_curry",
    "সবজি": "veg_curry",
}

AMBIGUOUS_DISH_TERMS = {
    "chicken": {
        "bn": "মুরগি",
        "en": "Chicken",
        "recipe_ids": ["chicken_bhuna", "chicken_curry", "chicken_biryani", "chicken_soup"],
    },
    "মুরগি": {
        "bn": "মুরগি",
        "en": "Chicken",
        "recipe_ids": ["chicken_bhuna", "chicken_curry", "chicken_biryani", "chicken_soup"],
    },
    "মুরগির": {
        "bn": "মুরগি",
        "en": "Chicken",
        "recipe_ids": ["chicken_bhuna", "chicken_curry", "chicken_biryani", "chicken_soup"],
    },
    "beef": {
        "bn": "গরুর মাংস",
        "en": "Beef",
        "recipe_ids": ["beef_bhuna", "beef_curry"],
    },
    "গরু": {
        "bn": "গরুর মাংস",
        "en": "Beef",
        "recipe_ids": ["beef_bhuna", "beef_curry"],
    },
    "cow": {
        "bn": "গরুর মাংস",
        "en": "Beef",
        "recipe_ids": ["beef_bhuna", "beef_curry"],
    },
    "cow meat": {
        "bn": "গরুর মাংস",
        "en": "Beef",
        "recipe_ids": ["beef_bhuna", "beef_curry"],
    },
    "গোমাংস": {
        "bn": "গরুর মাংস",
        "en": "Beef",
        "recipe_ids": ["beef_bhuna", "beef_curry"],
    },
    "গরুর মাংস": {
        "bn": "গরুর মাংস",
        "en": "Beef",
        "recipe_ids": ["beef_bhuna", "beef_curry"],
    },
    "গরুর": {
        "bn": "গরুর মাংস",
        "en": "Beef",
        "recipe_ids": ["beef_bhuna", "beef_curry"],
    },
    "fish": {
        "bn": "মাছ",
        "en": "Fish",
        "recipe_ids": ["fish_bhuna", "fish_curry", "prawn_malai_curry"],
    },
    "মাছ": {
        "bn": "মাছ",
        "en": "Fish",
        "recipe_ids": ["fish_bhuna", "fish_curry", "prawn_malai_curry"],
    },
    "tea": {
        "bn": "চা",
        "en": "Tea",
        "recipe_ids": ["cha", "lebu_cha"],
    },
    "cha": {
        "bn": "চা",
        "en": "Tea",
        "recipe_ids": ["cha", "lebu_cha"],
    },
    "চা": {
        "bn": "চা",
        "en": "Tea",
        "recipe_ids": ["cha", "lebu_cha"],
    },
    "coffee": {
        "bn": "কফি",
        "en": "Coffee",
        "recipe_ids": ["americano", "iced_coffee", "dalgona_coffee"],
    },
    "কফি": {
        "bn": "কফি",
        "en": "Coffee",
        "recipe_ids": ["americano", "iced_coffee", "dalgona_coffee"],
    },
    "soup": {
        "bn": "স্যুপ",
        "en": "Soup",
        "recipe_ids": ["chicken_soup", "veg_soup"],
    },
    "স্যুপ": {
        "bn": "স্যুপ",
        "en": "Soup",
        "recipe_ids": ["chicken_soup", "veg_soup"],
    },
    "bhorta": {
        "bn": "ভর্তা",
        "en": "Bhorta",
        "recipe_ids": ["aloo_bhorta", "begun_bhorta"],
    },
    "ভর্তা": {
        "bn": "ভর্তা",
        "en": "Bhorta",
        "recipe_ids": ["aloo_bhorta", "begun_bhorta"],
    },
    "rice": {
        "bn": "ভাত ও পোলাও",
        "en": "Rice dishes",
        "recipe_ids": ["khichuri", "pulao", "chicken_biryani"],
    },
    "ভাত": {
        "bn": "ভাত ও পোলাও",
        "en": "Rice dishes",
        "recipe_ids": ["khichuri", "pulao", "chicken_biryani"],
    },
}

_FILLER_WORDS = {
    "রেসিপি", "recipe", "দাও", "দেন", "চাই", "চাও", "please",
    "দেখাও", "রান্না", "করে", "একটা", "একটু", "আমাকে", "কি", "কী",
    "the", "a", "an", "me", "give", "show", "বানাব", "বানাবো"
}


def load_recipes():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["recipes"]


def find_recipe_by_id(recipe_id):
    for recipe in load_recipes():
        if recipe["id"] == recipe_id:
            return recipe
    return None


def get_all_recipes():
    recipes = load_recipes()
    return [
        {
            "id": r["id"],
            "dish": r["dish"],
            "dish_en": r["dish_en"],
            "category": r.get("category", "curry"),
            "category_bn": CATEGORY_META.get(r.get("category", "curry"), {}).get("bn", "অন্যান্য"),
            "category_icon": CATEGORY_META.get(r.get("category", "curry"), {}).get("icon", "🍲"),
            "base_servings": r.get("base_servings", 4),
            "prep_time_min": r.get("prep_time_min", 15),
            "cook_time_min": r.get("cook_time_min", 25),
            "total_time_min": r.get("total_time_min", 40),
            "heat_level": r.get("heat_level", "medium"),
            "image": r.get("image", {}),
            "source": r.get("source", {}),
        }
        for r in recipes
    ]


def get_categories():
    recipes = load_recipes()
    counts = {}
    for r in recipes:
        cat = r.get("category", "curry")
        counts[cat] = counts.get(cat, 0) + 1

    result = []
    for cat_id, meta in CATEGORY_META.items():
        if cat_id in counts:
            result.append({
                "id": cat_id,
                "name_bn": meta["bn"],
                "name_en": meta["en"],
                "icon": meta["icon"],
                "count": counts[cat_id],
            })
    return result


def check_ambiguous_query(raw_query):
    cleaned = raw_query.strip().lower().strip("।.,!?")
    words = [w for w in cleaned.split() if w not in _FILLER_WORDS]
    cleaned = " ".join(words).strip()

    if cleaned in AMBIGUOUS_DISH_TERMS:
        info = AMBIGUOUS_DISH_TERMS[cleaned]
        options = [find_recipe_by_id(rid) for rid in info["recipe_ids"]]
        options = [o for o in options if o is not None]
        if len(options) > 1:
            return {
                "is_ambiguous": True,
                "term": cleaned,
                "term_bn": info["bn"],
                "term_en": info["en"],
                "options": options,
            }
    return None


def resolve_dish_query(raw_query):
    cleaned = raw_query.strip().lower()
    if not cleaned:
        return None

    if cleaned in DISH_ALIASES:
        r = find_recipe_by_id(DISH_ALIASES[cleaned])
        if r:
            return r

    ambig = check_ambiguous_query(raw_query)
    if ambig:
        return ambig

    recipe = find_recipe(raw_query)
    if recipe:
        return recipe

    recipes = load_recipes()
    all_names = {}
    for r in recipes:
        all_names[r["dish"].lower()] = r
        all_names[r["dish_en"].lower()] = r
        all_names[r["id"].replace("_", " ").lower()] = r

    matches = difflib.get_close_matches(cleaned, all_names.keys(), n=1, cutoff=0.55)
    if matches:
        return all_names[matches[0]]

    return None


def _contains_phrase(query, phrase):
    split = lambda t: [x for x in re.split(r"[\s,।.!?;:()]+", t) if x]
    q, p = split(query), split(phrase)
    n = len(p)
    return n > 0 and any(q[i:i + n] == p for i in range(len(q) - n + 1))


def find_recipe(dish_query):
    recipes = load_recipes()
    query = dish_query.strip().lower()
    if not query:
        return None

    best_match = None
    best_key = None

    for recipe in recipes:
        candidates = {
            recipe["dish"].lower(),
            recipe["dish_en"].lower(),
            recipe["id"].replace("_", " ").lower(),
        }
        m = re.match(r"^(.*?)\s*\((.*?)\)\s*$", recipe["dish_en"].lower())
        if m:
            candidates.add(m.group(1).strip())
            candidates.add(m.group(2).strip())

        for c in candidates:
            if not c:
                continue
            if c == query:
                key = (0, 0)
            elif (len(c) >= 3 and c in query) or (len(c) < 3 and _contains_phrase(query, c)):
                key = (1, -len(c))
            elif query in c:
                key = (2, len(c))
            else:
                continue

            if best_key is None or key < best_key:
                best_key = key
                best_match = recipe

    return best_match


def scale_recipe(recipe, target_servings):
    if not isinstance(target_servings, int) or target_servings <= 0:
        raise ValueError("Target servings must be a positive integer greater than 0.")

    base_servings = recipe.get("base_servings", 4)
    if not isinstance(base_servings, int) or base_servings <= 0:
        raise ValueError("Recipe base_servings must be a positive integer greater than 0.")

    factor = target_servings / base_servings
    scaled = json.loads(json.dumps(recipe))
    scaled["base_servings"] = target_servings

    for ingredient in scaled.get("ingredients", []):
        raw_amt = ingredient.get("amount", 0)
        if raw_amt is None:
            continue
        name_en = ingredient.get("name_en", "").lower()
        name_bn = ingredient.get("name", "")

        is_salt = "salt" in name_en or "লবণ" in name_bn
        is_chili = (
            any(c in name_en for c in ["chili", "chilli", "pepper"]) or
            any(c in name_bn for c in ["মরিচ", "কাঁচামরিচ"])
        )
        is_water = "water" in name_en or "পানি" in name_bn

        if is_salt:
            if factor > 1:
                scaled_amt = raw_amt * (factor ** 0.82)
            else:
                scaled_amt = raw_amt * factor
            if not ingredient.get("note"):
                ingredient["note"] = "স্বাদমতো (adjust to taste)"
        elif is_chili:
            if factor > 1:
                scaled_amt = raw_amt * (factor ** 0.85)
            else:
                scaled_amt = raw_amt * factor
            if not ingredient.get("note"):
                ingredient["note"] = "ঝাল রুচিমতো (adjust to taste)"
        elif is_water:
            cat = recipe.get("category", "")
            if cat in ["curry", "bhuna", "soup"] and factor > 1:
                scaled_amt = raw_amt * (factor ** 0.9)
            else:
                scaled_amt = raw_amt * factor
        else:
            scaled_amt = raw_amt * factor

        if abs(scaled_amt - round(scaled_amt)) < 0.03:
            ingredient["amount"] = int(round(scaled_amt))
        elif abs(scaled_amt * 2 - round(scaled_amt * 2)) < 0.04:
            ingredient["amount"] = round(scaled_amt * 2) / 2
        elif abs(scaled_amt * 4 - round(scaled_amt * 4)) < 0.05:
            ingredient["amount"] = round(scaled_amt * 4) / 4
        else:
            ingredient["amount"] = round(scaled_amt, 2)

    scaled["prep_time_min"] = recipe.get("prep_time_min", 15)
    scaled["cook_time_min"] = recipe.get("cook_time_min", 25)
    if scaled["prep_time_min"] is None or scaled["cook_time_min"] is None:
        scaled["total_time_min"] = recipe.get("total_time_min")
    else:
        scaled["total_time_min"] = scaled["prep_time_min"] + scaled["cook_time_min"]

    return scaled


def suggest_by_ingredients(available_ingredients):
    STAPLES = {
        "salt", "oil", "water", "sugar", "onion", "onion, chopped",
        "garlic", "ginger", "turmeric powder", "turmeric",
        "লবণ", "তেল", "পানি", "চিনি", "পেঁয়াজ", "রসুন", "আদা", "হলুদ",
    }

    raw_avail = [i.strip().lower() for i in available_ingredients if i.strip()]
    if not raw_avail:
        return []

    recipes = load_recipes()
    results = []

    def ingredient_tokens(text):
        return set(re.findall(r"[\w]+", text.lower()))

    def is_token_match(user_word, target_word):
        user_w = user_word.rstrip("s")
        target_w = target_word.rstrip("s")
        if user_w == target_w:
            return True
        if user_w == "egg" and "eggplant" in target_w:
            return False
        if user_w == "pea" and "peanut" in target_w:
            return False
        if user_word == target_word:
            return True
        return False

    def is_available(name_str):
        if not name_str:
            return False
        name_lower = name_str.lower().strip()
        name_words = ingredient_tokens(name_lower)

        for u in raw_avail:
            if u == name_lower:
                return True
            u_words = ingredient_tokens(u)
            for uw in u_words:
                for nw in name_words:
                    if is_token_match(uw, nw):
                        return True
        return False

    def is_staple(name_en, name_bn):
        en_staple = any(s in name_en.lower() for s in STAPLES)
        bn_staple = any(s in name_bn for s in STAPLES)
        return en_staple or bn_staple

    for recipe in recipes:
        matched = 0
        matched_items = []
        missing = []

        for ing in recipe.get("ingredients", []):
            name_en = ing.get("name_en", "")
            name_bn = ing.get("name", "")

            if is_staple(name_en, name_bn):
                continue

            if is_available(name_en) or is_available(name_bn):
                matched += 1
                matched_items.append(name_bn if name_bn else name_en)
            elif not ing.get("optional", False):
                missing.append(name_bn if name_bn else name_en)

        if matched > 0:
            results.append({
                "recipe": recipe,
                "matched": matched,
                "matched_items": matched_items,
                "missing": missing,
            })

    results.sort(key=lambda r: (r["matched"], -len(r["missing"])), reverse=True)
    return results


def get_recipe_substitutions(recipe, ingredient_name=None):
    substitutions = recipe.get("substitutions", [])
    if not substitutions:
        COMMON_SUBS = {
            "plain yogurt": {
                "substitute": "1 tbsp lemon juice or vinegar mixed into 3 tbsp milk",
                "substitute_bn": "১ টেবিল চামচ লেবুর রস ও ৩ টেবিল চামচ দুধের মিশ্রণ",
                "impact": "Maintains proper acidity and tenderizing function with slightly lighter gravy.",
                "impact_bn": "টক ভাব ও মাংস নরম করার কাজ বজায় রাখবে, ঝোল সামান্য হালকা হতে পারে।"
            },
            "ghee": {
                "substitute": "Mustard oil or regular vegetable oil with a dash of butter",
                "substitute_bn": "সরিষার তেল অথবা সামান্য বাটারসহ সয়াবিন তেল",
                "impact": "Will alter aroma; mustard oil gives a pungent kick, butter mimics ghee aroma.",
                "impact_bn": "সুগন্ধে পরিবর্তন আসবে; সরিষার তেলে ঝাঁঝ আসবে, বাটারে চমৎকার স্বাদ থাকবে।"
            },
            "mustard oil": {
                "substitute": "Regular cooking oil (soybean/sunflower)",
                "substitute_bn": "সয়াবিন বা সূর্যমুখী তেল",
                "impact": "Milder aroma without the signature Bengali mustard kick.",
                "impact_bn": "সরিষার খাঁটি ঝাঁঝ থাকবে না, তবে রান্না স্বাভাবিক ও সুস্বাদু হবে।"
            },
            "green chili": {
                "substitute": "Black pepper powder or crushed dried chili flakes",
                "substitute_bn": "গোলমরিচ গুঁড়া অথবা শুকনা মরিচের চিলি ফ্লেক্স",
                "impact": "Substitutes fresh herbal heat with warm pungent heat.",
                "impact_bn": "তাজা কাঁচামরিচের সুবাস থাকবে না, তবে প্রয়োজনীয় ঝাল পূরণ হবে।"
            }
        }
        for ing in recipe.get("ingredients", []):
            for k, sub_info in COMMON_SUBS.items():
                if k in ing.get("name_en", "").lower():
                    substitutions.append({
                        "ingredient": ing.get("name_en"),
                        "ingredient_bn": ing.get("name"),
                        **sub_info
                    })

    if ingredient_name:
        ing_clean = ingredient_name.lower().strip()
        for s in substitutions:
            if ing_clean in s.get("ingredient", "").lower() or ing_clean in s.get("ingredient_bn", ""):
                return s
        return None

    return substitutions


def validate_recipe(recipe):
    problems = []

    if not recipe.get("id"):
        problems.append("Recipe missing 'id'.")
    if not recipe.get("dish") or not recipe.get("dish_en"):
        problems.append("Recipe missing 'dish' or 'dish_en'.")
    if not recipe.get("ingredients"):
        problems.append("Recipe has no ingredients listed.")
    if not recipe.get("steps"):
        problems.append("Recipe has no steps listed.")

    base_servings = recipe.get("base_servings", 0)
    if not isinstance(base_servings, int) or base_servings <= 0:
        problems.append(f"Invalid base_servings: {base_servings}. Must be positive integer.")

    step_time_sum = sum(s.get("duration_min", 0) for s in recipe.get("steps", []))
    total_time = recipe.get("prep_time_min", 0) + recipe.get("cook_time_min", 0)
    if step_time_sum > total_time + 5:
        problems.append(
            f"Step durations ({step_time_sum} min) exceed stated total time ({total_time} min)."
        )

    for ing in recipe.get("ingredients", []):
        if ing.get("amount", 0) < 0:
            problems.append(f"Ingredient '{ing.get('name_en')}' has a negative amount.")

    return problems
