def test_health_returns_contract_shape(api_client):
    response = api_client.get("/health")

    assert response.status_code in (200, 503)
    payload = response.json()

    assert "status" in payload
    assert "data" in payload
    assert "error" in payload


def test_v1_health_contract(api_client):
    response = api_client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "ok"
    assert payload["error"] is None
