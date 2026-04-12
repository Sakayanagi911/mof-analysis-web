import pytest

@pytest.mark.asyncio
async def test_structure_analysis_success(client, sample_cif_content):
    """
    Test /api/structure with a valid CIF file upload.
    Expect status 200 and complete structure analysis results.
    """
    files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
    response = await client.post("/api/structure", files=files)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "formula" in data
    assert "n_atoms" in data
    assert "n_sbu_atoms" in data
    assert "n_linker_atoms" in data
    assert "delta_e" in data
    assert "rmsd" in data
    assert "stability_score" in data
    assert "stability_status" in data
    assert "is_feasible" in data
    assert "structure_3d" in data
    assert "cell_params" in data
    assert "xtb_available" in data

    # Logical checks
    assert data["n_atoms"] == data["n_sbu_atoms"] + data["n_linker_atoms"]
    assert data["stability_status"] in ["Sangat stabil", "Cukup stabil", "Tidak stabil"]

    # 3D structure checks
    assert "atoms" in data["structure_3d"]
    assert len(data["structure_3d"]["atoms"]) == data["n_atoms"]
    for atom in data["structure_3d"]["atoms"]:
        assert "symbol" in atom
        assert "x" in atom
        assert "y" in atom
        assert "z" in atom

@pytest.mark.asyncio
async def test_structure_analysis_wrong_extension(client):
    """
    Test /api/structure with a non-CIF file extension.
    Expect 400 Bad Request.
    """
    files = {"file": ("test.txt", b"some text content", "text/plain")}
    response = await client.post("/api/structure", files=files)

    assert response.status_code == 400
    assert "Hanya file .cif yang diterima" in response.json()["detail"]

@pytest.mark.asyncio
async def test_structure_analysis_corrupt_content(client, invalid_cif_content):
    """
    Test /api/structure with a .cif extension but invalid/corrupt content.
    Expect 400 or 500 error depending on parser behavior.
    """
    files = {"file": ("corrupt.cif", invalid_cif_content, "application/octet-stream")}
    response = await client.post("/api/structure", files=files)

    # Based on implementation, it might raise ValueError (400) or Exception (500)
    assert response.status_code in [400, 500]

@pytest.mark.asyncio
async def test_structure_analysis_no_file(client):
    """
    Test /api/structure with no file uploaded.
    Expect 422 Unprocessable Entity.
    """
    response = await client.post("/api/structure")
    assert response.status_code == 422
