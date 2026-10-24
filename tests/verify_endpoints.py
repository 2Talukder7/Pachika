import sys
import os
import re
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app import app

client = app.test_client()

print("=== VERIFYING FRONTEND FETCH URLS ===")
js_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "script.js")
with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

fetch_urls = set()
for match in re.finditer(r'fetch\(\s*[`"\']([^`"\'?]+)[`"\']', js_content):
    fetch_urls.add(match.group(1))

for match in re.finditer(r'fetch\(\s*`([^`$?]+)', js_content):
    fetch_urls.add(match.group(1))

print("Found frontend fetch URLs:", fetch_urls)

backend_rules = [rule.rule for rule in app.url_map.iter_rules()]
print("Backend registered URL patterns:")
for r in backend_rules:
    print(" -", r)

for raw_url in fetch_urls:
    url = raw_url.replace("${API_BASE}", "")
    matched = False
    for rule in app.url_map.iter_rules():
        rule_regex = rule.rule.replace('<recipe_id>', '[^/]+').replace('<path:filename>', '.*')
        if re.fullmatch(rule_regex, url):
            matched = True
            break
    print(f"URL '{raw_url}' -> '{url}' mapped to backend? {matched}")
    assert matched, f"Frontend fetch URL {raw_url} has no matching backend endpoint!"

print("\n=== VERIFYING ENDPOINTS VIA FLASK TEST CLIENT ===")

r = client.get("/")
assert r.status_code == 200, f"GET / status: {r.status_code}"
assert "<!DOCTYPE html>" in r.data.decode("utf-8") or "<html" in r.data.decode("utf-8")
r.close()
print("PASS: GET /")

r = client.get("/style.css")
assert r.status_code == 200, f"GET /style.css status: {r.status_code}"
assert "--maroon" in r.data.decode("utf-8")
r.close()
print("PASS: GET /style.css")

r = client.get("/script.js")
assert r.status_code == 200, f"GET /script.js status: {r.status_code}"
assert "function" in r.data.decode("utf-8") or "const " in r.data.decode("utf-8")
r.close()
print("PASS: GET /script.js")

r = client.get("/api/recipes")
assert r.status_code == 200
data = r.get_json()
assert "recipes" in data and len(data["recipes"]) == 31
print(f"PASS: GET /api/recipes ({len(data['recipes'])} recipes)")

r = client.get("/api/categories")
assert r.status_code == 200
cats = r.get_json().get("categories", [])
assert len(cats) > 0
print(f"PASS: GET /api/categories ({len(cats)} categories)")

r = client.get("/api/recipe/khichuri")
assert r.status_code == 200
assert r.get_json()["id"] == "khichuri"
print("PASS: GET /api/recipe/khichuri (valid)")

r = client.get("/api/recipe/non_existent_id")
assert r.status_code == 404
print("PASS: GET /api/recipe/non_existent_id (404)")

r = client.post("/api/recipe", json={"dish": "খিচুড়ি", "servings": 6})
assert r.status_code == 200
assert r.get_json()["base_servings"] == 6
print("PASS: POST /api/recipe (valid dish and servings)")

r = client.post("/api/recipe", json={"dish": "খিচুড়ি", "servings": -2})
assert r.status_code == 400
print("PASS: POST /api/recipe (negative servings -> 400)")

r = client.post("/api/recipe", json={"dish": "", "servings": 4})
assert r.status_code == 400
print("PASS: POST /api/recipe (empty dish -> 400)")

r = client.post("/api/recipe", json={"dish": "xyzunknown12345", "servings": 4})
assert r.status_code == 404
print("PASS: POST /api/recipe (unknown dish -> 404)")

r = client.post("/api/recipe/scale", json={"id": "chicken_bhuna", "servings": 8})
assert r.status_code == 200
assert r.get_json()["base_servings"] == 8
print("PASS: POST /api/recipe/scale (valid)")

r = client.post("/api/recipe/scale", json={"id": "chicken_bhuna", "servings": 0})
assert r.status_code == 400
print("PASS: POST /api/recipe/scale (0 servings -> 400)")

r = client.post("/api/recipe/scale", json={"id": "chicken_bhuna", "servings": "abc"})
assert r.status_code == 400
print("PASS: POST /api/recipe/scale (invalid servings 'abc' -> 400)")

r = client.post("/api/recipe/scale", json={"id": "", "servings": 4})
assert r.status_code == 400
print("PASS: POST /api/recipe/scale (empty id -> 400)")

r = client.post("/api/recipe/scale", json={"id": "nonexistent_dish", "servings": 4})
assert r.status_code == 404
print("PASS: POST /api/recipe/scale (unknown id -> 404)")

r = client.post("/api/suggest", json={"ingredients": ["ডিম", "আলু"]})
assert r.status_code == 200
assert len(r.get_json().get("suggestions", [])) > 0
print("PASS: POST /api/suggest (valid ingredients)")

r = client.post("/api/suggest", json={"ingredients": []})
assert r.status_code == 400
print("PASS: POST /api/suggest (empty ingredients -> 400)")

r = client.get("/api/weather/recommendations?city=Dhaka")
assert r.status_code == 200
data = r.get_json()
assert "weather_recipes" in data or "offline" in data or "error" in data or "success" in data
print("PASS: GET /api/weather/recommendations?city=Dhaka")

r = client.post("/api/weather/recommendations", json={"city": "Chittagong"})
assert r.status_code == 200
print("PASS: POST /api/weather/recommendations (json body)")

r = client.get("/api/weather/recommendations?city=NonExistentCityXYZ99999")
assert r.status_code == 400
data = r.get_json()
assert not data.get("success") and ("error" in data or "error_bn" in data)
print("PASS: GET /api/weather/recommendations (unknown city returns 400 with error details)")

r = client.post("/api/chat", json={"message": "৪ জনের জন্য খিচুড়ি"})
assert r.status_code == 200
assert "recipe" in r.get_json()
print("PASS: POST /api/chat (recipe request)")

r = client.post("/api/chat", json={"message": ""})
assert r.status_code == 200
assert "reply" in r.get_json()
print("PASS: POST /api/chat (empty message prompt)")

r = client.post("/api/chat", json={"message": "chicken"})
assert r.status_code == 200
assert "clarification_options" in r.get_json()
print("PASS: POST /api/chat (ambiguous dish clarification)")

r = client.post("/api/speak", json={"text": "স্বাগতম"})
assert r.status_code == 200
assert "audio" in r.get_json() or "fallback" in r.get_json()
print("PASS: POST /api/speak (valid text)")

r = client.post("/api/speak", json={"text": ""})
assert r.status_code == 400
print("PASS: POST /api/speak (empty text -> 400)")

print("\n=== ALL ENDPOINT CHECKS PASSED ===")
