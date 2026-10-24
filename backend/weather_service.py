
import urllib.request
import urllib.parse
import json
import datetime
import re

WMO_CODES = {
    0: {"en": "Clear sky", "bn": "পরিষ্কার আকাশ", "type": "clear"},
    1: {"en": "Mainly clear", "bn": "বেশিরভাগ সময় পরিষ্কার", "type": "clear"},
    2: {"en": "Partly cloudy", "bn": "আংশিক মেঘলা", "type": "cloudy"},
    3: {"en": "Overcast", "bn": "মেঘলা আকাশ", "type": "cloudy"},
    45: {"en": "Foggy", "bn": "কুয়াশাচ্ছন্ন", "type": "fog"},
    48: {"en": "Depositing rime fog", "bn": "ঘন কুয়াশা", "type": "fog"},
    51: {"en": "Light drizzle", "bn": "হালকা গুঁড়ি গুঁড়ি বৃষ্টি", "type": "rain"},
    53: {"en": "Moderate drizzle", "bn": "গুঁড়ি গুঁড়ি বৃষ্টি", "type": "rain"},
    55: {"en": "Dense drizzle", "bn": "ঘন গুঁড়ি গুঁড়ি বৃষ্টি", "type": "rain"},
    61: {"en": "Slight rain", "bn": "হালকা বৃষ্টি", "type": "rain"},
    63: {"en": "Moderate rain", "bn": "মাঝারি বৃষ্টিপাত", "type": "rain"},
    65: {"en": "Heavy rain", "bn": "ভারী বর্ষণ", "type": "rain"},
    71: {"en": "Slight snow", "bn": "হালকা তুষারপাত", "type": "cold"},
    73: {"en": "Moderate snow", "bn": "তুষারপাত", "type": "cold"},
    75: {"en": "Heavy snow", "bn": "ভারী তুষারপাত", "type": "cold"},
    80: {"en": "Slight rain showers", "bn": "বৃষ্টির ঝাপটা", "type": "rain"},
    81: {"en": "Moderate rain showers", "bn": "মাঝারি বৃষ্টির ঝাপটা", "type": "rain"},
    82: {"en": "Violent rain showers", "bn": "প্রবল বৃষ্টিপাত", "type": "rain"},
    95: {"en": "Thunderstorm", "bn": "বজ্রবৃষ্টি", "type": "storm"},
    96: {"en": "Thunderstorm with slight hail", "bn": "শিলাবৃষ্টিসহ ঝড়", "type": "storm"},
    99: {"en": "Thunderstorm with heavy hail", "bn": "প্রবল শিলাবৃষ্টি", "type": "storm"},
}

DEFAULT_LOCATIONS = {
    "dhaka": {"name": "Dhaka", "name_bn": "ঢাকা", "lat": 23.8103, "lon": 90.4125, "country": "Bangladesh"},
    "chittagong": {"name": "Chittagong", "name_bn": "চট্টগ্রাম", "lat": 22.3569, "lon": 91.7832, "country": "Bangladesh"},
    "sylhet": {"name": "Sylhet", "name_bn": "সিলেট", "lat": 24.8949, "lon": 91.8687, "country": "Bangladesh"},
    "rajshahi": {"name": "Rajshahi", "name_bn": "রাজশাহী", "lat": 24.3745, "lon": 88.6042, "country": "Bangladesh"},
    "khulna": {"name": "Khulna", "name_bn": "খুলনা", "lat": 22.8456, "lon": 89.5403, "country": "Bangladesh"},
}


def geocode_city(city_name, timeout=5):
    clean_city = city_name.strip().lower()
    if clean_city in DEFAULT_LOCATIONS:
        return DEFAULT_LOCATIONS[clean_city]

    encoded = urllib.parse.quote(city_name.strip())
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded}&count=1&language=en&format=json"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PachikaCookingAssistant/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results")
            if results and len(results) > 0:
                first = results[0]
                return {
                    "name": first.get("name"),
                    "name_bn": first.get("name"),
                    "lat": first.get("latitude"),
                    "lon": first.get("longitude"),
                    "country": first.get("country", ""),
                }
    except Exception as e:
        print(f"Geocoding error for '{city_name}':", e)

    return None


def fetch_weather(lat, lon, timeout=5):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code,precipitation,is_day"
        f"&timezone=auto"
    )

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PachikaCookingAssistant/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            current = data.get("current", {})
            temperature = current.get("temperature_2m")
            if temperature is None:
                return None
            w_code = current.get("weather_code")
            meta = WMO_CODES.get(w_code, {"en": "Unknown", "bn": "অজানা", "type": "unknown"})
            precipitation = current.get("precipitation")

            return {
                "temperature_c": temperature,
                "humidity_percent": current.get("relative_humidity_2m"),
                "precipitation_mm": precipitation if precipitation is not None else 0.0,
                "weather_code": w_code,
                "is_day": current.get("is_day", 1),
                "condition_en": meta["en"],
                "condition_bn": meta["bn"],
                "condition_type": meta["type"],
            }
    except Exception as e:
        print("Weather fetch error:", e)
        return None


