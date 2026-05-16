from decimal import Decimal

import pytest

from api.core.parser import waste as waste_parser
from api.models.invoice import WasteInvoiceIn


def _sample_invoice(**overrides) -> WasteInvoiceIn:
    payload = {
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
    payload.update(overrides)
    return WasteInvoiceIn.model_validate(payload)


def test_parse_json_happy_path():
    invoice = _sample_invoice()
    result = waste_parser.parse_json(invoice)
    assert result.parser_confidence == 1.0
    assert result.record.total_quantity_kg == Decimal("2500")
    assert result.record.period_year == 2025
    assert result.record.period_quarter == 2
    assert result.record.ewc_codes == ["20 03 01"]
    assert result.record.disposal_methods == ["R3"]
    assert result.record.ingest_id.startswith("ing_")


def test_parse_json_is_deterministic():
    a = waste_parser.parse_json(_sample_invoice())
    b = waste_parser.parse_json(_sample_invoice())
    assert a.content_hash == b.content_hash
    assert a.record.ingest_id == b.record.ingest_id


def test_volumetric_unit_reduces_confidence():
    invoice = _sample_invoice(
        lines=[
            {
                "ewc_code": "200301",
                "description": "Sıvı atık",
                "quantity": "100",
                "unit": "litre",
                "disposal_method": "D10",
            }
        ]
    )
    result = waste_parser.parse_json(invoice)
    assert result.parser_confidence == 0.7
    assert result.record.total_quantity_kg == Decimal("100")


def test_ewc_code_normalization():
    invoice = _sample_invoice(
        lines=[
            {
                "ewc_code": "200301",  # no spaces in
                "description": "x",
                "quantity": "1",
                "unit": "kg",
                "disposal_method": "R3",
            }
        ]
    )
    result = waste_parser.parse_json(invoice)
    assert result.record.ewc_codes == ["20 03 01"]


def test_pdf_parser_is_not_implemented():
    with pytest.raises(NotImplementedError):
        waste_parser.parse_pdf(b"\x25PDF-1.4 fake")


def test_invalid_ewc_code_rejected():
    with pytest.raises(ValueError):
        _sample_invoice(
            lines=[
                {
                    "ewc_code": "BAD",
                    "description": "x",
                    "quantity": "1",
                    "unit": "kg",
                    "disposal_method": "R3",
                }
            ]
        )


def test_invalid_disposal_code_rejected():
    with pytest.raises(ValueError):
        _sample_invoice(
            lines=[
                {
                    "ewc_code": "200301",
                    "description": "x",
                    "quantity": "1",
                    "unit": "kg",
                    "disposal_method": "X99",
                }
            ]
        )
