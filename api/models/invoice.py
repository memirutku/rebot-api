"""Inbound invoice payload models — what KOBİs / their accountants send us."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

# EWC (European Waste Catalogue) code: 6 digits, often shown as "XX XX XX" or "XXXXXX".
# Source: Commission Decision 2014/955/EU.
EwcCode = Annotated[
    str,
    StringConstraints(min_length=6, max_length=8, pattern=r"^\d{2}\s?\d{2}\s?\d{2}$"),
    Field(description="European Waste Catalogue code, e.g. '20 03 01' or '200301'"),
]

# Turkish tax id: 10 digits (corporate) or 11 digits (natural person TC kimlik).
TaxId = Annotated[
    str,
    StringConstraints(min_length=10, max_length=11, pattern=r"^\d{10,11}$"),
    Field(description="Turkish tax id (10-digit VKN or 11-digit TC kimlik)"),
]

# Disposal/recovery codes from Annex I and II of Directive 2008/98/EC.
# Examples: D1 (landfill), D10 (incineration on land), R1 (energy recovery), R3 (recycling).
DisposalCode = Annotated[
    str,
    StringConstraints(min_length=2, max_length=3, pattern=r"^[DR]\d{1,2}$"),
    Field(
        description="Disposal (D) or Recovery (R) operation code per EU Waste Framework Directive"
    ),
]

Unit = Literal["kg", "tonne", "litre", "m3"]


class WasteLineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ewc_code: EwcCode
    description: str = Field(min_length=1, max_length=200)
    quantity: Decimal = Field(gt=0, description="Quantity in the unit specified")
    unit: Unit
    disposal_method: DisposalCode
    uatf_number: str | None = Field(
        default=None,
        max_length=32,
        description="Ulusal Atık Taşıma Formu (UATF) reference, if available",
    )

    @field_validator("ewc_code")
    @classmethod
    def normalize_ewc(cls, v: str) -> str:
        compact = v.replace(" ", "")
        return f"{compact[0:2]} {compact[2:4]} {compact[4:6]}"


class WasteInvoiceIn(BaseModel):
    """A single waste-transport invoice from a licensed carrier to an SME."""

    model_config = ConfigDict(extra="forbid")

    invoice_type: Literal["waste"] = "waste"
    invoice_number: str = Field(min_length=1, max_length=64)
    invoice_date: date
    issuer_tax_id: TaxId = Field(description="Waste carrier (issuer of invoice)")
    issuer_name: str = Field(min_length=1, max_length=200)
    customer_tax_id: TaxId = Field(description="SME receiving the service (ESG subject)")
    customer_name: str = Field(min_length=1, max_length=200)
    lines: list[WasteLineItem] = Field(min_length=1, max_length=200)
    total_amount_try: Decimal | None = Field(default=None, ge=0)
