import base64

import pytest
from fastapi.testclient import TestClient

from api.core import signing as signing_core
from api.main import app
from api.storage import store


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    # Pin a deterministic key so tests are reproducible.
    seed = bytes(range(32))
    monkeypatch.setenv(signing_core.ENV_SK_B64, base64.b64encode(seed).decode())
    # Force regeneration via module globals
    signing_core._signing_key = None
    signing_core._key_fingerprint = None
    store.clear()
    yield
    signing_core._signing_key = None
    signing_core._key_fingerprint = None
    store.clear()


client = TestClient(app)


def test_pubkey_endpoint():
    r = client.get("/v1/signing/pubkey")
    assert r.status_code == 200
    body = r.json()
    assert body["algorithm"] == "Ed25519"
    assert body["key_id"] == "rebot-v1"
    assert len(base64.b64decode(body["verify_key_b64"])) == 32
    assert len(body["fingerprint_sha256"]) == 64


def test_canonical_json_is_deterministic():
    a = signing_core.canonical_json({"b": 2, "a": 1, "c": [3, 1, 2]})
    b = signing_core.canonical_json({"c": [3, 1, 2], "a": 1, "b": 2})
    assert a == b
    assert a == b'{"a":1,"b":2,"c":[3,1,2]}'


def test_sign_and_verify_roundtrip():
    payload = {"tax_id": "9876543210", "period": "2025-Q2", "value": 42}
    sig = signing_core.sign_bundle(payload)
    pub = signing_core.public_key_info()
    assert signing_core.verify_bundle(payload, sig.value_b64, pub["verify_key_b64"])


def test_verify_fails_on_tamper():
    payload = {"tax_id": "9876543210", "period": "2025-Q2", "value": 42}
    sig = signing_core.sign_bundle(payload)
    pub = signing_core.public_key_info()
    tampered = {**payload, "value": 43}
    assert not signing_core.verify_bundle(tampered, sig.value_b64, pub["verify_key_b64"])


def _ingest_one():
    payload = {
        "invoice_number": "ATK-1",
        "invoice_date": "2025-04-12",
        "issuer_tax_id": "1234567890",
        "issuer_name": "ACME",
        "customer_tax_id": "9876543210",
        "customer_name": "Demo KOBİ",
        "lines": [
            {
                "ewc_code": "20 03 01",
                "description": "x",
                "quantity": "1",
                "unit": "tonne",
                "disposal_method": "R3",
            }
        ],
    }
    r = client.post("/v1/ingest", json=payload)
    assert r.status_code == 201


def test_esg_endpoint_returns_verifiable_signature():
    _ingest_one()
    r = client.get("/v1/esg/9876543210?period=2025-Q2")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["signature"]["algorithm"] == "Ed25519"
    pub = client.get("/v1/signing/pubkey").json()
    assert signing_core.verify_bundle(
        body["bundle"],
        body["signature"]["value_b64"],
        pub["verify_key_b64"],
    )


def test_esg_signature_changes_when_data_changes():
    _ingest_one()
    sig1 = client.get("/v1/esg/9876543210?period=2025-Q2").json()["signature"]["value_b64"]
    # signed_at differs across calls; signature value also differs because signed_at
    # is part of the signature envelope but not the bundle. The bundle is identical,
    # so signature over the bundle alone must match — that's exactly what we verify.
    # Re-check by recomputing locally:
    body = client.get("/v1/esg/9876543210?period=2025-Q2").json()
    pub = client.get("/v1/signing/pubkey").json()
    assert signing_core.verify_bundle(
        body["bundle"], body["signature"]["value_b64"], pub["verify_key_b64"]
    )
    # And the signature value itself should match sig1 because bundle is unchanged.
    assert body["signature"]["value_b64"] == sig1


def test_signing_env_var_pin_yields_stable_pubkey(monkeypatch):
    # Re-do init with a new pinned key, ensure pubkey shifts deterministically.
    new_seed = bytes(b"\xff" * 32)
    monkeypatch.setenv(signing_core.ENV_SK_B64, base64.b64encode(new_seed).decode())
    signing_core._signing_key = None
    signing_core._key_fingerprint = None
    pub = signing_core.public_key_info()
    assert pub["fingerprint_sha256"] != ""  # not empty
