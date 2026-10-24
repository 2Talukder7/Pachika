import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import online_recipes as online
import recipe_engine as engine
import app as pachika_app
from app import app


LOOKUP_52772 = json.loads(r'''{"meals":[{"idMeal":"52772","strMeal":"Teriyaki Chicken Casserole","strMealAlternate":null,"strCategory":"Chicken","strArea":"Japanese","strCountry":"Japan","strInstructions":"Preheat oven to 350\u00b0 F. Spray a 9x13-inch baking pan with non-stick spray.\r\nCombine soy sauce, \u00bd cup water, brown sugar, ginger and garlic in a small saucepan and cover. Bring to a boil over medium heat. Remove lid and cook for one minute once boiling.\r\nMeanwhile, stir together the corn starch and 2 tablespoons of water in a separate dish until smooth. Once sauce is boiling, add mixture to the saucepan and stir to combine. Cook until the sauce starts to thicken then remove from heat.\r\nPlace the chicken breasts in the prepared pan. Pour one cup of the sauce over top of chicken. Place chicken in oven and bake 35 minutes or until cooked through. Remove from oven and shred chicken in the dish using two forks.\r\n*Meanwhile, steam or cook the vegetables according to package directions.\r\nAdd the cooked vegetables and rice to the casserole dish with the chicken. Add most of the remaining sauce, reserving a bit to drizzle over the top when serving. Gently toss everything together in the casserole dish until combined. Return to oven and cook 15 minutes. Remove from oven and let stand 5 minutes before serving. Drizzle each serving with remaining sauce. Enjoy!","strMealThumb":"https:\/\/www.themealdb.com\/images\/media\/meals\/wvpsxx1468256321.jpg","strTags":"Meat,Casserole","strYoutube":"https:\/\/www.youtube.com\/watch?v=4aZr5hZXP_s","strIngredient1":"soy sauce","strIngredient2":"water","strIngredient3":"brown sugar","strIngredient4":"ground ginger","strIngredient5":"minced garlic","strIngredient6":"cornstarch","strIngredient7":"chicken breasts","strIngredient8":"stir-fry vegetables","strIngredient9":"brown rice","strIngredient10":"","strIngredient11":"","strIngredient16":null,"strMeasure1":"3\/4 cup","strMeasure2":"1\/2 cup","strMeasure3":"1\/4 cup","strMeasure4":"1\/2 teaspoon","strMeasure5":"1\/2 teaspoon","strMeasure6":"4 Tablespoons","strMeasure7":"2","strMeasure8":"1 (12 oz.)","strMeasure9":"3 cups","strMeasure10":"","strMeasure11":"","strMeasure16":null,"strSource":null,"strImageSource":null}]}''')


def meal(i, title):
    return {"strMeal": title, "strMealThumb": f"https://www.themealdb.com/images/media/meals/test{i}.jpg", "idMeal": str(i)}


class FakeApi:
    def __init__(self):
        self.calls = []
        self.fail = False
        self.routes = {}

    def __call__(self, url, timeout=6):
        self.calls.append(url)
        if self.fail:
            raise online.OnlineSearchError("network down")
        for fragment, payload in self.routes.items():
            if fragment in url:
                return payload
        return {"meals": None}


@pytest.fixture
def api(monkeypatch):
    fake = FakeApi()
    online.clear_cache()
    monkeypatch.setattr(online, "_http_get_json", fake)
    return fake


@pytest.fixture
def client():
    return app.test_client()


def chat(client, message, sid="t", servings=4):
    return client.post("/api/chat", json={"message": message, "session_id": sid, "servings": servings}).get_json()


KEYWORD_CASES = [
    ("cow", ["beef"]), ("beef", ["beef"]), ("Beef recipe", ["beef"]), ("গরু", ["beef"]), ("গরুর মাংস", ["beef"]),
    ("গরুর মাংসের রেসিপি", ["beef"]), ("mutton", ["mutton"]), ("goat", ["mutton"]), ("goat meat", ["mutton"]),
    ("খাসি", ["mutton"]), ("ছাগলের মাংস", ["mutton"]), ("chicken", ["chicken"]), ("roaster", ["chicken"]),
    ("মুরগি", ["chicken"]), ("মুরগির", ["chicken"]), ("রোস্টার মুরগি", ["chicken"]), ("fish", ["fish"]),
    ("fishes", ["fish"]), ("মাছ", ["fish"]), ("মাছের রেসিপি", ["fish"]), ("shrimp", ["shrimp"]),
    ("prawn recipes", ["shrimp"]), ("চিংড়ি", ["shrimp"]), ("lobster", ["lobster"]), ("লবস্টার", ["lobster"]),
    ("veg", ["vegetable"]), ("vegetables", ["vegetable"]), ("সবজি", ["vegetable"]), ("duck", ["duck"]),
    ("চিকেন", ["chicken"]), ("chicken and potato", ["chicken", "potato"]), ("beef for 5 people", ["beef"]),
    ("recipes with egg", ["egg"]), ("ডিম", ["egg"]),
]


