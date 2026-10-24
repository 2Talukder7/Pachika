import json
import re
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API_BASE = "https://www.themealdb.com/api/json/v1/1"
USER_AGENT = "PachikaCookingAssistant/2.0"
REQUEST_TIMEOUT = 10
CACHE_TTL_SECONDS = 600
CACHE_MAX_ITEMS = 200
MAX_RESULTS = 6
PROVIDER = "themealdb"
PROVIDER_NAME = "TheMealDB"

_CACHE = {}


try:
    import certifi
except ImportError:
    certifi = None


class OnlineSearchError(Exception):
    def __init__(self, message="", reason="network", detail=""):
        super().__init__(message)
        self.reason = reason
        self.detail = detail or message


def classify_error(exc):
    text = str(exc).lower()
    if isinstance(exc, urllib.error.HTTPError):
        return "blocked" if exc.code in (403, 429) else "http"
    if "certificate" in text or "ssl" in text:
        return "ssl"
    reason = getattr(exc, "reason", None)
    if isinstance(reason, socket.gaierror) or "getaddrinfo" in text or "name or service not known" in text or "11001" in text:
        return "dns"
    if isinstance(exc, (TimeoutError, socket.timeout)) or isinstance(reason, (TimeoutError, socket.timeout)) or "timed out" in text:
        return "timeout"
    return "network"


def _ssl_context():
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


INGREDIENT_GROUPS = {
    "beef": {
        "label_en": "Beef",
        "label_bn": "গরুর মাংস",
        "en": {"beef", "cow", "cows", "cattle", "veal", "steak"},
        "bn": ("গরু", "বিফ"),
        "sources": [("category", "Beef")],
    },
    "mutton": {
        "label_en": "Mutton / Goat",
        "label_bn": "খাসি / ছাগলের মাংস",
        "en": {"mutton", "goat", "goats", "lamb", "khashi", "khasi", "chagol"},
        "bn": ("খাসি", "ছাগল", "পাঁঠা", "পাঠা", "ভেড়া", "মাটন"),
        "sources": [("category", "Goat"), ("category", "Lamb")],
    },
    "chicken": {
        "label_en": "Chicken",
        "label_bn": "মুরগি",
        "en": {"chicken", "chickens", "murgi", "murghi", "broiler", "roaster", "roasters", "hen"},
        "bn": ("মুরগি", "মুরগী", "চিকেন", "রোস্টার", "ব্রয়লার"),
        "sources": [("category", "Chicken")],
    },
    "duck": {
        "label_en": "Duck",
        "label_bn": "হাঁস",
        "en": {"duck", "ducks"},
        "bn": ("হাঁস", "হাস"),
        "sources": [("ingredient", "duck")],
    },
    "fish": {
        "label_en": "Fish",
        "label_bn": "মাছ",
        "en": {"fish", "fishes", "hilsa", "ilish", "rui", "katla", "pangas", "tilapia", "salmon", "tuna"},
        "bn": ("মাছ", "ইলিশ", "রুই", "কাতলা", "পাঙ্গাস", "তেলাপিয়া"),
        "sources": [("search", "fish"), ("category", "Seafood")],
    },
    "shrimp": {
        "label_en": "Shrimp / Prawn",
        "label_bn": "চিংড়ি",
        "en": {"shrimp", "shrimps", "prawn", "prawns", "chingri", "golda"},
        "bn": ("চিংড়ি", "গলদা", "চিংরি"),
        "sources": [("ingredient", "prawns"), ("ingredient", "king_prawns"), ("ingredient", "tiger_prawns")],
    },
    "lobster": {
        "label_en": "Lobster",
        "label_bn": "লবস্টার",
        "en": {"lobster", "lobsters"},
        "bn": ("লবস্টার", "লোবস্টার"),
        "sources": [("search", "lobster")],
        "fallback": "shrimp",
    },
    "crab": {
        "label_en": "Crab",
        "label_bn": "কাঁকড়া",
        "en": {"crab", "crabs"},
        "bn": ("কাঁকড়া", "কাকড়া"),
        "sources": [("search", "crab")],
    },
    "vegetable": {
        "label_en": "Vegetables",
        "label_bn": "সবজি",
        "en": {"veg", "vegs", "veggie", "veggies", "vegetable", "vegetables", "vegetarian", "sabzi", "shobji"},
        "bn": ("সবজি", "সব্জি", "তরকারি", "শাকসবজি"),
        "sources": [("category", "Vegetarian"), ("category", "Vegan")],
    },
    "egg": {
        "label_en": "Egg",
        "label_bn": "ডিম",
        "en": {"egg", "eggs", "dim"},
        "bn": ("ডিম",),
        "sources": [("ingredient", "eggs"), ("ingredient", "egg")],
    },
    "potato": {
        "label_en": "Potato",
        "label_bn": "আলু",
        "en": {"potato", "potatoes", "aloo", "alu"},
        "bn": ("আলু",),
        "sources": [("ingredient", "potatoes")],
    },
    "lentil": {
        "label_en": "Lentils / Dal",
        "label_bn": "ডাল",
        "en": {"lentil", "lentils", "dal", "daal", "dhal"},
        "bn": ("ডাল", "মসুর", "মুগ", "মুগডাল"),
        "sources": [("ingredient", "lentils"), ("search", "dal")],
    },
}

