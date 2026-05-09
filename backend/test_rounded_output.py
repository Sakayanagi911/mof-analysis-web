#!/usr/bin/env python3
"""
Test output cost dengan pembulatan 4 angka di belakang koma
"""

from services.cost_analysis import run_economic_analysis

def test_rounded_output():
    """
    Test output cost dengan pembulatan 4 decimal places
    """
    
    print("=== TEST ROUNDED OUTPUT (4 DECIMAL PLACES) ===")
    
    # Use Case 1 parameters
    metal_name = "CuSO₄·5H₂O"
    linker_smiles = "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O"  # H₂L
    reaction_time = 24.0
    temperature = 85.0
    smiles = linker_smiles
    product_mass_mg = 9.12
    metal_mass_mg = 8.0
    linker_mass_mg = 5.0
    solvent_name = "DMF"
    solvent_volume_ml = 2.0
    modulator_name = "HNO3"
    modulator_volume_ml = 0.05
    
    print("Use Case 1 Input:")
    print(f"  Metal: {metal_name} {metal_mass_mg} mg")
    print(f"  Linker: H₂L {linker_mass_mg} mg")
    print(f"  Solvent: {solvent_name} {solvent_volume_ml} mL")
    print(f"  Modulator: {modulator_name} {modulator_volume_ml} mL")
    print(f"  Product: {product_mass_mg} mg")
    print()
    
    # Call run_economic_analysis
    result = run_economic_analysis(
        metal_name=metal_name,
        linker_smiles=linker_smiles,
        reaction_time=reaction_time,
        temperature=temperature,
        smiles=smiles,
        product_mass_mg=product_mass_mg,
        metal_mass_mg=metal_mass_mg,
        linker_mass_mg=linker_mass_mg,
        solvent_name=solvent_name,
        solvent_volume_ml=solvent_volume_ml,
        additive_name="-",
        additive_volume_ml=0.0,
        modulator_name=modulator_name,
        modulator_volume_ml=modulator_volume_ml
    )
    
    print("=== ROUNDED OUTPUT RESULTS ===")
    mof_cost = result['mof_cost_usd_per_kg']
    storage_cost = result['storage_cost_usd_per_kg_h2']
    
    print(f"MOF Cost: {mof_cost} USD/kg")
    print(f"Storage Cost: {storage_cost} USD/kg H2")
    print()
    
    # Check decimal places
    mof_cost_str = str(mof_cost)
    storage_cost_str = str(storage_cost)
    
    if '.' in mof_cost_str:
        mof_decimals = len(mof_cost_str.split('.')[1])
    else:
        mof_decimals = 0
        
    if '.' in storage_cost_str:
        storage_decimals = len(storage_cost_str.split('.')[1])
    else:
        storage_decimals = 0
    
    print("=== DECIMAL PLACES CHECK ===")
    print(f"MOF Cost decimal places: {mof_decimals}")
    print(f"Storage Cost decimal places: {storage_decimals}")
    
    if mof_decimals <= 4:
        print("✅ MOF Cost has ≤ 4 decimal places")
    else:
        print("❌ MOF Cost has > 4 decimal places")
        
    if storage_decimals <= 4:
        print("✅ Storage Cost has ≤ 4 decimal places")
    else:
        print("❌ Storage Cost has > 4 decimal places")
    
    print()
    print("=== COMPARISON WITH EXPECTED ===")
    expected_mof = 1.7914
    expected_storage = 24.6217
    
    print(f"Expected MOF Cost: {expected_mof}")
    print(f"Actual MOF Cost: {mof_cost}")
    print(f"Expected Storage Cost: {expected_storage}")
    print(f"Actual Storage Cost: {storage_cost}")
    
    mof_diff = abs(mof_cost - expected_mof)
    storage_diff = abs(storage_cost - expected_storage)
    
    print(f"MOF Cost difference: {mof_diff:.6f}")
    print(f"Storage Cost difference: {storage_diff:.6f}")
    
    if mof_diff < 0.01:
        print("✅ MOF Cost very close to expected")
    elif mof_diff < 0.1:
        print("✅ MOF Cost reasonably close to expected")
    else:
        print("⚠️ MOF Cost differs significantly from expected")

if __name__ == "__main__":
    test_rounded_output()