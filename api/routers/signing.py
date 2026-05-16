from fastapi import APIRouter

from api.core.signing import public_key_info

router = APIRouter(tags=["signing"])


@router.get(
    "/signing/pubkey",
    summary="Get the Ed25519 verify key used to sign ESG bundles",
    description=(
        "Returns the public key in base64 along with a SHA-256 fingerprint. "
        "Use this to verify the signature attached to /v1/esg/{tax_id} responses. "
        "The signature covers the canonical JSON of the `bundle` field "
        "(sorted keys, compact, UTF-8)."
    ),
)
def get_pubkey() -> dict:
    return public_key_info()
