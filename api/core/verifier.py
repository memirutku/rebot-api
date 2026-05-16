"""GHG Protocol Scope 3.5 emissions verifier for waste records.

Pure-function module: given a normalized record (or raw lines), returns
per-line and aggregate kgCO₂e using the bundled DEFRA 2024 factor catalogue.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from pydantic import BaseModel, Field

from api.core import factors as factors_core
from api.models.invoice import WasteLineItem

# Conservative fallback used when no specific factor matches. Equivalent to
# treating unknown disposal/recovery as mixed-commercial landfill.
FALLBACK_FACTOR_ID = "waste.mixed_commercial.landfill"

# Disposal/recovery code semantics from EU Waste Framework Directive (2008/98/EC).
# R-codes are recovery operations, D-codes are disposal. We map to DEFRA buckets.
RECYCLING_CODES = {"R3", "R4", "R5"}  # Material recycling
ENERGY_RECOVERY_CODES = {"R1"}        # Energy recovery
LANDFILL_CODES = {"D1", "D5"}
INCINERATION_CODES = {"D10", "D11"}

# EWC prefixes (2-digit chapter) that indicate organic / biodegradable waste.
ORGANIC_EWC_PREFIXES = {"02", "03"}  # agriculture, food, wood
ORGANIC_EWC_CODES_BIO = {"20 01 08", "20 02 01"}  # kitchen biodegradable, garden waste

UNIT_TO_TONNES: dict[str, Decimal] = {
    "kg": Decimal("0.001"),
    "tonne": Decimal("1"),
    "litre": Decimal("0.001"),  # water-equivalent density
    "m3": Decimal("1"),         # water-equivalent density
}


class LineEmission(BaseModel):
    line_index: int
    ewc_code: str
    disposal_method: str
    quantity_tonnes: Decimal
    factor_id: str
    factor_value: Decimal = Field(description="kgCO₂e per tonne")
    co2e_kg: Decimal
    notes: list[str] = Field(default_factory=list)


class VerifierResult(BaseModel):
    total_co2e_kg: Decimal
    ghg_scope: str = "3.5"
    factor_dataset: str = "defra_2024"
    line_emissions: list[LineEmission]
    warnings: list[str] = Field(default_factory=list)


def _pick_factor_id(line: WasteLineItem) -> tuple[str, list[str]]:
    """Return (factor_id, notes). Notes explain non-obvious choices."""
    notes: list[str] = []
    code = line.disposal_method
    ewc = line.ewc_code

    if code in LANDFILL_CODES:
        return "waste.mixed_commercial.landfill", notes

    if code in INCINERATION_CODES:
        return "waste.hazardous.incineration", notes

    if code in ENERGY_RECOVERY_CODES:
        # Energy recovery still releases CO₂; use incineration factor as proxy.
        notes.append("R1 energy recovery mapped to incineration factor (no credit applied)")
        return "waste.hazardous.incineration", notes

    if code in RECYCLING_CODES:
        ewc_compact = ewc.replace(" ", "")
        prefix = ewc_compact[:2]
        if ewc in ORGANIC_EWC_CODES_BIO or prefix in ORGANIC_EWC_PREFIXES:
            return "waste.organic.composting", notes
        return "waste.mixed_commercial.recycling", notes

    notes.append(f"Unknown disposal code '{code}'; applying conservative landfill fallback")
    return FALLBACK_FACTOR_ID, notes


def verify_lines(lines: Iterable[WasteLineItem]) -> VerifierResult:
    """Compute Scope 3.5 emissions for an iterable of waste line items."""
    line_emissions: list[LineEmission] = []
    warnings: list[str] = []
    total = Decimal("0")

    for idx, line in enumerate(lines):
        tonnes = (line.quantity * UNIT_TO_TONNES[line.unit]).quantize(Decimal("0.000001"))
        factor_id, notes = _pick_factor_id(line)
        factor = factors_core.find_by_id(factor_id)
        if factor is None:
            # Should never happen for bundled ids, but stay defensive.
            warnings.append(f"line {idx}: factor '{factor_id}' missing from catalogue; skipped")
            continue

        factor_value = Decimal(str(factor["value"]))
        co2e_kg = (tonnes * factor_value).quantize(Decimal("0.01"))
        total += co2e_kg

        if line.unit in {"litre", "m3"}:
            notes.append(
                "Volumetric unit converted using water-equivalent density (1.0 t/m³ assumed)"
            )

        line_emissions.append(
            LineEmission(
                line_index=idx,
                ewc_code=line.ewc_code,
                disposal_method=line.disposal_method,
                quantity_tonnes=tonnes,
                factor_id=factor_id,
                factor_value=factor_value,
                co2e_kg=co2e_kg,
                notes=notes,
            )
        )

    return VerifierResult(
        total_co2e_kg=total.quantize(Decimal("0.01")),
        line_emissions=line_emissions,
        warnings=warnings,
    )
