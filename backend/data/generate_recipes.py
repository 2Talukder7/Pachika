import json

def ing(name, name_en, amount, unit, **kw):
    d = {"name": name, "name_en": name_en, "amount": amount, "unit": unit}
    d.update(kw)
    return d

def step(order, bn, en, duration, heat=None):
    return {"order": order, "instruction": bn, "instruction_en": en,
            "duration_min": duration, "heat": heat}

recipes = []


recipes.append({
    "id": "chicken_bhuna", "dish": "মুরগির মাংস ভুনা", "dish_en": "Chicken Bhuna",
    "category": "bhuna", "base_servings": 4,
    "ingredients": [
        ing("মুরগির মাংস", "chicken", 1, "kg"),
        ing("পেঁয়াজ কুচি", "onion, sliced", 1.5, "cup"),
        ing("রসুন বাটা", "garlic paste", 1, "tbsp"),
        ing("আদা বাটা", "ginger paste", 1, "tbsp"),
        ing("টমেটো কুচি", "tomato, chopped", 0.5, "cup"),
        ing("টক দই", "plain yogurt", 0.25, "cup", optional=True),
        ing("হলুদ গুঁড়া", "turmeric powder", 1, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 1, "tsp"),
        ing("জিরা গুঁড়া", "cumin powder", 1, "tsp"),
        ing("ধনে গুঁড়া", "coriander powder", 1, "tsp"),
        ing("গরম মসলা গুঁড়া", "garam masala powder", 0.5, "tsp"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 4, "tbsp"),
    ],
    "prep_time_min": 15, "cook_time_min": 35, "total_time_min": 50, "heat_level": "medium-high",
    "steps": [
        step(1, "মুরগির মাংস ধুয়ে পানি ঝরিয়ে নিন।", "Wash chicken and drain well.", 5),
        step(2, "তেলে পেঁয়াজ ভেজে বাদামি করুন।", "Fry onion in oil until golden.", 6, "medium"),
        step(3, "আদা-রসুন বাটা দিয়ে কষান।", "Add ginger-garlic paste and cook.", 2, "medium"),
        step(4, "টমেটো ও সব গুঁড়া মসলা দিয়ে কষিয়ে নিন।", "Add tomato and all powdered spices, cook well.", 5, "medium"),
        step(5, "মুরগি দিয়ে ভালোভাবে কষান যতক্ষণ না তেল ছাড়ে।", "Add chicken and cook until oil separates.", 12, "medium-high"),
        step(6, "সামান্য পানি দিয়ে ঢেকে মাংস সেদ্ধ করুন।", "Add a little water, cover, and cook until tender.", 10, "medium"),
    ],
})

recipes.append({
    "id": "beef_bhuna", "dish": "গরুর মাংস ভুনা", "dish_en": "Beef Bhuna",
    "category": "bhuna", "base_servings": 4,
    "ingredients": [
        ing("গরুর মাংস", "beef", 1, "kg"),
        ing("পেঁয়াজ কুচি", "onion, sliced", 1.5, "cup"),
        ing("রসুন বাটা", "garlic paste", 1.5, "tbsp"),
        ing("আদা বাটা", "ginger paste", 1.5, "tbsp"),
        ing("টক দই", "plain yogurt", 0.5, "cup"),
        ing("হলুদ গুঁড়া", "turmeric powder", 1, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 1.5, "tsp"),
        ing("জিরা গুঁড়া", "cumin powder", 1, "tsp"),
        ing("ধনে গুঁড়া", "coriander powder", 1, "tsp"),
        ing("এলাচ-দারুচিনি-তেজপাতা", "cardamom, cinnamon, bay leaf", 1, "set"),
        ing("গরম মসলা গুঁড়া", "garam masala powder", 0.5, "tsp"),
        ing("লবণ", "salt", 1.5, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 5, "tbsp"),
    ],
    "prep_time_min": 20, "cook_time_min": 60, "total_time_min": 80, "heat_level": "medium-high",
    "steps": [
        step(1, "মাংস ধুয়ে দই ও অর্ধেক মসলা দিয়ে ম্যারিনেট করুন।", "Wash beef and marinate with yogurt and half the spices.", 20),
        step(2, "তেলে এলাচ-দারুচিনি-তেজপাতা ফোড়ন দিন।", "Temper oil with whole spices.", 2, "medium"),
        step(3, "পেঁয়াজ ভেজে বাদামি করুন।", "Fry onion until golden.", 8, "medium"),
        step(4, "আদা-রসুন বাটা ও বাকি গুঁড়া মসলা দিয়ে কষান।", "Add ginger-garlic paste and remaining spices, cook.", 5, "medium"),
        step(5, "ম্যারিনেট করা মাংস দিয়ে ভালোভাবে কষান।", "Add marinated beef and cook until well browned.", 15, "medium-high"),
        step(6, "পানি দিয়ে ঢেকে মাংস নরম না হওয়া পর্যন্ত রান্না করুন।", "Add water, cover, and simmer until tender.", 35, "low"),
    ],
})

recipes.append({
    "id": "mutton_bhuna", "dish": "খাসির মাংস ভুনা", "dish_en": "Mutton Bhuna",
    "category": "bhuna", "base_servings": 4,
    "ingredients": [
        ing("খাসির মাংস", "mutton", 1, "kg"),
        ing("পেঁয়াজ কুচি", "onion, sliced", 1.5, "cup"),
        ing("রসুন বাটা", "garlic paste", 1.5, "tbsp"),
        ing("আদা বাটা", "ginger paste", 1.5, "tbsp"),
        ing("টক দই", "plain yogurt", 0.5, "cup"),
        ing("হলুদ গুঁড়া", "turmeric powder", 1, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 1.5, "tsp"),
        ing("জিরা গুঁড়া", "cumin powder", 1, "tsp"),
        ing("ধনে গুঁড়া", "coriander powder", 1, "tsp"),
        ing("গরম মসলা গুঁড়া", "garam masala powder", 1, "tsp"),
        ing("লবণ", "salt", 1.5, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 5, "tbsp"),
    ],
    "prep_time_min": 20, "cook_time_min": 70, "total_time_min": 90, "heat_level": "medium-high",
    "steps": [
        step(1, "মাংস ধুয়ে দই দিয়ে ম্যারিনেট করে রাখুন।", "Wash mutton and marinate with yogurt.", 20),
        step(2, "তেলে পেঁয়াজ বাদামি করে ভাজুন।", "Fry onion in oil until golden.", 8, "medium"),
        step(3, "আদা-রসুন বাটা ও গুঁড়া মসলা দিয়ে কষান।", "Add ginger-garlic paste and powdered spices, cook.", 5, "medium"),
        step(4, "মাংস দিয়ে তেল ছাড়া পর্যন্ত কষান।", "Add mutton and cook until oil separates.", 15, "medium-high"),
        step(5, "পানি দিয়ে ঢেকে মাংস নরম না হওয়া পর্যন্ত সেদ্ধ করুন।", "Add water, cover, and cook until tender.", 40, "low"),
        step(6, "গরম মসলা ছিটিয়ে নামিয়ে নিন।", "Sprinkle garam masala and remove from heat.", 2, None),
    ],
})

