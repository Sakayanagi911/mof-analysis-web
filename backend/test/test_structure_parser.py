import pytest
import math
from services.structure_parser import (
    separate_sbu_and_linker, calculate_rmsd,
    calculate_stability_score, prepare_3d_structure_data,
    parse_cif_file
)

def test_separate_sbu_and_linker_mixed():
    """
    Test separation of metal (SBU) and non-metal (Linker) atoms.
    """
    atoms = ["Cu", "Zn", "C", "H", "O"]
    positions = [[0,0,0], [1,1,1], [2,2,2], [3,3,3], [4,4,4]]

    result = separate_sbu_and_linker(atoms, positions)

    assert result["sbu_count"] == 2
    assert result["linker_count"] == 3
    assert "Cu" in result["sbu_atoms"]
    assert "Zn" in result["sbu_atoms"]
    assert "C" in result["linker_atoms"]
    assert "H" in result["linker_atoms"]
    assert "O" in result["linker_atoms"]

def test_separate_sbu_and_linker_empty():
    """
    Test behavior with empty input lists.
    """
    result = separate_sbu_and_linker([], [])
    assert result["sbu_count"] == 0
    assert result["linker_count"] == 0
    assert result["sbu_atoms"] == []
    assert result["linker_atoms"] == []

def test_calculate_rmsd_identical():
    """
    RMSD between identical sets should be 0.
    """
    pos = [[0,0,0], [1,1,1], [2,2,2]]
    assert calculate_rmsd(pos, pos) == 0.0

def test_calculate_rmsd_different_lengths():
    """
    RMSD should raise ValueError if lengths don't match.
    """
    pos1 = [[0,0,0], [1,1,1]]
    pos2 = [[0,0,0]]
    with pytest.raises(ValueError):
        calculate_rmsd(pos1, pos2)

def test_calculate_rmsd_shifted():
    """
    RMSD should handle centroid alignment (shifted set should result in 0 RMSD).
    """
    pos1 = [[0,0,0], [1,0,0], [0,1,0]]
    pos2 = [[10,10,10], [11,10,10], [10,11,10]] # Shifted by (10,10,10)
    assert calculate_rmsd(pos1, pos2) == 0.0

def test_calculate_stability_score_ranges():
    """
    Test stability score mapping to status and feasibility.
    """
    # 1. Very stable (< 5)
    # score = abs(delta_e) * 0.7 + (rmsd * 10) * 0.3
    # If delta_e = 1, rmsd = 0.1 -> score = 0.7 + 0.3 = 1.0
    res1 = calculate_stability_score(1.0, 0.1)
    assert res1["stability_status"] == "Sangat stabil"
    assert res1["is_feasible"] is True

    # 2. Moderately stable (5-15)
    # If delta_e = 10, rmsd = 1.0 -> score = 7.0 + 3.0 = 10.0
    res2 = calculate_stability_score(10.0, 1.0)
    assert res2["stability_status"] == "Cukup stabil"
    assert res2["is_feasible"] is True

    # 3. Unstable (> 15)
    # If delta_e = 20, rmsd = 2.0 -> score = 14.0 + 6.0 = 20.0
    res3 = calculate_stability_score(20.0, 2.0)
    assert res3["stability_status"] == "Tidak stabil"
    assert res3["is_feasible"] is False

def test_prepare_3d_structure_data_basic():
    """
    Test preparation of data for frontend 3D rendering.
    """
    atoms = ["Cu", "C"]
    positions = [[0.1234567, 0.7654321, 0.0], [1.0, 1.0, 1.0]]

    result = prepare_3d_structure_data(atoms, positions)
    assert result["n_atoms"] == 2
    assert len(result["atoms"]) == 2

    # Check rounding (should be 6 decimals)
    assert result["atoms"][0]["symbol"] == "Cu"
    assert result["atoms"][0]["x"] == 0.123457 # Rounded from 0.1234567
    assert result["atoms"][1]["x"] == 1.0

def test_parse_cif_file_manual(sample_cif_content):
    """
    Test CIF parsing functionality (using the manual parser fallback if ASE is mocked or missing).
    """
    result = parse_cif_file(sample_cif_content, "test_file.cif")

    assert "atoms" in result
    assert "positions" in result
    assert "n_atoms" in result
    assert result["n_atoms"] == 3 # Based on conftest sample_cif_content fixture
    assert "Cu" in result["atoms"]
    assert "C" in result["atoms"]
    assert "O" in result["atoms"]

    # Check cell params
    assert result["cell_params"]["a"] == 10.0
    assert result["cell_params"]["b"] == 10.0
    assert result["cell_params"]["c"] == 10.0
