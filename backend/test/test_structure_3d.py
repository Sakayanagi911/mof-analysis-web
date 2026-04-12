import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_get_3d_view_success(client, sample_cif_content):
    """
    Test /api/structure/3d-view with a valid CIF file upload.
    Expect status 200 and well-formed data for 3D rendering.
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

    # cif_content must be a non-empty string
    assert isinstance(data["cif_content"], str)
    assert len(data["cif_content"]) > 0

    # structure_3d must expose atom list and count
    structure_3d = data["structure_3d"]
    assert "atoms" in structure_3d
    assert "n_atoms" in structure_3d
    assert structure_3d["n_atoms"] > 0
    assert len(structure_3d["atoms"]) == structure_3d["n_atoms"]

    # Every atom entry must carry the four mandatory keys
    for atom in structure_3d["atoms"]:
        assert "symbol" in atom
        assert "x" in atom
        assert "y" in atom
        assert "z" in atom
        assert isinstance(atom["x"], float)
        assert isinstance(atom["y"], float)
        assert isinstance(atom["z"], float)


@pytest.mark.asyncio
async def test_get_3d_view_cell_params(client, sample_cif_content):
    """
    Verify that cell_params is returned with all six crystallographic keys.
    """
    files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
    response = await client.post("/api/structure/3d-view", files=files)

    assert response.status_code == 200
    cell_params = response.json()["cell_params"]

    for key in ("a", "b", "c", "alpha", "beta", "gamma"):
        assert key in cell_params, f"Missing cell parameter: {key}"


@pytest.mark.asyncio
async def test_get_3d_view_wrong_extension(client):
    """
    Uploading a non-.cif file must return 400 Bad Request with an
    informative error message.
    """
    files = {"file": ("test.txt", b"some text", "text/plain")}
    response = await client.post("/api/structure/3d-view", files=files)

    assert response.status_code == 400
    assert "Hanya file .cif yang diterima" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_3d_view_no_file(client):
    """
    A request with no file upload must return 422 Unprocessable Entity.
    """
    response = await client.post("/api/structure/3d-view")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_3d_view_corrupt_content_manual_parser(client, invalid_cif_content):
    """
    When the manual parser processes garbage content it is lenient: it does
    NOT raise an exception but returns an empty atom list (n_atoms == 0).
    Therefore the endpoint returns 200 OK with an empty structure_3d.

    The manual parser code path is exercised by patching ASE_AVAILABLE to False.
    """
    with patch("services.structure_parser.ASE_AVAILABLE", False):
        files = {"file": ("corrupt.cif", invalid_cif_content, "application/octet-stream")}
        response = await client.post("/api/structure/3d-view", files=files)

    # Lenient manual parser → 200 with empty atom list
    assert response.status_code == 200
    data = response.json()
    assert data["structure_3d"]["n_atoms"] == 0
    assert data["structure_3d"]["atoms"] == []


@pytest.mark.asyncio
async def test_get_3d_view_corrupt_content_ase_parser(client, invalid_cif_content):
    """
    When ASE is reported as available but raises an exception while parsing
    a corrupt file, the router's general Exception handler must return 500.
    """
    with patch("services.structure_parser.ASE_AVAILABLE", True), \
         patch("services.structure_parser.ase_read", side_effect=Exception("ASE parse error")):
        files = {"file": ("corrupt.cif", invalid_cif_content, "application/octet-stream")}
        response = await client.post("/api/structure/3d-view", files=files)

    assert response.status_code == 500
