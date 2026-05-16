"""Ed25519 detached signatures for ESG bundles.

Signing key sources, in order of preference:
1. Environment variable ``REBOT_SIGNING_SK_B64`` — 32-byte seed, base64 encoded.
2. Auto-generated ephemeral key on first use (warning logged). Lost on
   process restart — fine for the public demo, never use this in production.

Public verification key is always retrievable via ``/v1/signing/public-key``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import threading
from datetime import UTC, datetime

from nacl import signing as nacl_signing
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

ENV_SK_B64 = "REBOT_SIGNING_SK_B64"
ALGORITHM = "Ed25519"
KEY_ID = "rebot-v1"


class SignatureInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    algorithm: str = ALGORITHM
    key_id: str = KEY_ID
    key_fingerprint_sha256: str = Field(
        description="SHA-256 of the raw 32-byte verify key (hex)"
    )
    value_b64: str = Field(description="Detached Ed25519 signature, base64 standard")
    signed_at: datetime
    payload_canonicalization: str = "json-sorted-keys-compact-utf8"


_lock = threading.Lock()
_signing_key: nacl_signing.SigningKey | None = None
_key_fingerprint: str | None = None


def _load_or_generate_key() -> nacl_signing.SigningKey:
    """Return the active signing key, loading from env or generating once."""
    global _signing_key, _key_fingerprint
    with _lock:
        if _signing_key is not None:
            return _signing_key

        b64 = os.environ.get(ENV_SK_B64)
        if b64:
            try:
                seed = base64.b64decode(b64, validate=True)
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(
                    f"Invalid {ENV_SK_B64}: must be base64 of 32-byte seed"
                ) from exc
            if len(seed) != 32:
                raise RuntimeError(
                    f"{ENV_SK_B64} must decode to 32 bytes (got {len(seed)})"
                )
            _signing_key = nacl_signing.SigningKey(seed)
            logger.info("Loaded REBOT signing key from %s", ENV_SK_B64)
        else:
            _signing_key = nacl_signing.SigningKey.generate()
            logger.warning(
                "No %s set; generated ephemeral signing key. "
                "Set the env var to pin a stable public key.",
                ENV_SK_B64,
            )

        vk_bytes = bytes(_signing_key.verify_key)
        _key_fingerprint = hashlib.sha256(vk_bytes).hexdigest()
        return _signing_key


def canonical_json(payload: dict) -> bytes:
    """Deterministic JSON: sorted keys, no whitespace, UTF-8.

    Mirrors the simpler subset of RFC 8785 (JCS). Sufficient as long as
    payloads contain only JSON-safe scalars; arrays preserve their order.
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


def sign_bundle(bundle_dict: dict) -> SignatureInfo:
    """Sign a YvoBundle.model_dump() result and return signature metadata."""
    key = _load_or_generate_key()
    payload = canonical_json(bundle_dict)
    signed = key.sign(payload)
    return SignatureInfo(
        key_fingerprint_sha256=_key_fingerprint or "",
        value_b64=base64.b64encode(signed.signature).decode("ascii"),
        signed_at=datetime.now(UTC),
    )


def verify_bundle(bundle_dict: dict, signature_b64: str, verify_key_b64: str) -> bool:
    """Verify a previously-signed bundle. Returns True if valid, False otherwise."""
    try:
        vk = nacl_signing.VerifyKey(base64.b64decode(verify_key_b64, validate=True))
        sig = base64.b64decode(signature_b64, validate=True)
        vk.verify(canonical_json(bundle_dict), sig)
        return True
    except Exception:  # noqa: BLE001
        return False


def public_key_info() -> dict:
    """Public key, fingerprint, algorithm — for /v1/signing/public-key."""
    key = _load_or_generate_key()
    vk_bytes = bytes(key.verify_key)
    return {
        "algorithm": ALGORITHM,
        "key_id": KEY_ID,
        "verify_key_b64": base64.b64encode(vk_bytes).decode("ascii"),
        "fingerprint_sha256": _key_fingerprint,
        "canonicalization": "json-sorted-keys-compact-utf8",
        "verification_example": (
            "vk = nacl.signing.VerifyKey(base64.b64decode(verify_key_b64)); "
            "vk.verify(canonical_json(bundle), base64.b64decode(signature.value_b64))"
        ),
    }
