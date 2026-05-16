"""Internal normalized records and ingest API response model."""

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class NormalizedWasteRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ingest_id: str
    invoice_type: Literal["waste"] = "waste"
    customer_tax_id: str
    issuer_tax_id: str
    invoice_number: str
    invoice_date: date
    period_year: int
    period_quarter: int = Field(ge=1, le=4)
    line_count: int = Field(ge=1)
    total_quantity_kg: Decimal = Field(ge=0)
    ewc_codes: list[str]
    disposal_methods: list[str]
    received_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class IngestResponse(BaseModel):
    ingest_id: str
    invoice_type: str
    normalized: NormalizedWasteRecord
    content_hash: str = Field(description="SHA-256 of the canonical input payload")
    parser_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="1.0 for structured JSON; <1.0 for PDF/OCR-derived data",
    )
    duplicate: bool = Field(
        default=False,
        description="True if a payload with the same content hash was previously ingested",
    )
