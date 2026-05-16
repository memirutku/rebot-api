import re

from fastapi import APIRouter, HTTPException, Query

from api.core.bddk_mapper import YvoBundle, build_bundle
from api.models.ingest import NormalizedWasteRecord
from api.storage import store

router = APIRouter(tags=["esg"])

PERIOD_RE = re.compile(r"^(\d{4})(?:-Q([1-4]))?$")


def _parse_period(period: str) -> tuple[int, int | None]:
    m = PERIOD_RE.match(period)
    if not m:
        raise HTTPException(
            400,
            f"Invalid period '{period}'. Expected 'YYYY' or 'YYYY-Q[1-4]', e.g. '2025-Q2'.",
        )
    year = int(m.group(1))
    quarter = int(m.group(2)) if m.group(2) else None
    return year, quarter


def _matches_period(record: NormalizedWasteRecord, year: int, quarter: int | None) -> bool:
    if record.period_year != year:
        return False
    return not (quarter is not None and record.period_quarter != quarter)


@router.get(
    "/esg/{tax_id}",
    response_model=YvoBundle,
    summary="BDDK YVO bundle for an SME's reporting period",
    description=(
        "Aggregates all previously ingested waste invoices for the given Turkish tax "
        "id and returns a BDDK YVO Ek-1 aligned ESG bundle (currently Objective 4 — "
        "Transition to circular economy). Period accepts year-only ('2025') or "
        "year-quarter ('2025-Q2'). Returns 404 if no records exist for the tax id."
    ),
)
def get_esg_bundle(
    tax_id: str,
    period: str = Query(
        ...,
        description="Reporting period: 'YYYY' or 'YYYY-Q[1-4]'",
        examples=["2025-Q2", "2025"],
    ),
) -> YvoBundle:
    if not tax_id.isdigit() or len(tax_id) not in (10, 11):
        raise HTTPException(
            400,
            f"Invalid tax_id '{tax_id}'. Expected 10-digit VKN or 11-digit TC kimlik.",
        )

    year, quarter = _parse_period(period)

    all_for_customer = list(store.by_customer(tax_id))
    if not all_for_customer:
        raise HTTPException(
            404,
            f"No ingested records for tax_id '{tax_id}'. POST invoices to /v1/ingest first.",
        )

    filtered = [r for r in all_for_customer if _matches_period(r, year, quarter)]
    if not filtered:
        # Return an empty bundle rather than 404 — caller knows tax_id exists but
        # has no data in the requested period.
        return build_bundle(tax_id=tax_id, period=period, records=[])

    return build_bundle(tax_id=tax_id, period=period, records=filtered)
