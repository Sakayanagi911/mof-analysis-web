import pytest
from unittest.mock import patch
from services.structure_parser import (
    separate_sbu_and_linker, calculate_rmsd,
    calculate_stability_score, prepare_3d_structure_data,
    parse_cif_file
)


# ---------------------------------------------------------------------------
# separate_sbu_and_linker
# ---------------------------------------------------------------------------

def test_separate_sbu_and_linker_mixed():
    """
    Test separation of metal (SBU) and non-metal (Linker) atoms.
    """
    atoms = ["Cu", "Zn", "C", "H", "O"]
    positions = [[0, 0, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]]

    result = separate_sbu_and_linker(atoms, positions)

    assert result["sbu_count"] == 2
    assert result["linker_count"] == 3
    assert "Cu" in result["sbu_atoms"]
    assert "Zn" in result["sbu_atoms"]
    assert "C" in result["linker_atoms"]
    assert "H" in result["linker_atoms"]
    assert "O" in result["linker_atoms"]


def test_separate_sbu_and_linker_total_count():
    """
    sbu_count + linker_count must always equal the number of input atoms.
    """
    atoms = ["Fe", "N", "C", "C", "O", "Zr", "H"]
    positions = [[i, i, i] for i in range(len(atoms))]

    result = separate_sbu_and_linker(atoms, positions)

    assert result["sbu_count"] + result["linker_count"] == len(atoms)


def test_separate_sbu_and_linker_all_metal():
    """
    Structure containing only metal atoms: linker_count must be 0.
    """
    atoms = ["Cu", "Zr", "Fe"]
    positions = [[0, 0, 0], [1, 1, 1], [2, 2, 2]]

    result = separate_sbu_and_linker(atoms, positions)

    assert result["sbu_count"] == 3
    assert result["linker_count"] == 0
    assert result["linker_atoms"] == []


def test_separate_sbu_and_linker_all_organic():
    """
    Structure containing only organic atoms: sbu_count must be 0.
    """
    atoms = ["C", "H", "O", "N"]
    positions = [[i, 0, 0] for i in range(4)]

    result = separate_sbu_and_linker(atoms, positions)

    assert result["sbu_count"] == 0
    assert result["linker_count"] == 4
    assert result["sbu_atoms"] == []


def test_separate_sbu_and_linker_empty():
    """
    Empty input must return zero counts and empty lists without crashing.
    """
    result = separate_sbu_and_linker([], [])

    assert result["sbu_count"] == 0
    assert result["linker_count"] == 0
    assert result["sbu_atoms"] == []
    assert result["linker_atoms"] == []


# ---------------------------------------------------------------------------
# calculate_rmsd
# ---------------------------------------------------------------------------

def test_calculate_rmsd_identical():
    """
    RMSD between two identical sets of positions must be 0.0.
    """
    pos = [[0, 0, 0], [1, 1, 1], [2, 2, 2]]
    assert calculate_rmsd(pos, pos) == 0.0


def test_calculate_rmsd_empty():
    """
    RMSD of two empty sets must return 0.0 without crashing.
    """
    assert calculate_rmsd([], []) == 0.0


def test_calculate_rmsd_different_lengths():
    """
    RMSD with mismatched atom counts must raise ValueError.
    """
    pos1 = [[0, 0, 0], [1, 1, 1]]
    pos2 = [[0, 0, 0]]
    with pytest.raises(ValueError):
        calculate_rmsd(pos1, pos2)


def test_calculate_rmsd_shifted_centroid():
    """
    RMSD uses centroid alignment: a uniformly shifted set of positions
    must produce RMSD = 0.0 because the geometry is identical.
    """
    pos1 = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    pos2 = [[10, 10, 10], [11, 10, 10], [10, 11, 10]]  # shifted by (10, 10, 10)
    assert calculate_rmsd(pos1, pos2) == pytest.approx(0.0, abs=1e-9)


def test_calculate_rmsd_symmetric():
    """
    RMSD(A, B) must equal RMSD(B, A).
    """
    pos1 = [[0, 0, 0], [1, 0, 0]]
    pos2 = [[0, 0, 1], [1, 0, 2]]
    assert calculate_rmsd(pos1, pos2) == pytest.approx(calculate_rmsd(pos2, pos1), rel=1e-9)