def fetch_hijri_date(target_date=None, timeout=5):
    if target_date is None:
        target_date = datetime.date.today()

    date_str = target_date.strftime("%d-%m-%Y")
    url = f"https://api.aladhan.com/v1/gToH/{date_str}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PachikaCookingAssistant/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("code") == 200:
                hijri = data.get("data", {}).get("hijri", {})
                month_num = int(hijri.get("month", {}).get("number", 1))
                day_num = int(hijri.get("day", 1))
                return {
                    "day": day_num,
                    "month_number": month_num,
                    "month_en": hijri.get("month", {}).get("en", ""),
                    "month_ar": hijri.get("month", {}).get("ar", ""),
                    "year": hijri.get("year", ""),
                }
    except Exception as e:
        print("Hijri date fetch error:", e)

    return None


def detect_festive_context(hijri_info=None, target_date=None):
    if target_date is None:
        target_date = datetime.date.today()

    month = target_date.month
    day = target_date.day

    if month == 4 and 10 <= day <= 18:
        return {
            "name_bn": "পহেলা বৈশাখ ও বাংলা নববর্ষ",
            "name_en": "Pahela Baishakh (Bengali New Year)",
            "description_bn": "নববর্ষের চিরায়ত ঐতিহ্য পান্তা-ইলিশ, ভর্তা এবং উৎসবের নানা পদ।",
            "description_en": "Traditional Bengali New Year celebration featuring fish bhuna and assorted bhortas.",
            "recommended_dishes": ["fish_bhuna", "aloo_bhorta", "begun_bhorta", "prawn_malai_curry"],
        }

    if month in [11, 12, 1]:
        return {
            "name_bn": "নবান্ন ও শীতের পিঠাপুলির আমেজ",
            "name_en": "Nabanna Harvest & Winter Treats",
            "description_bn": "শীতের হিমেল সন্ধ্যায় নতুন ধানের পায়েস ও হাঁসের মাংস ভুনার সুস্বাদু মৌসুম।",
            "description_en": "Winter harvest celebration featuring rich payesh and tender duck bhuna.",
            "recommended_dishes": ["duck_bhuna", "payesh", "beef_bhuna", "cha"],
        }

    if month in [6, 7, 8]:
        return {
            "name_bn": "বর্ষার বৃষ্টিমুখর আমেজ",
            "name_en": "Monsoon Culinary Tradition",
            "description_bn": "বাদলা দিনে খিচুড়ি, মাছের ঝোল ও বেগুন ভর্তার অবিচ্ছেদ্য বাঙালি স্বাদ।",
            "description_en": "Classic rainy season comfort of warm khichuri, fish, and comforting bhortas.",
            "recommended_dishes": ["khichuri", "fish_curry", "begun_bhorta", "lebu_cha"],
        }

    if hijri_info:
        h_month = hijri_info.get("month_number")
        h_day = hijri_info.get("day")

        if h_month == 9:
            return {
                "name_bn": "মাহে রমজান — ইফতার ও সাহরি",
                "name_en": "Holy Ramadan (Iftar & Suhoor)",
                "description_bn": "ইফতারে মুচমুচে পিঁয়াজু, সিঙ্গাড়া, পুষ্টিকর ছোলা ও পেট ঠান্ডা রাখতে দই ঘোল।",
                "description_en": "Ramadan culinary tradition with crunchy piyaju, singara, and cooling doi ghol.",
                "recommended_dishes": ["piyaju", "singara", "doi_ghol", "borhani", "khichuri"],
            }
        if h_month == 10 and h_day <= 4:
            return {
                "name_bn": "পবিত্র ঈদুল ফিতর",
                "name_en": "Eid-ul-Fitr Celebration",
                "description_bn": "ঈদের সকালে মিষ্টি পায়েস ও দুপুরে পোলাও-মাংসের রাজকীয় আয়োজন।",
                "description_en": "Eid sweet celebration with traditional payesh, mishti doi, and festive pulao.",
                "recommended_dishes": ["payesh", "mishti_doi", "pulao", "chicken_biryani", "chicken_bhuna"],
            }
        if h_month == 12 and 10 <= h_day <= 13:
            return {
                "name_bn": "পবিত্র ঈদুল আযহা (কোরবানি ঈদ)",
                "name_en": "Eid-ul-Adha Feast",
                "description_bn": "কোরবানির ঈদের বিশেষ গরুর মাংস ভুনা, খাসির মাংস ভুনা ও বোরহানি।",
                "description_en": "Sacrificial feast highlighting rich beef bhuna, mutton bhuna, and digestive borhani.",
                "recommended_dishes": ["beef_bhuna", "mutton_bhuna", "beef_curry", "borhani"],
            }

    return None