@pytest.mark.parametrize("text,expected", KEYWORD_CASES)
def test_keywords_detected(text, expected):
    found = online.detect_ingredient_keywords(text)
    assert found["groups"] == expected and not found["leftover"], found


@pytest.mark.parametrize("text", [
    "beef curry for 5 people", "kacchi for 3", "hello", "less spicy", "make it for 6 people", "chicken bhuna",
    "মুরগির ঝোল", "khichuri", "I want to cook beef curry",
])
def test_non_keyword_messages_are_not_hijacked(text):
    found = online.detect_ingredient_keywords(text)
    assert not found["groups"] or found["leftover"], found


MEASURES = [
    ("3/4 cup", (0.75, "cup", "")), ("4 Tablespoons", (4, "tbsp", "")), ("1/2 teaspoon", (0.5, "tsp", "")),
    ("2", (2, "", "")), ("1 (12 oz.)", (1, "", "(12 oz.)")), ("200g", (200, "g", "")), ("1 1/2 cups", (1.5, "cup", "")),
    ("2-3 tbsp", (2, "tbsp", "")), ("3 cloves", (3, "", "cloves")), ("Pinch", (None, "", "Pinch")),
    ("To taste", (None, "", "To taste")), ("", (None, "", "")), ("½ cup", (0.5, "cup", "")),
]


@pytest.mark.parametrize("raw,expected", MEASURES)
def test_measure_parsing(raw, expected):
    assert online.parse_measure(raw) == expected


def test_real_response_converts_to_recipe_card_shape():
    recipe = online.meal_to_recipe(LOOKUP_52772["meals"][0])
    assert recipe["dish_en"] == "Teriyaki Chicken Casserole" and recipe["id"] == "mealdb_52772"
    assert len(recipe["ingredients"]) == 9
    first = recipe["ingredients"][0]
    assert first["name_en"] == "soy sauce" and first["amount"] == 0.75 and first["unit"] == "cup"
    assert recipe["ingredients"][5]["amount"] == 4 and recipe["ingredients"][5]["unit"] == "tbsp"
    assert len(recipe["steps"]) >= 5
    durations = [s["duration_min"] for s in recipe["steps"] if s["duration_min"]]
    assert 35 in durations and 15 in durations
    assert recipe["source"]["type"] == "online" and recipe["source"]["source_url"] is None
    assert recipe["image"]["url"].startswith("https://") and recipe["base_servings"] == 4
    assert recipe["prep_time_min"] is None and recipe["assumptions_en"]


def test_online_recipe_scales_without_crashing_on_unknown_times_and_amounts():
    data = json.loads(json.dumps(LOOKUP_52772["meals"][0]))
    data["strIngredient10"] = "salt"
    data["strMeasure10"] = "To taste"
    recipe = online.meal_to_recipe(data)
    scaled = engine.scale_recipe(recipe, 8)
    assert scaled["base_servings"] == 8 and scaled["total_time_min"] is None
    assert scaled["ingredients"][0]["amount"] == 1.5
    assert scaled["ingredients"][-1]["amount"] is None
    assert recipe["ingredients"][0]["amount"] == 0.75


def test_cow_searches_online_first_and_skips_local_when_online_has_results(api, client):
    api.routes = {"filter.php?c=Beef": {"meals": [meal(1, "Test Beef One"), meal(2, "Test Beef Two"), meal(3, "Test Beef Three")]},
                  "filter.php?a=Indian": {"meals": [meal(3, "x")]}}
    data = chat(client, "cow")
    assert data["online_status"] == "ok"
    assert [r["id"] for r in data["online_results"]] == ["3", "1", "2"]
    assert any("c=Beef" in u for u in api.calls)
    assert data["online_results"][0]["thumb"].startswith("https://") and data["online_results"][0]["provider_name"] == "TheMealDB"
    assert "clarification_options" not in data
    assert "searched online first" in data["reply_en"] and "গরুর মাংস" in data["reply"]


