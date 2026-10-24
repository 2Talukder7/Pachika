import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
import app as pachika_app
import recipe_engine as engine


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
            ("৪ জনের জন্য খিচুড়ি", 4, "khichuri"),
            ("৬ জনের পোলাও", 6, "pulao"),
            ("৮ জনের জন্য করো", 8, None),
            ("২ প্লেট বিরিয়ানি", 2, "chicken_biryani"),
            ("১০ জনের জন্য চা", 10, "cha"),
            ("4 servings of khichuri", 4, "khichuri"),
        ]
        for msg, exp_servings, exp_dish in cases:
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

    def test_ingredient_only_query(self):
        res = self.client.post("/api/chat", json={"message": "আমার কাছে ডিম ও পেঁয়াজ আছে"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("recipe", data)
        self.assertIn("suggestions", data)

    def test_cooking_tips(self):
        res = self.client.post("/api/chat", json={"message": "বিরিয়ানি কীভাবে ঝরঝরে করব?"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("বিরিয়ানি", data["reply"])

    def test_multi_turn_context_and_reset(self):
        sess_id = "test_nlp_session_999"

        r1 = self.client.post("/api/chat", json={"message": "পোলাও রেসিপি দাও", "session_id": sess_id})
        self.assertEqual(r1.status_code, 200)
        d1 = r1.get_json()
        self.assertEqual(d1["recipe"]["id"], "pulao")

        r2 = self.client.post("/api/chat", json={"message": "৮ জনের জন্য করো", "session_id": sess_id})
        self.assertEqual(r2.status_code, 200)
        d2 = r2.get_json()
        self.assertEqual(d2["recipe"]["base_servings"], 8)

        r3 = self.client.post("/api/chat", json={"message": "লবণ কতটুকু লাগবে?", "session_id": sess_id})
        self.assertEqual(r3.status_code, 200)
        d3 = r3.get_json()
        self.assertIn("লবণ", d3["reply"])

        r4 = self.client.post("/api/chat", json={"message": "ঘি না থাকলে কী দেব?", "session_id": sess_id})
        self.assertEqual(r4.status_code, 200)
        d4 = r4.get_json()
        self.assertIn("বিকল্প", d4["reply"])

        r5 = self.client.post("/api/chat", json={"message": "নতুন আলাপ", "session_id": sess_id})
        self.assertEqual(r5.status_code, 200)
        self.assertIn("নতুন রান্নার আলাপ শুরু করা হলো", r5.get_json()["reply"])

        r6 = self.client.post("/api/chat", json={"message": "লবণ কতটুকু লাগবে?", "session_id": sess_id})
        self.assertEqual(r6.status_code, 200)
        self.assertNotIn("পোলাও", r6.get_json()["reply"])


if __name__ == "__main__":
    unittest.main()
