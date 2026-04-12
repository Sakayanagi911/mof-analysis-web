import pytest
from services.joback import calculate_cp_joback, count_joback_groups, RDKIT_AVAILABLE, KNOWN_CP_VALUES

def test_calculate_cp_joback_known_lookup():
    """
    Test calculate_cp_joback for a SMILES string present in KNOWN_CP_VALUES.
    """
    # H3BTC: C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O
    smiles = "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O"
    expected_val = KNOWN_CP_VALUES[smiles]

    # At T=298.15, it should match the lookup (or be very close if rdkit is used)
    result = calculate_cp_joback(smiles, T=298.15)
    assert result is not None
    assert isinstance(result, float)

    if not RDKIT_AVAILABLE:
        assert result == expected_val
    else:
        # If rdkit is available, it might calculate it more precisely or use the same
        assert result > 0

def test_calculate_cp_joback_temperature_dependency():
    """
    Test that Cp value changes with temperature.
    """
    smiles = "OC(=O)c1ccc(cc1)C(O)=O" # H2BDC

    cp_298 = calculate_cp_joback(smiles, T=298.15)
    cp_400 = calculate_cp_joback(smiles, T=400.0)

    if cp_298 and cp_400:
        assert cp_400 > cp_298
    else:
        pytest.skip("RDKit not available and SMILES not in lookup")

def test_calculate_cp_joback_invalid_smiles():
    """
    Test with an invalid SMILES string.
    """
    result = calculate_cp_joback("INVALID_SMILES")
    # If rdkit is available, it should return None for invalid SMILES
    # If not available, it should return None as it's not in lookup
    assert result is None

@pytest.mark.skipif(not RDKIT_AVAILABLE, reason="rdkit not installed")
def test_count_joback_groups_h3btc():
    """
    Verify group counting for H3BTC (Trimesic acid).
    It has 3 -COOH groups and a benzene ring (6 =C< ring atoms).
    """
    smiles = "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O"
    counts = count_joback_groups(smiles)

    assert isinstance(counts, dict)
    # Check for carboxylic acid group
    assert "-COOH" in counts
    assert counts["-COOH"] == 3

    # Check for aromatic ring carbons
    # In H3BTC, we have 3 =CH- (ring) and 3 =C< (ring)
    assert "=CH- (ring)" in counts
    assert counts["=CH- (ring)"] == 3
    assert "=C< (ring)" in counts
    assert counts["=C< (ring)"] == 3

@pytest.mark.skipif(not RDKIT_AVAILABLE, reason="rdkit not installed")
def test_count_joback_groups_no_double_counting():
    """
    Ensure atoms are not counted multiple times for different groups.
    """
    smiles = "CCO" # Ethanol
    counts = count_joback_groups(smiles)

    # Ethanol has 1 -CH3, 1 -CH2-, 1 -OH
    assert counts.get("-CH3") == 1
    assert counts.get("-CH2-") == 1
    assert counts.get("-OH (alcohol)") == 1

    # Total primary atoms (C, C, O) = 3
    total_atoms_counted = sum(counts.values())
    assert total_atoms_counted == 3
