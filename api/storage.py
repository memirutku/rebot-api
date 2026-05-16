"""In-memory ingest store. Replace with SQLite/Postgres-backed impl for production."""

from __future__ import annotations

import threading
from collections.abc import Iterator

from api.models.ingest import NormalizedWasteRecord


class IngestStore:
    """Thread-safe dictionary keyed by ingest_id. Also indexes by content_hash for dedupe."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_id: dict[str, NormalizedWasteRecord] = {}
        self._by_hash: dict[str, str] = {}  # content_hash -> ingest_id

    def find_by_hash(self, content_hash: str) -> NormalizedWasteRecord | None:
        with self._lock:
            ingest_id = self._by_hash.get(content_hash)
            return self._by_id.get(ingest_id) if ingest_id else None

    def put(self, record: NormalizedWasteRecord, content_hash: str) -> None:
        with self._lock:
            self._by_id[record.ingest_id] = record
            self._by_hash[content_hash] = record.ingest_id

    def get(self, ingest_id: str) -> NormalizedWasteRecord | None:
        with self._lock:
            return self._by_id.get(ingest_id)

    def by_customer(self, customer_tax_id: str) -> Iterator[NormalizedWasteRecord]:
        with self._lock:
            records = list(self._by_id.values())
        for r in records:
            if r.customer_tax_id == customer_tax_id:
                yield r

    def clear(self) -> None:
        with self._lock:
            self._by_id.clear()
            self._by_hash.clear()


# Module-level singleton used by routers. Tests can call .clear().
store = IngestStore()
