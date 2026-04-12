import pytest
import os
from pathlib import Path
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


@pytest.mark.asyncio
async def test_concurrent_uploads_different_content(client, sample_cif_content):
    """
    Test bahwa upload concurrent dengan nama file sama
    menghasilkan analisis yang benar untuk masing-masing.

    Race condition fix: setiap upload harus mendapat file temporary
    dengan nama unik (UUID) sehingga tidak saling menimpa.
    """
    import asyncio

    with patch("services.structure_parser.ASE_AVAILABLE", False):
        # Buat 2 file CIF dengan konten berbeda tapi nama sama
        cif_1 = sample_cif_content                                      # cell_a = 10.0000
        cif_2 = sample_cif_content.replace(b"10.0000", b"20.0000")     # cell_a = 20.0000

        async def upload(content):
            return await client.post(
                "/api/structure",
                files={"file": ("test.cif", content, "chemical/x-cif")}
            )

        # Upload bersamaan
        r1, r2 = await asyncio.gather(upload(cif_1), upload(cif_2))

    assert r1.status_code == 200
    assert r2.status_code == 200

    d1 = r1.json()
    d2 = r2.json()

    # Pastikan hasilnya berbeda karena cell parameter berbeda
    assert d1["cell_params"]["a"] != d2["cell_params"]["a"], (
        f"Kedua upload mengembalikan cell_a yang sama ({d1['cell_params']['a']}), "
        "kemungkinan race condition masih terjadi"
    )

    # Pastikan masing-masing nilai sesuai konten yang dikirim
    assert d1["cell_params"]["a"] == pytest.approx(10.0, abs=0.01)
    assert d2["cell_params"]["a"] == pytest.approx(20.0, abs=0.01)


@pytest.mark.asyncio
async def test_temp_file_cleaned_up(client, sample_cif_content):
    """
    Test bahwa file temporary dihapus setelah parsing selesai.

    Cleanup fix: blok finally harus memastikan file UUID dihapus
    dari disk meskipun parsing gagal.
    """
    upload_dir = Path(__file__).parent.parent / "data" / "uploads"

    # Hitung file sebelum upload
    files_before = set(os.listdir(upload_dir)) if upload_dir.exists() else set()

    with patch("services.structure_parser.ASE_AVAILABLE", False):
        response = await client.post(
            "/api/structure",
            files={"file": ("cleanup_test.cif", sample_cif_content, "chemical/x-cif")}
        )

    assert response.status_code == 200

    # Pastikan tidak ada file baru yang tertinggal di upload_dir
    files_after = set(os.listdir(upload_dir)) if upload_dir.exists() else set()
    new_files = files_after - files_before

    assert not any("cleanup_test" in f for f in new_files), (
        f"File temporary tidak dihapus setelah parsing selesai: {new_files}"
    )


@pytest.mark.asyncio
async def test_temp_file_cleaned_up_on_parse_error(client, invalid_cif_content):
    """
    Test bahwa file temporary tetap dihapus meskipun terjadi error saat parsing.

    Blok finally harus berjalan bahkan ketika ASE melempar exception,
    sehingga tidak ada file yang tertinggal di disk.
    """
    upload_dir = Path(__file__).parent.parent / "data" / "uploads"

    files_before = set(os.listdir(upload_dir)) if upload_dir.exists() else set()

    with patch("services.structure_parser.ASE_AVAILABLE", True), \
         patch("services.structure_parser.ase_read", side_effect=Exception("ASE parse error")):
        response = await client.post(
            "/api/structure",
            files={"file": ("error_test.cif", invalid_cif_content, "application/octet-stream")}
        )

    # Router menangkap ValueError dari ASE dan mengembalikan 400
    assert response.status_code == 400

    # Meskipun parsing gagal, file temporary harus sudah dihapus
    files_after = set(os.listdir(upload_dir)) if upload_dir.exists() else set()
    new_files = files_after - files_before

    assert not any("error_test" in f for f in new_files), (
        f"File temporary tidak dihapus setelah parse error: {new_files}"
    )
