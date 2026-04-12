import pytest

@pytest.mark.asyncio
async def test_feasibility_success(client, sample_feasibility_payload):
    """
    Test /api/feasibility with valid payload and expect success response.
    """
    response = await client.post("/api/feasibility", json=sample_feasibility_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "gravimetric_wc" in data
    assert "volumetric_wc" in data
    assert "is_feasible" in data
    assert data["thresholds"] == {"gravimetric": 5.5, "volumetric": 40.0}

    assert isinstance(data["gravimetric_wc"], (float, int))
    assert isinstance(data["volumetric_wc"], (float, int))
    assert isinstance(data["is_feasible"], bool)

@pytest.mark.asyncio
async def test_feasibility_logic_check(client):
    """
    Test scenario to verify if is_feasible flag correctly reflects the thresholds.
    """
    # High values likely to be feasible
    high_uptake_payload = {
        "p": 100.0,
        "gsa": 5000.0,
        "vsa": 2500.0,
        "vf": 0.9,
        "pv": 2.5,
        "lcd": 25.0,
        "pld": 20.0
    }
    response = await client.post("/api/feasibility", json=high_uptake_payload)
    assert response.status_code == 200
    data = response.json()

    expected_feasible = (data["gravimetric_wc"] >= 5.5) and (data["volumetric_wc"] >= 40.0)
    assert data["is_feasible"] == expected_feasible

@pytest.mark.asyncio
async def test_feasibility_low_uptake(client):
    """
    Test scenario with very low parameters which should result in is_feasible=False.
    """
    low_uptake_payload = {
        "p": 1.0,
        "gsa": 10.0,
        "vsa": 10.0,
        "vf": 0.1,
        "pv": 0.05,
        "lcd": 1.0,
        "pld": 0.5
    }
    response = await client.post("/api/feasibility", json=low_uptake_payload)
    assert response.status_code == 200
    data = response.json()
    # At these values, it should definitely be below threshold
    assert data["is_feasible"] is False

@pytest.mark.asyncio
async def test_feasibility_missing_field(client):
    """
    Test /api/feasibility with missing required field (e.g., 'p').
    Expect 422 Unprocessable Entity.
    """
    payload = {
        # 'p' is missing
        "gsa": 3500.0,
        "vsa": 1800.0,
        "vf": 0.75,
        "pv": 1.25,
        "lcd": 15.0,
        "pld": 10.0
    }
    response = await client.post("/api/feasibility", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_feasibility_invalid_type(client):
    """
    Test /api/feasibility with invalid data type for a numeric field.
    Expect 422 Unprocessable Entity.
    """
    payload = {
        "p": "invalid_string",
        "gsa": 3500.0,
        "vsa": 1800.0,
        "vf": 0.75,
        "pv": 1.25,
        "lcd": 15.0,
        "pld": 10.0
    }
    response = await client.post("/api/feasibility", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_feasibility_empty_body(client):
    """
    Test /api/feasibility with empty JSON body.
    Expect 422 Unprocessable Entity.
    """
    response = await client.post("/api/feasibility", json={})
    assert response.status_code == 422