def test_local_dishes_are_listed_alongside_online_only_when_enabled(api, client, monkeypatch):
    api.routes = {"filter.php?c=Beef": {"meals": [meal(1, "Test Beef One")]}}
    monkeypatch.setattr(pachika_app, "SHOW_LOCAL_WITH_ONLINE", True)
    data = chat(client, "cow", sid="both")
    assert data["online_results"] and {o["id"] for o in data["clarification_options"]} >= {"beef_bhuna"}


@pytest.mark.parametrize("message,expected_fragments", [
    ("beef", ["c=Beef"]), ("গরু", ["c=Beef"]), ("goat", ["c=Goat", "c=Lamb"]), ("mutton", ["c=Goat", "c=Lamb"]),
    ("খাসি", ["c=Goat", "c=Lamb"]), ("chicken", ["c=Chicken"]), ("roaster", ["c=Chicken"]), ("মুরগি", ["c=Chicken"]),
    ("fish", ["s=fish", "c=Seafood"]), ("মাছ", ["s=fish", "c=Seafood"]), ("fishes", ["s=fish", "c=Seafood"]),
    ("shrimp", ["i=prawns", "i=king_prawns", "i=tiger_prawns"]), ("চিংড়ি", ["i=prawns"]),
    ("veg", ["c=Vegetarian", "c=Vegan"]), ("সবজি", ["c=Vegetarian"]), ("duck", ["i=duck"]), ("egg", ["i=eggs"]),
])
def test_every_keyword_triggers_the_right_online_queries(api, client, message, expected_fragments):
    api.routes = {"filter.php": {"meals": [meal(10, "Test Dish")]}, "search.php": {"meals": [meal(11, "Test Search Dish")]}}
    data = chat(client, message, sid=f"kw-{message}")
    assert data["online_status"] == "ok" and data["online_results"], data
    for fragment in expected_fragments:
        assert any(fragment in u for u in api.calls), (fragment, api.calls)


def test_lobster_falls_back_to_prawns_and_says_so(api, client):
    api.routes = {"search.php?s=lobster": {"meals": None}, "filter.php?i=prawns": {"meals": [meal(20, "Test Prawn Dish")]}}
    data = chat(client, "lobster")
    assert data["online_status"] == "ok" and data["online_results"][0]["id"] == "20"
    assert "No lobster recipes were found" in data["reply_en"] and "লবস্টারের রেসিপি পাওয়া যায়নি" in data["reply"]


def test_lobster_found_directly_has_no_fallback_note(api, client):
    api.routes = {"search.php?s=lobster": {"meals": [meal(21, "Test Lobster Thermidor")]}}
    data = chat(client, "lobster")
    assert data["online_results"][0]["title"] == "Test Lobster Thermidor" and "No lobster" not in data["reply_en"]


def test_internet_down_falls_back_to_local_and_says_why(api, client):
    api.fail = True
    data = chat(client, "beef")
    assert data["online_status"] == "unavailable" and "online_results" not in data
    assert "not working right now" in data["reply_en"] and "অনলাইন সার্চ এখন কাজ করছে না" in data["reply"]
    assert "Pachika's own dishes" in data["reply_en"]
    assert any(o["id"] == "beef_bhuna" for o in data["clarification_options"])


def test_failure_reason_is_shown_to_the_user(api, client, monkeypatch):
    def failing(url, timeout=6):
        raise online.OnlineSearchError("x", reason="ssl", detail="CERTIFICATE_VERIFY_FAILED")
    monkeypatch.setattr(online, "_http_get_json", failing)
    online.clear_cache()
    data = chat(client, "chicken", sid="ssl")
    assert "SSL certificate" in data["reply_en"] and "সার্টিফিকেট" in data["reply"]


def test_nothing_found_online_falls_back_to_local(api, client):
    data = chat(client, "chicken", sid="empty-local")
    assert data["online_status"] == "empty" and "No recipes were found online" in data["reply_en"]
    assert data["clarification_options"] and "Pachika's own dishes" in data["reply_en"]


def test_nothing_found_online_and_nothing_similar_locally_is_reported(api, client, monkeypatch):
    monkeypatch.setattr(pachika_app, "similar_local_dishes", lambda groups, limit=6: {"dishes": [], "similar_of": []})
    data = chat(client, "lobster", sid="empty")
    assert data["online_status"] == "empty" and "No recipes were found online" in data["reply_en"]
    assert "clarification_options" not in data and "try again" in data["reply_en"]


