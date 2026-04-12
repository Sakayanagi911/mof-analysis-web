import pytest

@pytest.mark.asyncio
async def test_analyze_success(client, sample_analyze_form_data):
    """
    Test the main /analyze endpoint with all required form fields.
    This endpoint uses multipart/form-data.
    """
    # Note: data parameter is used for form fields in httpx
    response = await client.post("/analyze", data=sample_analyze_form_data)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "results" in data

    results = data["results"]
    expected_keys = [
        "gravimetric_h2", "volumetric_h2", "doe_feasible",
        "mof_cost", "storage_cost", "q_energy", "q_loss",
        "econ_feasible", "delta_e", "rmsd",
        "stability_status", "stability_feasible", "is_overall_feasible"
    ]
    for key in expected_keys:
        assert key in results

@pytest.mark.asyncio
async def test_analyze_with_file(client, sample_analyze_form_data, sample_cif_content):
    """
    Test the /analyze endpoint including an optional CIF file upload.
    """
    files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}

    response = await client.post(
        "/analyze",
        data=sample_analyze_form_data,
        files=files
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_analyze_missing_field(client, sample_analyze_form_data):
    """
    Test /analyze with a missing required form field (e.g., 'pv').
    Expect 422 Unprocessable Entity.
    """
    payload = sample_analyze_form_data.copy()
    del payload["pv"]

    response = await client.post("/analyze", data=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_analyze_invalid_type(client, sample_analyze_form_data):
    """
    Test /analyze with an invalid data type for a numeric field.
    Expect 422 Unprocessable Entity.
    """
    payload = sample_analyze_form_data.copy()
    payload["pv"] = "not_a_number"

    response = await client.post("/analyze", data=payload)
    assert response.status_code == 422
