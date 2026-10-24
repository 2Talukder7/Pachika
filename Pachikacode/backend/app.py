
import os
import sys
import re
import json
import base64
import io
import time
import urllib.request
import urllib.error

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from flask import Flask, request, jsonify, send_from_directory
try:
    from flask_cors import CORS
except ImportError:
    CORS = None
from dotenv import load_dotenv

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

import recipe_engine as engine
import weather_service
import online_recipes

load_dotenv()

app = Flask(__name__)
# Make Unicode (including Bengali text and emoji) explicit in JSON responses.
app.json.ensure_ascii = False
if CORS:
    CORS(app)
else:
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

SESSIONS = {}
SESSION_TTL_SECONDS = 3600 * 4


def clean_expired_sessions():
    now = time.time()
    expired = [sid for sid, s in SESSIONS.items() if now - s.get("updated_at", now) > SESSION_TTL_SECONDS]
    for sid in expired:
        SESSIONS.pop(sid, None)


def get_or_create_session(session_id):
    clean_expired_sessions()
    if not session_id:
        session_id = f"sess_{int(time.time()*1000)}"
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "session_id": session_id,
            "current_recipe_id": None,
            "current_servings": 4,
            "last_intent": None,
            "history": [],
            "updated_at": time.time(),
        }
    else:
        SESSIONS[session_id]["updated_at"] = time.time()
    return SESSIONS[session_id]


@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/api/recipes", methods=["GET"])
def get_recipes():
    return jsonify({"recipes": engine.get_all_recipes()})


@app.route("/api/categories", methods=["GET"])
def get_categories():
    return jsonify({"categories": engine.get_categories()})


@app.route("/api/recipe/<recipe_id>", methods=["GET"])
def get_recipe_by_id(recipe_id):
    servings_str = request.args.get("servings", "4")
    try:
        servings = int(servings_str)
        if servings <= 0:
            return jsonify({"error": "Servings must be a positive integer greater than 0."}), 400
    except ValueError:
        return jsonify({"error": f"Invalid servings value '{servings_str}'. Must be an integer."}), 400

    recipe = engine.find_recipe_by_id(recipe_id)
    if not recipe:
        return jsonify({"error": f"Recipe '{recipe_id}' not found."}), 404

    scaled = engine.scale_recipe(recipe, servings)
    return jsonify(scaled)