BN_SUFFIXES = {"", "র", "ের", "কে", "গুলো", "গুলি", "গুলোর", "টা", "টি", "ও", "য়", "য়ের", "ে", "তে", "দের"}

FILLER_EN = {
    "recipe", "recipes", "of", "for", "with", "using", "from", "show", "me", "give", "find", "search",
    "online", "web", "internet", "a", "an", "the", "some", "please", "pls", "want", "wanna", "to", "cook",
    "cooking", "make", "dish", "dishes", "meat", "item", "items", "i", "need", "ideas", "idea", "any",
    "and", "or", "can", "you", "how", "do", "let", "lets", "us", "what", "about", "food", "today",
    "people", "person", "persons", "servings", "serving", "serve", "best", "good", "tasty", "new",
    "more", "other", "only", "just", "in", "on", "my", "get", "see", "all", "which",
}

FILLER_BN = {
    "রেসিপি", "রেসিপিগুলো", "রেসিপিটি", "দাও", "দিন", "দেখাও", "দেখান", "খুঁজে", "খুজে", "দিয়ে", "জন",
    "জনের", "জন্য", "এর", "আমি", "চাই", "রান্না", "করতে", "করব", "মাংস", "মাংসের", "খাবার", "অনলাইনে",
    "ইন্টারনেটে", "ও", "এবং", "আর", "কী", "কি", "কোনো", "একটি", "আজ", "আজকে", "বলো", "বলুন",
}

FILLER_BANGLISH = {
    "amar", "kache", "ase", "ache", "achhe", "ar", "ki", "ranna", "korte", "pari", "korbo", "dao", "den",
    "diye", "dia", "ekta", "kono", "kichu", "lagbe", "chai", "ami", "khub", "bhalo", "dekhao", "khuje",
}

MINOR_INGREDIENTS = {
    "onion", "onions", "peyaj", "piyaj", "piaj", "tomato", "tomatoes", "garlic", "rosun", "ginger", "ada",
    "chili", "chilli", "lonka", "morich", "salt", "noon", "oil", "tel", "rice", "bhat", "chal",
    "পেঁয়াজ", "পেয়াজ", "পিঁয়াজ", "টমেটো", "রসুন", "আদা", "মরিচ", "লবণ", "তেল", "ভাত", "চাল",
}

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9\u0980-\u09FF]+")


def tokenize(text):
    return TOKEN_PATTERN.findall((text or "").lower())


