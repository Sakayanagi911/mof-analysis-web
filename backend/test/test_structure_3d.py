import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_get_3d_view_success(client, sample_cif_content):
    files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
    response = await client.post("/api/structure/3d-view", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "structure_3d" in data
    assert "formula" in data
    assert "cell_params" in data
    assert "cif_content" not in data

    structure_3d = data["structure_3d"]
    assert "atoms" in structure_3d
    assert "n_atoms" in structure_3d
    assert structure_3d["n_atoms"] > 0
    assert len(structure_3d["atoms"]) == structure_3d["n_atoms"]


@pytest.mark.asyncio
async def test_get_3d_view_cell_params(client, sample_cif_content):
    files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
    response = await client.post("/api/structure/3d-view", files=files)
    assert response.status_code == 200
    for key in ("a", "b", "c", "alpha", "beta", "gamma"):
        assert key in response.json()["cell_params"]


@pytest.mark.asyncio
async def test_get_3d_view_wrong_extension(client):
    files = {"file": ("test.txt", b"some text", "text/plain")}
    response = await client.post("/api/structure/3d-view", files=files)
    assert response.status_code == 400
    assert "Hanya file .cif yang diterima" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_3d_view_no_file(client):
    response = await client.post("/api/structure/3d-view")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_3d_view_corrupt_content_manual_parser(client, invalid_cif_content):
    with patch("services.structure_parser.ASE_AVAILABLE", False):
        files = {"file": ("corrupt.cif", invalid_cif_content, "application/octet-stream")}
        response = await client.post("/api/structure/3d-view", files=files)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_3d_view_corrupt_content_ase_parser(client, invalid_cif_content):
    with patch("services.structure_parser.ASE_AVAILABLE", True), \
         patch("services.structure_parser.ase_read", create=True, side_effect=Exception("ASE parse error")):
        files = {"file": ("corrupt.cif", invalid_cif_content, "application/octet-stream")}
        response = await client.post("/api/structure/3d-view", files=files)
    assert response.status_code == 400
