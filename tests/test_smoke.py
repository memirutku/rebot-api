from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_root_banner():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "rebot-api"
    assert "docs" in body


def test_openapi_served():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert r.json()["info"]["title"] == "REBOT API"


def test_factors_list_returns_datasets():
    r = client.get("/v1/factors")
    assert r.status_code == 200
    body = r.json()
    assert body["license"] == "CC BY-SA 4.0"
    assert body["total_factors"] > 0
    assert len(body["datasets"]) >= 2  # defra + tuik


def test_factors_filter_by_scope():
    r = client.get("/v1/factors?scope=2")
    assert r.status_code == 200
    body = r.json()
    for ds in body["datasets"]:
        for f in ds["factors"]:
            assert f["ghg_scope"].startswith("2")


def test_factors_filter_by_region_tr():
    r = client.get("/v1/factors?region=TR")
    assert r.status_code == 200
    body = r.json()
    for ds in body["datasets"]:
        for f in ds["factors"]:
            assert f.get("region") == "TR"


def test_factor_by_id_found():
    r = client.get("/v1/factors/electricity.tr.grid_average")
    assert r.status_code == 200
    body = r.json()
    assert body["factor"]["value"] == 0.443


def test_factor_by_id_not_found():
    r = client.get("/v1/factors/does.not.exist")
    assert r.status_code == 404
