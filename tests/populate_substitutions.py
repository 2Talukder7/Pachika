import json

recipes_file = "backend/data/recipes.json"
with open(recipes_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for r in data["recipes"]:
    if r["id"] == "beef_bhuna":
        r["cook_time_min"] = 65
        r["total_time_min"] = 85
        print("Updated beef_bhuna timing: cook=65, total=85")

SUBS_MAP = {
    "fish_bhuna": [
        {
            "ingredient": "Rui / Rohu fish",
            "ingredient_bn": "রুই মাছ",
            "substitute": "Catla, Tilapia, or Basa fish fillets",
            "substitute_bn": "কাতলা, তিলাপিয়া বা বাসা মাছের ফিলে",
            "impact": "Mild change in texture; tilapia and basa cook slightly faster.",
            "impact_bn": "মাছের টেক্সচারে সামান্য পরিবর্তন আসবে, তিলাপিয়া ও বাসা কিছুটা দ্রুত সেদ্ধ হবে।"
        },
        {
            "ingredient": "Mustard oil",
            "ingredient_bn": "সরিষার তেল",
            "substitute": "Refined sunflower or soybean oil",
            "substitute_bn": "সয়াবিন বা সূর্যমুখী তেল",
            "impact": "Milder aroma without traditional mustard pungency.",
            "impact_bn": "সরিষার খাঁটি ঝাঁঝ থাকবে না, তবে হালকা ও সুস্বাদু স্বাদ হবে।"
        }
    ],
    "prawn_malai_curry": [
        {
            "ingredient": "Coconut milk",
            "ingredient_bn": "নারিকেলের দুধ",
            "substitute": "Full-cream cow milk whisked with 1 tbsp heavy cream or cashew paste",
            "substitute_bn": "ঘন দুধ ও ১ চামচ হেভি ক্রিম বা কাজুবাদাম বাটা",
            "impact": "Maintains rich velvety gravy with lighter nutty aroma.",
            "impact_bn": "ঝোল ঘন ও ক্রিমি থাকবে, নারিকেলের গন্ধের বদলে বাদামি সুবাস আসবে।"
        },
        {
            "ingredient": "Ghee",
            "ingredient_bn": "ঘি",
            "substitute": "Unsalted butter or cooking oil with a drop of butter",
            "substitute_bn": "বাটার বা সামান্য সয়াবিন তেল",
            "impact": "Slight variation in royal aroma, rich taste remains intact.",
            "impact_bn": "শাহী সুবাসে সামান্য তারতম্য হবে, তবে স্বাদ চমৎকার থাকবে।"
        }
    ],
    "veg_curry": [
        {
            "ingredient": "Cauliflower",
            "ingredient_bn": "ফুলকপি",
            "substitute": "Broccoli, cabbage, or knolkhol",
            "substitute_bn": "ব্রকলি বা বাঁধাকপি",
            "impact": "Slightly shorter cooking duration with crisp texture.",
            "impact_bn": "রান্নার সময় ৩-৪ মিনিট কম লাগবে, ভিন্ন টেক্সচার আসবে।"
        },
        {
            "ingredient": "Mustard oil",
            "ingredient_bn": "সরিষার তেল",
            "substitute": "Soybean or vegetable oil",
            "substitute_bn": "সয়াবিন বা সূর্যমুখী তেল",
            "impact": "Lighter vegetable aroma.",
            "impact_bn": "মৃদু স্বাদ ও হালকা সুবাস থাকবে।"
        }
    ],
    "dal": [
        {
            "ingredient": "Red lentils (Masoor dal)",
            "ingredient_bn": "মসুর ডাল",
            "substitute": "Mung dal or split yellow peas (Chana dal)",
            "substitute_bn": "মুগ ডাল অথবা ছোলার ডাল",
            "impact": "Mung dal gives a sweet nutty aroma; requires light dry roasting first.",
            "impact_bn": "মুগ ডাল আগে সামান্য ভেজে নিতে হয়, ঘন ও সুমিষ্ট সুবাস আসবে।"
        },
        {
            "ingredient": "Panch phoron",
            "ingredient_bn": "পাঁচফোড়ন",
            "substitute": "Whole cumin seeds (Jeera) and dried red chili",
            "substitute_bn": "আস্ত জিরা ও শুকনা মরিচ ফোড়ন",
            "impact": "Cleaner single-spice cumin aroma rather than complex 5-spice blend.",
            "impact_bn": "পাঁচফোড়নের বদলে জিরার খাঁটি সুবাস আসবে, চমৎকার স্বাদ হবে।"
        }
    ],
    "chicken_soup": [
        {
            "ingredient": "Bone-in chicken",
            "ingredient_bn": "মুরগির মাংস",
            "substitute": "Boneless chicken breast or shredded boiled chicken",
            "substitute_bn": "হাড় ছাড়া মুরগির বুকের মাংস",
            "impact": "Stock is lighter with lower collagen richness.",
            "impact_bn": "স্যুপের স্টক হালকা হবে, তেল কম থাকবে।"
        },
        {
            "ingredient": "Cornstarch",
            "ingredient_bn": "কর্নফ্লাওয়ার",
            "substitute": "Wheat flour whisked with 2 tbsp cold water, or potato starch",
            "substitute_bn": "ময়দা ও ঠাণ্ডা পানির মিশ্রণ বা আলুর স্টার্চ",
            "impact": "Gives appropriate thickness with slight opacity.",
            "impact_bn": "স্যুপ যথাযথ ঘন হবে, রং সামান্য ঘোলাটে হতে পারে।"
        }
    ],
    "veg_soup": [
        {
            "ingredient": "French beans",
            "ingredient_bn": "শিম / বিনস",
            "substitute": "Green peas or sweet corn",
            "substitute_bn": "মটরশুঁটি বা মিষ্টি ভুট্টা",
            "impact": "Adds natural sweetness and soft bite.",
            "impact_bn": "মিষ্টি স্বাদ ও নরম টেক্সচার যোগ হবে।"
        },
        {
            "ingredient": "Black pepper",
            "ingredient_bn": "গোলমরিচ গুঁড়া",
            "substitute": "White pepper powder",
            "substitute_bn": "সাদা গোলমরিচ গুঁড়া",
            "impact": "Keeps broth clear with earthy heat.",
            "impact_bn": "স্যুপের পরিষ্কার রং বজায় থাকবে, সুষম ঝাল আসবে।"
        }
    ],
    "egg_bhurji": [
        {
            "ingredient": "Green chili",
            "ingredient_bn": "কাঁচামরিচ",
            "substitute": "Coarsely ground black pepper or red pepper flakes",
            "substitute_bn": "গোলমরিচ গুঁড়া বা চিলি ফ্লেক্স",
            "impact": "Smoky peppery heat instead of fresh vegetal spice.",
            "impact_bn": "কাঁচামরিচের সুবাসের বদলে মনোরম গোলমরিচের ঝাল আসবে।"
        },
        {
            "ingredient": "Butter",
            "ingredient_bn": "বাটার",
            "substitute": "Ghee or cooking oil",
            "substitute_bn": "ঘি বা সয়াবিন তেল",
            "impact": "Ghee adds authentic aroma; oil yields a lighter texture.",
            "impact_bn": "ঘি দিলে শাহী সুবাস হবে, তেল দিলে হালকা টেক্সচার হবে।"
        }
    ],
    "singara": [
        {
            "ingredient": "Peanuts",
            "ingredient_bn": "ভাজা চিনাবাদাম",
            "substitute": "Cashew nuts or green peas",
            "substitute_bn": "কাজুবাদাম বা কচি মটরশুঁটি",
            "impact": "Richer crunch and texture inside potato filling.",
            "impact_bn": "আলুর পুরের ভেতর চমৎকার মুচমুচে টেক্সচার এনে দেবে।"
        },
        {
            "ingredient": "Ghee in dough",
            "ingredient_bn": "ময়দার ময়ানের ঘি",
            "substitute": "Hot refined vegetable oil",
            "substitute_bn": "হালকা গরম সয়াবিন তেল",
            "impact": "Maintains signature crisp flaky crust (khasta texture).",
            "impact_bn": "খাস্তা ও মুচমুচে টেক্সচার পুরোপুরি বজায় থাকবে।"
        }
    ],
    "payesh": [
        {
            "ingredient": "Chinigura aromatic rice",
            "ingredient_bn": "চিনিগুঁড়া সুগন্ধি চাল",
            "substitute": "Kalijira, Gobindobhog, or Basmati rice",
            "substitute_bn": "কালিজিরার চাল, গোবিন্দভোগ বা বাসমতি চাল",
            "impact": "Signature sweet aroma preserved; cooking duration identical.",
            "impact_bn": "মিষ্টি সুবাস বজায় থাকবে, রান্নার সময় একই থাকবে।"
        },
        {
            "ingredient": "Cardamom",
            "ingredient_bn": "এলাচ",
            "substitute": "Cinnamon stick or pinch of nutmeg powder",
            "substitute_bn": "দারুচিনি বা সামান্য জায়ফল গুঁড়া",
            "impact": "Warm aromatic undertone.",
            "impact_bn": "পায়েশে উষ্ণ মিষ্টি সুবাস ছড়াবে।"
        }
    ],
    "cha": [
        {
            "ingredient": "Full cream liquid milk",
            "ingredient_bn": "তরল দুধ",
            "substitute": "Full cream milk powder (3 tbsp dissolved in 1/2 cup warm water)",
            "substitute_bn": "ঘন গুঁড়া দুধের মিশ্রণ",
            "impact": "Creates extra thick, creamy, tea-stall style rich milk tea.",
            "impact_bn": "চা অত্যন্ত ঘন, ক্রিমি ও টঙের দোকানের মতো দারুণ লালচে হবে।"
        },
        {
            "ingredient": "Fresh ginger",
            "ingredient_bn": "আদা",
            "substitute": "Dry ginger powder (Sonth)",
            "substitute_bn": "শুকনা আদা গুঁড়া",
            "impact": "Sharp warm spice with soothing throat feel.",
            "impact_bn": "গলা আরামদায়ী উষ্ণ ঝাঁঝ পাওয়া যাবে।"
        }
    ],
    "lebu_cha": [
        {
            "ingredient": "Fresh lemon juice",
            "ingredient_bn": "লেবুর রস",
            "substitute": "Green lime juice or Kaffir lime (Kagoji lebu)",
            "substitute_bn": "কাগজি লেবু বা সবুজ বাতাবি লেবুর রস",
            "impact": "Intensely fragrant floral citrus aroma with refreshing acidity.",
            "impact_bn": "কাগজি লেবুর তীব্র মিষ্টি সুবাস ও সতেজ টক ভাব এনে দেবে।"
        },
        {
            "ingredient": "Black salt (Bit lobon)",
            "ingredient_bn": "বিট লবণ",
            "substitute": "Rock salt with a pinch of chat masala",
            "substitute_bn": "সাধারণ লবণ ও সামান্য চাট মসলা",
            "impact": "Tangy savory balance preserved.",
            "impact_bn": "চমৎকার মুখরোচক টক-ঝাল স্বাদ বজায় থাকবে।"
        }
    ],
    "dalgona_coffee": [
        {
            "ingredient": "White granulated sugar",
            "ingredient_bn": "চিনি",
            "substitute": "Brown sugar or powdered sugar",
            "substitute_bn": "বাদামি চিনি বা আইসিং সুগার",
            "impact": "Rich caramel notes in the whipped coffee foam.",
            "impact_bn": "কফির ফোমে চমৎকার ক্যারামেল স্বাদ ও গাড় রং তৈরি হবে।"
        },
        {
            "ingredient": "Instant coffee",
            "ingredient_bn": "ইনস্ট্যান্ট কফি",
            "substitute": "Concentrated espresso reduction",
            "substitute_bn": "ঘন এসপ্রেসো কফি ডিককশন",
            "impact": "Deep roasted flavor; whip may take slightly longer.",
            "impact_bn": "তীব্র কফির স্বাদ পাওয়া যাবে; ফোম হতে সামান্য বেশি সময় লাগতে পারে।"
        }
    ],
    "iced_coffee": [
        {
            "ingredient": "Whole cow milk",
            "ingredient_bn": "দুধ",
            "substitute": "Oat milk, almond milk, or condensed milk",
            "substitute_bn": "ওট মিল্ক, বাদাম দুধ অথবা কনডেন্সড মিল্ক",
            "impact": "Condensed milk gives Vietnamese iced coffee sweetness; oat milk gives vegan creaminess.",
            "impact_bn": "কনডেন্সড মিল্ক দিলে ভিয়েতনামিজ স্টাইল স্বাদ হবে, ওট মিল্ক দিলে ভেগান ও ক্রিমি হবে।"
        },
        {
            "ingredient": "Granulated sugar",
            "ingredient_bn": "চিনি",
            "substitute": "Vanilla syrup or caramel sauce",
            "substitute_bn": "ভ্যানিলা সিরাপ বা মধু",
            "impact": "Adds subtle aromatic sweetness.",
            "impact_bn": "মনোরম সুবাস ও মিষ্টি স্বাদ যোগ হবে।"
        }
    ],
    "chocolate_milk": [
        {
            "ingredient": "Cocoa powder",
            "ingredient_bn": "কোকো পাউডার",
            "substitute": "Melted dark chocolate or chocolate syrup",
            "substitute_bn": "গলানো ডার্ক চকলেট বা চকলেট সিরাপ",
            "impact": "Richer, thicker texture with glossy chocolate body.",
            "impact_bn": "চকলেটের গভীর রিচ স্বাদ ও ঘন টেক্সচার আসবে।"
        },
        {
            "ingredient": "Dairy milk",
            "ingredient_bn": "দুধ",
            "substitute": "Soy milk or almond milk",
            "substitute_bn": "সয়া দুধ বা আমন্ড মিল্ক",
            "impact": "100% plant-based with light nutty finish.",
            "impact_bn": "ল্যাকটোজ-মুক্ত ভেগান অপশন, হজমে সহজ হবে।"
        }
    ],
    "americano": [
        {
            "ingredient": "Espresso roast coffee",
            "ingredient_bn": "এসপ্রেসো কফি",
            "substitute": "Strong French press brew or Moka pot coffee",
            "substitute_bn": "মোকা পট বা ফ্রেঞ্চ প্রেসের স্ট্রং কফি",
            "impact": "Robust full-bodied cup with less crema but authentic roasted punch.",
            "impact_bn": "ক্রিমা সামান্য কম হলেও গভীর রোস্টেড স্বাদ চমৎকার থাকবে।"
        }
    ]
}

added_count = 0
for r in data["recipes"]:
    rid = r["id"]
    if rid in SUBS_MAP and not r.get("substitutions"):
        r["substitutions"] = SUBS_MAP[rid]
        added_count += 1
        print(f"Added substitutions for {rid}")

with open(recipes_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Successfully updated recipes.json! Added substitutions to {added_count} recipes.")
