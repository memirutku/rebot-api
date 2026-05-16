"""BDDK YVO (Yeşil Varlık Oranı) alignment mapper.

Maps normalized waste records to BDDK YVO Ek-1 environmental objectives.
Currently implements Objective 4 (Transition to circular economy) with a
tonnage-based alignment ratio. Revenue-weighted alignment requires invoice
amount data and per-objective taxonomy rules from the regulator — both
deferred to a later revision.

This data contract is the public interoperability surface for banks; bump
the major version of schemas/esg_bundle.schema.json on any breaking change.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from api.core.signing import SignatureInfo
from api.core.verifier import VerifierResult
from api.models.ingest import NormalizedWasteRecord

# Disposal/recovery code categorization for circular-economy alignment.
# Source: EU Waste Framework Directive 2008/98/EC Annex I/II + sector practice.
FULL_CREDIT_CODES = {"R3", "R4", "R5"}      # Material recycling
HALF_CREDIT_CODES = {"R1"}                  # Energy recovery (partial CE)
NOT_ALIGNED_CODES = {"D1", "D5", "D10", "D11"}


class ObjectiveAlignment(BaseModel):
    """Single BDDK YVO Ek-1 objective alignment result."""

    model_config = ConfigDict(extra="forbid")

    objective_id: int = Field(ge=1, le=6)
    objective_name_tr: str
    objective_name_en: str
    aligned_tonnes: Decimal = Field(ge=0)
    total_tonnes: Decimal = Field(ge=0)
    aligned_ratio: Decimal = Field(
        ge=0, le=1, description="Tonnage-weighted alignment in [0, 1]"
    )
    methodology: str
    evidence: list[str] = Field(
        default_factory=list,
        description="List of ingest_id references that fed this calculation",
    )


class YvoBundle(BaseModel):
    """Public data contract — bank-facing ESG bundle for a single SME period."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "0.1.0"
    tax_id: str
    period: str = Field(description="ISO-ish period label, e.g. '2025-Q2' or '2025'")
    invoice_count: int = Field(ge=0)
    total_waste_tonnes: Decimal = Field(ge=0)
    scope_3_5_co2e_kg: Decimal = Field(ge=0)
    objectives: list[ObjectiveAlignment]
    notes: list[str] = Field(default_factory=list)


def _classify_record(record: NormalizedWasteRecord) -> tuple[Decimal, Decimal, Decimal]:
    """Return (full_credit_tonnes, half_credit_tonnes, total_tonnes) for a record.

    Tonnage attribution is uniform across the record's lines: we use line-level
    quantities from the verifier (line_emissions) since they carry per-line
    disposal codes and tonnages computed at ingest time.
    """
    if record.emissions is None:
        # No verifier output; can't classify reliably.
        return Decimal("0"), Decimal("0"), Decimal("0")

    full = Decimal("0")
    half = Decimal("0")
    total = Decimal("0")
    for le in record.emissions.line_emissions:
        total += le.quantity_tonnes
        if le.disposal_method in FULL_CREDIT_CODES:
            full += le.quantity_tonnes
        elif le.disposal_method in HALF_CREDIT_CODES:
            half += le.quantity_tonnes
        # NOT_ALIGNED_CODES contribute to total but not to aligned counters
    return full, half, total


def map_objective_4(records: list[NormalizedWasteRecord]) -> ObjectiveAlignment:
    """YVO Objective 4 — Transition to circular economy."""
    full_total = Decimal("0")
    half_total = Decimal("0")
    grand_total = Decimal("0")
    evidence: list[str] = []

    for record in records:
        full, half, total = _classify_record(record)
        full_total += full
        half_total += half
        grand_total += total
        if total > 0:
            evidence.append(record.ingest_id)

    aligned = full_total + (half_total * Decimal("0.5"))
    aligned_ratio = (
        (aligned / grand_total).quantize(Decimal("0.0001"))
        if grand_total > 0
        else Decimal("0")
    )

    return ObjectiveAlignment(
        objective_id=4,
        objective_name_tr="Döngüsel ekonomiye geçiş",
        objective_name_en="Transition to a circular economy",
        aligned_tonnes=aligned.quantize(Decimal("0.001")),
        total_tonnes=grand_total.quantize(Decimal("0.001")),
        aligned_ratio=aligned_ratio,
        methodology=(
            "Tonnage-weighted: R3/R4/R5 → 1.0 credit, R1 → 0.5 credit, "
            "D1/D5/D10/D11 → 0.0. Revenue-weighted alignment deferred to v1.0."
        ),
        evidence=evidence,
    )


def build_bundle(
    tax_id: str,
    period: str,
    records: list[NormalizedWasteRecord],
) -> YvoBundle:
    """Aggregate normalized waste records into a YVO bundle for one period."""
    total_tonnes = Decimal("0")
    total_co2e = Decimal("0")
    for r in records:
        if r.emissions is not None:
            total_co2e += r.emissions.total_co2e_kg
            for le in r.emissions.line_emissions:
                total_tonnes += le.quantity_tonnes

    objective4 = map_objective_4(records)
    notes: list[str] = []
    if not records:
        notes.append("No ingested waste invoices for this tax_id and period.")

    return YvoBundle(
        tax_id=tax_id,
        period=period,
        invoice_count=len(records),
        total_waste_tonnes=total_tonnes.quantize(Decimal("0.001")),
        scope_3_5_co2e_kg=total_co2e.quantize(Decimal("0.01")),
        objectives=[objective4],
        notes=notes,
    )


class SignedYvoBundle(BaseModel):
    """Bundle + detached Ed25519 signature. The signature covers a canonical
    JSON serialization of the ``bundle`` field only."""

    model_config = ConfigDict(extra="forbid")

    bundle: YvoBundle
    signature: SignatureInfo


# Helper kept for symmetry with verifier; not currently consumed elsewhere.
__all__ = [
    "ObjectiveAlignment",
    "YvoBundle",
    "SignedYvoBundle",
    "VerifierResult",  # re-export for typing in other modules
    "map_objective_4",
    "build_bundle",
]
