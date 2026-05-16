import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.storage import store


@pytest.fixture(autouse=True)
def _reset_store():
    store.clear()
    yield
    store.clear()


client = TestClient(app)


SAMPLE = {
    "invoice_number": "ATK-2025-00042",
    "invoice_date": "2025-04-12",
    "issuer_tax_id": "1234567890",
    "issuer_name": "ACME Atık Taşıma A.Ş.",
    "customer_tax_id": "9876543210",
    "customer_name": "Demo KOBİ Ltd.",
    "lines": [
        {
            "ewc_code": "20 03 01",
            "description": "Karışık ticari atık",
            "quantity": "2.5",
            "unit": "tonne",
            "disposal_method": "R3",
            "uatf_number": "UATF-0001",
        }
    ],
    "total_amount_try": "4250.00",
}


def test_post_ingest_returns_normalized_record():
    r = client.post("/v1/invoices", json=SAMPLE)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["invoice_type"] == "waste"
    assert body["parser_confidence"] == 1.0
    assert body["duplicate"] is False
    from decimal import Decimal
    assert Decimal(body["normalized"]["total_quantity_kg"]) == Decimal("2500")
    assert body["normalized"]["customer_tax_id"] == "9876543210"
    assert body["ingest_id"].startswith("ing_")


def test_duplicate_post_flagged_and_idempotent():
    first = client.post("/v1/invoices", json=SAMPLE).json()
    second = client.post("/v1/invoices", json=SAMPLE).json()
    assert first["ingest_id"] == second["ingest_id"]
    assert first["content_hash"] == second["content_hash"]
    assert second["duplicate"] is True


def test_get_ingest_by_id():
    posted = client.post("/v1/invoices", json=SAMPLE).json()
    ingest_id = posted["ingest_id"]
    r = client.get(f"/v1/invoices/{ingest_id}")
    assert r.status_code == 200
    assert r.json()["ingest_id"] == ingest_id


def test_get_ingest_404_for_unknown():
    r = client.get("/v1/invoices/ing_nonexistent")
    assert r.status_code == 404


def test_ingest_rejects_missing_lines():
    bad = {**SAMPLE, "lines": []}
    r = client.post("/v1/invoices", json=bad)
    assert r.status_code == 422


def test_ingest_rejects_bad_tax_id():
    bad = {**SAMPLE, "customer_tax_id": "abc"}
    r = client.post("/v1/invoices", json=bad)
    assert r.status_code == 422
