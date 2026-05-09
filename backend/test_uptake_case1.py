#!/usr/bin/env python3
"""
Test Use Case 1 dengan uptake data dari database
"""

from services.cost_analysis import calculate_energy, calculate_mof_cost, run_economic_analysis, get_uptake_data

def test_uptake_case1():
    """
    Test Use Case 1 dengan gravimetric WC dari database
    """
    
    # Input parameters
    solvent_name = "DMF"
    solvent_volume_ml = 2.0
    modulator_name = "HNO3"
    modulator_volume_ml = 0.05
    metal_name = "CuSO₄·5H₂O"
    metal_mass_mg = 8.0
    linker_smiles = "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O"  # H₂L
    linker_mass_mg = 5.0
    product_mass_mg = 9.12
    reaction_time_h = 24.0
    temperature_c = 85.0
    
    print("=== USE CASE 1 - UPTAKE FROM DATABASE TEST ===")
    print(f"Solvent: {solvent_name} {solvent_volume_ml} mL")
    print(f"Modulator: {modulator_name} {modulator_volume_ml} mL")
    print(f"Metal: {metal_name} {metal_mass_mg} mg")
    print(f"Linker: H₂L {linker_mass_mg} mg")
    print(f"Product: {product_mass_mg} mg")
    print(f"Time: {reaction_time_h} h, Temp: {temperature_c} °C")
    print()
    
    # Lookup uptake data dari database
    uptake_data = get_uptake_data()
    smiles_normalized = linker_smiles.strip()
    
    print("=== UPTAKE DATA LOOKUP ===")
    print(f"SMILES: {smiles_normalized}")
    
    if smiles_normalized in uptake_data:
        uptake_info = uptake_data[smiles_normalized]
        gravimetric_wc = uptake_info.get("gravimetric_wc_percent", 5.5)
        volumetric_wc = uptake_info.get("volumetric_wc_g_per_l", 40.0)
        print(f"✅ Found uptake data for H₂L:")
        print(f"   Gravimetric WC: {gravimetric_wc}%")
        print(f"   Volumetric WC: {volumetric_wc} g/L")
    else:
        # Default MOF properties
        gravimetric_wc = 5.5  # %
        volumetric_wc = 40.0  # g/L
        print(f"⚠️ SMILES not found in uptake database")
        print(f"   Using defaults: Grav={gravimetric_wc}%, Vol={volumetric_wc} g/L")
    print()
    
    # Test dengan run_economic_analysis (yang sekarang auto-lookup uptake)
    print("=== TESTING run_economic_analysis (AUTO UPTAKE LOOKUP) ===")
    
    economic_result = run_economic_analysis(
        metal_name=metal_name,
        linker_smiles=linker_smiles,
        reaction_time=reaction_time_h,
        temperature=temperature_c,
        smiles=linker_smiles,  # Same as linker_smiles for this case
        product_mass_mg=product_mass_mg,
        metal_mass_mg=metal_mass_mg,
        linker_mass_mg=linker_mass_mg,
        solvent_name=solvent_name,
        solvent_volume_ml=solvent_volume_ml,
        additive_name="-",
        additive_volume_ml=0.0,
        modulator_name=modulator_name,
        modulator_volume_ml=modulator_volume_ml
        # Note: gravimetric_wc dan volumetric_wc tidak di-pass, akan auto-lookup
    )
    
    print("=== RESULTS ===")
    print(f"MOF Cost: {economic_result['mof_cost_usd_per_kg']} USD/kg")
    print(f"Storage Cost: {economic_result['storage_cost_usd_per_kg_h2']} USD/kg H2")
    print(f"Qheat: {economic_result['q_energy_mj']} MJ")
    print(f"E total: {economic_result['e_total_mj']} MJ")
    print()
    
    # Show energy details
    energy_details = economic_result['energy_details']
    print("=== ENERGY BREAKDOWN ===")
    print(f"Cp linker: {energy_details['cp_value']} J/mol.K")
    print(f"Solvent: {energy_details['e_sensible_solvent_j']} J")
    print(f"Additive: {energy_details['e_sensible_additive_j']} J")
    print(f"Modulator: {energy_details['e_sensible_modulator_j']} J")
    print(f"Metal: {energy_details['e_sensible_metal_j']} J")
    print(f"Linker: {energy_details['e_sensible_linker_j']} J")
    print(f"Total Sensible: {energy_details['e_sensible_total_j']} J")
    print()
    
    print("=== COMPARISON WITH EXPECTED ===")
    expected_grav_wc = 7.275655632659123  # From database for H₂L SMILES
    print(f"Expected Gravimetric WC (from database): {expected_grav_wc}%")
    print(f"Used Gravimetric WC: {gravimetric_wc}%")
    print(f"Match: {'✅' if abs(expected_grav_wc - gravimetric_wc) < 0.01 else '❌'}")

if __name__ == "__main__":
    test_uptake_case1()