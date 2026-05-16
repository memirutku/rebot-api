"""Smoke tests for the bilingual OpenAPI spec."""

from fastapi.testclient import TestClient

from api.i18n import EN_TO_TR
from api.main import app

client = TestClient(app)


def test_default_openapi_is_turkish():
    spec = client.get("/openapi.json").json()
    assert "KOBİ" in spec["info"]["description"] or "Türk" in spec["info"]["description"]


def test_en_openapi_is_english():
    spec = client.get("/openapi.en.json").json()
    assert "SME" in spec["info"]["description"]


def test_tr_translates_path_summaries():
    spec = client.get("/openapi.tr.json").json()
    health = spec["paths"]["/health"]["get"]["summary"]
    assert health == "Sağlık kontrolü"


def test_tr_translates_field_descriptions():
    spec = client.get("/openapi.tr.json").json()
    waste_line = spec["components"]["schemas"]["WasteLineItem"]
    ewc_field = waste_line["properties"]["ewc_code"]
    # Translated description
    assert "Avrupa Atık Kataloğu" in ewc_field["description"]


def test_tr_translates_pydantic_titles():
    spec = client.get("/openapi.tr.json").json()
    waste_line = spec["components"]["schemas"]["WasteLineItem"]
    quantity_title = waste_line["properties"]["quantity"]["title"]
    assert quantity_title == "Miktar"


def test_tr_translates_query_parameter_descriptions():
    spec = client.get("/openapi.tr.json").json()
    factors = spec["paths"]["/v1/emission-factors"]["get"]
    region_param = next(p for p in factors["parameters"] if p["name"] == "region")
    assert "bölge" in region_param["description"].lower()


def test_en_keeps_english_summaries():
    spec = client.get("/openapi.en.json").json()
    health = spec["paths"]["/health"]["get"]["summary"]
    assert health == "Liveness probe"


def test_docs_default_is_turkish():
    html = client.get("/docs").text
    assert "API Dokümantasyonu" in html
    assert "/openapi.tr.json" in html
    assert 'class="active"' in html


def test_docs_with_lang_en_is_english():
    html = client.get("/docs?lang=en").text
    assert "API documentation" in html
    assert "/openapi.en.json" in html


def test_tr_has_no_residual_english_in_descriptions():
    """No description in the TR spec should contain obvious English glue
    words (heuristic but cheap regression guard)."""
    spec = client.get("/openapi.tr.json").json()
    english_giveaways = {"the", "and", "with", "for", "or "}

    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "description" and isinstance(v, str):
                    lc = v.lower()
                    has_english = any(f" {w} " in f" {lc} " for w in english_giveaways)
                    has_safe = any(t in v for t in ("``", "Apache", "CC BY-SA", "REBOT"))
                    if has_english and not has_safe:
                        yield v
                else:
                    yield from walk(v)
        elif isinstance(obj, list):
            for item in obj:
                yield from walk(item)

    leaks = list(walk(spec))
    assert leaks == [], f"English leaks in TR spec: {leaks[:3]}"


def test_translation_dict_has_no_dangling_unicode_issues():
    # All values should be non-empty strings
    for en, trval in EN_TO_TR.items():
        assert isinstance(trval, str) and trval, f"Bad translation for {en!r}"
