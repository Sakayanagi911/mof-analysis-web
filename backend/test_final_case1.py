#!/usr/bin/env python3
"""
Test final Use Case 1 dengan semua perubahan terbaru
"""

from services.cost_analysis import run_economic_analysis

def test_final_case1():
    """
    Test Use Case 1 dengan sistem terbaru:
    - Gravimetric WC dari database
    - Storage cost yang benar
    """
    
    print("=== FINAL TEST USE CASE 1 ===")
    print("Testing dengan sistem terbaru (gravimetric WC dari database)")
    print()
    
    # Use Case 1 parameters
    metal_name = "CuSO₄·5H₂O"
    linker_smiles = "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O"  # H₂L
    reaction_time = 24.0
    temperature = 85.0
    smiles = linker_smiles  # Same for this case
    product_mass_mg = 9.12
    metal_mass_mg = 8.0
    linker_mass_mg = 5.0
    solvent_name = "DMF"
    solvent_volume_ml = 2.0
    additive_name = "-"
    additive_volume_ml = 0.0
    modulator_name = "HNO3"
    modulator_volume_ml = 0.05
    
    print("Input Parameters:")
    print(f"  Metal: {metal_name} {metal_mass_mg} mg")
    print(f"  Linker: H₂L {linker_mass_mg} mg")
    print(f"  Solvent: {solvent_name} {solvent_volume_ml} mL")
    print(f"  Modulator: {modulator_name} {modulator_volume_ml} mL")
    print(f"  Product: {product_mass_mg} mg")
    print(f"  Time: {reaction_time} h, Temp: {temperature} °C")
    print()
    
    # Call run_economic_analysis (akan auto-lookup uptake dari database)
    result = run_economic_analysis(
        metal_name=metal_name,
        linker_smiles=linker_smiles,
        reaction_time=reaction_time,
        temperature=temperature,
        smiles=smiles,
        # Note: gravimetric_wc dan volumetric_wc tidak di-pass
        # Akan auto-lookup dari database berdasarkan SMILES
        product_mass_mg=product_mass_mg,
        metal_mass_mg=metal_mass_mg,
        linker_mass_mg=linker_mass_mg,
        solvent_name=solvent_name,
        solvent_volume_ml=solvent_volume_ml,
        additive_name=additive_name,
        additive_volume_ml=additive_volume_ml,
        modulator_name=modulator_name,
        modulator_volume_ml=modulator_volume_ml
    )
    
    print("=== RESULTS ===")
    print(f"MOF Cost: {result['mof_cost_usd_per_kg']} USD/kg")
    print(f"Storage Cost: {result['storage_cost_usd_per_kg_h2']} USD/kg H2")
    print(f"Is Feasible: {result['is_feasible']}")
    print()
    
    print("=== ENERGY BREAKDOWN ===")
    energy_details = result['energy_details']
    print(f"Cp Linker: {energy_details['cp_value']} J/mol.K")
    print(f"Solvent: {energy_details['e_sensible_solvent_j']} J")
    print(f"Additive: {energy_details['e_sensible_additive_j']} J")
    print(f"Modulator: {energy_details['e_sensible_modulator_j']} J")
    print(f"Metal: {energy_details['e_sensible_metal_j']} J")
    print(f"Linker: {energy_details['e_sensible_linker_j']} J")
    print(f"Total Sensible: {energy_details['e_sensible_total_j']} J")
    print()
    
    print("=== HEAT METRICS ===")
    print(f"Qheat: {result['q_energy_mj']} MJ")
    print(f"Qloss: {result['q_loss_mj']} MJ")
    print(f"Estirr: {result['e_stirr_mj']} MJ")
    print(f"E total: {result['e_total_mj']} MJ")
    print()
    
    print("=== COMPARISON WITH EXPECTED ===")
    
    # Expected values from use case
    expected = {
        "mof_cost": 1.7955,  # Should be same
        "storage_cost": 24.68,  # Should be lower due to higher gravimetric WC from database
        "cp_linker": 364.47,
        "solvent": 229.74,
        "additive": 0.00,
        "modulator": 0.25,
        "metal": 0.18,
        "linker": 0.33,
        "total_sensible": 230.50,
        "qheat_mj": 0.53810,  # Still need to fix this
        "etot_mj": 24.70082,
        "qloss_mj": 22.83034,
        "estirr_mj": 1.33238
    }
    
    actual = {
        "mof_cost": result['mof_cost_usd_per_kg'],
        "storage_cost": result['storage_cost_usd_per_kg_h2'],
        "cp_linker": energy_details['cp_value'],
        "solvent": energy_details['e_sensible_solvent_j'],
        "additive": energy_details['e_sensible_additive_j'],
        "modulator": energy_details['e_sensible_modulator_j'],
        "metal": energy_details['e_sensible_metal_j'],
        "linker": energy_details['e_sensible_linker_j'],
        "total_sensible": energy_details['e_sensible_total_j'],
        "qheat_mj": result['q_energy_mj'],
        "etot_mj": result['e_total_mj'],
        "qloss_mj": result['q_loss_mj'],
        "estirr_mj": result['e_stirr_mj']
    }
    
    print("Key Comparisons:")
    for key in ["mof_cost", "storage_cost", "cp_linker", "total_sensible"]:
        exp_val = expected[key]
        act_val = actual[key]
        diff = abs(exp_val - act_val)
        pct_diff = (diff / exp_val * 100) if exp_val != 0 else 0
        status = "✅" if pct_diff < 5 else "❌"
        print(f"  {key}: Expected {exp_val}, Actual {act_val}, Diff {pct_diff:.2f}% {status}")
    
    print()
    print("=== SUMMARY ===")
    if actual["storage_cost"] < 30:
        print("✅ Storage cost is reasonable (< 30 USD/kg H2)")
    else:
        print("❌ Storage cost is too high")
        
    if abs(actual["mof_cost"] - expected["mof_cost"]) < 0.01:
        print("✅ MOF cost calculation is accurate")
    else:
        print("❌ MOF cost calculation needs review")

if __name__ == "__main__":
    test_final_case1()