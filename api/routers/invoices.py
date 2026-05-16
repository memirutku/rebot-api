from fastapi import APIRouter, HTTPException, status

from api.core.parser import waste as waste_parser
from api.models.ingest import IngestResponse, NormalizedWasteRecord
from api.models.invoice import WasteInvoiceIn
from api.storage import store

router = APIRouter(tags=["invoices"])


@router.post(
    "/invoices",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a structured invoice payload",
    description=(
        "Accepts a structured JSON invoice (currently `invoice_type=waste`). "
        "Returns a normalized record with a stable `ingest_id` derived from the "
        "SHA-256 of the canonical payload — re-posting the same invoice yields "
        "the same id and is flagged as `duplicate=true`."
    ),
)
def create_invoice(invoice: WasteInvoiceIn) -> IngestResponse:
    if invoice.invoice_type != "waste":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported invoice_type '{invoice.invoice_type}'. "
            f"Currently only 'waste' is implemented. See ROADMAP.",
        )

    result = waste_parser.parse_json(invoice)

    existing = store.find_by_hash(result.content_hash)
    duplicate = existing is not None

    if not duplicate:
        store.put(result.record, result.content_hash)

    return IngestResponse(
        ingest_id=result.record.ingest_id,
        invoice_type=invoice.invoice_type,
        normalized=result.record,
        content_hash=result.content_hash,
        parser_confidence=result.parser_confidence,
        duplicate=duplicate,
    )


@router.get(
    "/invoices/{ingest_id}",
    response_model=NormalizedWasteRecord,
    summary="Retrieve a previously submitted invoice",
)
def get_invoice(ingest_id: str) -> NormalizedWasteRecord:
    record = store.get(ingest_id)
    if record is None:
        raise HTTPException(404, f"invoice '{ingest_id}' not found")
    return record
