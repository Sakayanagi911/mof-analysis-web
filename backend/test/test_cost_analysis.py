import pytest
from services.cost_analysis import (
    load_price_database, calculate_mof_cost,
    calculate_energy, calculate_storage_cost,
    run_economic_analysis,
    MAX_MOF_COST, MAX_STORAGE_COST, MAX_REACTION_TIME, MAX_TEMPERATURE
)

def test_load_price_database():
    """
    Test that the price database is loaded correctly and contains essential keys.
    """
    db = load_price_database()
    assert isinstance(db, dict)
    assert "metals" in db
    assert "linkers" in db
    assert "eur_to_usd" in db
    assert "scale_factors" in db
    assert isinstance(db["eur_to_usd"], float)

def test_calculate_mof_cost_known_inputs():
    """
    Test MOF cost calculation with metal and linker present in the database.
    """
    # Use Cu(NO3)2 and H3BTC which are typically in the database
    result = calculate_mof_cost(metal_name="Cu(NO3)2", linker_name="H3BTC")

    assert "mof_cost_eur_per_kg" in result
    assert "mof_cost_usd_per_kg" in result
    assert result["mof_cost_eur_per_kg"] > 0
    assert result["mof_cost_usd_per_kg"] > 0

    # Verify conversion consistency
    db = load_price_database()
    expected_usd = result["mof_cost_eur_per_kg"] * db["eur_to_usd"]
    assert pytest.approx(result["mof_cost_usd_per_kg"], rel=1e-3) == expected_usd

def test_calculate_mof_cost_unknown_inputs():
    """
    Test that the system doesn't crash with unknown metal/linker and uses fallback.
    """
    result = calculate_mof_cost(metal_name="NonExistentMetal", linker_name="NonExistentLinker")
    assert result["mof_cost_usd_per_kg"] > 0

def test_calculate_mof_cost_zero_mass():
    """
    Test edge case where product mass is zero to ensure no division by zero.
    """
    result = calculate_mof_cost(metal_name="Cu(NO3)2", linker_name="H3BTC", product_mass_mg=0)
    assert result["mof_cost_eur_per_kg"] >= 0

def test_calculate_storage_cost():
    """
    Test storage cost calculation logic.
    Formula: mof_cost / (wc / 100)
    """
    mof_cost = 20.0  # USD/kg
    wc = 5.0        # wt.%

    # Calculation: 20.0 / (5.0 / 100) = 20.0 / 0.05 = 400.0
    result = calculate_storage_cost(mof_cost, wc)
    assert result == 400.0

def test_calculate_storage_cost_zero_wc():
    """
    Test that zero working capacity returns infinity as per implementation.
    """
    result = calculate_storage_cost(10.0, 0.0)
    assert result == float('inf')

def test_calculate_energy_basic():
    """
    Test energy calculation returns expected keys and values.
    """
    # SMILES for H3BTC
    smiles = "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O"
    temp = 120.0
    time = 24.0

    result = calculate_energy(smiles, temp, time)
    assert "q_energy_kj" in result
    assert "q_loss_kj" in result
    assert "cp_value" in result
    assert result["q_energy_kj"] > 0
    assert result["q_loss_kj"] > 0

def test_calculate_energy_loss_proportionality():
    """
    Test that heat loss is proportional to reaction time.
    """
    smiles = "OC(=O)c1ccc(cc1)C(O)=O"
    temp = 100.0

    res_short = calculate_energy(smiles, temp, 10.0)
    res_long = calculate_energy(smiles, temp, 40.0)

    assert res_long["q_loss_kj"] > res_short["q_loss_kj"]

def test_run_economic_analysis_output():
    """
    Test the main entry point for economic analysis service.
    """
    result = run_economic_analysis(
        metal_name="Zn(NO3)2",
        linker_name="H2BDC",
        reaction_time=24.0,
        temperature=120.0,
        smiles="OC(=O)c1ccc(cc1)C(O)=O",
        gravimetric_wc=6.0
    )

    expected_keys = [
        "mof_cost_usd_per_kg", "storage_cost_usd_per_kg_h2",
        "q_energy_kj", "q_loss_kj", "is_feasible", "feasibility_details"
    ]
    for key in expected_keys:
        assert key in result

def test_run_economic_analysis_feasibility_flags():
    """
    Test that is_feasible correctly reflects combined constraints.
    """
    # 1. Everything OK
    res_ok = run_economic_analysis(
        metal_name="Zn(NO3)2", linker_name="H2BDC",
        reaction_time=12.0, temperature=100.0,
        smiles="C1=CC=CC=C1", gravimetric_wc=10.0
    )
    # Zn(NO3)2 and H2BDC are cheap, so this should be feasible
    assert res_ok["is_feasible"] is True

    # 2. Too hot
    res_hot = run_economic_analysis(
        metal_name="Zn(NO3)2", linker_name="H2BDC",
        reaction_time=12.0, temperature=MAX_TEMPERATURE + 10,
        smiles="C1=CC=CC=C1", gravimetric_wc=10.0
    )
    assert res_hot["is_feasible"] is False
    assert res_hot["feasibility_details"]["temperature_ok"] is False

    # 3. Too long
    res_long = run_economic_analysis(
        metal_name="Zn(NO3)2", linker_name="H2BDC",
        reaction_time=MAX_REACTION_TIME + 1, temperature=100.0,
        smiles="C1=CC=CC=C1", gravimetric_wc=10.0
    )
    assert res_long["is_feasible"] is False
    assert res_long["feasibility_details"]["time_ok"] is False
