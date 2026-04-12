import pytest

@pytest.mark.asyncio
async def test_economic_success(client, sample_economic_payload):
    """
    Test /api/economic with a standard valid payload.
    Expect status 200 and correct response structure.
    """
    response = await client.post("/api/economic", json=sample_economic_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "mof_cost_usd_per_kg" in data
    assert "storage_cost_usd_per_kg_h2" in data
    assert "q_energy_kj" in data
    assert "q_loss_kj" in data
    assert "is_feasible" in data
    assert "feasibility_details" in data

    details = data["feasibility_details"]
    assert "mof_cost_ok" in details
    assert "storage_cost_ok" in details
    assert "time_ok" in details
    assert "temperature_ok" in details

@pytest.mark.asyncio
async def test_economic_feasibility_logic(client, sample_economic_payload):
    """
    Test that is_feasible flag reflects the internal logic thresholds.
    Scenario: Excessive reaction time should make it infeasible.
    """
    payload = sample_economic_payload.copy()
    payload["reaction_time"] = 100.0  # Threshold is 48.0

    response = await client.post("/api/economic", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["is_feasible"] is False
    assert data["feasibility_details"]["time_ok"] is False

@pytest.mark.asyncio
async def test_economic_unknown_metal_linker(client, sample_economic_payload):
    """
    Test with metal/linker names not present in price_database.json.
    Should use fallback default prices without crashing.
    """
    payload = sample_economic_payload.copy()
    payload["metal_name"] = "UnknownMetal"
    payload["linker_name"] = "UnknownLinker"

    response = await client.post("/api/economic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["mof_cost_usd_per_kg"] > 0

@pytest.mark.asyncio
async def test_economic_invalid_smiles(client, sample_economic_payload):
    """
    Test with an invalid SMILES string.
    The service should handle rdkit failures gracefully and use fallback Cp values.
    """
    payload = sample_economic_payload.copy()
    payload["smiles"] = "NOT_A_SMILES"

    response = await client.post("/api/economic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "q_energy_kj" in data

@pytest.mark.asyncio
async def test_economic_zero_gravimetric_wc(client, sample_economic_payload):
    """
    Test scenario where gravimetric_wc is 0.
    Storage cost calculation might result in infinity (inf).
    """
    payload = sample_economic_payload.copy()
    payload["gravimetric_wc"] = 0.0

    response = await client.post("/api/economic", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Check if storage_cost is returned as inf or handled gracefully
    assert data["storage_cost_usd_per_kg_h2"] == float('inf')
    assert data["is_feasible"] is False

@pytest.mark.asyncio
async def test_economic_missing_fields(client):
    """
    Test /api/economic with missing required fields.
    Expect 422 Unprocessable Entity.
    """
    payload = {
        "metal_name": "Cu(NO3)2"
        # missing other required fields
    }
    response = await client.post("/api/economic", json=payload)
    assert response.status_code == 422
