import sys
import os

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from app import app

client = app.test_client()

r_index = client.get("/")
assert r_index.status_code == 200, f"Index failed: {r_index.status_code}"
assert "পাচিকা" in r_index.data.decode("utf-8"), "Title not found in index.html"
print("[PASS] GET / (index.html)")

r_css = client.get("/style.css")
assert r_css.status_code == 200, "style.css failed"
print("[PASS] GET /style.css")

r_js = client.get("/script.js")
assert r_js.status_code == 200, "script.js failed"
print("[PASS] GET /script.js")

r_img = client.get("/assets/pachika-avatar.png")
assert r_img.status_code == 200, "avatar image failed"
print("[PASS] GET /assets/pachika-avatar.png")

r_recipes = client.get("/api/recipes")
assert r_recipes.status_code == 200
assert len(r_recipes.json["recipes"]) == 31
print("[PASS] GET /api/recipes (31 recipes)")

r_cats = client.get("/api/categories")
assert r_cats.status_code == 200
assert len(r_cats.json["categories"]) > 0
print(f"[PASS] GET /api/categories ({len(r_cats.json['categories'])} categories)")

r_scale = client.post("/api/recipe/scale", json={"id": "chicken_bhuna", "servings": 8})
assert r_scale.status_code == 200
assert r_scale.json["base_servings"] == 8
chicken_ing = [i for i in r_scale.json["ingredients"] if i["name_en"] == "chicken"][0]
assert chicken_ing["amount"] == 2, f"Expected 2, got {chicken_ing['amount']}"
print("[PASS] POST /api/recipe/scale (accurate scaling 1kg -> 2kg)")

r_chat = client.post("/api/chat", json={"message": "খাসির মাংস ভুনা", "servings": 4})
assert r_chat.status_code == 200
assert "recipe" in r_chat.json
assert r_chat.json["recipe"]["id"] == "mutton_bhuna"
print("[PASS] POST /api/chat (Bengali protein fallback -> mutton_bhuna)")

r_chat_num = client.post("/api/chat", json={"message": "৬ জনের জন্য খিচুড়ি", "servings": 2})
assert r_chat_num.status_code == 200
assert r_chat_num.json["recipe"]["base_servings"] == 6
print("[PASS] POST /api/chat (Bengali numeral extraction: ৬ -> 6 servings)")

r_ing = client.post("/api/chat", json={"message": "আমার কাছে ডিম ও পেঁয়াজ আছে", "servings": 4})
assert r_ing.status_code == 200
assert "recipe" in r_ing.json
print(f"[PASS] POST /api/chat (Bengali ingredient matching -> {r_ing.json['recipe']['dish_en']})")

r_tip = client.post("/api/chat", json={"message": "বিরিয়ানি কীভাবে ঝরঝরে করব?", "servings": 4})
assert r_tip.status_code == 200
assert "বিরিয়ানি" in r_tip.json["reply"]
print("[PASS] POST /api/chat (Bengali cooking advice tip)")

r_speak = client.post("/api/speak", json={"text": "রান্না শুরু করুন"})
assert r_speak.status_code == 200
assert "audio" in r_speak.json or "fallback" in r_speak.json
print("[PASS] POST /api/speak (TTS audio/fallback generated)")

print("\n=== ALL 8 END-TO-END TESTS PASSED SUCCESSFULLY! ===")
