import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest

from app import app, extract_servings, clean_dish_query


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def ask(client, message, session="t", servings=4):
    return client.post("/api/chat", json={"message": message, "servings": servings, "session_id": session}).get_json()


@pytest.mark.parametrize("text,expected", [
    ("kacchi for 3", 3),
    ("৬ জনের জন্য কাচ্চি", 6),
    ("beef curry for 5 people", 5),
    ("৪ জনের জন্য মুরগির ঝোল রান্না করতে চাই।", 4),
    ("khichuri 12 jon", 12),
    ("চার জনের জন্য পোলাও", 4),
    ("pulao for six", 6),
    ("make it for 6 people", 6),
    ("beef curry 2 kg", None),
    ("I have 3 eggs", None),
    ("make 500 gm rice", None),
    ("for 1000000 people", None),
    ("chicken for 0 people", None),
    ("khichuri", None),
])
def test_extract_servings(text, expected):
    assert extract_servings(text, None) == expected


@pytest.mark.parametrize("text,expected", [
    ("kacchi for 3", "kacchi"),
    ("৬ জনের জন্য কাচ্চি", "কাচ্চি"),
    ("৪ জনের জন্য মুরগির ঝোল রান্না করতে চাই।", "মুরগির ঝোল"),
    ("I want to cook beef curry for 5 people.", "beef curry"),
    ("how to make pulao", "pulao"),
    ("খিচুড়ি রেসিপি দাও", "খিচুড়ি"),
])
def test_clean_dish_query(text, expected):
    assert clean_dish_query(text) == expected


def test_cow_offers_beef_dishes(client):
    j = ask(client, "cow")
    assert {o["id"] for o in j["clarification_options"]} == {"beef_bhuna", "beef_curry"}


def test_kacchi_is_not_a_dead_end(client):
    j = ask(client, "kacchi for 3")
    assert "kacchi 3" not in j["reply_en"]
    assert "'kacchi'" in j["reply_en"]
    assert j["clarification_options"], "closest dishes should be offered as buttons"
    assert "chicken_biryani" in {o["id"] for o in j["clarification_options"]}


def test_bengali_kacchi_servings_not_left_in_name(client):
    j = ask(client, "৬ জনের জন্য কাচ্চি")
    assert "ের জন্য" not in j["reply"]
    assert "'কাচ্চি'" in j["reply"]
    assert j["clarification_options"]


def test_chicken_jhol_is_not_milk_tea(client):
    j = ask(client, "৪ জনের জন্য মুরগির ঝোল রান্না করতে চাই।")
    assert j["recipe"]["id"] == "chicken_curry"
    assert j["recipe"]["base_servings"] == 4


@pytest.mark.parametrize("message,dish_id,servings", [
    ("I want to cook beef curry for 5 people.", "beef_curry", 5),
    ("pulao for 2", "pulao", 2),
    ("খিচুড়ি ৩ জন", "khichuri", 3),
    ("chicken biryani 6 jon", "chicken_biryani", 6),
])
def test_recipe_requests(client, message, dish_id, servings):
    j = ask(client, message, session="r" + message)
    assert j["recipe"]["id"] == dish_id
    assert j["recipe"]["base_servings"] == servings


def test_followup_rescale_keeps_dish(client):
    ask(client, "pulao for 2", session="f")
    j = ask(client, "make it for 6 people", session="f")
    assert j["recipe"]["id"] == "pulao"
    assert j["recipe"]["base_servings"] == 6


def test_bare_tea_offers_both_teas(client):
    j = ask(client, "চা")
    assert {o["id"] for o in j["clarification_options"]} == {"cha", "lebu_cha"}


def test_requested_servings_survive_a_suggestion_click(client):
    ask(client, "kacchi for 3", session="keep")
    j = ask(client, "মুরগির বিরিয়ানি", session="keep")
    assert j["recipe"]["id"] == "chicken_biryani"
    assert j["recipe"]["base_servings"] == 3
    j2 = ask(client, "pulao", session="keep")
    assert j2["recipe"]["base_servings"] == 4


def test_ambiguous_term_remembers_servings(client):
    ask(client, "cow for 5", session="amb")
    j = ask(client, "গরুর মাংস ভুনা", session="amb")
    assert j["recipe"]["id"] == "beef_bhuna"
    assert j["recipe"]["base_servings"] == 5


def test_explicit_servings_override_remembered_ones(client):
    ask(client, "kacchi for 3", session="over")
    j = ask(client, "pulao for 8", session="over")
    assert j["recipe"]["base_servings"] == 8