recipes.append({
    "id": "duck_bhuna", "dish": "হাঁসের মাংস ভুনা", "dish_en": "Duck Bhuna",
    "category": "bhuna", "base_servings": 4,
    "ingredients": [
        ing("হাঁসের মাংস", "duck meat", 1, "kg"),
        ing("পেঁয়াজ কুচি", "onion, sliced", 1.5, "cup"),
        ing("রসুন বাটা", "garlic paste", 1.5, "tbsp"),
        ing("আদা বাটা", "ginger paste", 1.5, "tbsp"),
        ing("নারকেল বাটা", "coconut paste", 0.25, "cup", optional=True),
        ing("হলুদ গুঁড়া", "turmeric powder", 1, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 1.5, "tsp"),
        ing("জিরা গুঁড়া", "cumin powder", 1, "tsp"),
        ing("ধনে গুঁড়া", "coriander powder", 1, "tsp"),
        ing("লবণ", "salt", 1.5, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 5, "tbsp"),
    ],
    "prep_time_min": 20, "cook_time_min": 75, "total_time_min": 95, "heat_level": "medium-high",
    "steps": [
        step(1, "হাঁসের মাংস ভালোভাবে ধুয়ে পরিষ্কার করুন।", "Wash and clean the duck meat thoroughly.", 15),
        step(2, "তেলে পেঁয়াজ বাদামি করে ভাজুন।", "Fry onion in oil until golden.", 8, "medium"),
        step(3, "আদা-রসুন বাটা ও গুঁড়া মসলা দিয়ে কষান।", "Add ginger-garlic paste and spices, cook.", 5, "medium"),
        step(4, "মাংস দিয়ে ভালোভাবে কষান।", "Add duck meat and cook well.", 15, "medium-high"),
        step(5, "পানি দিয়ে ঢেকে মাংস নরম না হওয়া পর্যন্ত রান্না করুন।", "Add water, cover, cook until tender (duck takes longer).", 45, "low"),
        step(6, "নারকেল বাটা দিয়ে কিছুক্ষণ কষিয়ে নামান।", "Stir in coconut paste briefly and remove from heat.", 3, "medium"),
    ],
})

recipes.append({
    "id": "fish_bhuna", "dish": "মাছ ভুনা", "dish_en": "Fish Bhuna",
    "category": "bhuna", "base_servings": 4,
    "ingredients": [
        ing("মাছ (রুই/কাতলা)", "fish (rui/katla)", 6, "piece"),
        ing("পেঁয়াজ কুচি", "onion, sliced", 1, "cup"),
        ing("রসুন বাটা", "garlic paste", 1, "tbsp"),
        ing("আদা বাটা", "ginger paste", 1, "tbsp"),
        ing("টমেটো কুচি", "tomato, chopped", 0.5, "cup"),
        ing("হলুদ গুঁড়া", "turmeric powder", 1, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 1, "tsp"),
        ing("জিরা গুঁড়া", "cumin powder", 0.5, "tsp"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 5, "tbsp"),
    ],
    "prep_time_min": 15, "cook_time_min": 25, "total_time_min": 40, "heat_level": "medium",
    "steps": [
        step(1, "মাছ ধুয়ে হলুদ-লবণ মাখিয়ে ভেজে তুলে রাখুন।", "Wash fish, rub with turmeric-salt, fry and set aside.", 8, "medium-high"),
        step(2, "একই তেলে পেঁয়াজ বাদামি করে ভাজুন।", "In the same oil, fry onion until golden.", 6, "medium"),
        step(3, "আদা-রসুন বাটা, টমেটো ও গুঁড়া মসলা দিয়ে কষান।", "Add ginger-garlic paste, tomato, and spices, cook.", 6, "medium"),
        step(4, "সামান্য পানি দিয়ে মসলা কষিয়ে নিন।", "Add a little water and cook the masala down.", 5, "medium"),
        step(5, "ভাজা মাছ দিয়ে অল্প আঁচে ৫ মিনিট রাখুন।", "Add fried fish and simmer gently for 5 minutes.", 5, "low"),
    ],
})


recipes.append({
    "id": "chicken_curry", "dish": "মুরগির মাংসের ঝোল", "dish_en": "Chicken Curry",
    "category": "curry", "base_servings": 4,
    "ingredients": [
        ing("মুরগির মাংস", "chicken", 1, "kg"),
        ing("আলু", "potato", 2, "piece"),
        ing("পেঁয়াজ কুচি", "onion, sliced", 1, "cup"),
        ing("রসুন বাটা", "garlic paste", 1, "tbsp"),
        ing("আদা বাটা", "ginger paste", 1, "tbsp"),
        ing("হলুদ গুঁড়া", "turmeric powder", 1, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 1, "tsp"),
        ing("জিরা-ধনে গুঁড়া", "cumin-coriander powder", 1, "tsp"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 4, "tbsp"),
        ing("পানি", "water", 3, "cup"),
    ],
    "prep_time_min": 15, "cook_time_min": 30, "total_time_min": 45, "heat_level": "medium",
    "steps": [
        step(1, "আলু ও মাংস ধুয়ে রাখুন।", "Wash potato and chicken.", 5),
        step(2, "তেলে পেঁয়াজ ভেজে নিন।", "Fry onion in oil.", 5, "medium"),
        step(3, "আদা-রসুন ও গুঁড়া মসলা দিয়ে কষান।", "Add ginger-garlic and spices, cook.", 4, "medium"),
        step(4, "মাংস ও আলু দিয়ে ভালোভাবে কষান।", "Add chicken and potato, cook well.", 8, "medium"),
        step(5, "পানি দিয়ে ঝোল ফুটিয়ে নিন।", "Add water and bring the curry to a boil.", 15, "medium"),
        step(6, "মাংস সেদ্ধ হলে নামিয়ে পরিবেশন করুন।", "Once chicken is cooked through, serve.", 3, None),
    ],
})