def _bn_match(token, stem):
    return token.startswith(stem) and token[len(stem):] in BN_SUFFIXES


def match_group(token):
    for key, group in INGREDIENT_GROUPS.items():
        if token in group["en"]:
            return key
        for stem in group["bn"]:
            if _bn_match(token, stem):
                return key
    return None


def detect_ingredient_keywords(text):
    groups = []
    leftover = []
    for token in tokenize(text):
        key = match_group(token)
        if key:
            if key not in groups:
                groups.append(key)
        elif token in FILLER_EN or token in FILLER_BN or token in FILLER_BANGLISH or token in MINOR_INGREDIENTS or token.isdigit() or re.fullmatch(r"[\u09E6-\u09EF]+", token):
            continue
        else:
            leftover.append(token)
    return {"groups": groups, "leftover": leftover}


def _api(endpoint, **params):
    url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    now = time.time()
    cached = _CACHE.get(url)
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]
    data = _http_get_json(url)
    if len(_CACHE) >= CACHE_MAX_ITEMS:
        oldest = min(_CACHE, key=lambda k: _CACHE[k][0])
        _CACHE.pop(oldest, None)
    _CACHE[url] = (now, data)
    return data


def _http_get_json(url, timeout=REQUEST_TIMEOUT):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    last = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=timeout, context=_ssl_context()) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            last = OnlineSearchError(str(exc), reason=classify_error(exc), detail=f"{type(exc).__name__}: {exc}")
            if last.reason in ("ssl", "dns", "blocked"):
                break
            time.sleep(0.4)
    raise last


def check_health():
    started = time.time()
    try:
        meals = _meals(_http_get_json(f"{API_BASE}/search.php?s=chicken"))
        return {
            "ok": bool(meals),
            "reason": "ok" if meals else "empty",
            "detail": f"{len(meals)} meals returned",
            "ms": int((time.time() - started) * 1000),
            "api": API_BASE,
            "uses_certifi": certifi is not None,
        }
    except OnlineSearchError as exc:
        return {
            "ok": False,
            "reason": exc.reason,
            "detail": exc.detail,
            "ms": int((time.time() - started) * 1000),
            "api": API_BASE,
            "uses_certifi": certifi is not None,
        }


def _meals(data):
    meals = data.get("meals") if isinstance(data, dict) else None
    if not isinstance(meals, list):
        return []
    return [m for m in meals if isinstance(m, dict) and m.get("idMeal") and m.get("strMeal")]


def _summary(meal):
    thumb = meal.get("strMealThumb") or ""
    return {
        "provider": PROVIDER,
        "provider_name": PROVIDER_NAME,
        "id": str(meal["idMeal"]),
        "title": str(meal["strMeal"]).strip(),
        "thumb": thumb if thumb.startswith("https://") else "",
        "category": meal.get("strCategory") or "",
        "area": meal.get("strArea") or "",
    }


def _run_source(source):
    kind, value = source
    if kind == "category":
        return _meals(_api("filter.php", c=value))
    if kind == "ingredient":
        return _meals(_api("filter.php", i=value))
    return _meals(_api("search.php", s=value))


def _fetch_sources(sources):
    results = []
    failures = []
    with ThreadPoolExecutor(max_workers=min(3, len(sources))) as pool:
        futures = [pool.submit(_run_source, s) for s in sources]
        for future in futures:
            try:
                results.append(future.result())
            except OnlineSearchError as exc:
                failures.append(exc)
                results.append([])
    if len(failures) == len(sources):
        raise failures[0]
    return results


def _indian_ids():
    try:
        return {str(m["idMeal"]) for m in _meals(_api("filter.php", a="Indian"))}
    except OnlineSearchError:
        return set()


def _merge_unique(lists):
    seen = set()
    merged = []
    for meals in lists:
        for meal in meals:
            mid = str(meal["idMeal"])
            if mid not in seen:
                seen.add(mid)
                merged.append(meal)
    return merged