def test_health_endpoint_reports_ok_and_failure(api, client, monkeypatch):
    api.routes = {"search.php?s=chicken": {"meals": [meal(1, "Test Chicken")]}}
    good = client.get("/api/online/health").get_json()
    assert good["ok"] is True and good["reason"] == "ok"
    def failing(url, timeout=6):
        raise online.OnlineSearchError("x", reason="dns", detail="Name or service not known")
    monkeypatch.setattr(online, "_http_get_json", failing)
    bad = client.get("/api/online/health").get_json()
    assert bad["ok"] is False and bad["reason"] == "dns" and "Name or service" in bad["detail"]


@pytest.mark.parametrize("message,reason", [
    ("<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed>", "ssl"),
    ("<urlopen error [Errno 11001] getaddrinfo failed>", "dns"),
    ("<urlopen error timed out>", "timeout"),
    ("<urlopen error [WinError 10061] connection refused>", "network"),
])
def test_error_classification(message, reason):
    import urllib.error
    assert online.classify_error(urllib.error.URLError(message)) == reason


def test_malformed_api_payloads_do_not_crash(api, client):
    for payload in ({"meals": "None Found"}, {"meals": [{"idMeal": None}]}, {"meals": [1, 2]}, [], "oops", {}):
        online.clear_cache()
        api.routes = {"filter.php": payload}
        data = chat(client, "beef", sid="bad")
        assert data["online_status"] == "empty", payload


def test_unknown_dish_falls_back_to_online_name_search_with_servings(api, client):
    api.routes = {"search.php?s=kacchi": {"meals": None}, "search.php?s=kacchi+biryani": {"meals": None}}
    data = chat(client, "kacchi for 3", sid="k1")
    assert "online_results" not in data and "couldn't find a recipe for 'kacchi'" in data["reply_en"]
    online.clear_cache()
    api.routes = {"search.php?s=kacchi": {"meals": [dict(LOOKUP_52772["meals"][0])]}}
    data = chat(client, "kacchi for 3", sid="k2")
    assert data["online_results"][0]["id"] == "52772" and "not in our collection" in data["reply_en"]
    api.routes = {"lookup.php?i=52772": LOOKUP_52772}
    got = client.get("/api/online/recipe?provider=themealdb&id=52772&session_id=k2").get_json()
    assert got["recipe"]["base_servings"] == 3 and got["recipe"]["ingredients"][0]["amount"] == 0.56
    follow = chat(client, "make it for 6 people", sid="k2")
    assert follow["recipe"]["base_servings"] == 6 and follow["recipe"]["id"] == "mealdb_52772"
    assert follow["recipe"]["ingredients"][0]["amount"] == 1.12


def test_bengali_serving_phrase_regression(api, client):
    for message, servings, dish in [("৬ জনের জন্য কাচ্চি", 6, "কাচ্চি"), ("kacchi for 3", 3, "kacchi"), ("kacchi 3", 3, "kacchi"), ("কাচ্চি ৪", 4, "কাচ্চি"), ("chicken curry 5", 5, "chicken curry"), ("৪ জনের জন্য মুরগির ঝোল", 4, "মুরগির ঝোল"), ("beef curry for 5 people", 5, "beef curry"), ("beef 2 kg", 4, "beef 2 kg")]:
        from app import parse_intent
        intent = parse_intent(message)
        assert intent["type"] == "recipe_request" and intent["dish"] == dish and intent["servings"] == servings, (message, intent)


def test_online_recipe_endpoint_validates_input(api, client):
    for query in ("provider=themealdb&id=abc", "provider=themealdb&id=52772/../x", "provider=evil&id=52772", "provider=themealdb&id=", "id=1;drop"):
        assert client.get(f"/api/online/recipe?{query}").status_code == 400, query
    assert not api.calls


def test_online_recipe_endpoint_errors(api, client):
    api.routes = {"lookup.php": {"meals": None}}
    assert client.get("/api/online/recipe?provider=themealdb&id=1").status_code == 404
    api.fail = True
    online.clear_cache()
    response = client.get("/api/online/recipe?provider=themealdb&id=52772")
    assert response.status_code == 502 and "internet" in response.get_json()["error"]


def test_ingredient_phrase_still_uses_local_suggestions_and_adds_online(api, client):
    api.routes = {"filter.php?c=Chicken": {"meals": [meal(30, "Test Chicken")]}, "filter.php?i=potatoes": {"meals": [meal(31, "Test Potato")]}}
    data = chat(client, "I have chicken and potato, what can I cook?", sid="have")
    assert data.get("recipe") and data["suggestions"]
    assert {r["id"] for r in data["online_results"]} == {"30", "31"}