def test_calculate_rmsd_nonzero_for_distorted():
    """
    RMSD must be > 0 for two genuinely different (non-shifted) geometries.
    """
    pos1 = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    pos2 = [[0, 0, 0], [1, 0, 0], [0, 0, 1]]  # last atom moved to different axis
    assert calculate_rmsd(pos1, pos2) > 0.0


# ---------------------------------------------------------------------------
# calculate_stability_score
# ---------------------------------------------------------------------------

def test_stability_score_very_stable():
    """
    score = abs(delta_e)*0.7 + (rmsd*10)*0.3
    delta_e=1.0, rmsd=0.1 → score = 0.7 + 0.3 = 1.0 → Sangat stabil, feasible.
    """
    res = calculate_stability_score(1.0, 0.1)
    assert res["stability_score"] == pytest.approx(1.0, rel=1e-6)
    assert res["stability_status"] == "Sangat stabil"
    assert res["is_feasible"] is True


def test_stability_score_moderately_stable():
    """
    delta_e=10.0, rmsd=1.0 → score = 7.0 + 3.0 = 10.0 → Cukup stabil, feasible.
    """
    res = calculate_stability_score(10.0, 1.0)
    assert res["stability_score"] == pytest.approx(10.0, rel=1e-6)
    assert res["stability_status"] == "Cukup stabil"
    assert res["is_feasible"] is True


def test_stability_score_unstable():
    """
    delta_e=20.0, rmsd=2.0 → score = 14.0 + 6.0 = 20.0 → Tidak stabil, not feasible.
    """
    res = calculate_stability_score(20.0, 2.0)
    assert res["stability_score"] == pytest.approx(20.0, rel=1e-6)
    assert res["stability_status"] == "Tidak stabil"
    assert res["is_feasible"] is False


def test_stability_score_zero_inputs():
    """
    Both zero → score = 0 → Sangat stabil.
    """
    res = calculate_stability_score(0.0, 0.0)
    assert res["stability_score"] == 0.0
    assert res["stability_status"] == "Sangat stabil"
    assert res["is_feasible"] is True


def test_stability_score_negative_delta_e():
    """
    Negative delta_e is handled via abs(), so a negative value should
    produce the same score as the equivalent positive value.
    """
    res_pos = calculate_stability_score(5.0, 0.0)
    res_neg = calculate_stability_score(-5.0, 0.0)
    assert res_pos["stability_score"] == pytest.approx(res_neg["stability_score"], rel=1e-9)
    assert res_pos["stability_status"] == res_neg["stability_status"]


def test_stability_score_boundary_exactly_five():
    """
    A score of exactly 5.0 falls into 'Cukup stabil' (5 <= score <= 15).
    delta_e = 5/0.7, rmsd = 0 → score ≈ 5.0
    """
    delta_e = 5.0 / 0.7
    res = calculate_stability_score(delta_e, 0.0)
    # score should be approximately 5.0, which maps to Cukup stabil
    assert res["stability_score"] == pytest.approx(5.0, rel=1e-5)
    assert res["stability_status"] == "Cukup stabil"
    assert res["is_feasible"] is True


# ---------------------------------------------------------------------------
# prepare_3d_structure_data
# ---------------------------------------------------------------------------

def test_prepare_3d_structure_data_basic():
    """
    Test preparation of data for frontend 3D rendering.
    """
    atoms = ["Cu", "C"]
    positions = [[0.1234567, 0.7654321, 0.0], [1.0, 1.0, 1.0]]

    result = prepare_3d_structure_data(atoms, positions)

    assert result["n_atoms"] == 2
    assert len(result["atoms"]) == 2

    first = result["atoms"][0]
    assert first["symbol"] == "Cu"
    # Use pytest.approx to avoid floating-point exact equality pitfalls
    assert first["x"] == pytest.approx(0.123457, rel=1e-5)
    assert first["y"] == pytest.approx(0.765432, rel=1e-5)
    assert first["z"] == pytest.approx(0.0, abs=1e-9)

    second = result["atoms"][1]
    assert second["symbol"] == "C"
    assert second["x"] == pytest.approx(1.0, rel=1e-9)


