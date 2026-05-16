import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(tags=["factors"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "emission_factors"


@lru_cache(maxsize=1)
def _load_all() -> list[dict]:
    bundles = []
    for path in sorted(DATA_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as fp:
            bundles.append(json.load(fp))
    return bundles


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
    datasets = _load_all()
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
    for ds in _load_all():
        for f in ds["factors"]:
            if f["id"] == factor_id:
                return {"dataset": ds["dataset"], "factor": f, "license": "CC BY-SA 4.0"}
    raise HTTPException(404, f"Factor '{factor_id}' not found")
