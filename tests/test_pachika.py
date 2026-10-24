
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import app as pachika_app
import recipe_engine as engine
import weather_service


class TestStartupAndStatic(unittest.TestCase):
    def setUp(self):
        self.client = pachika_app.app.test_client()

    def test_startup_and_index_route(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")
        self.assertIn("পাচিকা", content)
        self.assertIn("landingScreen", content)
        self.assertIn("chatScreen", content)
        self.assertIn("weatherScreen", content)
        res.close()

    def test_static_assets(self):
        res_css = self.client.get("/style.css")
        self.assertEqual(res_css.status_code, 200)
        self.assertIn("--maroon", res_css.data.decode("utf-8"))
        res_css.close()

        res_js = self.client.get("/script.js")
        self.assertEqual(res_js.status_code, 200)
        self.assertIn("switchScreen", res_js.data.decode("utf-8"))
        res_js.close()

        res_img = self.client.get("/assets/pachika-avatar.png")
        self.assertEqual(res_img.status_code, 200)
        res_img.close()


class TestRecipeCatalogAndSchema(unittest.TestCase):
    def setUp(self):
        self.client = pachika_app.app.test_client()

    def test_all_recipes_count_and_schema(self):
        res = self.client.get("/api/recipes")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        recipes = data.get("recipes", [])
        self.assertEqual(len(recipes), 31)

        all_full_recipes = engine.load_recipes()
        for r in all_full_recipes:
            problems = engine.validate_recipe(r)
            self.assertEqual(problems, [], f"Validation failed for recipe '{r.get('id')}': {problems}")

            self.assertIn("source", r)
            self.assertFalse(r["source"]["is_ai_generated"])
            self.assertEqual(r["source"]["type"], "curated_catalog")

            self.assertIn("image", r)
            self.assertTrue(bool(r["image"].get("url")))
            self.assertTrue(bool(r["image"].get("license")))

    def test_categories_endpoint(self):
        res = self.client.get("/api/categories")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        cats = data.get("categories", [])
        self.assertGreaterEqual(len(cats), 10)


class TestRecipeScalingLogic(unittest.TestCase):
    def setUp(self):
        self.client = pachika_app.app.test_client()
        self.recipe = engine.find_recipe_by_id("chicken_bhuna")

    def test_scaling_linear_ingredients(self):
        scaled = engine.scale_recipe(self.recipe, 8)
        self.assertEqual(scaled["base_servings"], 8)
        chicken = [i for i in scaled["ingredients"] if i["name_en"] == "chicken"][0]
        self.assertEqual(chicken["amount"], 2)

    def test_conservative_scaling_salt_and_chili(self):
        scaled = engine.scale_recipe(self.recipe, 8)
        salt = [i for i in scaled["ingredients"] if "salt" in i["name_en"].lower()][0]
        self.assertLess(salt["amount"], 2.0)
        self.assertGreater(salt["amount"], 1.5)

    def test_cooking_time_not_multiplied(self):
        scaled = engine.scale_recipe(self.recipe, 12)
        orig_cook = self.recipe["cook_time_min"]
        self.assertLessEqual(scaled["cook_time_min"], orig_cook + 10)
        self.assertNotEqual(scaled["cook_time_min"], orig_cook * 3)

    def test_invalid_servings_rejection(self):
        with self.assertRaises(ValueError):
            engine.scale_recipe(self.recipe, 0)
        with self.assertRaises(ValueError):
            engine.scale_recipe(self.recipe, -5)

        res = self.client.post("/api/recipe/scale", json={"id": "chicken_bhuna", "servings": 0})
        self.assertEqual(res.status_code, 400)
        res_neg = self.client.post("/api/recipe/scale", json={"id": "chicken_bhuna", "servings": -2})
        self.assertEqual(res_neg.status_code, 400)


class TestAmbiguityAndAliases(unittest.TestCase):
    def setUp(self):
        self.client = pachika_app.app.test_client()

    def test_transliteration_aliases(self):
        r1 = engine.resolve_dish_query("biriyani")
        self.assertEqual(r1["id"], "chicken_biryani")

        r2 = engine.resolve_dish_query("polao")
        self.assertEqual(r2["id"], "pulao")

        r3 = engine.resolve_dish_query("khechuri")
        self.assertEqual(r3["id"], "khichuri")

    def test_ambiguous_protein_clarification_no_bhuna_fallback(self):
        res = self.client.post("/api/chat", json={"message": "chicken"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("clarification_options", data)
        opt_ids = [o["id"] for o in data["clarification_options"]]
        self.assertIn("chicken_bhuna", opt_ids)
        self.assertIn("chicken_curry", opt_ids)
        self.assertIn("chicken_biryani", opt_ids)
        self.assertNotIn("recipe", data)

        res_tea = self.client.post("/api/chat", json={"message": "চা"})
        data_tea = res_tea.get_json()
        self.assertIn("clarification_options", data_tea)


class TestIngredientMatchingStrictTokens(unittest.TestCase):
    def test_egg_does_not_match_eggplant(self):
        suggestions = engine.suggest_by_ingredients(["egg"])
        suggested_ids = [s["recipe"]["id"] for s in suggestions]
        self.assertIn("egg_bhurji", suggested_ids)
        self.assertNotIn("begun_bhorta", suggested_ids)

    def test_bengali_ingredient_matching(self):
        suggestions = engine.suggest_by_ingredients(["ডিম", "পেঁয়াজ"])
        suggested_ids = [s["recipe"]["id"] for s in suggestions]
        self.assertIn("egg_bhurji", suggested_ids)


class TestSessionContextPreservation(unittest.TestCase):
    def setUp(self):
        self.client = pachika_app.app.test_client()

    def test_contextual_followups(self):
        sess_id = "test_session_123"

        r1 = self.client.post("/api/chat", json={
            "message": "পোলাও রেসিপি দাও",
            "servings": 4,
            "session_id": sess_id
        })
        self.assertEqual(r1.status_code, 200)
        d1 = r1.get_json()
        self.assertIn("recipe", d1)
        self.assertEqual(d1["recipe"]["id"], "pulao")

        r2 = self.client.post("/api/chat", json={
            "message": "৮ জনের জন্য করো",
            "session_id": sess_id
        })
        self.assertEqual(r2.status_code, 200)
        d2 = r2.get_json()
        self.assertIn("recipe", d2)
        self.assertEqual(d2["recipe"]["id"], "pulao")
        self.assertEqual(d2["recipe"]["base_servings"], 8)

        r3 = self.client.post("/api/chat", json={
            "message": "লবণ কতটুকু লাগবে?",
            "session_id": sess_id
        })
        self.assertEqual(r3.status_code, 200)
        d3 = r3.get_json()
        self.assertIn("লবণ", d3["reply"])

        r4 = self.client.post("/api/chat", json={
            "message": "ঘি না থাকলে কী দেব?",
            "session_id": sess_id
        })
        self.assertEqual(r4.status_code, 200)
        d4 = r4.get_json()
        self.assertIn("বিকল্প", d4["reply"])


class TestWeatherAndFestiveRecommendations(unittest.TestCase):
    def setUp(self):
        self.client = pachika_app.app.test_client()

    @patch("weather_service.fetch_weather")
    @patch("weather_service.fetch_hijri_date")
    def test_rainy_weather_recommendations(self, mock_hijri, mock_weather):
        mock_weather.return_value = {
            "temperature_c": 24.0,
            "humidity_percent": 85,
            "precipitation_mm": 5.2,
            "weather_code": 61,
            "is_day": 1,
            "condition_en": "Moderate rain",
            "condition_bn": "বৃষ্টিপাত",
            "condition_type": "rain",
        }
        mock_hijri.return_value = {"day": 10, "month_number": 3, "month_en": "Rabi al-Awwal", "year": "1448"}

        res = self.client.get("/api/weather/recommendations?city=Dhaka")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        dish_ids = [d["id"] for d in data["weather_recipes"]]
        self.assertIn("khichuri", dish_ids)
        self.assertIn("বৃষ্টি", data["reason_bn"])

    @patch("weather_service.fetch_weather")
    @patch("weather_service.fetch_hijri_date")
    def test_hot_weather_recommendations(self, mock_hijri, mock_weather):
        mock_weather.return_value = {
            "temperature_c": 34.0,
            "humidity_percent": 70,
            "precipitation_mm": 0.0,
            "weather_code": 0,
            "is_day": 1,
            "condition_en": "Clear sky",
            "condition_bn": "পরিষ্কার আকাশ",
            "condition_type": "clear",
        }
        mock_hijri.return_value = {"day": 10, "month_number": 3, "month_en": "Rabi al-Awwal", "year": "1448"}

        res = self.client.get("/api/weather/recommendations?city=Dhaka")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        dish_ids = [d["id"] for d in data["weather_recipes"]]
        self.assertTrue("doi_ghol" in dish_ids or "borhani" in dish_ids)
        self.assertIn("গরম", data["reason_bn"])

    @patch("weather_service.geocode_city")
    def test_invalid_city_weather_handling(self, mock_geocode):
        mock_geocode.return_value = None
        res = self.client.get("/api/weather/recommendations?city=NonExistentCityXYZ")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("could not be located", data["error"])


class TestSpeechAndErrorHandling(unittest.TestCase):
    def setUp(self):
        self.client = pachika_app.app.test_client()

    def test_speak_empty_text_rejection(self):
        res = self.client.post("/api/speak", json={"text": ""})
        self.assertEqual(res.status_code, 400)

    def test_speak_valid_text(self):
        res = self.client.post("/api/speak", json={"text": "খিচুড়ি রান্না শুরু করুন"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue("audio" in data or "fallback" in data)

    def test_ai_fallback_truthful_when_no_api_key(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True):
            pachika_app.GEMINI_API_KEY = None
            res = self.client.post("/api/chat", json={"message": "Spaghetti Carbonara"})
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertIsNone(data.get("recipe"))
            self.assertIn("খুঁজে পাইনি", data["reply"])
            self.assertNotIn("GEMINI", data["reply"])
            self.assertNotIn(".env", data["reply"])


class TestComprehensiveNLP(unittest.TestCase):
    def setUp(self):
        self.client = pachika_app.app.test_client()

    def test_transliterations_and_aliases(self):
        cases = [
            ("biriyani", "chicken_biryani"),
            ("biryani", "chicken_biryani"),
            ("polao", "pulao"),
            ("pulao", "pulao"),
            ("khechuri", "khichuri"),
            ("khichuri", "khichuri"),
            ("doodh cha", "cha"),
            ("milk tea", "cha"),
            ("piyaju", "piyaju"),
            ("alu bhorta", "aloo_bhorta"),
            ("dimer dalna", "egg_bhurji"),
            ("ডিমের ডালনা", "egg_bhurji"),
        ]
        for query, expected_id in cases:
            resolved = engine.resolve_dish_query(query)
            self.assertIsNotNone(resolved, f"Failed to resolve: {query}")
            self.assertFalse(isinstance(resolved, dict) and resolved.get("is_ambiguous"), f"Unexpectedly ambiguous: {query}")
            self.assertEqual(resolved["id"], expected_id, f"Query '{query}' resolved to '{resolved['id']}', expected '{expected_id}'")

    def test_bengali_numerals_and_words(self):
        cases = [
            ("৪ জনের জন্য খিচুড়ি", 4),
            ("৬ জনের পোলাও", 6),
            ("৮ জনের জন্য করো", 8),
            ("২ প্লেট বিরিয়ানি", 2),
            ("১০ জনের জন্য চা", 10),
            ("4 servings of khichuri", 4),
        ]
        for msg, exp_servings in cases:
            s = pachika_app.extract_servings(msg)
            self.assertEqual(s, exp_servings, f"Msg '{msg}' extracted servings {s}, expected {exp_servings}")

    def test_egg_vs_eggplant_matching(self):
        res_egg = engine.suggest_by_ingredients(["egg"])
        matched_ids = [r["recipe"]["id"] for r in res_egg]
        self.assertIn("egg_bhurji", matched_ids)
        self.assertNotIn("begun_bhorta", matched_ids)

        res_eggplant = engine.suggest_by_ingredients(["eggplant"])
        matched_ids2 = [r["recipe"]["id"] for r in res_eggplant]
        self.assertIn("begun_bhorta", matched_ids2)
        self.assertNotIn("egg_bhurji", matched_ids2)

    def test_generic_ambiguous_queries(self):
        generic_terms = ["chicken", "beef", "fish", "tea"]
        for term in generic_terms:
            res = self.client.post("/api/chat", json={"message": term})
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertIn("clarification_options", data, f"Term '{term}' did not return clarification options!")
            self.assertTrue(len(data["clarification_options"]) > 1)

    def test_multi_turn_context_and_reset(self):
        sess_id = "test_nlp_session_999"
        r1 = self.client.post("/api/chat", json={"message": "পোলাও রেসিপি দাও", "session_id": sess_id})
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.get_json()["recipe"]["id"], "pulao")

        r2 = self.client.post("/api/chat", json={"message": "৮ জনের জন্য করো", "session_id": sess_id})
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.get_json()["recipe"]["base_servings"], 8)

        r5 = self.client.post("/api/chat", json={"message": "নতুন আলাপ", "session_id": sess_id})
        self.assertEqual(r5.status_code, 200)
        self.assertIn("নতুন রান্নার আলাপ শুরু করা হলো", r5.get_json()["reply"])

        r6 = self.client.post("/api/chat", json={"message": "লবণ কতটুকু লাগবে?", "session_id": sess_id})
        self.assertEqual(r6.status_code, 200)
        self.assertNotIn("পোলাও", r6.get_json()["reply"])


if __name__ == "__main__":
    unittest.main()
