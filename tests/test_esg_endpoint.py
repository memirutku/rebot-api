from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.storage import store


@pytest.fixture(autouse=True)
def _reset():
    store.clear()
    yield
    store.clear()


client = TestClient(app)


def _post(
    disposal: str,
    qty: str = "1",
    invoice_number: str = "TST-1",
    date: str = "2025-04-12",
) -> dict:
    payload = {
        "invoice_number": invoice_number,
        "invoice_date": date,
        "issuer_tax_id": "1234567890",
        "issuer_name": "ACME",
        "customer_tax_id": "9876543210",
        "customer_name": "Demo KOBİ",
        "lines": [
            {
                "ewc_code": "20 03 01",
                "description": "x",
                "quantity": qty,
                "unit": "tonne",
                "disposal_method": disposal,
            }
        ],
    }
    r = client.post("/v1/ingest", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def test_esg_404_when_no_records():
    r = client.get("/v1/esg/9876543210?period=2025-Q2")
    assert r.status_code == 404


def test_esg_returns_bundle_after_ingest():
    _post("R3", qty="1")
    r = client.get("/v1/esg/9876543210?period=2025-Q2")
    assert r.status_code == 200, r.text
    b = r.json()["bundle"]
    assert b["tax_id"] == "9876543210"
    assert b["period"] == "2025-Q2"
    assert b["invoice_count"] == 1
    assert Decimal(b["total_waste_tonnes"]) == Decimal("1.000")
    assert Decimal(b["objectives"][0]["aligned_ratio"]) == Decimal("1.0000")


def test_esg_multi_invoice_aggregates():
    _post("R3", qty="3", invoice_number="A")
    _post("D1", qty="1", invoice_number="B")
    b = client.get("/v1/esg/9876543210?period=2025-Q2").json()["bundle"]
    assert b["invoice_count"] == 2
    assert Decimal(b["objectives"][0]["aligned_ratio"]) == Decimal("0.7500")


def test_esg_filters_by_quarter():
    _post("R3", qty="1", invoice_number="Q1", date="2025-02-01")
    _post("D1", qty="1", invoice_number="Q2", date="2025-04-01")
    q1 = client.get("/v1/esg/9876543210?period=2025-Q1").json()["bundle"]
    q2 = client.get("/v1/esg/9876543210?period=2025-Q2").json()["bundle"]
    assert q1["invoice_count"] == 1
    assert Decimal(q1["objectives"][0]["aligned_ratio"]) == Decimal("1.0000")
    assert q2["invoice_count"] == 1
    assert Decimal(q2["objectives"][0]["aligned_ratio"]) == Decimal("0")


def test_esg_year_only_period_returns_both_quarters():
    _post("R3", qty="1", invoice_number="A", date="2025-02-01")
    _post("R3", qty="1", invoice_number="B", date="2025-08-01")
    b = client.get("/v1/esg/9876543210?period=2025").json()["bundle"]
    assert b["invoice_count"] == 2
    assert Decimal(b["total_waste_tonnes"]) == Decimal("2.000")


def test_esg_empty_period_returns_empty_bundle_not_404():
    _post("R3", qty="1", invoice_number="A", date="2025-04-01")
    r = client.get("/v1/esg/9876543210?period=2024")
    assert r.status_code == 200
    b = r.json()["bundle"]
    assert b["invoice_count"] == 0
    assert "No ingested" in " ".join(b["notes"])


def test_esg_invalid_period_400():
    r = client.get("/v1/esg/9876543210?period=BAD")
    assert r.status_code == 400


def test_esg_invalid_tax_id_400():
    r = client.get("/v1/esg/abc?period=2025-Q2")
    assert r.status_code == 400
