#!/usr/bin/env python3
"""
Debug Use Case 4 yang memiliki perbedaan 237%
"""

from services.cost_analysis import calculate_mof_cost, get_smiles_mapping

def debug_case4():
    """
    Debug Use Case 4 secara detail
    """
    
    print("=== DEBUG USE CASE 4 ===")
    print("Expected: 0.0413 USD/kg MOF, 0.7236 USD/kg H2")
    print("Actual: 0.1391 USD/kg MOF, 2.4401 USD/kg H2")
    print("Difference: 237%")
    print()
    
    # Use Case 4 parameters
    solvent_name = "DMF"
    solvent_volume_ml = 1.5
    modulator_name = "HCl"
    modulator_volume_ml = 19.0  # Very large volume!
    metal_name = "Cu(NO₃)₂·2.5H₂O"
    metal_mass_mg = 15.0
    smiles = "C(=O)O"  # H₄L (formate) - very simple molecule
    linker_mass_mg = 5.0
    product_mass_mg = 17.13
    
    print("Input Parameters:")
    print(f"  Solvent: {solvent_name} {solvent_volume_ml} mL")
    print(f"  Modulator: {modulator_name} {modulator_volume_ml} mL ← VERY LARGE!")
    print(f"  Metal: {metal_name} {metal_mass_mg} mg")
    print(f"  SMILES: {smiles} (formic acid - very simple)")
    print(f"  Linker mass: {linker_mass_mg} mg")
    print(f"  Product: {product_mass_mg} mg")
    print()
    
    # Check SMILES data
    smiles_mapping = get_smiles_mapping()
    if smiles in smiles_mapping:
        linker_data = smiles_mapping[smiles]
        print("SMILES Data:")
        print(f"  Linker Name: {linker_data.get('linker_name')}")
        print(f"  Price: {linker_data.get('price_eur_per_g')} EUR/g")
        print()
    
    # Calculate with detailed breakdown
    result = calculate_mof_cost(
        metal_name=metal_name,
        linker_smiles=smiles,
        metal_mass_mg=metal_mass_mg,
        linker_mass_mg=linker_mass_mg,
        product_mass_mg=product_mass_mg,
        solvent_name=solvent_name,
        solvent_volume_ml=solvent_volume_ml,
        additive_name="-",
        additive_volume_ml=0.0,
        modulator_name=modulator_name,
        modulator_volume_ml=modulator_volume_ml
    )
    
    print("=== DETAILED COST BREAKDOWN ===")
    print("Raw Costs (EUR):")
    raw_costs = result['raw_costs']
    for component, cost in raw_costs.items():
        print(f"  {component}: {cost}")
    
    print("\nScale Factors:")
    scale_factors = result['scale_factors']
    for factor_type, factor in scale_factors.items():
        print(f"  {factor_type}: {factor}")
    
    print("\nScaled Costs (EUR):")
    scaled_costs = result['scaled_costs']
    for component, cost in scaled_costs.items():
        print(f"  {component}: {cost}")
    
    print(f"\nTotal Scaled Cost: {result['total_scaled_eur']} EUR")
    print(f"Product Mass: {result['product_kg']} kg")
    print(f"MOF Cost: {result['mof_cost_eur_per_kg']} EUR/kg")
    print(f"MOF Cost: {result['mof_cost_usd_per_kg']} USD/kg")
    
    print("\n=== ANALYSIS ===")
    
    # Check if modulator cost is dominating
    modulator_raw = raw_costs['modulator_eur']
    total_raw = sum(raw_costs.values())
    modulator_pct = (modulator_raw / total_raw * 100) if total_raw > 0 else 0
    
    print(f"Modulator dominance: {modulator_pct:.1f}% of total raw cost")
    
    if modulator_volume_ml > 10:
        print("⚠️  ISSUE: Modulator volume is very large (19 mL)")
        print("   This might be causing the high cost")
    
    if linker_data.get('price_eur_per_g', 0) < 0.1:
        print("✅ Linker price is very low (formic acid)")
    
    # Check if the issue is with scale factors
    general_scale = scale_factors['general']
    if general_scale < 0.001:
        print(f"⚠️  Scale factor is very small: {general_scale}")
        print("   This should reduce costs significantly")
    
    # Check product mass
    if result['product_kg'] < 0.00002:  # < 20 mg
        print(f"⚠️  Product mass is very small: {result['product_kg']} kg")
        print("   Small product mass increases cost per kg")
    
    print("\n=== POTENTIAL FIXES ===")
    print("1. Check if modulator volume (19 mL) is correct")
    print("2. Verify modulator price in database")
    print("3. Check if scale factor calculation is correct for large volumes")
    print("4. Verify product mass (17.13 mg) is realistic")

if __name__ == "__main__":
    debug_case4()