def _search_group(key):
    group = INGREDIENT_GROUPS[key]
    meals = _merge_unique(_fetch_sources(group["sources"]))
    note = None
    if not meals and group.get("fallback"):
        fallback = INGREDIENT_GROUPS[group["fallback"]]
        meals = _merge_unique(_fetch_sources(fallback["sources"]))
        if meals:
            note = f"no_{key}_showing_{group['fallback']}"
    if meals:
        indian = _indian_ids()
        meals.sort(key=lambda m: 0 if str(m["idMeal"]) in indian else 1)
    return meals, note


def search_by_groups(groups, limit=MAX_RESULTS):
    per_group = []
    notes = []
    errors = []
    for key in groups:
        try:
            meals, note = _search_group(key)
        except OnlineSearchError as exc:
            errors.append(exc)
            continue
        per_group.append(meals)
        if note:
            notes.append(note)
    if len(errors) == len(groups):
        raise errors[0]
    picked = []
    seen = set()
    index = 0
    while len(picked) < limit and any(index < len(lst) for lst in per_group):
        for lst in per_group:
            if index < len(lst):
                mid = str(lst[index]["idMeal"])
                if mid not in seen:
                    seen.add(mid)
                    picked.append(_summary(lst[index]))
                    if len(picked) >= limit:
                        break
        index += 1
    return {"items": picked, "note": notes[0] if notes else None}


def search_by_name(query, limit=MAX_RESULTS):
    tokens = [t for t in tokenize(query) if len(t) >= 4 and t not in FILLER_EN and t not in FILLER_BN]
    attempts = [" ".join(tokenize(query))] + sorted(set(tokens), key=len, reverse=True)[:2]
    attempts = [a for a in dict.fromkeys(attempts) if a]
    errors = []
    for attempt in attempts:
        try:
            meals = _meals(_api("search.php", s=attempt))
        except OnlineSearchError as exc:
            errors.append(exc)
            continue
        if meals:
            return {"items": [_summary(m) for m in meals[:limit]], "note": None, "matched_query": attempt}
    if attempts and len(errors) == len(attempts):
        raise errors[0]
    return {"items": [], "note": None, "matched_query": None}


UNIT_MAP = {
    "g": "g", "gm": "g", "gms": "g", "gram": "g", "grams": "g",
    "kg": "kg", "kilo": "kg", "kilos": "kg", "kilogram": "kg", "kilograms": "kg",
    "ml": "ml", "millilitre": "ml", "millilitres": "ml", "milliliter": "ml", "milliliters": "ml",
    "l": "l", "litre": "l", "litres": "l", "liter": "l", "liters": "l",
    "tsp": "tsp", "tsps": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "tbsp": "tbsp", "tbs": "tbsp", "tblsp": "tbsp", "tbls": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
    "cup": "cup", "cups": "cup",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
}

FRACTIONS = {"½": " 1/2", "¼": " 1/4", "¾": " 3/4", "⅓": " 1/3", "⅔": " 2/3", "⅛": " 1/8"}

MEASURE_PATTERN = re.compile(
    r"^\s*(\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?)(?:\s*(?:-|to)\s*\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)?\s*([A-Za-z]+\.?)?\s*(.*)$"
)


def _to_number(text):
    text = text.strip()
    if " " in text:
        whole, frac = text.split(None, 1)
        return float(whole) + _to_number(frac)
    if "/" in text:
        num, den = text.split("/")
        return float(num) / float(den) if float(den) else 0.0
    return float(text)


