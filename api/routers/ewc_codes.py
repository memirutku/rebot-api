from fastapi import APIRouter, HTTPException, Query

from api.core import waste_codes as catalogue

router = APIRouter(tags=["ewc-codes"])


@router.get(
    "/ewc-codes",
    summary="List EWC waste codes (Turkish + English)",
    description=(
        "European Waste Catalogue (EU 2014/955) Turkish-language subset focused on "
        "SME-relevant chapters (15 packaging, 17 C&D, 20 municipal, etc.). "
        "Returns the chapter index along with codes; supports filtering by chapter, "
        "hazardous flag, and free-text search across descriptions."
    ),
)
def list_codes(
    chapter: str | None = Query(
        default=None,
        description="2-digit chapter prefix (e.g. '15', '17', '20')",
        examples=["15"],
        pattern=r"^\d{2}$",
    ),
    hazardous: bool | None = Query(
        default=None,
        description="Filter by hazardous flag (true = '*' codes in EU EWC)",
    ),
    q: str | None = Query(
        default=None,
        description="Case-insensitive substring search across Turkish + English descriptions",
        examples=["plastik"],
        min_length=2,
    ),
    limit: int = Query(default=200, ge=1, le=1000),
) -> dict:
    cat = catalogue.catalogue()
    codes = catalogue.all_codes()

    if chapter is not None:
        codes = [c for c in codes if c["code"].startswith(chapter + " ")]
    if hazardous is not None:
        codes = [c for c in codes if c["hazardous"] == hazardous]
    if q is not None:
        needle = q.lower()
        codes = [
            c
            for c in codes
            if needle in c["description_tr"].lower()
            or needle in c["description_en"].lower()
        ]

    return {
        "dataset": cat["dataset"],
        "version": cat["version"],
        "license": "CC BY-SA 4.0",
        "chapters": cat["chapters"],
        "total_in_catalogue": len(cat["codes"]),
        "returned": len(codes[:limit]),
        "codes": codes[:limit],
    }


@router.get(
    "/ewc-codes/{code}",
    summary="Look up a single EWC code",
    description="Accepts the spaced form '20 03 01' or the compact form '200301'.",
)
def get_code(code: str) -> dict:
    entry = catalogue.find(code)
    if entry is None:
        raise HTTPException(404, f"EWC code '{code}' not in catalogue subset")
    return {"license": "CC BY-SA 4.0", "code": entry}