@app.route("/api/recipe", methods=["POST"])
def get_recipe():
    body = request.get_json(force=True, silent=True) or {}
    dish = body.get("dish", "").strip()
    servings = body.get("servings", 4)

    try:
        servings = int(servings)
        if servings <= 0:
            return jsonify({"error": "Servings must be a positive integer greater than 0."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Servings must be a valid integer."}), 400

    if not dish:
        return jsonify({"error": "Please provide a dish name."}), 400

    resolved = engine.resolve_dish_query(dish)
    if not resolved:
        return jsonify({"error": f"No recipe found for '{dish}'."}), 404

    if isinstance(resolved, dict) and resolved.get("is_ambiguous"):
        return jsonify({
            "is_ambiguous": True,
            "message": f"'{dish}' নামে একাধিক সুস্বাদু খাবার রয়েছে। আপনি কোনটি চান?",
            "options": [
                {"id": o["id"], "dish": o["dish"], "dish_en": o["dish_en"]}
                for o in resolved["options"]
            ]
        }), 200

    scaled = engine.scale_recipe(resolved, servings)
    return jsonify(scaled)


@app.route("/api/recipe/scale", methods=["POST"])
def scale_recipe_endpoint():
    body = request.get_json(force=True, silent=True) or {}
    recipe_id = body.get("id", "")
    servings = body.get("servings")

    if not recipe_id:
        return jsonify({"error": "Missing 'id' parameter."}), 400

    try:
        servings = int(servings)
        if servings <= 0:
            return jsonify({"error": "Servings must be a positive integer greater than 0."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Servings must be a valid integer greater than 0."}), 400

    recipe = engine.find_recipe_by_id(recipe_id)
    if not recipe:
        return jsonify({"error": f"Recipe '{recipe_id}' not found."}), 404

    try:
        scaled = engine.scale_recipe(recipe, servings)
        return jsonify(scaled)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/suggest", methods=["POST"])
def suggest_dishes():
    body = request.get_json(force=True, silent=True) or {}
    ingredients = body.get("ingredients", [])

    if isinstance(ingredients, str):
        ingredients = [i.strip() for i in re.split(r"[,、\n]| and | ও | এবং | আর ", ingredients) if i.strip()]

    if not ingredients:
        return jsonify({"error": "Provide at least one ingredient."}), 400

    results = engine.suggest_by_ingredients(ingredients)
    return jsonify({
        "suggestions": [
            {
                "id": r["recipe"]["id"],
                "dish": r["recipe"]["dish"],
                "dish_en": r["recipe"]["dish_en"],
                "category": r["recipe"].get("category", "curry"),
                "matched_count": r["matched"],
                "matched_items": r["matched_items"],
                "missing": r["missing"],
                "image": r["recipe"].get("image", {}),
            }
            for r in results
        ]
    })


@app.route("/api/weather/recommendations", methods=["GET", "POST"])
def weather_recommendations():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        lat = data.get("lat")
        lon = data.get("lon")
        city = data.get("city")
    else:
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        city = request.args.get("city")

    result = weather_service.get_weather_recommendations(lat=lat, lon=lon, city=city, recipe_engine=engine)
    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200


def pair(bn, en):
    return {"reply": bn, "reply_en": en}


def get_session_recipe(session):
    rid = session.get("current_recipe_id")
    if not rid:
        return None
    stored = session.get("current_recipe")
    if isinstance(stored, dict) and stored.get("id") == rid:
        return stored
    return engine.find_recipe_by_id(rid)


LOCAL_TERMS = {
    "beef": ["beef", "গরু", "বিফ"],
    "mutton": ["mutton", "goat", "lamb", "খাসি", "ছাগল", "পাঁঠা", "মাটন"],
    "chicken": ["chicken", "মুরগি", "মুরগী", "চিকেন"],
    "duck": ["duck", "হাঁস"],
    "fish": ["fish", "hilsa", "ilish", "rui", "katla", "মাছ", "ইলিশ", "রুই", "কাতলা"],
    "shrimp": ["prawn", "shrimp", "chingri", "চিংড়ি"],
    "lobster": ["lobster", "লবস্টার", "গলদা"],
    "crab": ["crab", "কাঁকড়া"],
    "egg": ["egg", "ডিম"],
    "potato": ["potato", "aloo", "আলু"],
    "lentil": ["dal", "lentil", "ডাল", "মসুর"],
    "vegetable": ["vegetable", "brinjal", "eggplant", "gourd", "cauliflower", "cabbage", "pumpkin", "begun", "সবজি", "বেগুন"],
}

LOCAL_CATEGORIES = {"vegetable": {"vegetable", "bhorta"}}

SIMILAR_GROUPS = {
    "lobster": ["shrimp", "fish"],
    "crab": ["shrimp", "fish"],
    "shrimp": ["fish"],
    "fish": ["shrimp"],
    "duck": ["chicken"],
    "mutton": ["beef"],
    "beef": ["mutton"],
}


def _term_in(text, term):
    term = term.lower()
    if term.isascii():
        return re.search(r"(?<![a-z])" + re.escape(term) + r"s?(?![a-z])", text) is not None
    return term in text


def ingredient_score(recipe, group):
    terms = LOCAL_TERMS.get(group, [])
    name = f"{recipe['dish_en']} {recipe['dish']}".lower()
    if any(_term_in(name, t) for t in terms):
        return 5
    best = 0
    for index, ing in enumerate(recipe.get("ingredients", [])):
        text = f"{ing.get('name_en', '')} {ing.get('name', '')}".lower()
        if any(_term_in(text, t) for t in terms):
            best = max(best, 3 if index < 2 else 1)
    if not best and recipe.get("category") in LOCAL_CATEGORIES.get(group, ()):
        best = 2
    return best


def _rank_local(group_keys):
    scored = []
    for recipe in engine.load_recipes():
        if recipe.get("category") == "drink":
            continue
        scores = [ingredient_score(recipe, g) for g in group_keys]
        hits = sum(1 for s in scores if s)
        if hits:
            scored.append((hits, sum(scores), recipe))
    scored.sort(key=lambda item: (-item[0], -item[1], item[2]["dish_en"]))
    return [recipe for _, _, recipe in scored]


def similar_local_dishes(groups, limit=6):
    exact = _rank_local(groups)
    if exact:
        return {"dishes": exact[:limit], "similar_of": []}
    similar = []
    for g in groups:
        for s in SIMILAR_GROUPS.get(g, []):
            if s not in similar and s not in groups:
                similar.append(s)
    return {"dishes": _rank_local(similar)[:limit] if similar else [], "similar_of": similar}


def local_option(recipe):
    return {"id": recipe["id"], "dish": recipe["dish"], "dish_en": recipe["dish_en"]}


def group_labels(keys):
    bn = " ও ".join(online_recipes.INGREDIENT_GROUPS[g]["label_bn"] for g in keys)
    en = ", ".join(online_recipes.INGREDIENT_GROUPS[g]["label_en"] for g in keys)
    return bn, en


def resolved_fits_query(recipe, dish_query):
    tokens = [t for t in re.split(r"[\s,।.!?;:]+", dish_query.lower()) if t]
    for t in tokens:
        if t in RELATED_DISH_HINTS and recipe["id"] not in RELATED_DISH_HINTS[t]:
            return False
    groups = online_recipes.detect_ingredient_keywords(dish_query)["groups"]
    return all(ingredient_score(recipe, g) > 0 for g in groups)


SHOW_LOCAL_WITH_ONLINE = os.getenv("PACHIKA_SHOW_LOCAL_WITH_ONLINE", "0") == "1"

ONLINE_REASON_TEXT = {
    "timeout": ("সংযোগে অনেক সময় লাগছে", "the connection timed out"),
    "ssl": ("নিরাপত্তা সার্টিফিকেট যাচাই ব্যর্থ", "the secure connection (SSL certificate) failed"),
    "dns": ("ইন্টারনেট বা ডিএনএস সংযোগ নেই", "no internet or DNS connection"),
    "blocked": ("সার্ভিসটি অনুরোধ আটকে দিয়েছে", "the service blocked or rate-limited the request"),
    "http": ("সার্ভিসের সার্ভারে সমস্যা", "the service had a server error"),
    "network": ("নেটওয়ার্ক সংযোগে সমস্যা", "a network problem"),
}


def reason_note(reason):
    bn, en = ONLINE_REASON_TEXT.get(reason, ONLINE_REASON_TEXT["network"])
    return f" ({bn})", f" ({en})"


def online_lookup(groups=None, name_query=None):
    try:
        if groups:
            found = online_recipes.search_by_groups(groups)
        else:
            found = online_recipes.search_by_name(name_query)
    except online_recipes.OnlineSearchError as exc:
        print(f"Online search unavailable [{exc.reason}]: {exc.detail}")
        return {"status": "unavailable", "items": [], "note": None, "reason": exc.reason}
    items = found.get("items") or []
    return {"status": "ok" if items else "empty", "items": items, "note": found.get("note")}


def online_fallback_note(note):
    if note and note.startswith("no_lobster"):
        return (
            "\n\n*(লবস্টারের রেসিপি পাওয়া যায়নি, তাই চিংড়ির রেসিপি দেখানো হলো।)*",
            "\n\n*(No lobster recipes were found, so prawn recipes are shown instead.)*",
        )
    return "", ""


ONLINE_LANGUAGE_NOTE_BN = "\n\n*(অনলাইন রেসিপিগুলো ইংরেজিতে এবং বেশিরভাগই আন্তর্জাতিক ধাঁচের।)*"
ONLINE_LANGUAGE_NOTE_EN = "\n\n*(Online recipes are in English and mostly international in style.)*"


@app.route("/api/online/health", methods=["GET"])
def online_health():
    return jsonify(online_recipes.check_health())


@app.route("/api/online/recipe", methods=["GET"])
def online_recipe():
    provider = request.args.get("provider", online_recipes.PROVIDER)
    meal_id = request.args.get("id", "")
    if provider != online_recipes.PROVIDER or not re.fullmatch(r"\d{1,10}", meal_id):
        return jsonify({
            "error": "Invalid online recipe request.",
            "error_bn": "অনলাইন রেসিপির অনুরোধটি সঠিক নয়।",
        }), 400

    try:
        recipe = online_recipes.get_recipe(meal_id)
    except online_recipes.OnlineSearchError as exc:
        print("Online recipe fetch failed:", exc)
        return jsonify({
            "error": "The online recipe service could not be reached. Please check your internet connection and try again.",
            "error_bn": "অনলাইন রেসিপি সার্ভিসে সংযোগ করা যায়নি। ইন্টারনেট সংযোগ দেখে আবার চেষ্টা করুন।",
        }), 502

    if not recipe:
        return jsonify({
            "error": "That online recipe was not found.",
            "error_bn": "এই অনলাইন রেসিপিটি পাওয়া যায়নি।",
        }), 404

    session = get_or_create_session(request.args.get("session_id"))
    servings = session.pop("pending_servings", None)
    if not isinstance(servings, int) or not 1 <= servings <= 50:
        servings = recipe["base_servings"]

    session["current_recipe"] = recipe
    session["current_recipe_id"] = recipe["id"]
    session["current_servings"] = servings
    shown = engine.scale_recipe(recipe, servings) if servings != recipe["base_servings"] else recipe

    return jsonify({
        **pair(
            f"এই নিন ইন্টারনেট থেকে পাওয়া **{shown['dish']}** রেসিপি ({shown['base_servings']} জনের জন্য)। উৎস: {online_recipes.PROVIDER_NAME}।",
            f"Here is the **{shown['dish_en']}** recipe found online ({shown['base_servings']} servings). Source: {online_recipes.PROVIDER_NAME}.",
        ),
        "recipe": shown,
        "session_id": session["session_id"],
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json(force=True, silent=True) or {}
    message = body.get("message", "").strip()
    selector_servings = body.get("servings", 4)
    session_id = body.get("session_id")

    try:
        selector_servings = int(selector_servings)
        if selector_servings <= 0:
            selector_servings = 4
    except (ValueError, TypeError):
        selector_servings = 4

    session = get_or_create_session(session_id)
    sid = session["session_id"]

    if not message:
        return jsonify({
            **pair(
                "দয়া করে আপনার প্রশ্ন লিখুন বা কোনো খাবারের নাম বলুন।",
                "Please type a question or name a dish.",
            ),
            "session_id": sid,
        })

    intent = parse_intent(message, default_servings=selector_servings, session=session)

    if intent["type"] == "ingredient_online_search":
        groups = intent["groups"]
        if intent.get("pending_servings"):
            session["pending_servings"] = intent["pending_servings"]
        labels_bn = " ও ".join(online_recipes.INGREDIENT_GROUPS[g]["label_bn"] for g in groups)
        labels_en = ", ".join(online_recipes.INGREDIENT_GROUPS[g]["label_en"] for g in groups)
        found = online_lookup(groups=groups)
        fb_bn, fb_en = online_fallback_note(found["note"])
        similar = similar_local_dishes(groups)
        local = [local_option(r) for r in similar["dishes"]]

        if found["status"] == "ok":
            show_local = bool(local) and SHOW_LOCAL_WITH_ONLINE
            also_bn = " সাথে পাচিকার নিজস্ব রেসিপিও দেওয়া হলো।" if show_local else ""
            also_en = " Pachika's own recipes are listed too." if show_local else ""
            reply_bn = f"**{labels_bn}** দিয়ে ইন্টারনেট (TheMealDB) থেকে রেসিপি পেয়েছি।{also_bn} যেকোনো একটি বেছে নিন।{fb_bn}{ONLINE_LANGUAGE_NOTE_BN}"
            reply_en = f"I searched online first and found recipes with **{labels_en}** (TheMealDB).{also_en} Pick any one.{fb_en}{ONLINE_LANGUAGE_NOTE_EN}"
        else:
            show_local = bool(local)
            if found["status"] == "unavailable":
                why_bn, why_en = reason_note(found.get("reason"))
                head_bn = f"**{labels_bn}**-এর জন্য অনলাইন সার্চ এখন কাজ করছে না{why_bn}।"
                head_en = f"Online search for **{labels_en}** is not working right now{why_en}."
            else:
                head_bn = f"**{labels_bn}** দিয়ে অনলাইনে কোনো রেসিপি পাওয়া যায়নি।"
                head_en = f"No recipes were found online for **{labels_en}**."
            if show_local and similar["similar_of"]:
                sim_bn, sim_en = group_labels(similar["similar_of"])
                reply_bn = f"{head_bn} পাচিকার সংগ্রহে **{labels_bn}**-এর রেসিপি নেই, তবে **{sim_bn}** দিয়ে তৈরি এই কাছাকাছি পদগুলো দেখতে পারেন:"
                reply_en = f"{head_en} Pachika has no **{labels_en}** dish of its own, but these similar dishes use **{sim_en}**:"
            elif show_local:
                reply_bn = f"{head_bn} তাই **{labels_bn}** দিয়ে তৈরি পাচিকার নিজস্ব পদগুলো দেখাচ্ছি:"
                reply_en = f"{head_en} So here are Pachika's own dishes made with **{labels_en}**:"
            else:
                reply_bn = f"{head_bn} ইন্টারনেট সংযোগ দেখে আবার চেষ্টা করুন অথবা অন্য কোনো নাম লিখুন।"
                reply_en = f"{head_en} Check your internet connection and try again, or type another name."

        payload = {**pair(reply_bn, reply_en), "session_id": sid}
        if show_local:
            payload["clarification_options"] = local
        if found["items"]:
            payload["online_results"] = found["items"]
        payload["online_status"] = found["status"]
        return jsonify(payload)

    if intent["type"] == "ambiguous_dish":
        if intent.get("pending_servings"):
            session["pending_servings"] = intent["pending_servings"]
        options = intent["options"]
        reply_bn = (
            f"**{intent['term_bn']} ({intent['term_en']})** দিয়ে আমাদের একাধিক জনপ্রিয় ঐতিহ্যবাহী রেসিপি রয়েছে:\n" +
            "\n".join([f"• **{o['dish']}** ({o['dish_en']})" for o in options]) +
            "\n\nআপনি কোনটি তৈরি করতে চান? যেকোনো একটি বেছে নিন।"
        )
        reply_en = (
            f"We have several traditional recipes with **{intent['term_en']}**:\n" +
            "\n".join([f"• **{o['dish_en']}** ({o['dish']})" for o in options]) +
            "\n\nWhich one would you like to make? Pick any one."
        )
        return jsonify({
            **pair(reply_bn, reply_en),
            "session_id": sid,
            "clarification_options": [
                {"id": o["id"], "dish": o["dish"], "dish_en": o["dish_en"]}
                for o in options
            ]
        })

    if intent["type"] == "recipe_request":
        dish_query = intent["dish"]
        servings = intent["servings"]
        resolved = engine.resolve_dish_query(dish_query)

        if isinstance(resolved, dict) and resolved.get("is_ambiguous"):
            if intent.get("servings_explicit"):
                session["pending_servings"] = servings
            options = resolved["options"]
            reply_bn = (
                f"**{resolved['term_bn']}** দিয়ে আমাদের একাধিক সুস্বাদু পদ রয়েছে:\n" +
                "\n".join([f"• **{o['dish']}** ({o['dish_en']})" for o in options]) +
                "\n\nআপনি কোনটি রান্না করতে চান?"
            )
            reply_en = (
                f"We have several tasty dishes with **{resolved.get('term_en', resolved['term_bn'])}**:\n" +
                "\n".join([f"• **{o['dish_en']}** ({o['dish']})" for o in options]) +
                "\n\nWhich one would you like to cook?"
            )
            return jsonify({
                **pair(reply_bn, reply_en),
                "session_id": sid,
                "clarification_options": [
                    {"id": o["id"], "dish": o["dish"], "dish_en": o["dish_en"]}
                    for o in options
                ]
            })

        if resolved and not resolved_fits_query(resolved, dish_query):
            resolved = None

        if resolved:
            session.pop("pending_servings", None)
            scaled = engine.scale_recipe(resolved, servings)
            session["current_recipe_id"] = scaled["id"]
            session["current_servings"] = servings

            return jsonify({
                **pair(
                    f"এই নিন ঐতিহ্যবাহী **{scaled['dish']}** রেসিপি ({scaled['base_servings']} জনের জন্য)। "
                    f"উপকরণ মেপে প্রস্তুত করে রান্নার ধাপগুলো অনুসরণ করুন। শুভ রান্না!",
                    f"Here is the traditional **{scaled['dish_en']}** recipe (for {scaled['base_servings']} servings). "
                    f"Measure the ingredients and follow the steps. Happy cooking!",
                ),
                "recipe": scaled,
                "session_id": sid,
            })

        online_found = online_lookup(name_query=dish_query)
        related_hint = None
        if online_found["status"] != "ok":
            for token in re.split(r"[\s,।.!?;:]+", dish_query.lower()):
                if token in RELATED_ONLINE_HINTS:
                    related_hint = RELATED_ONLINE_HINTS[token]
                    break
            if related_hint:
                hinted = online_lookup(name_query=related_hint)
                if hinted["status"] == "ok":
                    online_found = hinted
                else:
                    related_hint = None
        if online_found["status"] == "ok":
            if intent.get("servings_explicit"):
                session["pending_servings"] = servings
            if related_hint:
                reply_bn = f"'{dish_query}' ঠিক এই নামে পাইনি, তবে কাছাকাছি '{related_hint}' রেসিপি ইন্টারনেট (TheMealDB) থেকে পেয়েছি। যেকোনো একটি বেছে নিন।{ONLINE_LANGUAGE_NOTE_BN}"
                reply_en = f"I couldn't find '{dish_query}' by that exact name, but here are '{related_hint}' recipes found online (TheMealDB), the closest match. Pick any one.{ONLINE_LANGUAGE_NOTE_EN}"
            else:
                reply_bn = f"'{dish_query}' আমাদের সংগ্রহে নেই, তবে ইন্টারনেট (TheMealDB) থেকে এই রেসিপিগুলো পেয়েছি। যেকোনো একটি বেছে নিন।{ONLINE_LANGUAGE_NOTE_BN}"
                reply_en = f"'{dish_query}' is not in our collection, but I found these recipes online (TheMealDB). Pick any one.{ONLINE_LANGUAGE_NOTE_EN}"
            payload = {
                **pair(reply_bn, reply_en),
                "session_id": sid,
                "online_results": online_found["items"],
                "online_status": "ok",
            }
            close_local = closest_dishes(dish_query) if (related_hint and SHOW_LOCAL_WITH_ONLINE) else []
            if close_local:
                payload["clarification_options"] = [
                    {"id": r["id"], "dish": r["dish"], "dish_en": r["dish_en"]} for r in close_local
                ]
            return jsonify(payload)
        online_down = online_found["status"] == "unavailable"

        if GEMINI_API_KEY:
            ai_recipe = try_gemini_recipe_generation(dish_query, servings)
            if ai_recipe:
                session["current_recipe"] = ai_recipe
                session["current_recipe_id"] = ai_recipe["id"]
                session["current_servings"] = servings
                return jsonify({
                    **pair(
                        f"আমাদের লোকাল ক্যাটালগে না থাকায় গুগল জেমিনাই (Gemini AI) দিয়ে "
                        f"**{ai_recipe['dish']}** ({servings} জন)-এর বিশেষ রেসিপি প্রস্তুত করা হলো।",
                        f"This dish is not in our local catalog, so a recipe for "
                        f"**{ai_recipe.get('dish_en', ai_recipe['dish'])}** ({servings} servings) was generated with Google Gemini AI.",
                    ),
                    "recipe": ai_recipe,
                    "session_id": sid,
                })

        if intent.get("servings_explicit"):
            session["pending_servings"] = servings
        query_groups = online_recipes.detect_ingredient_keywords(dish_query)["groups"]
        similar = similar_local_dishes(query_groups) if query_groups else {"dishes": [], "similar_of": []}
        matches = []
        for token in re.split(r"[\s,।.!?;:]+", dish_query.lower()):
            for rid in RELATED_DISH_HINTS.get(token, []):
                hinted = engine.find_recipe_by_id(rid)
                if hinted and hinted not in matches:
                    matches.append(hinted)
        for r in similar["dishes"]:
            if r not in matches and len(matches) < 6:
                matches.append(r)
        if not matches:
            matches = closest_dishes(dish_query)
        if matches and similar["similar_of"]:
            sim_bn, sim_en = group_labels(similar["similar_of"])
            sugg_bn = f" পাচিকার সংগ্রহে এটি নেই, তবে **{sim_bn}** দিয়ে তৈরি এই কাছাকাছি পদগুলো দেখতে পারেন:"
            sugg_en = f" Pachika doesn't have it, but these similar dishes use **{sim_en}**:"
        elif matches:
            sugg_bn = " তবে পাচিকার সংগ্রহ থেকে এই কাছাকাছি পদগুলো দেখতে পারেন:"
            sugg_en = " But these similar dishes from Pachika's collection may help:"
        else:
            sugg_bn = sugg_en = ""

        note_bn = note_en = ""
        if online_down:
            why_bn, why_en = reason_note(online_found.get("reason"))
            note_bn += f"\n\n*(অনলাইন সার্চ এখন কাজ করছে না{why_bn} — ইন্টারনেট সংযোগ দেখে আবার চেষ্টা করুন।)*"
            note_en += f"\n\n*(Online search is not working right now{why_en}. Check your internet connection and try again.)*"

        return jsonify({
            **pair(
                f"দুঃখিত, আমি '{dish_query}' রেসিপি খুঁজে পাইনি।{note_bn}" + (f"\n\n{sugg_bn.strip()}" if sugg_bn else ""),
                f"Sorry, I couldn't find a recipe for '{dish_query}'.{note_en}" + (f"\n\n{sugg_en.strip()}" if sugg_en else ""),
            ),
            "session_id": sid,
            "clarification_options": [local_option(r) for r in matches],
        })

    if intent["type"] == "followup_scale":
        active_id = session.get("current_recipe_id")
        if not active_id:
            return jsonify({
                **pair(
                    "আপনি বর্তমানে কোন খাবারের পরিমাণ পরিবর্তন করতে চান তা জানান (যেমন: '৪ জনের জন্য খিচুড়ি')।",
                    "Tell me which dish you want to rescale (for example: 'khichuri for 4 people').",
                ),
                "session_id": sid,
            })
        recipe = get_session_recipe(session)
        if not recipe:
            return jsonify({
                **pair(
                    "পূর্ববর্তী রেসিপিটি পাওয়া যায়নি। আবার খাবারের নাম বলুন।",
                    "I couldn't find the previous recipe. Please name the dish again.",
                ),
                "session_id": sid,
            })

        new_servings = intent["servings"]
        scaled = engine.scale_recipe(recipe, new_servings)
        session["current_servings"] = new_servings

        return jsonify({
            **pair(
                f"**{scaled['dish']}** রেসিপিটি এখন **{new_servings} জনের জন্য** নতুন পরিমাপে সমন্বয় করা হলো:",
                f"The **{scaled['dish_en']}** recipe is now adjusted for **{new_servings} servings**:",
            ),
            "recipe": scaled,
            "session_id": sid,
        })

    if intent["type"] == "followup_substitution":
        active_id = session.get("current_recipe_id")
        active_recipe = get_session_recipe(session)
        target_ing = intent.get("ingredient")

        sub = engine.get_recipe_substitutions(active_recipe or {}, target_ing)
        if sub and isinstance(sub, dict):
            return jsonify({
                **pair(
                    f"💡 **{sub.get('ingredient_bn', target_ing)}-এর বিকল্প:**\n"
                    f"আপনি **{sub.get('substitute_bn', sub.get('substitute'))}** ব্যবহার করতে পারেন।\n"
                    f"• *স্বাদের প্রভাব:* {sub.get('impact_bn', sub.get('impact'))}",
                    f"💡 **Substitute for {sub.get('ingredient', target_ing)}:**\n"
                    f"You can use **{sub.get('substitute', sub.get('substitute_bn'))}**.\n"
                    f"• *Effect on the dish:* {sub.get('impact', sub.get('impact_bn'))}",
                ),
                "session_id": sid,
            })
        elif sub and isinstance(sub, list) and len(sub) > 0:
            lines_bn = [f"• **{s['ingredient_bn']}**: {s['substitute_bn']} ({s['impact_bn']})" for s in sub]
            lines_en = [f"• **{s.get('ingredient', s['ingredient_bn'])}**: {s.get('substitute', s['substitute_bn'])} ({s.get('impact', s['impact_bn'])})" for s in sub]
            return jsonify({
                **pair(
                    "💡 **এই রেসিপির কার্যকর বিকল্প উপকরণ:**\n" + "\n".join(lines_bn),
                    "💡 **Useful substitutes for this recipe:**\n" + "\n".join(lines_en),
                ),
                "session_id": sid,
            })
        else:
            return jsonify({
                **pair(
                    f"'{target_ing or 'এই উপকরণ'}' না থাকলে রান্নার মূল স্বাদে পরিবর্তন আসতে পারে। সম্ভব হলে নিকটস্থ বাজার থেকে সংগ্রহ করা ভালো।",
                    f"Without '{target_ing or 'this ingredient'}' the core flavour may change. If possible, get it from your nearest market.",
                ),
                "session_id": sid,
            })

    if intent["type"] == "followup_ingredient_query":
        active_id = session.get("current_recipe_id")
        if active_id:
            recipe = get_session_recipe(session)
            if recipe:
                curr_s = session.get("current_servings", 4)
                scaled = engine.scale_recipe(recipe, curr_s)
                raw_ing = intent.get("ingredient", "").strip().lower()
                clean_target = re.sub(r"[\?\।\.,!\s]+", " ", raw_ing).strip()
                matched_ing = [
                    i for i in scaled["ingredients"]
                    if clean_target in i["name_en"].lower() or clean_target in i["name"].lower()
                    or any(w in i["name"].lower() or w in i["name_en"].lower() for w in clean_target.split() if len(w) > 1)
                ]
                if matched_ing:
                    i = matched_ing[0]
                    return jsonify({
                        **pair(
                            f"**{scaled['dish']}**-এ {curr_s} জনের জন্য **{i['amount']} {i['unit']} {i['name']}** লাগবে।",
                            f"**{scaled['dish_en']}** needs **{i['amount']} {i['unit']} {i['name_en']}** for {curr_s} servings.",
                        ),
                        "session_id": sid,
                    })
                else:
                    return jsonify({
                        **pair(
                            f"**{scaled['dish']}** রেসিপিতে '{clean_target}' উপকরণের নির্দিষ্ট মাপ উল্লেখ নেই। সাধারণত স্বাদমতো লবণ ও মসলা ব্যবহার করা হয়।",
                            f"The **{scaled['dish_en']}** recipe has no fixed amount for '{clean_target}'. Salt and spices are usually added to taste.",
                        ),
                        "session_id": sid,
                    })

    if intent["type"] == "ingredient_suggestion":
        results = engine.suggest_by_ingredients(intent["ingredients"])
        if not results:
            return jsonify({
                **pair(
                    "আপনার দেওয়া উপকরণ দিয়ে সরাসরি কোনো মিল পাওয়া যায়নি। ডিম, আলু, ডাল বা পেঁয়াজের মতো উপাদান উল্লেখ করে দেখতে পারেন।",
                    "I couldn't find a direct match for those ingredients. Try naming things like egg, potato, lentils or onion.",
                ),
                "session_id": sid,
            })

        top = results[0]["recipe"]
        scaled_top = engine.scale_recipe(top, selector_servings)
        session["current_recipe_id"] = scaled_top["id"]
        session["current_servings"] = selector_servings

        names_bn = [f"**{r['recipe']['dish']}**" for r in results[:3]]
        names_en = [f"**{r['recipe']['dish_en']}**" for r in results[:3]]
        extra_groups = online_recipes.detect_ingredient_keywords(" ".join(intent["ingredients"]))["groups"]
        extra = online_lookup(groups=extra_groups) if extra_groups else {"items": []}
        extra_bn = "\n\nইন্টারনেট (TheMealDB) থেকে আরও রেসিপি নিচে দেওয়া হলো।" if extra["items"] else ""
        extra_en = "\n\nMore recipes from the internet (TheMealDB) are listed below." if extra["items"] else ""
        return jsonify({
            **pair(
                f"আপনার উপকরণ দিয়ে আপনি {', '.join(names_bn)} রান্না করতে পারেন। "
                f"নিচে সবচেয়ে মানানসই **{scaled_top['dish']}**-এর পূর্ণাঙ্গ রেসিপি দেওয়া হলো:{extra_bn}",
                f"With your ingredients you can cook {', '.join(names_en)}. "
                f"Here is the full recipe for the best match, **{scaled_top['dish_en']}**:{extra_en}",
            ),
            "recipe": scaled_top,
            "session_id": sid,
            **({"online_results": extra["items"]} if extra["items"] else {}),
            "suggestions": [
                {
                    "id": r["recipe"]["id"],
                    "dish": r["recipe"]["dish"],
                    "dish_en": r["recipe"]["dish_en"],
                    "matched": r["matched"],
                }
                for r in results[:4]
            ],
        })

    if intent["type"] == "cooking_tip":
        return jsonify({**pair(intent["reply"], intent["reply_en"]), "session_id": sid})

    if intent["type"] == "greeting":
        return jsonify({
            **pair(
                "আমি পাচিকা, আপনার রান্নার সঙ্গী। আজ আপনি কী রান্না করতে চান? কোনো খাবারের নাম বলুন অথবা ঘরে কী কী উপকরণ আছে জানান।",
                "I'm Pachika, your cooking companion. What would you like to cook today? Name a dish or tell me which ingredients you have.",
            ),
            "session_id": sid,
        })

    if intent["type"] == "help":
        return jsonify({
            **pair(
                "👩‍🍳 **আমি পাচিকা — আপনার খাঁটি বাঙালি রান্নার সহকারী!**\n\n"
                "আমি কীভাবে আপনাকে সাহায্য করতে পারি:\n"
                "• **রেসিপি ও স্কেলিং**: যেমন লিখুন '৪ জনের জন্য খিচুড়ি' বা 'পোলাও রেসিপি'।\n"
                "• **উপকরণ দিয়ে খোঁজ**: ফ্রিজে যা আছে লিখুন ।\n"
                "• **বিকল্প উপকরণ**: 'টক দই না থাকলে কী দেব?'\n"
                "• **আজকের সুপারিশ**: ওপরের 'আজকের সুপারিশ' ট্যাবে গিয়ে আজকের আবহাওয়ায় মানানসই খাবারের তালিকা দেখুন।\n"
                "• **টাইমার ও চেকলিস্ট**: রেসিপি কার্ডের টাইমার দিয়ে প্রয়োজনীয় ধাপ ট্র্যাক করুন।",
                "👩‍🍳 **I'm Pachika — your authentic Bengali cooking assistant!**\n\n"
                "Here is how I can help:\n"
                "• **Recipes & scaling**: for example 'khichuri for 4 people' or 'pulao recipe'.\n"
                "• **Cook from what you have**: tell me the ingredients you have.\n"
                "• **Substitutes**: 'what can I use if I have no yogurt?'\n"
                "• **Today's Recommendation**: open the 'Today's Recommendation' tab for dishes that suit today's weather.\n"
                "• **Timers & checklist**: use the recipe card timers to track the steps that need waiting.",
            ),
            "session_id": sid,
        })

    if intent["type"] == "new_session":
        session["current_recipe_id"] = None
        session["current_servings"] = 4
        return jsonify({
            **pair(
                "নতুন রান্নার আলাপ শুরু করা হলো! আপনি কোন খাবারের রেসিপি দেখতে চান?",
                "A new cooking chat has started! Which dish would you like a recipe for?",
            ),
            "session_id": sid,
        })

    return jsonify({
        **pair(
            "আমি বুঝতে একটু অসুবিধা হলো। কোনো খাবারের নাম বলুন (যেমন: 'খিচুড়ি', 'মুরগির মাংস ভুনা', 'পোলাও'), "
            "অথবা আপনার কাছে কী কী উপকরণ আছে বলুন (যেমন: 'ডিম ও আলু আছে')। কত জনের জন্য রাঁধবেন তাও জানাতে পারেন!",
            "I had trouble understanding that. Name a dish (for example 'khichuri', 'chicken bhuna', 'pulao'), "
            "or tell me what ingredients you have (for example 'I have eggs and potatoes'). You can also say how many people you're cooking for!",
        ),
        "session_id": sid,
    })


@app.route("/api/speak", methods=["POST"])
def speak():
    body = request.get_json(force=True, silent=True) or {}
    text = body.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if GOOGLE_TTS_API_KEY:
        try:
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_API_KEY}"
            payload = json.dumps({
                "input": {"text": text},
                "voice": {"languageCode": "bn-IN", "ssmlGender": "FEMALE"},
                "audioConfig": {"audioEncoding": "MP3"}
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as response:
                result = json.loads(response.read().decode("utf-8"))
                if result.get("audioContent"):
                    return jsonify({"audio": result.get("audioContent"), "format": "mp3", "source": "google_cloud"})
        except Exception as e:
            print("Google TTS error:", e)

    if HAS_GTTS:
        try:
            clean_text = re.sub(r"[\*#_•`]", "", text)
            clean_text = clean_text[:400].strip()
            if clean_text:
                tts = gTTS(text=clean_text, lang="bn")
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                b64_audio = base64.b64encode(fp.read()).decode("utf-8")
                return jsonify({
                    "audio": b64_audio,
                    "format": "mp3",
                    "source": "gtts"
                })
        except Exception as e:
            print("gTTS error:", e)

    return jsonify({
        "fallback": "web_speech",
        "lang": "bn-BD",
        "text": text,
        "message": "Use client Web Speech API"
    })


BENGALI_NUM_MAP = {
    "০": 0, "১": 1, "২": 2, "৩": 3, "৪": 4, "৫": 5,
    "৬": 6, "৭": 7, "৮": 8, "৯": 9, "১০": 10,
    "শূন্য": 0, "শূণ্য": 0, "এক": 1, "দুই": 2, "তিন": 3, "চার": 4, "পাঁচ": 5,
    "ছয়": 6, "ছয়": 6, "সাত": 7, "আট": 8, "নয়": 9, "নয়": 9, "দশ": 10,
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

COOKING_TIPS = {
    "কষানো": (
        "💡 **কষানোর আসল কৌশল**: মাঝারি আঁচে মসলা ও মাংস ভালোভাবে ভাজুন। "
        "যতক্ষণ না মসলা থেকে তেল চকচকে হয়ে উপরে ভেসে ওঠে এবং কাঁচা গন্ধ দূর হয়, "
        "ততক্ষণ অল্প অল্প করে গরম পানি ছিটিয়ে নাড়তে থাকুন। এটাই মাংসের অতুলনীয় স্বাদের রহস্য।",
        "💡 **The real technique of kosha (slow frying)**: fry the spices and meat on medium heat. "
        "Keep stirring, sprinkling a little hot water at a time, until oil separates and floats on top and the raw smell is gone. "
        "That is the secret of deeply flavoured meat.",
    ),
    "মাংস নরম": (
        "💡 **মাংস নরম ও তুলতুলে করার উপায়**: মাংস রান্নার আগে সামান্য টক দই, পেঁপে বাটা বা "
        "লেবুর রস মাখিয়ে ২০-৩০ মিনিট রাখুন। ভুনা বা ঝোলের সময় ফুটন্ত গরম পানি ব্যবহার করবেন, "
        "ঠাণ্ডা পানি দিলে মাংস শক্ত হয়ে যায়।",
        "💡 **How to make meat soft and tender**: marinate the meat with a little sour yogurt, raw papaya paste or "
        "lemon juice for 20-30 minutes before cooking. Use boiling hot water for bhuna or curry; cold water makes meat tough.",
    ),
    "হাঁসের মাংস": (
        "💡 **হাঁসের মাংসের গন্ধ দূর করার টিপস**: মাংস পরিষ্কারের পর সামান্য লেবুর রস ও "
        "হলুদ মাখিয়ে ১৫ মিনিট রেখে ধুয়ে নিন। রান্নায় রসুন বাটা ও গরম মসলার পরিমাণ একটু বাড়িয়ে দিলে "
        "কোনো গন্ধ থাকে না।",
        "💡 **Removing the smell of duck meat**: after cleaning, rub the meat with a little lemon juice and "
        "turmeric, rest it 15 minutes, then rinse. A little extra garlic paste and garam masala in the cooking removes any odour.",
    ),
    "বিরিয়ানি": (
        "💡 **ঝরঝরে পারফেক্ট বিরিয়ানি**: বাসমতি বা সুগন্ধি চাল ৭০% সেদ্ধ করে পানি ঝরিয়ে নিন। "
        "এরপর মাংসের উপর লেয়ার করে হাঁড়ির নিচে একটি মোটা তাওয়া রেখে প্রথম ৫ মিনিট মাঝারি ও পরের ২০ মিনিট খুব মৃদু আঁচে দমে রাখুন।",
        "💡 **Perfectly fluffy biryani**: parboil basmati or aromatic rice to about 70% and drain. "
        "Layer it over the meat, put a thick tawa under the pot, and dum-cook 5 minutes on medium, then 20 minutes on very low heat.",
    ),
    "চা": (
        "💡 **পারফেক্ট দুধ চা**: পানিতে আগে আদা, এলাচ ও তেজপাতা দিয়ে ২ মিনিট ফুটিয়ে নিন। এরপর চা পাতা দিন "
        "এবং ঘন দুধ ঢেলে মৃদু আঁচে আরও ২-৩ মিনিট ফুটান। সুন্দর লালচে সোনালি রং এলে নামিয়ে নিন।",
        "💡 **Perfect milk tea**: first boil ginger, cardamom and a bay leaf in water for 2 minutes. Add the tea leaves, "
        "pour in thick milk and simmer on low heat for 2-3 more minutes. Take it off when it turns a lovely reddish gold.",
    ),
}


TIP_ALIASES = {
    "কষানো": ["kosha", "kasha", "kosano"],
    "মাংস নরম": ["tender", "soft meat", "meat soft", "soften the meat"],
    "হাঁসের মাংস": ["duck smell", "duck meat"],
    "বিরিয়ানি": ["biryani tips", "fluffy biryani"],
    "চা": ["perfect tea", "milk tea", "make tea", "special tea"],
}


BN_DIGIT_TABLE = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
NUMBER_WORDS = {
    "এক": 1, "দুই": 2, "তিন": 3, "চার": 4, "পাঁচ": 5, "ছয়": 6, "সাত": 7, "আট": 8, "নয়": 9, "দশ": 10,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
_NUM = r"([0-9০-৯]+)"
_BN_UNITS = r"(?:জনের\s*জন্য|জনের|জনকে|জনে|জন|প্লেট|পরিবেশন)"
_EN_UNITS = r"(?:people|persons?|servings?|portions?|pax|jon|jone|jan)"
_MEASURES = r"(?:kg|kgs|g|gm|gms|gram|grams|ml|l|ltr|litre|liter|cup|cups|tsp|tbsp|pieces?|pcs|eggs?)"
_WORDS = "|".join(sorted(NUMBER_WORDS, key=len, reverse=True))

NUMERIC_SERVING_PATTERNS = [
    re.compile(_NUM + r"\s*" + _BN_UNITS),
    re.compile(r"\b" + _NUM + r"\s*" + _EN_UNITS + r"\b", re.IGNORECASE),
    re.compile(r"\b(?:for|serves?|serving|feeds?)\s+" + _NUM + r"\b(?!\s*" + _MEASURES + r"\b)", re.IGNORECASE),
    re.compile(r"(?<=[A-Za-z\u0980-\u09FF])\s+" + _NUM + r"\s*$"),
]
WORD_SERVING_PATTERNS = [
    re.compile(r"(" + _WORDS + r")\s*" + _BN_UNITS),
    re.compile(r"\b(?:for|serves?)\s+(" + _WORDS + r")\b", re.IGNORECASE),
]

DISH_STOP_TOKENS = {
    "রেসিপি", "রান্না", "রান্নার", "করতে", "চাই", "চাও", "নিয়ম", "বানানোর", "বানাতে", "বানাও", "করো", "করুন",
    "দাও", "দেন", "প্লিজ", "জন্য", "আমি", "আমাকে", "একটা", "একটু", "দেখাও", "কীভাবে", "কিভাবে", "রাঁধব",
    "রাঁধবো", "বানাব", "বানাবো", "করব", "কি", "কী", "এটা", "এটি",
    "i", "want", "wanna", "to", "cook", "make", "how", "recipe", "for", "please", "give", "show", "me", "the",
    "a", "an", "like", "would", "can", "you", "tell", "some", "need", "it", "this", "that", "scale", "lets", "let's",
}


def _valid_servings(value):
    return value if 1 <= value <= 100 else None


def extract_servings(text, default_servings=4):
    for pattern in NUMERIC_SERVING_PATTERNS:
        m = pattern.search(text)
        if m:
            value = _valid_servings(int(m.group(1).translate(BN_DIGIT_TABLE)))
            if value:
                return value
    for pattern in WORD_SERVING_PATTERNS:
        m = pattern.search(text)
        if m:
            return NUMBER_WORDS[m.group(1).lower()]
    return default_servings


def strip_serving_phrases(text):
    for pattern in NUMERIC_SERVING_PATTERNS + WORD_SERVING_PATTERNS:
        text = pattern.sub(" ", text)
    return text


def clean_dish_query(text):
    stripped = strip_serving_phrases(text)
    tokens = re.split(r"[\s,।.!?;:]+", stripped)
    kept = [t for t in tokens if t and t.lower() not in DISH_STOP_TOKENS]
    return " ".join(kept).strip()


RELATED_ONLINE_HINTS = {
    "kacchi": "biryani",
    "কাচ্চি": "biryani",
    "tehari": "biryani",
    "তেহারি": "biryani",
}


RELATED_DISH_HINTS = {
    "kacchi": ["chicken_biryani", "pulao"],
    "কাচ্চি": ["chicken_biryani", "pulao"],
    "tehari": ["chicken_biryani", "pulao"],
    "তেহারি": ["chicken_biryani", "pulao"],
}


def closest_dishes(dish_query):
    tokens = [t for t in re.split(r"[\s,।.!?;:]+", dish_query.lower()) if t]
    found = []
    for t in tokens:
        for rid in RELATED_DISH_HINTS.get(t, []):
            r = engine.find_recipe_by_id(rid)
            if r and r not in found:
                found.append(r)
    if found:
        return found[:3]
    words = [t for t in tokens if len(t) >= 3]
    return [r for r in engine.load_recipes() if any(w in r["dish_en"].lower() or w in r["dish"] for w in words)][:3]


def parse_intent(message, default_servings=4, session=None):
    text = message.strip()
    lower = text.lower()

    greetings = ["হ্যালো", "হাই", "সালাম", "নমস্কার", "শুভ দিন", "কেমন আছো", "hi", "hello", "hey", "ধন্যবাদ", "thanks", "thank you"]
    if any(lower == g or lower.startswith(g + " ") for g in greetings):
        if "ধন্যবাদ" in lower or "thank" in lower:
            return {
                "type": "cooking_tip",
                "reply": "আপনাকেও অনেক ধন্যবাদ! আপনার রান্না চমৎকার হোক। অন্য যেকোনো প্রশ্নে আমি আছি!",
                "reply_en": "Thank you too! I hope your cooking turns out wonderful. I'm here for any other question!",
            }
        return {"type": "greeting"}

    help_words = ["কী করতে পারো", "সাহায্য", "help", "who are you", "কে তুমি", "পাচিকা কী", "menu"]
    if any(hw in lower for hw in help_words):
        return {"type": "help"}

    if any(w in lower for w in ["নতুন আলাপ", "নতুন শুরু", "reset", "new chat", "start over"]):
        return {"type": "new_session"}

    tip_keywords = ["টিপস", "উপায়", "নিয়ম", "কৌশল", "কীভাবে", "কিভাবে", "পরামর্শ", "how to", "tip", "tips", "technique", "secret", "কষানো"]
    if any(tk in lower for tk in tip_keywords):
        for keyword, (tip_bn, tip_en) in COOKING_TIPS.items():
            aliases = TIP_ALIASES.get(keyword, [])
            if keyword in lower or any(re.search(r"\b" + re.escape(a) + r"\b", lower) for a in aliases):
                return {"type": "cooking_tip", "reply": tip_bn, "reply_en": tip_en}

    has_active_recipe = session and session.get("current_recipe_id")
    servings = extract_servings(text, None)

    if has_active_recipe and servings and any(sp in lower for sp in ["জন", "people", "person", "scale", "make it"]):
        if not clean_dish_query(text):
            return {"type": "followup_scale", "servings": servings}

    sub_indicators = ["না থাকলে", "বিকল্প", "বদলে", "substitute", "instead of", "কী দেব", "কি দিব", "কী দিব", "কি দেবো"]
    if any(ind in lower for ind in sub_indicators):
        cleaned_ing = re.sub(r"(না থাকলে|বিকল্প|বদলে|কি দেব|কী দেব|কী দিব|কি দিব|কি দেবো|ব্যবহার করব|substitute for|instead of|if i don't have)", "", text, flags=re.IGNORECASE).strip()
        cleaned_ing = re.sub(r"[\?\।\.,!\s]+", " ", cleaned_ing).strip()
        return {"type": "followup_substitution", "ingredient": cleaned_ing}

    qty_indicators = ["কতটুকু", "কতটা", "কত পরিমাণ", "how much", "কতখানি", "কতটুকু লাগবে"]
    if has_active_recipe and any(qi in lower for qi in qty_indicators):
        cleaned_ing = re.sub(r"(কতটুকু|কতটা|কত পরিমাণ|কতখানি|লাগবে|দেবো|দিব|দিতে হবে|how much|amount of)", "", text, flags=re.IGNORECASE).strip()
        cleaned_ing = re.sub(r"[\?\।\.,!\s]+", " ", cleaned_ing).strip()
        return {"type": "followup_ingredient_query", "ingredient": cleaned_ing}

    has_indicators = ["আছে", "have", "দিয়ে কি", "দিয়ে কী", "উপকরণ", "ingredients", "কী রাঁধব", "what to cook with"]
    if any(ind in lower for ind in has_indicators):
        cleaned = re.sub(r"(আমার কাছে|কাছে|আছে|ঘরে|দিয়ে কি|দিয়ে কী|রান্না করব|কী রাঁধব|i have|what to cook with|with|can i cook)", "", text, flags=re.IGNORECASE)
        ingredients = [i.strip() for i in re.split(r"[,、\n]| and | ও | এবং | আর ", cleaned) if i.strip()]
        if len(ingredients) >= 1 and not (len(ingredients) == 1 and len(ingredients[0]) < 2):
            return {"type": "ingredient_suggestion", "ingredients": ingredients}

    keywords = online_recipes.detect_ingredient_keywords(text)
    if keywords["groups"] and not keywords["leftover"]:
        return {"type": "ingredient_online_search", "groups": keywords["groups"], "pending_servings": servings}

    ambig = engine.check_ambiguous_query(text)
    if ambig:
        return {"type": "ambiguous_dish", **ambig, "pending_servings": servings}

    clean_dish = clean_dish_query(text)

    if clean_dish:
        pending = session.get("pending_servings") if session else None
        final_servings = servings if servings is not None else (pending or default_servings)
        return {
            "type": "recipe_request",
            "dish": clean_dish,
            "servings": final_servings,
            "servings_explicit": servings is not None,
        }

    return {"type": "unknown"}


def try_gemini_recipe_generation(dish_name, servings=4):
    if not GEMINI_API_KEY:
        return None

    prompt = (
        f"Generate an authentic recipe for '{dish_name}' scaled for {servings} people. "
        f"Return ONLY valid JSON with keys: id, dish (Bengali name), dish_en (English name), "
        f"category, base_servings (integer), prep_time_min, cook_time_min, total_time_min, "
        f"heat_level ('low', 'medium', or 'high'), "
        f"ingredients: list of objects with name (Bengali), name_en (English), amount (number), unit (string), note (optional string), "
        f"steps: list of objects with order (int), instruction (Bengali), instruction_en (English), duration_min (int), heat ('low', 'medium', etc.)."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            recipe_obj = json.loads(raw_text)

            recipe_obj["source"] = {
                "type": "ai_generated",
                "name": "Google Gemini (AI Generated)",
                "attribution": "Generated by Google Gemini 1.5 Flash API",
                "is_ai_generated": True,
                "source_url": None,
            }
            recipe_obj["base_servings"] = servings
            if not recipe_obj.get("id"):
                recipe_obj["id"] = re.sub(r"\W+", "_", dish_name.lower().strip())
            return recipe_obj
    except Exception as e:
        print("Gemini recipe generation error:", e)

    return None


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print(f"Starting Pachika backend on port {port} (debug={debug})...")
    app.run(host="0.0.0.0", port=port, debug=debug)
