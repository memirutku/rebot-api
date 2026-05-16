from fastapi.testclient import TestClient

from api.core import waste_codes as catalogue
from api.main import app

client = TestClient(app)


def test_list_default_returns_full_catalogue():
    r = client.get("/v1/waste-codes")
    assert r.status_code == 200
    body = r.json()
    assert body["license"] == "CC BY-SA 4.0"
    assert body["total_in_catalogue"] >= 80
    assert body["returned"] >= 80
    assert len(body["chapters"]) >= 10


def test_filter_by_chapter():
    r = client.get("/v1/waste-codes?chapter=20")
    assert r.status_code == 200
    body = r.json()
    for c in body["codes"]:
        assert c["code"].startswith("20 ")


def test_filter_hazardous_true_only():
    r = client.get("/v1/waste-codes?hazardous=true")
    assert r.status_code == 200
    for c in r.json()["codes"]:
        assert c["hazardous"] is True


def test_search_finds_plastik():
    r = client.get("/v1/waste-codes?q=plastik")
    assert r.status_code == 200
    body = r.json()
    assert body["returned"] >= 1
    assert any("plastik" in c["description_tr"].lower() for c in body["codes"])


def test_search_finds_in_english_too():
    r = client.get("/v1/waste-codes?q=concrete")
    assert r.status_code == 200
    assert r.json()["returned"] >= 1


def test_invalid_chapter_pattern_422():
    r = client.get("/v1/waste-codes?chapter=ABC")
    assert r.status_code == 422


def test_lookup_spaced():
    r = client.get("/v1/waste-codes/20 03 01")
    assert r.status_code == 200
    assert r.json()["code"]["description_tr"].startswith("Karışık belediye")


def test_lookup_compact():
    r = client.get("/v1/waste-codes/200301")
    assert r.status_code == 200
    assert r.json()["code"]["code"] == "20 03 01"


def test_lookup_unknown_404():
    r = client.get("/v1/waste-codes/999999")
    assert r.status_code == 404


def test_lookup_invalid_format_404():
    r = client.get("/v1/waste-codes/abc")
    assert r.status_code == 404


def test_is_organic_helper_routes_food_waste_to_composting():
    # Verifier now consults the EWC catalogue via is_organic()
    assert catalogue.is_organic("20 01 08") is True   # biodegradable kitchen waste
    assert catalogue.is_organic("20 02 01") is True   # biodegradable garden waste
    assert catalogue.is_organic("20 03 01") is False  # mixed municipal
    assert catalogue.is_organic("999999") is False    # unknown
