"""Shared loader for emission-factor datasets bundled with the API."""

from __future__ import annotations

import json
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "emission_factors"


@lru_cache(maxsize=1)
def all_datasets() -> list[dict]:
    bundles = []
    for path in sorted(DATA_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as fp:
            bundles.append(json.load(fp))
    return bundles


def iter_factors() -> Iterator[dict]:
    for ds in all_datasets():
        yield from ds["factors"]


@lru_cache(maxsize=128)
def find_by_id(factor_id: str) -> dict | None:
    for f in iter_factors():
        if f["id"] == factor_id:
            return f
    return None
