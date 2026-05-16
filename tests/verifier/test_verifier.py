from decimal import Decimal

from api.core.verifier import verify_lines
from api.models.invoice import WasteLineItem


def _line(**overrides) -> WasteLineItem:
    payload = {
        "ewc_code": "20 03 01",
        "description": "Karışık ticari atık",
        "quantity": "1",
        "unit": "tonne",
        "disposal_method": "R3",
    }
    payload.update(overrides)
    return WasteLineItem.model_validate(payload)


def test_recycling_uses_low_factor():
    result = verify_lines([_line(disposal_method="R3")])
    assert result.line_emissions[0].factor_id == "waste.mixed_commercial.recycling"
    assert result.total_co2e_kg == Decimal("21.30")


def test_landfill_uses_high_factor():
    result = verify_lines([_line(disposal_method="D1")])
    assert result.line_emissions[0].factor_id == "waste.mixed_commercial.landfill"
    assert result.total_co2e_kg == Decimal("580.00")


def test_organic_recycling_uses_composting():
    result = verify_lines([_line(ewc_code="20 02 01", disposal_method="R3")])
    assert result.line_emissions[0].factor_id == "waste.organic.composting"
    assert result.total_co2e_kg == Decimal("8.90")


def test_incineration_uses_dedicated_factor():
    result = verify_lines([_line(disposal_method="D10")])
    assert result.line_emissions[0].factor_id == "waste.hazardous.incineration"


def test_energy_recovery_falls_through_to_incineration_with_note():
    result = verify_lines([_line(disposal_method="R1")])
    assert result.line_emissions[0].factor_id == "waste.hazardous.incineration"
    assert any("R1 energy recovery" in n for n in result.line_emissions[0].notes)


def test_unit_kg_scales_correctly():
    # 500 kg = 0.5 t × 21.3 kgCO₂e/t = 10.65
    result = verify_lines([_line(quantity="500", unit="kg", disposal_method="R3")])
    assert result.total_co2e_kg == Decimal("10.65")


def test_mixed_lines_aggregate():
    lines = [
        _line(quantity="1", unit="tonne", disposal_method="R3"),  # 21.3
        _line(quantity="500", unit="kg", disposal_method="D1"),    # 290.0
    ]
    result = verify_lines(lines)
    assert result.total_co2e_kg == Decimal("311.30")
    assert len(result.line_emissions) == 2


def test_volumetric_unit_adds_note():
    result = verify_lines([_line(quantity="100", unit="litre", disposal_method="R3")])
    note_blob = " ".join(result.line_emissions[0].notes)
    assert "Volumetric unit" in note_blob


def test_unknown_disposal_code_would_be_rejected_by_pydantic():
    # Sanity: the model itself blocks unrecognized code shapes.
    import pytest
    with pytest.raises(ValueError):
        _line(disposal_method="XX9")
