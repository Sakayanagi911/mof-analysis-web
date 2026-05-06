"""Verify energy calculations against use case expected values."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from services.cost_analysis import calculate_energy, calculate_mof_cost, calculate_storage_cost, get_chem_prop

# ===== USE CASE INPUT =====
smiles = "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O"  # H2L
temp_c = 85.0
time_h = 24.0
solvent = "DMF"
sol_vol = 2.0
mod_name = "HNO3"
mod_vol = 0.05
metal = "CuSO\u2084\u00b75H\u2082O"  # CuSO₄·5H₂O
metal_mass = 8.0
linker_mass = 5.0
product_mass = 9.12

print("===== CHEM PROP CHECK =====")
print(f"DMF: {get_chem_prop('DMF')}")
print(f"HNO3: {get_chem_prop('HNO3')}")
print(f"CuSO4·5H2O: {get_chem_prop(metal, is_metal=True)}")
print(f"None: {get_chem_prop('-')}")

print("\n===== ENERGY CALCULATION =====")
result = calculate_energy(
    smiles=smiles,
    temperature_c=temp_c,
    reaction_time_h=time_h,
    linker_mass_mg=linker_mass,
    metal_mass_mg=metal_mass,
    solvent_name=solvent,
    solvent_volume_ml=sol_vol,
    additive_name="-",
    additive_volume_ml=0.0,
    modulator_name=mod_name,
    modulator_volume_ml=mod_vol,
    metal_name=metal,
)

print(f"Cp linker: {result['cp_value']} J/mol.K")
print(f"Linker MW: {result['linker_mw']}")
print(f"Solvent E: {result['e_sensible_solvent_j']} J (expected 229.74)")
print(f"Additive E: {result['e_sensible_additive_j']} J (expected 0)")
print(f"Modulator E: {result['e_sensible_modulator_j']} J")
print(f"Metal E: {result['e_sensible_metal_j']} J")
print(f"Linker E: {result['e_sensible_linker_j']} J")
print(f"Total Sens: {result['e_sensible_total_j']} J")
print(f"Qheat: {result['q_energy_mj']:.5f} MJ (expected 0.53810)")
print(f"Qloss: {result['q_loss_mj']:.5f} MJ (expected 22.83034)")
print(f"Estirr: {result['e_stirr_mj']:.5f} MJ (expected 1.33238)")
print(f"Etot: {result['e_total_mj']:.5f} MJ (expected 24.70082)")

print("\n===== COST CALCULATION =====")
cost = calculate_mof_cost(metal, "H\u2082L",
                          metal_mass_mg=metal_mass,
                          linker_mass_mg=linker_mass,
                          product_mass_mg=product_mass)
print(f"MOF USD/kg: {cost['mof_cost_usd_per_kg']} (expected 1.7914)")
print(f"MOF EUR/kg: {cost['mof_cost_eur_per_kg']}")

# Try different gravimetric_wc to get expected storage cost
for wc in [5.0, 7.0, 7.11, 7.27, 13.11]:
    sc = calculate_storage_cost(cost['mof_cost_usd_per_kg'], wc)
    print(f"Storage cost (wc={wc}%): {sc} USD/kg H2")