BN_DIGITS = "০১২৩৪৫৬৭৮৯"


def _bn_digits(text):
    return "".join(BN_DIGITS[int(c)] if c.isdigit() else c for c in str(text))


WEATHER_PROFILES = {
    "stormy": {
        "dishes": ["khichuri", "beef_bhuna", "piyaju", "cha"],
        "bn": "বাইরে প্রবল বৃষ্টি-ঝড়। এমন দিনে গরম ভুনা খিচুড়ি, ঝাল গরুর ভুনা আর মুচমুচে পিঁয়াজু-চা-ই সেরা।",
        "en": "A rain-and-thunder day: steaming bhuna khichuri, spicy beef bhuna and crisp piyaju with hot tea fit perfectly.",
    },
    "rain_cool": {
        "dishes": ["khichuri", "beef_bhuna", "singara", "cha"],
        "bn": "বৃষ্টি পড়ছে আর বাতাসও ঠান্ডা। গরম খিচুড়ি, গরুর ভুনা আর সিঙ্গারা-চা শরীর গরম রাখবে।",
        "en": "It is raining and cool. Hot khichuri, beef bhuna and singara with tea will keep you warm.",
    },
    "rain_warm": {
        "dishes": ["khichuri", "fish_bhuna", "begun_bhorta", "lebu_cha"],
        "bn": "বাইরে বৃষ্টি। এই স্যাঁতসেঁতে দিনে ভুনা খিচুড়ি, মাছ ভুনা, বেগুন ভর্তা আর লেবু চা অতুলনীয়।",
        "en": "It is raining. Bhuna khichuri, fish bhuna, begun bhorta and lemon tea are the classic comfort on a wet day.",
    },
    "very_cold": {
        "dishes": ["beef_bhuna", "mutton_bhuna", "chicken_soup", "cha"],
        "bn": "কনকনে ঠান্ডা! গরুর ও খাসির ভুনা, গরম মুরগির স্যুপ আর ধোঁয়া ওঠা দুধ চা শরীরে উষ্ণতা আনবে।",
        "en": "Bitterly cold! Rich beef and mutton bhuna, hot chicken soup and steaming milk tea bring real warmth.",
    },
    "cold": {
        "dishes": ["duck_bhuna", "beef_bhuna", "cha", "payesh"],
        "bn": "ঠান্ডা আবহাওয়া। হাঁসের ভুনা, গরুর ভুনা, এলাচ-দুধ চা আর গরম পায়েস শীতে দারুণ মানায়।",
        "en": "Chilly weather. Duck bhuna, beef bhuna, cardamom milk tea and warm payesh suit it well.",
    },
    "mild": {
        "dishes": ["pulao", "chicken_bhuna", "chicken_biryani", "egg_bhurji"],
        "bn": "মনোরম আবহাওয়া। সুগন্ধি পোলাও, মুরগির ভুনা, বিরিয়ানি বা ডিম ভুজিয়া রাঁধার আদর্শ দিন।",
        "en": "Pleasant weather: a good day for aromatic pulao, chicken bhuna, biryani or egg bhurji.",
    },
    "warm_humid": {
        "dishes": ["dal", "fish_curry", "veg_curry", "lebu_cha"],
        "bn": "গরম না হলেও বাতাসে আর্দ্রতা বেশি। হালকা ডাল, মাছের ঝোল, সবজি আর লেবু চা আরাম দেবে।",
        "en": "Not scorching, but quite humid. Light dal, fish curry, vegetables and lemon tea feel just right.",
    },
    "hot": {
        "dishes": ["doi_ghol", "borhani", "dal", "veg_curry"],
        "bn": "বেশ গরম। পেট ঠান্ডা রাখতে হালকা মসলার ডাল, সবজি আর ঠান্ডা দই ঘোল বা বোরহানি মানানসই।",
        "en": "Hot weather. Lightly spiced dal and vegetables with chilled doi ghol or borhani keep you cool.",
    },
    "very_hot": {
        "dishes": ["doi_ghol", "lebu_cha", "dal", "aloo_bhorta"],
        "bn": "প্রচণ্ড গরম! ঠান্ডা দই ঘোল, লেবুর শরবত-চা, পাতলা ডাল আর আলু ভর্তা-ভাত সবচেয়ে স্বস্তির।",
        "en": "Scorching heat! Chilled doi ghol, lemon tea, thin dal and aloo bhorta with rice are the most comfortable choices.",
    },
}


