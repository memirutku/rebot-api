"""Waste-transport invoice parser.

The JSON pathway is fully deterministic; PDF parsing is a stub until anonymized
sample invoices are available. See ROADMAP in README.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

from api.core.verifier import verify_lines
from api.models.ingest import NormalizedWasteRecord
from api.models.invoice import WasteInvoiceIn

# Conversion factors to kilograms.
# litre/m3 → kg: assumed water-equivalent density (1.0). Real-world densities vary
# by waste stream; parser_confidence is reduced when this assumption is applied.
UNIT_TO_KG: dict[str, Decimal] = {
    "kg": Decimal("1"),
    "tonne": Decimal("1000"),
    "litre": Decimal("1"),
    "m3": Decimal("1000"),
}

UNITS_WITH_FULL_CONFIDENCE = {"kg", "tonne"}


class ParseResult:
    __slots__ = ("record", "content_hash", "parser_confidence")

    def __init__(
        self,
        record: NormalizedWasteRecord,
        content_hash: str,
        parser_confidence: float,
    ) -> None:
        self.record = record
        self.content_hash = content_hash
        self.parser_confidence = parser_confidence


def _canonical_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _quarter(month: int) -> int:
    return (month - 1) // 3 + 1


def parse_json(invoice: WasteInvoiceIn) -> ParseResult:
    """Normalize a structured waste invoice payload.

    Confidence is 1.0 when all line items are in kg/tonne, 0.7 if any line uses a
    volumetric unit (litre/m3) that requires a density assumption.
    """
    total_kg = Decimal("0")
    ewc_codes: list[str] = []
    disposal_methods: list[str] = []
    has_volumetric = False

    for line in invoice.lines:
        factor = UNIT_TO_KG[line.unit]
        total_kg += line.quantity * factor
        ewc_codes.append(line.ewc_code)
        disposal_methods.append(line.disposal_method)
        if line.unit not in UNITS_WITH_FULL_CONFIDENCE:
            has_volumetric = True

    content_hash = _canonical_hash(invoice.model_dump(mode="json"))
    ingest_id = f"ing_{content_hash[:16]}"
    emissions = verify_lines(invoice.lines)

    record = NormalizedWasteRecord(
        ingest_id=ingest_id,
        customer_tax_id=invoice.customer_tax_id,
        issuer_tax_id=invoice.issuer_tax_id,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        period_year=invoice.invoice_date.year,
        period_quarter=_quarter(invoice.invoice_date.month),
        line_count=len(invoice.lines),
        total_quantity_kg=total_kg,
        ewc_codes=sorted(set(ewc_codes)),
        disposal_methods=sorted(set(disposal_methods)),
        emissions=emissions,
    )

    confidence = 0.7 if has_volumetric else 1.0
    return ParseResult(record=record, content_hash=content_hash, parser_confidence=confidence)


def parse_pdf(_file_bytes: bytes) -> ParseResult:
    """Reserved for PDF/OCR pathway. Implementation deferred until anonymized
    sample invoices from licensed Turkish waste carriers are available."""
    raise NotImplementedError(
        "PDF parsing not yet implemented. Send structured JSON to POST /v1/invoices. "
        "See https://github.com/memirutku/rebot-api/issues for progress."
    )