def parse_measure(measure):
    raw = (measure or "").strip()
    if not raw:
        return None, "", ""
    text = raw
    for glyph, replacement in FRACTIONS.items():
        text = text.replace(glyph, replacement)
    match = MEASURE_PATTERN.match(text)
    if not match:
        return None, "", raw
    try:
        value = _to_number(match.group(1))
    except (ValueError, ZeroDivisionError):
        return None, "", raw
    word = (match.group(2) or "").rstrip(".")
    rest = (match.group(3) or "").strip()
    unit = UNIT_MAP.get(word.lower())
    if unit:
        note = rest
    else:
        unit = ""
        note = f"{word} {rest}".strip()
    if value <= 0:
        return None, "", raw
    value = int(value) if abs(value - round(value)) < 1e-9 else round(value, 3)
    return value, unit, note


def split_steps(instructions):
    text = (instructions or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    cleaned = []
    for line in lines:
        line = re.sub(r"^(?:step\s*\d+\s*[:.\-)]*|\d+\s*[.)])\s*", "", line, flags=re.I).strip()
        if line and not re.fullmatch(r"step\s*\d+", line, flags=re.I):
            cleaned.append(line)
    if len(cleaned) <= 2:
        joined = " ".join(cleaned)
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", joined)
        cleaned = [p.strip() for p in parts if p.strip()]
    merged = []
    for part in cleaned:
        if merged and len(part) < 25:
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)
    return merged[:30]


DURATION_PATTERN = re.compile(r"(\d+)(?:\s*(?:-|to)\s*(\d+))?\s*(hours?|hrs?|minutes?|mins?)\b", re.I)


def extract_duration_minutes(text):
    match = DURATION_PATTERN.search(text or "")
    if not match:
        return None
    value = int(match.group(2) or match.group(1))
    if match.group(3).lower().startswith("h"):
        value *= 60
    return max(1, min(value, 600))


def meal_to_recipe(meal):
    meal_id = str(meal.get("idMeal"))
    title = str(meal.get("strMeal") or "").strip()
    ingredients = []
    for i in range(1, 21):
        name = (meal.get(f"strIngredient{i}") or "").strip()
        if not name:
            continue
        amount, unit, note = parse_measure(meal.get(f"strMeasure{i}"))
        item = {"name": name, "name_en": name, "amount": amount, "unit": unit}
        if note:
            item["note"] = note
        ingredients.append(item)

    steps = []
    for order, text in enumerate(split_steps(meal.get("strInstructions")), start=1):
        steps.append({
            "order": order,
            "instruction": text,
            "instruction_en": text,
            "duration_min": extract_duration_minutes(text),
            "heat": None,
        })

    thumb = meal.get("strMealThumb") or ""
    source_url = (meal.get("strSource") or "").strip()
    if not source_url.lower().startswith(("http://", "https://")):
        source_url = ""

    category = meal.get("strCategory") or ""
    area = meal.get("strArea") or ""
    return {
        "id": f"mealdb_{meal_id}",
        "dish": title,
        "dish_en": title,
        "category": " • ".join(p for p in (category, area) if p),
        "base_servings": 4,
        "prep_time_min": None,
        "cook_time_min": None,
        "total_time_min": None,
        "heat_level": None,
        "ingredients": ingredients,
        "steps": steps,
        "substitutions": [],
        "image": {
            "url": thumb if thumb.startswith("https://") else "",
            "alt": title,
            "alt_bn": title,
            "author": PROVIDER_NAME,
            "license": "online source",
        },
        "source": {
            "type": "online",
            "name": PROVIDER_NAME,
            "is_ai_generated": False,
            "source_url": source_url or None,
            "attribution": "Recipe found online via TheMealDB (community-contributed, English)",
        },
        "assumptions_en": ["The source does not state how many people this serves. 4 servings are assumed."],
        "assumptions_bn": ["উৎসে কত জনের জন্য রেসিপি তা বলা নেই। ৪ জন ধরে নেওয়া হয়েছে।"],
    }


def get_recipe(meal_id):
    if not re.fullmatch(r"\d{1,10}", str(meal_id)):
        return None
    meals = _meals(_api("lookup.php", i=str(meal_id)))
    if not meals:
        return None
    return meal_to_recipe(meals[0])


def clear_cache():
    _CACHE.clear()