def test_other_messages_unchanged(api, client):
    assert chat(client, "beef curry for 5 people", sid="c1")["recipe"]["base_servings"] == 5
    assert chat(client, "hello", sid="c2")["reply_en"].startswith("I'm Pachika")
    assert not api.calls


def test_banglish_sentence_is_ingredient_search():
    found = online.detect_ingredient_keywords("amar kache alu, dim ar peyaj ase. ki ranna korte pari?")
    assert found["groups"] == ["potato", "egg"]
    assert found["leftover"] == []


@pytest.mark.parametrize("word,group", [
    ("cow", "beef"), ("গরু", "beef"), ("beef", "beef"), ("mutton", "mutton"), ("goat", "mutton"), ("খাসি", "mutton"),
    ("chicken", "chicken"), ("roaster", "chicken"), ("মুরগি", "chicken"), ("fishes", "fish"), ("মাছ", "fish"),
    ("shrimp", "shrimp"), ("চিংড়ি", "shrimp"), ("lobster", "lobster"), ("লবস্টার", "lobster"),
    ("veg", "vegetable"), ("সবজি", "vegetable"),
])
def test_listed_keywords_in_english_and_bangla(word, group):
    assert online.detect_ingredient_keywords(word)["groups"] == [group]


@pytest.mark.parametrize("text", ["chicken bhuna", "beef curry", "khichuri", "মুরগির মাংস ভুনা"])
def test_dish_names_are_not_keyword_searches(text):
    found = online.detect_ingredient_keywords(text)
    assert found["leftover"] or not found["groups"]


def test_similar_local_dishes_exact_and_similar():
    shrimp = pachika_app.similar_local_dishes(["shrimp"])
    assert [r["id"] for r in shrimp["dishes"]][:1] == ["prawn_malai_curry"] and shrimp["similar_of"] == []
    lobster = pachika_app.similar_local_dishes(["lobster"])
    ids = [r["id"] for r in lobster["dishes"]]
    assert lobster["similar_of"] == ["shrimp", "fish"] and "prawn_malai_curry" in ids and "fish_curry" in ids
    crab = pachika_app.similar_local_dishes(["crab"])
    assert crab["dishes"] and crab["similar_of"]


@pytest.mark.parametrize("group", ["lentil", "egg", "potato", "vegetable", "chicken", "beef", "mutton", "duck", "fish"])
def test_ingredient_fallback_never_suggests_drinks(group):
    dishes = pachika_app.similar_local_dishes([group])["dishes"]
    assert dishes and all(r["category"] != "drink" for r in dishes)


@pytest.mark.parametrize("message", ["lobster", "লবস্টার", "crab", "কাঁকড়া", "shrimp", "পাঁঠা"])
def test_online_down_still_gives_local_suggestions_for_every_listed_keyword(api, client, message):
    api.fail = True
    data = chat(client, message, sid=f"fb-{message}")
    assert data["online_status"] == "unavailable" and data["clarification_options"], data["reply_en"]


def test_lobster_fallback_says_it_is_similar_and_uses_ingredients(api, client):
    api.fail = True
    data = chat(client, "lobster", sid="lob")
    ids = {o["id"] for o in data["clarification_options"]}
    assert {"prawn_malai_curry"} <= ids and "similar dishes use" in data["reply_en"] and "Prawn" in data["reply_en"]
    assert "কাছাকাছি পদগুলো" in data["reply"]


def test_empty_online_result_also_falls_back_to_similar_local_dishes(api, client):
    data = chat(client, "lobster", sid="lob-empty")
    assert data["online_status"] == "empty" and "No recipes were found online" in data["reply_en"]
    assert any(o["id"] == "prawn_malai_curry" for o in data["clarification_options"])


def test_wrong_dish_is_not_presented_for_lobster_curry(api, client):
    api.fail = True
    data = chat(client, "lobster curry", sid="lc")
    assert "recipe" not in data
    ids = {o["id"] for o in data["clarification_options"]}
    assert "beef_curry" not in ids and "chicken_curry" not in ids and "prawn_malai_curry" in ids


def test_known_dishes_still_open_directly(api, client):
    for text, dish in [("khichuri for 4 people", "khichuri"), ("chicken bhuna", "chicken_bhuna"), ("beef curry for 5 people", "beef_curry")]:
        data = chat(client, text, sid=f"known-{dish}")
        assert data["recipe"]["id"] == dish


def test_kacchi_fallback_offers_biryani_and_pulao_when_online_is_down(api, client):
    api.fail = True
    data = chat(client, "kacchi for 3", sid="kac")
    assert [o["id"] for o in data["clarification_options"]][:2] == ["chicken_biryani", "pulao"]
