import pytest

@pytest.mark.asyncio
async def test_get_3d_view_success(client, sample_cif_content):
    """
    Test /api/structure/3d-view with a valid CIF file upload.
    Expect status 200 and data for 3D rendering.
    """
    files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
    response = await client.post("/api/structure/3d-view", files=files)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "cif_content" in data
    assert "structure_3d" in data
    assert "formula" in data
    assert "cell_params" in data

    # Verify content structure
    assert isinstance(data["cif_content"], str)
    assert len(data["cif_content"]) > 0
    assert "atoms" in data["structure_3d"]
    assert "n_atoms" in data["structure_3d"]
    assert data["structure_3d"]["n_atoms"] > 0

    # Check if atoms have required keys
    for atom in data["structure_3d"]["atoms"]:
        assert "symbol" in atom
        assert "x" in atom
        assert "y" in atom
        assert "z" in atom

@pytest.mark.asyncio
async def test_get_3d_view_wrong_extension(client):
    """
    Test /api/structure/3d-view with a non-CIF file extension.
    Expect 400 Bad Request.
    """
    files = {"file": ("test.txt", b"some text", "text/plain")}
    response = await client.post("/api/structure/3d-view", files=files)

    assert response.status_code == 400
    assert "Hanya file .cif yang diterima" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_3d_view_no_file(client):
    """
    Test /api/structure/3d-view with no file uploaded.
    Expect 422 Unprocessable Entity.
    """
    # FastAPI automatically handles missing required File(...) with 422
    response = await client.post("/api/structure/3d-view")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_3d_view_corrupt_content(client, invalid_cif_content):
    """
    Test /api/structure/3d-view with a .cif extension but invalid content.
    Expect 500 Internal Server Error (as per current router implementation).
    """
    files = {"file": ("corrupt.cif", invalid_cif_content, "application/octet-stream")}
    response = await client.post("/api/structure/3d-view", files=files)

    # General Exception catch in the router returns 500
    assert response.status_code == 500
