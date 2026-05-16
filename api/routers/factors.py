from fastapi import APIRouter, HTTPException, Query

from api.core import factors as factors_core

router = APIRouter(tags=["factors"])


@router.get("/factors", summary="List emission factor datasets")
def list_factors(
    scope: str | None = Query(
        default=None,
        description="Filter by GHG Protocol scope: '1', '2', or '3' (substring match)",
        examples=["2"],
    ),
    region: str | None = Query(
        default=None,
        description="ISO 3166-1 alpha-2 region filter (e.g. 'TR')",
        examples=["TR"],
    ),
) -> dict:
    datasets = factors_core.all_datasets()
    if not datasets:
        raise HTTPException(503, "Emission factor catalogue not loaded")

    out_datasets = []
    for ds in datasets:
        filtered = ds["factors"]
        if scope is not None:
            filtered = [f for f in filtered if f.get("ghg_scope", "").startswith(scope)]
        if region is not None:
            filtered = [f for f in filtered if f.get("region", "").upper() == region.upper()]
        if not filtered:
            continue
        out_datasets.append({**ds, "factors": filtered})

    return {
        "license": "CC BY-SA 4.0",
        "datasets": out_datasets,
        "total_factors": sum(len(d["factors"]) for d in out_datasets),
    }


@router.get("/factors/{factor_id}", summary="Get a single emission factor by id")
def get_factor(factor_id: str) -> dict:
    factor = factors_core.find_by_id(factor_id)
    if factor is None:
        raise HTTPException(404, f"Factor '{factor_id}' not found")
    # Find owning dataset for citation context
    for ds in factors_core.all_datasets():
        if factor in ds["factors"]:
            return {"dataset": ds["dataset"], "factor": factor, "license": "CC BY-SA 4.0"}
    return {"dataset": "unknown", "factor": factor, "license": "CC BY-SA 4.0"}
