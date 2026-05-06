import pytest
from services.joback import calculate_cp_joback, count_joback_groups_no_overlap


def test_calculate_cp_joback_positive_result():
    """
    Test calculate_cp_joback returns a positive Cp for a valid SMILES (H2BDC).
    """
    smiles = "OC(=O)c1ccc(cc1)C(O)=O"  # H2BDC (terephthalic acid)
    result = calculate_cp_joback(smiles, T=298.15)
    assert result is not None
    assert isinstance(result, float)
    assert result > 0


def test_calculate_cp_joback_temperature_dependency():
    """
    Test that Cp value changes with temperature (should increase for organics).
    """
    smiles = "OC(=O)c1ccc(cc1)C(O)=O"  # H2BDC

    cp_298 = calculate_cp_joback(smiles, T=298.15)
    cp_400 = calculate_cp_joback(smiles, T=400.0)

    assert cp_298 is not None
    assert cp_400 is not None
    # For most organic molecules, Cp increases with temperature
    assert cp_400 > cp_298


def test_calculate_cp_joback_invalid_smiles():
    """
    Test with an invalid SMILES string — should return fallback 150.0.
    """
    result = calculate_cp_joback("INVALID_SMILES")
    # RDKit can't parse it → returns fallback
    assert result == 150.0


def test_calculate_cp_joback_per_group_universal_constants():
    """
    Verify that the universal constants (-37.93, +0.21, etc.) are applied
    per group, matching the notebook old_model implementation.
    """
    smiles = "CCO"  # Ethanol: CH3 + CH2 + OH = 3 groups
    cp = calculate_cp_joback(smiles, T=298.15)

    # Expected range for ethanol gas heat capacity at 298K.
    assert cp is not None
    assert 40 < cp < 120, f"Cp={cp} seems out of range for ethanol gas"


def test_count_joback_groups_h3btc():
    """
    Verify group counting for H3BTC (Trimesic acid).
    It has 3 -COOH groups and aromatic ring atoms.
    """
    smiles = "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O"
    counts = count_joback_groups_no_overlap(smiles)

    assert isinstance(counts, dict)
    # Check for carboxylic acid group
    assert "COOH" in counts
    assert counts["COOH"] == 3


def test_count_joback_groups_no_double_counting():
    """
    Ensure atoms are not counted multiple times for different groups.
    """
    smiles = "CCO"  # Ethanol
    counts = count_joback_groups_no_overlap(smiles)

    # Ethanol has 1 CH3, 1 CH2, 1 OH_alcohol
    assert counts.get("CH3") == 1
    assert counts.get("CH2") == 1
    assert counts.get("OH_alcohol") == 1

    # Total groups = 3 (one per non-H atom)
    total_groups = sum(counts.values())
    assert total_groups == 3