def test_prepare_3d_structure_data_empty():
    """
    Empty input must return a dict with n_atoms=0 and an empty atoms list.
    """
    result = prepare_3d_structure_data([], [])
    assert result["n_atoms"] == 0
    assert result["atoms"] == []


def test_prepare_3d_structure_data_required_keys():
    """
    Every atom entry must contain the four required keys: symbol, x, y, z.
    """
    atoms = ["Zr", "O", "C"]
    positions = [[i, i * 0.5, i * 0.25] for i in range(3)]

    result = prepare_3d_structure_data(atoms, positions)

    for atom_entry in result["atoms"]:
        assert "symbol" in atom_entry
        assert "x" in atom_entry
        assert "y" in atom_entry
        assert "z" in atom_entry


def test_prepare_3d_structure_data_n_atoms_matches():
    """
    n_atoms in the result must always equal the length of the atoms list.
    """
    atoms = ["Cu", "Cu", "C", "O", "N"]
    positions = [[i, 0, 0] for i in range(len(atoms))]

    result = prepare_3d_structure_data(atoms, positions)

    assert result["n_atoms"] == len(atoms)
    assert len(result["atoms"]) == result["n_atoms"]


# ---------------------------------------------------------------------------
# parse_cif_file
# ---------------------------------------------------------------------------

def test_parse_cif_file_valid(sample_cif_content):
    """
    A well-formed CIF fixture must parse successfully and return the
    expected structure.  The test patches ASE_AVAILABLE to False so
    the deterministic manual parser is always exercised.
    """
    with patch("services.structure_parser.ASE_AVAILABLE", False):
        result = parse_cif_file(sample_cif_content, "test_file.cif")

    assert "atoms" in result
    assert "positions" in result
    assert "n_atoms" in result
    assert "cell_params" in result
    assert "formula" in result

    # Fixture has 3 atoms: Cu, C, O
    assert result["n_atoms"] == 3
    assert len(result["atoms"]) == result["n_atoms"]
    assert len(result["positions"]) == result["n_atoms"]
    assert "Cu" in result["atoms"]
    assert "C" in result["atoms"]
    assert "O" in result["atoms"]


def test_parse_cif_file_cell_params(sample_cif_content):
    """
    Cell parameters from the fixture must be parsed correctly.
    Fixture defines a=b=c=10.0, alpha=beta=gamma=90.0.
    """
    with patch("services.structure_parser.ASE_AVAILABLE", False):
        result = parse_cif_file(sample_cif_content, "test_cell.cif")

    cp = result["cell_params"]
    for key in ("a", "b", "c", "alpha", "beta", "gamma"):
        assert key in cp

    assert cp["a"] == pytest.approx(10.0, rel=1e-5)
    assert cp["b"] == pytest.approx(10.0, rel=1e-5)
    assert cp["c"] == pytest.approx(10.0, rel=1e-5)


def test_parse_cif_file_invalid_content_manual_parser():
    """
    Completely invalid CIF content processed by the manual parser should
    NOT raise an exception — the parser is lenient and returns an empty
    structure (n_atoms == 0).  This is intentional and tested explicitly.
    Callers (routers) are responsible for validating n_atoms > 0.
    """
    garbage = b"this is not a valid cif file"
    with patch("services.structure_parser.ASE_AVAILABLE", False):
        result = parse_cif_file(garbage, "bad.cif")

    # Manual parser does not crash; it yields an empty atom list
    assert result["n_atoms"] == 0
    assert result["atoms"] == []


def test_parse_cif_file_ase_raises_value_error(sample_cif_content):
    """
    When ASE is available but raises an exception (e.g. on a corrupt file),
    parse_cif_file must propagate a ValueError.
    """
    with patch("services.structure_parser.ASE_AVAILABLE", True), \
         patch("services.structure_parser.ase_read", side_effect=Exception("ASE parse error")):
        with pytest.raises(ValueError, match="Gagal membaca file CIF"):
            parse_cif_file(b"anything", "bad.cif")