recipes.append({
    "id": "beef_curry", "dish": "গরুর মাংসের ঝোল", "dish_en": "Beef Curry",
    "category": "curry", "base_servings": 4,
    "ingredients": [
        ing("গরুর মাংস", "beef", 1, "kg"),
        ing("আলু", "potato", 2, "piece"),
        ing("পেঁয়াজ কুচি", "onion, sliced", 1, "cup"),
        ing("রসুন বাটা", "garlic paste", 1.5, "tbsp"),
        ing("আদা বাটা", "ginger paste", 1.5, "tbsp"),
        ing("হলুদ গুঁড়া", "turmeric powder", 1, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 1.5, "tsp"),
        ing("জিরা-ধনে গুঁড়া", "cumin-coriander powder", 1, "tsp"),
        ing("লবণ", "salt", 1.5, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 5, "tbsp"),
        ing("পানি", "water", 4, "cup"),
    ],
    "prep_time_min": 15, "cook_time_min": 60, "total_time_min": 75, "heat_level": "medium",
    "steps": [
        step(1, "মাংস ধুয়ে পানি ঝরিয়ে নিন।", "Wash beef and drain.", 5),
        step(2, "তেলে পেঁয়াজ ভেজে নিন।", "Fry onion in oil.", 6, "medium"),
        step(3, "আদা-রসুন ও গুঁড়া মসলা দিয়ে কষান।", "Add ginger-garlic and spices, cook.", 5, "medium"),
        step(4, "মাংস দিয়ে তেল ছাড়া পর্যন্ত কষান।", "Add beef and cook until oil separates.", 12, "medium-high"),
        step(5, "পানি ও আলু দিয়ে ঢেকে মাংস নরম না হওয়া পর্যন্ত রান্না করুন।", "Add water and potato, cover, cook until tender.", 40, "low"),
    ],
})

recipes.append({
    "id": "fish_curry", "dish": "মাছের ঝোল", "dish_en": "Fish Curry",
    "category": "curry", "base_servings": 4,
    "ingredients": [
        ing("মাছ", "fish", 6, "piece"),
        ing("আলু", "potato", 1, "piece"),
        ing("পেঁয়াজ কুচি", "onion, sliced", 0.75, "cup"),
        ing("রসুন বাটা", "garlic paste", 1, "tbsp"),
        ing("আদা বাটা", "ginger paste", 1, "tbsp"),
        ing("হলুদ গুঁড়া", "turmeric powder", 1, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 1, "tsp"),
        ing("কাঁচা মরিচ", "green chili", 3, "piece"),
        ing("ধনে পাতা", "coriander leaves", 0.25, "cup", optional=True),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 4, "tbsp"),
        ing("পানি", "water", 2.5, "cup"),
    ],
    "prep_time_min": 15, "cook_time_min": 25, "total_time_min": 40, "heat_level": "medium",
    "steps": [
        step(1, "মাছ হলুদ-লবণ মাখিয়ে হালকা ভেজে তুলুন।", "Rub fish with turmeric-salt and lightly fry.", 6, "medium-high"),
        step(2, "একই তেলে পেঁয়াজ ভাজুন।", "Fry onion in the same oil.", 5, "medium"),
        step(3, "আদা-রসুন ও গুঁড়া মসলা দিয়ে কষান।", "Add ginger-garlic and spices, cook.", 4, "medium"),
        step(4, "আলু ও পানি দিয়ে ফুটিয়ে নিন।", "Add potato and water, bring to a boil.", 10, "medium"),
        step(5, "মাছ ও কাঁচা মরিচ দিয়ে ৫ মিনিট রান্না করুন।", "Add fish and green chili, cook for 5 minutes.", 5, "medium"),
    ],
})

recipes.append({
    "id": "prawn_malai_curry", "dish": "চিংড়ি মালাইকারি", "dish_en": "Prawn Malai Curry",
    "category": "curry", "base_servings": 4,
    "ingredients": [
        ing("চিংড়ি মাছ", "prawns", 500, "g"),
        ing("নারকেলের দুধ", "coconut milk", 1.5, "cup"),
        ing("পেঁয়াজ বাটা", "onion paste", 0.5, "cup"),
        ing("আদা-রসুন বাটা", "ginger-garlic paste", 1.5, "tbsp"),
        ing("হলুদ গুঁড়া", "turmeric powder", 1, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 0.5, "tsp"),
        ing("কাঁচা মরিচ", "green chili", 4, "piece"),
        ing("তেজপাতা ও এলাচ", "bay leaf and cardamom", 1, "set"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 3, "tbsp"),
    ],
    "prep_time_min": 15, "cook_time_min": 20, "total_time_min": 35, "heat_level": "medium",
    "steps": [
        step(1, "চিংড়ি পরিষ্কার করে হলুদ-লবণ মাখিয়ে রাখুন।", "Clean prawns and rub with turmeric-salt.", 10),
        step(2, "তেলে তেজপাতা-এলাচ ফোড়ন দিয়ে পেঁয়াজ বাটা কষান।", "Temper oil with bay leaf-cardamom, cook onion paste.", 6, "medium"),
        step(3, "আদা-রসুন বাটা ও গুঁড়া মসলা দিয়ে কষান।", "Add ginger-garlic paste and spices, cook.", 5, "medium"),
        step(4, "নারকেলের দুধ দিয়ে ফুটিয়ে নিন।", "Add coconut milk and bring to a simmer.", 5, "medium"),
        step(5, "চিংড়ি ও কাঁচা মরিচ দিয়ে ৫-৬ মিনিট রান্না করুন।", "Add prawns and green chili, cook 5-6 minutes.", 6, "low"),
    ],
})

