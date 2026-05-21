import pytest
from services.cost_analysis import (
    load_price_database,
    calculate_mof_cost,
    calculate_energy,
    calculate_storage_cost,
    run_economic_analysis,
    MAX_REACTION_TIME,
    MAX_TEMPERATURE,
)


def test_load_price_database():
    db = load_price_database()
    assert isinstance(db, dict)
    assert "metals" in db
    assert "smiles_mapping" in db
    assert "eur_to_usd" in db


def test_calculate_mof_cost_known_inputs():
    result = calculate_mof_cost(metal_name="Cu(NO3)2", linker_name="H3BTC")
    assert "mof_cost_eur_per_kg" in result
    assert "mof_cost_usd_per_kg" in result
    assert result["mof_cost_eur_per_kg"] > 0
    assert result["mof_cost_usd_per_kg"] > 0


def test_calculate_mof_cost_unknown_inputs():
    result = calculate_mof_cost(metal_name="NonExistentMetal", linker_name="NonExistentLinker")
    assert result["mof_cost_usd_per_kg"] > 0


def test_calculate_mof_cost_zero_mass_raises():
    with pytest.raises(ValueError):
        run_economic_analysis(
            metal_name="Cu(NO3)2",
            linker_name="H3BTC",
            reaction_time=24.0,
            temperature=120.0,
            smiles="C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O",
            product_mass_mg=0,
            metal_mass_mg=100.0,
            linker_mass_mg=50.0,
            gravimetric_wc=8.5,
            volumetric_wc=50.0,
        )


def test_calculate_storage_cost():
    result = calculate_storage_cost(20.0, 5.0)
    assert result == 400.0


def test_calculate_storage_cost_zero_wc():
    result = calculate_storage_cost(10.0, 0.0)
    assert result == 99999.0


def test_calculate_energy_basic():
    smiles = "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O"
    result = calculate_energy(smiles, 120.0, 24.0)
    assert "q_energy_mj" in result
    assert "q_loss_mj" in result
    assert "e_stirr_mj" in result
    assert "e_total_mj" in result
    assert result["q_energy_mj"] > 0
    assert result["q_loss_mj"] > 0
    assert result["e_stirr_mj"] >= 0


def test_calculate_energy_loss_proportionality():
    smiles = "OC(=O)c1ccc(cc1)C(O)=O"
    res_short = calculate_energy(smiles, 100.0, 10.0)
    res_long = calculate_energy(smiles, 100.0, 40.0)
    assert res_long["q_loss_mj"] > res_short["q_loss_mj"]
    ratio = res_long["q_loss_mj"] / res_short["q_loss_mj"]
    assert 3.8 < ratio < 4.2


def test_run_economic_analysis_output():
    result = run_economic_analysis(
        metal_name="Zn(NO3)2",
        linker_name="H2BDC",
        reaction_time=24.0,
        temperature=120.0,
        smiles="OC(=O)c1ccc(cc1)C(O)=O",
        gravimetric_wc=6.0,
        volumetric_wc=45.0,
    )
    for key in (
        "mof_cost_usd_per_kg",
        "storage_cost_usd_per_kg_h2",
        "q_energy_mj",
        "q_loss_mj",
        "e_stirr_mj",
        "e_total_mj",
        "is_feasible",
        "feasibility_details",
    ):
        assert key in result


def test_run_economic_analysis_feasibility_flags():
    res_ok = run_economic_analysis(
        metal_name="Zn(NO3)2",
        linker_name="H2BDC",
        reaction_time=12.0,
        temperature=100.0,
        smiles="C1=CC=CC=C1",
        gravimetric_wc=10.0,
        volumetric_wc=50.0,
    )
    assert res_ok["is_feasible"] is True

    res_hot = run_economic_analysis(
        metal_name="Zn(NO3)2",
        linker_name="H2BDC",
        reaction_time=12.0,
        temperature=MAX_TEMPERATURE + 10,
        smiles="C1=CC=CC=C1",
        gravimetric_wc=10.0,
        volumetric_wc=50.0,
    )
    assert res_hot["is_feasible"] is False
    assert res_hot["feasibility_details"]["temperature_ok"] is False

    res_long = run_economic_analysis(
        metal_name="Zn(NO3)2",
        linker_name="H2BDC",
        reaction_time=MAX_REACTION_TIME + 1,
        temperature=100.0,
        smiles="C1=CC=CC=C1",
        gravimetric_wc=10.0,
        volumetric_wc=50.0,
    )
    assert res_long["is_feasible"] is False
    assert res_long["feasibility_details"]["time_ok"] is False
