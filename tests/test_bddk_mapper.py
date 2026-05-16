from decimal import Decimal

from api.core.bddk_mapper import build_bundle, map_objective_4
from api.core.parser.waste import parse_json
from api.models.invoice import WasteInvoiceIn


def _invoice(
    lines: list[dict],
    invoice_number: str = "TST-1",
    date: str = "2025-04-12",
) -> WasteInvoiceIn:
    return WasteInvoiceIn.model_validate({
        "invoice_number": invoice_number,
        "invoice_date": date,
        "issuer_tax_id": "1234567890",
        "issuer_name": "ACME Atık",
        "customer_tax_id": "9876543210",
        "customer_name": "Demo KOBİ",
        "lines": lines,
    })


def _line(disposal: str, qty: str = "1", unit: str = "tonne", ewc: str = "20 03 01") -> dict:
    return {
        "ewc_code": ewc,
        "description": "x",
        "quantity": qty,
        "unit": unit,
        "disposal_method": disposal,
    }


def test_full_recycling_yields_ratio_1():
    record = parse_json(_invoice([_line("R3")])).record
    res = map_objective_4([record])
    assert res.aligned_ratio == Decimal("1.0000")
    assert res.aligned_tonnes == Decimal("1.000")
    assert record.ingest_id in res.evidence


def test_full_landfill_yields_ratio_0():
    record = parse_json(_invoice([_line("D1")])).record
    res = map_objective_4([record])
    assert res.aligned_ratio == Decimal("0")
    assert res.aligned_tonnes == Decimal("0")


def test_energy_recovery_gets_half_credit():
    record = parse_json(_invoice([_line("R1", qty="2")])).record  # 2 t energy recovery
    res = map_objective_4([record])
    # half credit: 0.5 × 2 = 1 t aligned out of 2 t total
    assert res.aligned_ratio == Decimal("0.5000")


def test_mixed_disposal_50_50():
    record = parse_json(_invoice([_line("R3"), _line("D1")])).record  # 1 t R3 + 1 t D1
    res = map_objective_4([record])
    assert res.aligned_ratio == Decimal("0.5000")


def test_multiple_records_aggregate():
    r1 = parse_json(_invoice([_line("R3", qty="3")], invoice_number="A")).record
    r2 = parse_json(_invoice([_line("D1", qty="1")], invoice_number="B")).record
    res = map_objective_4([r1, r2])
    # 3 t aligned / 4 t total
    assert res.aligned_ratio == Decimal("0.7500")
    assert sorted(res.evidence) == sorted([r1.ingest_id, r2.ingest_id])


def test_empty_records_returns_zero():
    res = map_objective_4([])
    assert res.aligned_ratio == Decimal("0")
    assert res.total_tonnes == Decimal("0")


def test_build_bundle_aggregates_co2e_and_tonnage():
    r1 = parse_json(_invoice([_line("R3", qty="1")], invoice_number="A")).record  # 21.30 kg CO2e
    r2 = parse_json(_invoice([_line("D1", qty="1")], invoice_number="B")).record  # 580.00 kg CO2e
    bundle = build_bundle(tax_id="9876543210", period="2025-Q2", records=[r1, r2])
    assert bundle.invoice_count == 2
    assert bundle.scope_3_5_co2e_kg == Decimal("601.30")
    assert bundle.total_waste_tonnes == Decimal("2.000")
    assert bundle.objectives[0].objective_id == 4


def test_build_bundle_empty_attaches_note():
    bundle = build_bundle(tax_id="9876543210", period="2025-Q2", records=[])
    assert bundle.invoice_count == 0
    assert any("No ingested" in n for n in bundle.notes)