recipes.append({
    "id": "veg_curry", "dish": "মিক্সড সবজি", "dish_en": "Mixed Vegetable Curry",
    "category": "vegetable", "base_servings": 4,
    "ingredients": [
        ing("আলু", "potato", 1, "piece"),
        ing("গাজর", "carrot", 0.5, "cup"),
        ing("বরবটি", "long beans", 0.5, "cup"),
        ing("ফুলকপি", "cauliflower", 1, "cup"),
        ing("পেঁয়াজ কুচি", "onion, chopped", 0.5, "cup"),
        ing("রসুন কুচি", "garlic, chopped", 1, "tsp"),
        ing("হলুদ গুঁড়া", "turmeric powder", 0.5, "tsp"),
        ing("জিরা", "cumin seeds", 0.5, "tsp"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 3, "tbsp"),
    ],
    "prep_time_min": 15, "cook_time_min": 20, "total_time_min": 35, "heat_level": "low-medium",
    "steps": [
        step(1, "সব সবজি ধুয়ে কেটে নিন।", "Wash and chop all vegetables.", 10),
        step(2, "তেলে জিরা ফোড়ন দিয়ে পেঁয়াজ-রসুন ভাজুন।", "Temper oil with cumin, fry onion-garlic.", 5, "medium"),
        step(3, "হলুদ ও লবণ দিয়ে সবজি দিয়ে নাড়ুন।", "Add turmeric, salt, and vegetables, stir.", 3, "medium"),
        step(4, "ঢেকে অল্প আঁচে সবজি নরম না হওয়া পর্যন্ত রান্না করুন।", "Cover and cook on low heat until vegetables are tender.", 15, "low"),
    ],
})

recipes.append({
    "id": "dal", "dish": "মসুর ডাল", "dish_en": "Red Lentil Dal", "category": "dal", "base_servings": 4,
    "ingredients": [
        ing("মসুর ডাল", "red lentils (masoor dal)", 1, "cup"),
        ing("পানি", "water", 3, "cup"),
        ing("পেঁয়াজ কুচি", "onion, chopped", 0.25, "cup"),
        ing("রসুন কুচি", "garlic, chopped", 1, "tsp"),
        ing("হলুদ গুঁড়া", "turmeric powder", 0.5, "tsp"),
        ing("কাঁচা মরিচ", "green chili", 2, "piece"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 2, "tbsp"),
    ],
    "prep_time_min": 5, "cook_time_min": 20, "total_time_min": 25, "heat_level": "medium",
    "steps": [
        step(1, "ডাল ধুয়ে পানি ও হলুদ দিয়ে সেদ্ধ করুন।", "Wash lentils, add water and turmeric, boil.", 15, "medium"),
        step(2, "ডাল নরম হলে লবণ ও কাঁচা মরিচ দিন।", "Once soft, add salt and green chili.", 3, "medium"),
        step(3, "আলাদা প্যানে তেলে পেঁয়াজ-রসুন ভেজে ডালে ছেড়ে দিন (বাগার)।", "In a separate pan, fry onion-garlic in oil and pour over the dal (tempering).", 4, "medium"),
    ],
})


