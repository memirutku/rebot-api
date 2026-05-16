"""Shared loader for the EWC (European Waste Catalogue) Turkish catalogue."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "waste_codes"
    / "ewc_tr.json"
)


@lru_cache(maxsize=1)
def catalogue() -> dict:
    with DATA_PATH.open(encoding="utf-8") as fp:
        return json.load(fp)


def all_codes() -> list[dict]:
    return catalogue()["codes"]


@lru_cache(maxsize=256)
def find(code: str) -> dict | None:
    # Normalize to "XX XX XX"
    compact = code.replace(" ", "")
    if not (compact.isdigit() and len(compact) == 6):
        return None
    canonical = f"{compact[0:2]} {compact[2:4]} {compact[4:6]}"
    for c in all_codes():
        if c["code"] == canonical:
            return c
    return None


def is_organic(code: str) -> bool:
    """True if EWC code typically represents biodegradable / organic waste.

    Used by the verifier to route recycling-coded organic waste to the
    composting emission factor instead of mixed recycling.
    """
    entry = find(code)
    if entry is None:
        return False
    desc = (entry.get("description_tr", "") + " " + entry.get("description_en", "")).lower()
    return "biyobozun" in desc or "biodegradable" in desc or "organic" in desc
