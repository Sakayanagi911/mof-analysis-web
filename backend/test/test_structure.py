import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_structure_analysis_success(client, sample_cif_content):
    """
    Test /api/structure with a valid CIF file upload.
    Expect status 200 and a complete, logically consistent response body.
    """
    files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
    response = await client.post("/api/structure", files=files)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"

    # Verify all expected top-level keys are present
    expected_keys = [
        "formula", "n_atoms", "n_sbu_atoms", "n_linker_atoms",
        "delta_e", "rmsd", "stability_score", "stability_status",
        "is_feasible", "structure_3d", "cell_params", "xtb_available"
    ]
    for key in expected_keys:
        assert key in data, f"Missing key in response: {key}"

    # Logical consistency: atom counts must add up
    assert data["n_atoms"] == data["n_sbu_atoms"] + data["n_linker_atoms"]

    # Stability status must be one of the three defined values
    assert data["stability_status"] in ["Sangat stabil", "Cukup stabil", "Tidak stabil"]

    # xTB flag must be boolean
    assert isinstance(data["xtb_available"], bool)

    # cell_params must contain all six crystallographic parameters
    for param in ("a", "b", "c", "alpha", "beta", "gamma"):
        assert param in data["cell_params"], f"Missing cell param: {param}"


@pytest.mark.asyncio
async def test_structure_analysis_3d_data(client, sample_cif_content):
    """
    Test that structure_3d contains a valid list of atom entries
    and that each entry has the required fields.
    """
    files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
    response = await client.post("/api/structure", files=files)

    assert response.status_code == 200
    data = response.json()

    structure_3d = data["structure_3d"]
    assert "atoms" in structure_3d
    assert "n_atoms" in structure_3d
    assert len(structure_3d["atoms"]) == data["n_atoms"]

    for atom in structure_3d["atoms"]:
        assert "symbol" in atom
        assert "x" in atom
        assert "y" in atom
        assert "z" in atom
        assert isinstance(atom["x"], float)
        assert isinstance(atom["y"], float)
        assert isinstance(atom["z"], float)


@pytest.mark.asyncio
async def test_structure_analysis_no_xtb(client, sample_cif_content):
    """
    When xTB is unavailable, the endpoint must still succeed and return
    delta_e=0.0 and rmsd=0.0 as documented defaults.
    """
    with patch("routers.structure.XTB_AVAILABLE", False):
        files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
        response = await client.post("/api/structure", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["delta_e"] == 0.0
    assert data["rmsd"] == 0.0
    assert data["xtb_available"] is False


@pytest.mark.asyncio
async def test_structure_analysis_wrong_extension(client):
    """
    Uploading a non-.cif file must return 400 Bad Request with an
    informative Indonesian-language error message.
    """
    files = {"file": ("test.txt", b"some text content", "text/plain")}
    response = await client.post("/api/structure", files=files)

    assert response.status_code == 400
    assert "Hanya file .cif yang diterima" in response.json()["detail"]


@pytest.mark.asyncio
async def test_structure_analysis_no_file(client):
    """
    A request with no file upload must return 422 Unprocessable Entity.
    """
    response = await client.post("/api/structure")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_structure_analysis_corrupt_content_manual_parser(client, invalid_cif_content):
    """
    When the manual parser processes garbage content it is lenient: it does
    NOT raise an exception but returns an empty atom list (n_atoms == 0).
    Therefore the endpoint returns 200 OK with an empty structure.

    NOTE: This is different from ASE mode.  If ASE is available and raises an
    exception on the same file, the router converts it to a 400 ValueError.
    This test exercises the manual-parser code path by patching ASE_AVAILABLE.
    """
    with patch("services.structure_parser.ASE_AVAILABLE", False):
        files = {"file": ("corrupt.cif", invalid_cif_content, "application/octet-stream")}
        response = await client.post("/api/structure", files=files)

    # Manual parser is lenient → 200 with n_atoms == 0
    assert response.status_code == 200
    data = response.json()
    assert data["n_atoms"] == 0
    assert data["structure_3d"]["atoms"] == []


@pytest.mark.asyncio
async def test_structure_analysis_corrupt_content_ase_parser(client, invalid_cif_content):
    """
    When ASE is reported as available but raises an exception on a corrupt
    file, the router must catch the ValueError and return 400 Bad Request.
    """
    with patch("services.structure_parser.ASE_AVAILABLE", True), \
         patch("services.structure_parser.ase_read", side_effect=Exception("ASE parse error")):
        files = {"file": ("corrupt.cif", invalid_cif_content, "application/octet-stream")}
        response = await client.post("/api/structure", files=files)

    assert response.status_code == 400