recipes.append({
    "id": "pulao", "dish": "পোলাও", "dish_en": "Pulao", "category": "rice", "base_servings": 4,
    "ingredients": [
        ing("পোলাওর চাল", "polao rice", 2, "cup"),
        ing("পেঁয়াজ কুচি", "onion, sliced", 0.5, "cup"),
        ing("আদা-রসুন বাটা", "ginger-garlic paste", 1, "tbsp"),
        ing("এলাচ-দারুচিনি-তেজপাতা", "cardamom, cinnamon, bay leaf", 1, "set"),
        ing("ঘি", "ghee", 2, "tbsp"),
        ing("তেল", "oil", 2, "tbsp"),
        ing("চিনি", "sugar", 1, "tsp"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("গরম পানি", "hot water", 3.5, "cup"),
    ],
    "prep_time_min": 15, "cook_time_min": 25, "total_time_min": 40, "heat_level": "low-medium",
    "steps": [
        step(1, "চাল ধুয়ে ২০ মিনিট ভিজিয়ে রেখে পানি ঝরিয়ে নিন।", "Wash rice, soak 20 minutes, then drain.", 20),
        step(2, "ঘি-তেলে গরম মসলা ফোড়ন দিন।", "Temper ghee-oil with whole spices.", 2, "medium"),
        step(3, "পেঁয়াজ হালকা ভেজে আদা-রসুন বাটা দিন।", "Lightly fry onion, add ginger-garlic paste.", 4, "medium"),
        step(4, "চাল দিয়ে ২-৩ মিনিট ভেজে নিন।", "Add rice and stir-fry for 2-3 minutes.", 3, "medium"),
        step(5, "গরম পানি, চিনি ও লবণ দিয়ে ঢেকে দিন।", "Add hot water, sugar, and salt; cover.", 3, "medium"),
        step(6, "অল্প আঁচে চাল সেদ্ধ না হওয়া পর্যন্ত রাখুন।", "Cook on low heat until rice is done.", 15, "low"),
    ],
})

recipes.append({
    "id": "chicken_biryani", "dish": "মুরগির বিরিয়ানি", "dish_en": "Chicken Biryani",
    "category": "rice", "base_servings": 4,
    "ingredients": [
        ing("বাসমতি চাল", "basmati rice", 2, "cup"),
        ing("মুরগির মাংস", "chicken", 1, "kg"),
        ing("টক দই", "plain yogurt", 0.5, "cup"),
        ing("পেঁয়াজ বেরেস্তা", "fried onion (beresta)", 1, "cup"),
        ing("আদা-রসুন বাটা", "ginger-garlic paste", 2, "tbsp"),
        ing("বিরিয়ানি মসলা", "biryani masala", 2, "tbsp"),
        ing("দুধে ভেজানো জাফরান/দুধ", "milk (with saffron if available)", 0.25, "cup", optional=True),
        ing("ঘি", "ghee", 3, "tbsp"),
        ing("লবণ", "salt", 1.5, "tsp", note="adjust to taste"),
        ing("গরম পানি", "hot water", 3.5, "cup"),
    ],
    "prep_time_min": 30, "cook_time_min": 45, "total_time_min": 75, "heat_level": "medium",
    "steps": [
        step(1, "মুরগি দই, আদা-রসুন বাটা ও বিরিয়ানি মসলা দিয়ে ম্যারিনেট করুন।", "Marinate chicken with yogurt, ginger-garlic paste, and biryani masala.", 30),
        step(2, "চাল ধুয়ে ২০ মিনিট ভিজিয়ে রাখুন।", "Wash rice and soak for 20 minutes.", 20),
        step(3, "ঘিতে ম্যারিনেট করা মাংস কষিয়ে নিন।", "Cook the marinated chicken in ghee.", 15, "medium-high"),
        step(4, "চাল আলাদাভাবে ৭০% সেদ্ধ করে পানি ঝরিয়ে নিন।", "Parboil rice separately to about 70% and drain.", 10, "medium"),
        step(5, "মাংসের উপর চাল বিছিয়ে বেরেস্তা ও দুধ ছড়িয়ে দিন।", "Layer rice over the chicken, top with fried onion and milk.", 3, None),
        step(6, "ঢেকে দমে (অল্প আঁচে) ২০ মিনিট রাখুন।", "Cover and cook on very low heat (dum) for 20 minutes.", 20, "low"),
    ],
})

recipes.append({
    "id": "khichuri", "dish": "খিচুড়ি", "dish_en": "Khichuri", "category": "rice", "base_servings": 4,
    "ingredients": [
        ing("চাল", "rice", 1, "cup"),
        ing("মুগ ডাল", "moong dal", 0.5, "cup"),
        ing("আলু", "potato (medium)", 1, "piece"),
        ing("গাজর", "carrot", 0.5, "cup"),
        ing("পেঁয়াজ কুচি", "onion, chopped", 0.5, "cup"),
        ing("রসুন বাটা", "garlic paste", 1, "tsp"),
        ing("আদা বাটা", "ginger paste", 1, "tsp", alternatives=["skip if unavailable, flavor will be milder"]),
        ing("হলুদ গুঁড়া", "turmeric powder", 0.5, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 0.5, "tsp"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 3, "tbsp"),
        ing("পানি", "water", 5, "cup"),
        ing("ঘি", "ghee", 1, "tbsp", optional=True),
    ],
    "prep_time_min": 10, "cook_time_min": 30, "total_time_min": 40, "heat_level": "medium",
    "steps": [
        step(1, "চাল এবং ডাল ভালো করে ধুয়ে নিন।", "Wash the rice and dal thoroughly.", 5),
        step(2, "একটি পাত্রে তেল গরম করে পেঁয়াজ কুচি ভেজে নিন।", "Heat oil in a pot and fry the chopped onion.", 3, "medium"),
        step(3, "আদা রসুন বাটা দিয়ে নেড়ে নিন।", "Add ginger-garlic paste and stir.", 1, "medium"),
        step(4, "আলু ও গাজর দিয়ে কিছুক্ষণ ভেজে নিন।", "Add potato and carrot, fry for a few minutes.", 4, "medium"),
        step(5, "হলুদ, মরিচ ও লবণ দিয়ে নেড়ে নিন।", "Add turmeric, chili powder, and salt; stir well.", 1, "medium"),
        step(6, "চাল ও ডাল দিয়ে নেড়ে ২ মিনিট ভাজুন।", "Add rice and dal, stir-fry for 2 minutes.", 2, "medium"),
        step(7, "পানি দিয়ে ঢেকে দিন এবং মাঝারি আঁচে রান্না করুন।", "Add water, cover, and cook on medium heat.", 20, "medium"),
        step(8, "সবজি ও ডাল নরম হলে ঘি দিয়ে নামিয়ে পরিবেশন করুন।", "Once vegetables and dal are soft, finish with ghee and serve.", 2, None),
    ],
})


recipes.append({
    "id": "aloo_bhorta", "dish": "আলু ভর্তা", "dish_en": "Potato Bhorta", "category": "bhorta", "base_servings": 4,
    "ingredients": [
        ing("আলু", "potato", 4, "piece"),
        ing("পেঁয়াজ কুচি", "onion, chopped", 0.25, "cup"),
        ing("কাঁচা মরিচ", "green chili", 2, "piece"),
        ing("সরিষার তেল", "mustard oil", 2, "tbsp"),
        ing("লবণ", "salt", 0.5, "tsp", note="adjust to taste"),
        ing("ধনে পাতা", "coriander leaves", 2, "tbsp", optional=True),
    ],
    "prep_time_min": 5, "cook_time_min": 20, "total_time_min": 25, "heat_level": "medium",
    "steps": [
        step(1, "আলু সেদ্ধ করে খোসা ছাড়িয়ে নিন।", "Boil potatoes and peel.", 18, "medium"),
        step(2, "আলু ভালো করে চটকে নিন।", "Mash the potatoes well.", 2),
        step(3, "পেঁয়াজ, কাঁচা মরিচ, তেল ও লবণ দিয়ে মেখে নিন।", "Mix in onion, green chili, oil, and salt.", 3),
    ],
})

recipes.append({
    "id": "begun_bhorta", "dish": "বেগুন ভর্তা", "dish_en": "Eggplant Bhorta", "category": "bhorta", "base_servings": 4,
    "ingredients": [
        ing("বেগুন", "eggplant", 1, "piece"),
        ing("পেঁয়াজ কুচি", "onion, chopped", 0.25, "cup"),
        ing("কাঁচা মরিচ", "green chili", 3, "piece"),
        ing("সরিষার তেল", "mustard oil", 2, "tbsp"),
        ing("লবণ", "salt", 0.5, "tsp", note="adjust to taste"),
    ],
    "prep_time_min": 5, "cook_time_min": 15, "total_time_min": 20, "heat_level": "medium",
    "steps": [
        step(1, "বেগুন সরাসরি আঁচে বা চুলায় পুড়িয়ে নিন।", "Roast the eggplant directly over a flame until soft.", 12, "medium"),
        step(2, "পোড়া খোসা ফেলে দিয়ে বেগুন চটকে নিন।", "Remove the charred skin and mash the eggplant.", 3),
        step(3, "পেঁয়াজ, কাঁচা মরিচ, তেল ও লবণ দিয়ে মেখে নিন।", "Mix in onion, green chili, oil, and salt.", 3),
    ],
})


recipes.append({
    "id": "chicken_soup", "dish": "মুরগির স্যুপ", "dish_en": "Chicken Soup", "category": "soup", "base_servings": 4,
    "ingredients": [
        ing("মুরগির মাংস", "chicken (boneless)", 300, "g"),
        ing("গাজর কুচি", "carrot, diced", 0.5, "cup"),
        ing("ভুট্টা দানা", "corn kernels", 0.5, "cup"),
        ing("রসুন কুচি", "garlic, chopped", 1, "tsp"),
        ing("কর্নফ্লাওয়ার", "cornflour", 2, "tbsp"),
        ing("গোলমরিচ গুঁড়া", "black pepper powder", 0.5, "tsp"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("পানি/স্টক", "water/stock", 5, "cup"),
    ],
    "prep_time_min": 10, "cook_time_min": 20, "total_time_min": 30, "heat_level": "medium",
    "steps": [
        step(1, "মুরগি ছোট টুকরো করে পানি দিয়ে সেদ্ধ করুন।", "Cut chicken into small pieces and boil in water.", 12, "medium"),
        step(2, "গাজর, ভুট্টা ও রসুন দিয়ে আরও কিছুক্ষণ ফুটান।", "Add carrot, corn, and garlic, simmer further.", 5, "medium"),
        step(3, "কর্নফ্লাওয়ার পানিতে গুলে স্যুপে দিয়ে ঘন করুন।", "Mix cornflour with water and stir in to thicken.", 3, "medium"),
        step(4, "লবণ ও গোলমরিচ দিয়ে নামিয়ে নিন।", "Season with salt and pepper, then serve.", 1, None),
    ],
})

recipes.append({
    "id": "veg_soup", "dish": "সবজি স্যুপ", "dish_en": "Mixed Vegetable Soup", "category": "soup", "base_servings": 4,
    "ingredients": [
        ing("গাজর", "carrot", 0.5, "cup"),
        ing("বাঁধাকপি কুচি", "cabbage, shredded", 0.5, "cup"),
        ing("মটরশুঁটি", "green peas", 0.25, "cup"),
        ing("রসুন কুচি", "garlic, chopped", 1, "tsp"),
        ing("কর্নফ্লাওয়ার", "cornflour", 1.5, "tbsp"),
        ing("সয়া সস", "soy sauce", 1, "tsp", optional=True),
        ing("লবণ ও গোলমরিচ", "salt and pepper", 1, "tsp", note="adjust to taste"),
        ing("পানি", "water", 4, "cup"),
    ],
    "prep_time_min": 10, "cook_time_min": 15, "total_time_min": 25, "heat_level": "medium",
    "steps": [
        step(1, "সব সবজি ছোট টুকরো করে কেটে নিন।", "Chop all vegetables into small pieces.", 8),
        step(2, "পানিতে রসুন ও সবজি দিয়ে ফুটান।", "Boil vegetables with garlic in water.", 8, "medium"),
        step(3, "কর্নফ্লাওয়ার গুলে দিয়ে ঘন করুন।", "Mix in cornflour slurry to thicken.", 3, "medium"),
        step(4, "সয়া সস, লবণ ও গোলমরিচ দিয়ে নামান।", "Season with soy sauce, salt, and pepper, then serve.", 1, None),
    ],
})


recipes.append({
    "id": "egg_bhurji", "dish": "ডিম ভুনা", "dish_en": "Egg Bhurji", "category": "quick", "base_servings": 2,
    "ingredients": [
        ing("ডিম", "eggs", 3, "piece"),
        ing("পেঁয়াজ কুচি", "onion, chopped", 0.5, "cup"),
        ing("কাঁচা মরিচ", "green chili, chopped", 2, "piece"),
        ing("হলুদ গুঁড়া", "turmeric powder", 0.25, "tsp"),
        ing("লবণ", "salt", 0.5, "tsp", note="adjust to taste"),
        ing("তেল", "oil", 2, "tbsp"),
    ],
    "prep_time_min": 5, "cook_time_min": 10, "total_time_min": 15, "heat_level": "medium",
    "steps": [
        step(1, "ডিম ফেটিয়ে লবণ ও হলুদ মিশিয়ে নিন।", "Beat eggs with salt and turmeric.", 2),
        step(2, "তেলে পেঁয়াজ ও কাঁচা মরিচ ভেজে নিন।", "Fry onion and green chili in oil.", 3, "medium"),
        step(3, "ডিমের মিশ্রণ দিয়ে নেড়ে ভুনা করুন।", "Add the egg mixture and stir-fry until done.", 5, "medium"),
    ],
})

recipes.append({
    "id": "singara", "dish": "সিঙ্গারা", "dish_en": "Singara (Samosa)", "category": "snack", "base_servings": 4,
    "ingredients": [
        ing("ময়দা", "all-purpose flour", 2, "cup"),
        ing("আলু সেদ্ধ", "boiled potato, mashed", 2, "cup"),
        ing("মটরশুঁটি", "green peas", 0.5, "cup"),
        ing("পেঁয়াজ কুচি", "onion, chopped", 0.25, "cup"),
        ing("জিরা", "cumin seeds", 0.5, "tsp"),
        ing("মরিচ গুঁড়া", "chili powder", 0.5, "tsp"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("তেল (ময়ানের জন্য)", "oil (for dough)", 3, "tbsp"),
        ing("তেল (ভাজার জন্য)", "oil (for frying)", 2, "cup"),
    ],
    "prep_time_min": 30, "cook_time_min": 25, "total_time_min": 55, "heat_level": "medium-high",
    "steps": [
        step(1, "ময়দা, তেল ও লবণ দিয়ে শক্ত খামির তৈরি করুন।", "Make a firm dough with flour, oil, and salt.", 10),
        step(2, "আলু, মটরশুঁটি, পেঁয়াজ ও মসলা দিয়ে পুর তৈরি করুন।", "Make the filling with potato, peas, onion, and spices.", 10, "medium"),
        step(3, "খামির বেলে ত্রিভুজ আকারে পুর ভরে মুড়ে নিন।", "Roll dough, fill with the mixture, and fold into triangles.", 20),
        step(4, "গরম তেলে সোনালি করে ভেজে নিন।", "Deep fry in hot oil until golden.", 15, "medium-high"),
    ],
})

recipes.append({
    "id": "piyaju", "dish": "পিঁয়াজু", "dish_en": "Piyaju (Onion Fritters)", "category": "snack", "base_servings": 4,
    "ingredients": [
        ing("মুসুর ডাল বাটা", "ground lentils (masoor dal)", 1, "cup"),
        ing("পেঁয়াজ কুচি", "onion, sliced", 1, "cup"),
        ing("কাঁচা মরিচ কুচি", "green chili, chopped", 2, "piece"),
        ing("ধনে পাতা কুচি", "coriander leaves, chopped", 2, "tbsp"),
        ing("লবণ", "salt", 1, "tsp", note="adjust to taste"),
        ing("তেল (ভাজার জন্য)", "oil (for frying)", 2, "cup"),
    ],
    "prep_time_min": 20, "cook_time_min": 15, "total_time_min": 35, "heat_level": "medium-high",
    "steps": [
        step(1, "ডাল ২ ঘণ্টা ভিজিয়ে রেখে বেটে নিন।", "Soak lentils for 2 hours and grind.", 5),
        step(2, "পেঁয়াজ, মরিচ, ধনেপাতা ও লবণ দিয়ে মিশিয়ে নিন।", "Mix in onion, chili, coriander leaves, and salt.", 5),
        step(3, "গরম তেলে ছোট ছোট বলা দিয়ে ভেজে নিন।", "Drop spoonfuls into hot oil and fry until crisp.", 12, "medium-high"),
    ],
})


recipes.append({
    "id": "payesh", "dish": "পায়েস", "dish_en": "Payesh (Rice Pudding)", "category": "dessert", "base_servings": 4,
    "ingredients": [
        ing("দুধ", "milk", 1, "l"),
        ing("পোলাওর চাল", "rice", 0.25, "cup"),
        ing("চিনি", "sugar", 0.5, "cup"),
        ing("এলাচ", "cardamom", 3, "piece"),
        ing("কিশমিশ", "raisins", 2, "tbsp", optional=True),
        ing("বাদাম কুচি", "chopped nuts", 2, "tbsp", optional=True),
    ],
    "prep_time_min": 10, "cook_time_min": 40, "total_time_min": 50, "heat_level": "low-medium",
    "steps": [
        step(1, "দুধ ফুটিয়ে ঘন করতে শুরু করুন।", "Bring milk to a boil and start reducing it.", 15, "medium"),
        step(2, "ধুয়ে রাখা চাল ও এলাচ দিয়ে দিন।", "Add washed rice and cardamom.", 2, "medium"),
        step(3, "অল্প আঁচে নাড়তে নাড়তে ঘন করুন।", "Simmer on low heat, stirring often, until thickened.", 20, "low"),
        step(4, "চিনি, কিশমিশ ও বাদাম দিয়ে আরও কিছুক্ষণ রান্না করুন।", "Add sugar, raisins, and nuts, cook a few more minutes.", 3, "low"),
    ],
})

recipes.append({
    "id": "mishti_doi", "dish": "মিষ্টি দই", "dish_en": "Mishti Doi (Sweet Yogurt)", "category": "dessert", "base_servings": 4,
    "ingredients": [
        ing("দুধ", "milk", 1, "l"),
        ing("চিনি", "sugar", 0.75, "cup"),
        ing("টক দইয়ের বীজ", "plain yogurt (starter culture)", 2, "tbsp"),
    ],
    "prep_time_min": 10, "cook_time_min": 30, "total_time_min": 40, "heat_level": "medium",
    "steps": [
        step(1, "চিনি ক্যারামেল করে দুধে মিশিয়ে ফুটান।", "Caramelize sugar and mix into boiling milk.", 15, "medium"),
        step(2, "দুধ ঘন হয়ে ঠান্ডা (কুসুম গরম) হলে দই মিশিয়ে দিন।", "Once reduced and lukewarm, whisk in the yogurt starter.", 10, "low"),
        step(3, "মাটির পাত্রে ঢেলে ৬-৮ ঘণ্টা গরম জায়গায় রেখে জমতে দিন।", "Pour into an earthen pot and set in a warm place for 6-8 hours.", 5, None),
    ],
})


recipes.append({
    "id": "cha", "dish": "চা", "dish_en": "Milk Tea", "category": "drink", "base_servings": 2,
    "ingredients": [
        ing("পানি", "water", 1, "cup"),
        ing("দুধ", "milk", 1, "cup"),
        ing("চা পাতা", "tea leaves", 2, "tsp"),
        ing("চিনি", "sugar", 2, "tsp", note="adjust to taste"),
    ],
    "prep_time_min": 2, "cook_time_min": 8, "total_time_min": 10, "heat_level": "medium",
    "steps": [
        step(1, "পানি ফুটিয়ে চা পাতা দিন।", "Boil water and add tea leaves.", 3, "high"),
        step(2, "দুধ ও চিনি দিয়ে ফুটিয়ে নিন।", "Add milk and sugar, bring to a boil.", 5, "medium"),
        step(3, "ছেঁকে কাপে ঢেলে পরিবেশন করুন।", "Strain and serve hot.", 1, None),
    ],
})

recipes.append({
    "id": "lebu_cha", "dish": "লেবু চা", "dish_en": "Lemon Tea", "category": "drink", "base_servings": 2,
    "ingredients": [
        ing("পানি", "water", 2, "cup"),
        ing("চা পাতা", "tea leaves", 2, "tsp"),
        ing("লেবুর রস", "lemon juice", 1, "tbsp"),
        ing("চিনি বা মধু", "sugar or honey", 2, "tsp", note="adjust to taste"),
        ing("আদা কুচি", "ginger, sliced", 1, "tsp", optional=True),
    ],
    "prep_time_min": 2, "cook_time_min": 6, "total_time_min": 8, "heat_level": "medium",
    "steps": [
        step(1, "পানি ফুটিয়ে চা পাতা ও আদা দিন।", "Boil water and add tea leaves and ginger.", 4, "high"),
        step(2, "ছেঁকে কাপে ঢেলে লেবুর রস ও চিনি মেশান।", "Strain into a cup and stir in lemon juice and sugar.", 2, None),
    ],
})

recipes.append({
    "id": "dalgona_coffee", "dish": "ডালগোনা কফি", "dish_en": "Dalgona Coffee", "category": "drink", "base_servings": 2,
    "ingredients": [
        ing("ইনস্ট্যান্ট কফি", "instant coffee", 2, "tbsp"),
        ing("চিনি", "sugar", 2, "tbsp"),
        ing("গরম পানি", "hot water", 2, "tbsp"),
        ing("দুধ (ঠান্ডা)", "milk (cold)", 2, "cup"),
        ing("বরফ", "ice", 1, "cup", optional=True),
    ],
    "prep_time_min": 5, "cook_time_min": 5, "total_time_min": 10, "heat_level": None,
    "steps": [
        step(1, "কফি, চিনি ও গরম পানি একসাথে ফেনা হওয়া পর্যন্ত ফেটান।", "Whisk coffee, sugar, and hot water until fluffy and thick.", 5, None),
        step(2, "গ্লাসে দুধ (ও চাইলে বরফ) ঢেলে উপরে ফেনা দিয়ে দিন।", "Pour milk (and ice, if using) into a glass, top with the whipped coffee.", 2, None),
    ],
})

recipes.append({
    "id": "iced_coffee", "dish": "আইসড কফি", "dish_en": "Iced Coffee", "category": "drink", "base_servings": 2,
    "ingredients": [
        ing("ইনস্ট্যান্ট কফি", "instant coffee", 2, "tsp"),
        ing("গরম পানি", "hot water", 0.25, "cup"),
        ing("দুধ (ঠান্ডা)", "milk (cold)", 1.5, "cup"),
        ing("চিনি", "sugar", 2, "tsp", note="adjust to taste"),
        ing("বরফ", "ice cubes", 1, "cup"),
    ],
    "prep_time_min": 5, "cook_time_min": 0, "total_time_min": 5, "heat_level": None,
    "steps": [
        step(1, "গরম পানিতে কফি ও চিনি গুলে নিন।", "Dissolve coffee and sugar in hot water.", 2, None),
        step(2, "গ্লাসে বরফ দিয়ে কফি মিশ্রণ ও ঠান্ডা দুধ ঢেলে দিন।", "Fill a glass with ice, pour in the coffee mixture and cold milk.", 2, None),
        step(3, "নেড়ে পরিবেশন করুন।", "Stir and serve.", 1, None),
    ],
})

recipes.append({
    "id": "borhani", "dish": "বোরহানি", "dish_en": "Borhani (Spiced Yogurt Drink)", "category": "drink", "base_servings": 4,
    "ingredients": [
        ing("টক দই", "plain yogurt", 2, "cup"),
        ing("পুদিনা পাতা", "mint leaves", 0.25, "cup"),
        ing("কাঁচা মরিচ", "green chili", 2, "piece"),
        ing("ভাজা জিরা গুঁড়া", "roasted cumin powder", 1, "tsp"),
        ing("বিট লবণ", "black salt", 0.5, "tsp"),
        ing("চিনি", "sugar", 1, "tbsp", note="adjust to taste"),
        ing("ঠান্ডা পানি", "cold water", 1, "cup"),
    ],
    "prep_time_min": 10, "cook_time_min": 0, "total_time_min": 10, "heat_level": None,
    "steps": [
        step(1, "পুদিনা পাতা ও কাঁচা মরিচ বেটে নিন।", "Grind mint leaves and green chili into a paste.", 5, None),
        step(2, "দই, পানি, মসলা ও বাটা মিশিয়ে ব্লেন্ড করুন।", "Blend yogurt, water, spices, and the paste together.", 3, None),
        step(3, "ঠান্ডা করে পরিবেশন করুন।", "Chill and serve cold.", 2, None),
    ],
})

recipes.append({
    "id": "doi_ghol", "dish": "দই ঘোল", "dish_en": "Doi Ghol (Yogurt Lassi)", "category": "drink", "base_servings": 4,
    "ingredients": [
        ing("টক দই", "plain yogurt", 2, "cup"),
        ing("ঠান্ডা পানি", "cold water", 1.5, "cup"),
        ing("চিনি বা লবণ", "sugar or salt", 2, "tbsp", note="pick one, adjust to taste"),
        ing("বরফ", "ice", 0.5, "cup", optional=True),
    ],
    "prep_time_min": 5, "cook_time_min": 0, "total_time_min": 5, "heat_level": None,
    "steps": [
        step(1, "দই ও পানি একসাথে ব্লেন্ড করুন।", "Blend yogurt and water together.", 3, None),
        step(2, "চিনি বা লবণ মিশিয়ে বরফসহ পরিবেশন করুন।", "Stir in sugar or salt, serve with ice.", 2, None),
    ],
})

recipes.append({
    "id": "chocolate_milk", "dish": "চকলেট মিল্ক", "dish_en": "Hot Chocolate Milk", "category": "drink", "base_servings": 2,
    "ingredients": [
        ing("দুধ", "milk", 2, "cup"),
        ing("কোকো পাউডার", "cocoa powder", 2, "tbsp"),
        ing("চিনি", "sugar", 2, "tbsp", note="adjust to taste"),
    ],
    "prep_time_min": 2, "cook_time_min": 8, "total_time_min": 10, "heat_level": "medium",
    "steps": [
        step(1, "দুধ হালকা গরম করুন।", "Warm the milk gently.", 4, "medium"),
        step(2, "কোকো পাউডার ও চিনি মিশিয়ে ভালোভাবে গুলিয়ে নিন।", "Whisk in cocoa powder and sugar until fully dissolved.", 4, "low"),
    ],
})

recipes.append({
    "id": "americano", "dish": "আমেরিকানো", "dish_en": "Americano", "category": "drink", "base_servings": 1,
    "ingredients": [
        ing("এসপ্রেসো/কড়া কফি", "espresso or strong coffee", 2, "shot"),
        ing("গরম পানি", "hot water", 1, "cup"),
    ],
    "prep_time_min": 2, "cook_time_min": 3, "total_time_min": 5, "heat_level": "high",
    "steps": [
        step(1, "কাপে গরম পানি নিন।", "Pour hot water into a cup.", 1, None),
        step(2, "উপরে এসপ্রেসো/কড়া কফি ঢেলে দিন।", "Pour espresso or strong coffee on top.", 1, None),
    ],
})


output = {"recipes": recipes}
with open("recipes.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(recipes)} recipes to recipes.json")