def classify_weather(weather):
    temp = float(weather["temperature_c"])
    humidity = weather.get("humidity_percent")
    precip = weather.get("precipitation_mm") or 0.0
    cond = weather.get("condition_type")

    if cond == "storm" or precip >= 5:
        band = "stormy"
    elif cond == "rain" or precip > 0.5:
        band = "rain_cool" if temp <= 22 else "rain_warm"
    elif temp <= 12:
        band = "very_cold"
    elif temp <= 21 or (cond == "fog" and temp <= 24):
        band = "cold"
    elif temp >= 35:
        band = "very_hot"
    elif temp >= 29:
        band = "hot"
    elif temp >= 25 and humidity is not None and humidity >= 75:
        band = "warm_humid"
    else:
        band = "mild"

    profile = WEATHER_PROFILES[band]
    shown = round(temp)
    return {
        "band": band,
        "dishes": list(profile["dishes"]),
        "reason_bn": f"এখন তাপমাত্রা {_bn_digits(shown)}°সে। {profile['bn']}",
        "reason_en": f"It is {shown}°C right now. {profile['en']}",
    }


def get_weather_recommendations(lat=None, lon=None, city=None, recipe_engine=None):
    location_info = None

    if city and city.strip():
        location_info = geocode_city(city.strip())
        if not location_info:
            return {
                "success": False,
                "error": f"City '{city}' could not be located. Please check spelling or try another city.",
                "error_bn": f"'{city}' শহরের অবস্থান খুঁজে পাওয়া যায়নি। বানানের সঠিকতা যাচাই করে আবার চেষ্টা করুন।"
            }
    elif lat is not None and lon is not None:
        try:
            lat = float(lat)
            lon = float(lon)
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError("coordinates out of range")
            location_info = {
                "name": "Your Location",
                "name_bn": "আপনার অবস্থান",
                "lat": lat,
                "lon": lon,
                "country": ""
            }
        except (ValueError, TypeError):
            return {
                "success": False,
                "error": "The location coordinates are not valid. Please type a city name instead.",
                "error_bn": "অবস্থানের স্থানাঙ্ক সঠিক নয়। অনুগ্রহ করে শহরের নাম লিখুন।"
            }
    else:
        location_info = DEFAULT_LOCATIONS["dhaka"]

    weather = fetch_weather(location_info["lat"], location_info["lon"])
    if not weather:
        return {
            "success": False,
            "error": "Weather data service is currently unavailable. Please check your internet connection.",
            "error_bn": "আবহাওয়া সেবা এই মুহূর্তে অনুপলব্ধ। ইন্টারনেট সংযোগ যাচাই করে আবার চেষ্টা করুন।",
            "location": location_info
        }

    today = datetime.date.today()
    hijri = fetch_hijri_date(today)
    festive = detect_festive_context(hijri, today)

    profile = classify_weather(weather)
    rec_dish_ids = profile["dishes"]
    weather_reason_bn = profile["reason_bn"]
    weather_reason_en = profile["reason_en"]

    def resolve_recipes(id_list):
        items = []
        if not recipe_engine:
            return items
        for rid in id_list:
            r = recipe_engine.find_recipe_by_id(rid)
            if r:
                items.append({
                    "id": r["id"],
                    "dish": r["dish"],
                    "dish_en": r["dish_en"],
                    "category": r.get("category", ""),
                    "total_time_min": r.get("total_time_min", 40),
                    "heat_level": r.get("heat_level", "medium"),
                    "image": r.get("image", {}),
                })
        return items

    weather_dishes = resolve_recipes(rec_dish_ids)

    festive_data = None
    if festive:
        festive_dishes = resolve_recipes(festive.get("recommended_dishes", []))
        festive_data = {
            "name_bn": festive["name_bn"],
            "name_en": festive["name_en"],
            "description_bn": festive["description_bn"],
            "description_en": festive["description_en"],
            "recipes": festive_dishes,
        }

    return {
        "success": True,
        "location": location_info,
        "weather": weather,
        "reason_bn": weather_reason_bn,
        "reason_en": weather_reason_en,
        "weather_band": profile["band"],
        "weather_recipes": weather_dishes,
        "festive": festive_data,
        "date_info": {
            "gregorian": today.strftime("%B %d, %Y"),
            "hijri": f"{hijri['day']} {hijri['month_en']} {hijri['year']} AH" if hijri else None,
        }
    }
