#!/usr/bin/env python3
"""
Debug Use Case 3 yang memiliki 7.8% difference
"""

from services.cost_analysis import calculate_mof_cost, get_smiles_mapping

def debug_case3():
    """
    Debug Use Case 3 untuk memahami 7.8% difference
    """
    
    print("=== DEBUG USE CASE 3 ===")
    print("Expected: 0.1056 USD/kg MOF, 1.771 USD/kg H2")
    print("Actual: 0.1138 USD/kg MOF, 1.9087 USD/kg H2")
    print("Difference: 7.8%")
    print()
    
    # Use Case 3 parameters
    solvent_name = "DMF"
    solvent_volume_ml = 4.0
    additive_name = "MeCN"
    additive_volume_ml = 1.0
    modulator_name = "-"
    modulator_volume_ml = 0.0
    metal_name = "Zn(NO₃)₂·6H₂O"
    metal_mass_mg = 119.0  # Large metal mass
    smiles = "S1C(=CC=C1C(=O)O)C(=O)O"  # H₂thb
    linker_mass_mg = 52.0  # Large linker mass
    product_mass_mg = 52.3  # Large product mass
    
    print("Input Parameters:")
    print(f"  Solvent: {solvent_name} {solvent_volume_ml} mL")
    print(f"  Additive: {additive_name} {additive_volume_ml} mL")
    print(f"  Metal: {metal_name} {metal_mass_mg} mg ← LARGE")
    print(f"  SMILES: {smiles}")
    print(f"  Linker mass: {linker_mass_mg} mg ← LARGE")
    print(f"  Product: {product_mass_mg} mg ← LARGE")
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
        additive_name=additive_name,
        additive_volume_ml=additive_volume_ml,
        modulator_name=modulator_name,
        modulator_volume_ml=modulator_volume_ml
    )
    
    print("=== DETAILED COST BREAKDOWN ===")
    print("Raw Costs (EUR):")
    raw_costs = result['raw_costs']
    total_raw = sum(raw_costs.values())
    for component, cost in raw_costs.items():
        pct = (cost / total_raw * 100) if total_raw > 0 else 0
        print(f"  {component}: {cost:.6f} ({pct:.1f}%)")
    
    print(f"\nTotal Raw Cost: {total_raw:.6f} EUR")
    
    print("\nScale Factors:")
    scale_factors = result['scale_factors']
    for factor_type, factor in scale_factors.items():
        print(f"  {factor_type}: {factor}")
    
    print("\nScaled Costs (EUR):")
    scaled_costs = result['scaled_costs']
    total_scaled = sum(scaled_costs.values())
    for component, cost in scaled_costs.items():
        pct = (cost / total_scaled * 100) if total_scaled > 0 else 0
        print(f"  {component}: {cost:.8f} ({pct:.1f}%)")
    
    print(f"\nTotal Scaled Cost: {result['total_scaled_eur']:.8f} EUR")
    print(f"Product Mass: {result['product_kg']:.8f} kg")
    print(f"MOF Cost: {result['mof_cost_eur_per_kg']:.6f} EUR/kg")
    print(f"MOF Cost: {result['mof_cost_usd_per_kg']:.6f} USD/kg")
    
    print("\n=== ANALYSIS ===")
    
    # Check component dominance
    max_raw_component = max(raw_costs.items(), key=lambda x: x[1])
    print(f"Dominant raw cost: {max_raw_component[0]} ({max_raw_component[1]:.6f} EUR)")
    
    # Check if scale factors are reasonable
    general_scale = scale_factors['general']
    linker_scale = scale_factors['linker']
    
    print(f"Scale factor (general): {general_scale:.8f}")
    print(f"Scale factor (linker): {linker_scale:.8f}")
    
    # Check if the difference is within acceptable range
    expected_mof_cost = 0.1056
    actual_mof_cost = result['mof_cost_usd_per_kg']
    diff_pct = abs(actual_mof_cost - expected_mof_cost) / expected_mof_cost * 100
    
    print(f"\nDifference: {diff_pct:.2f}%")
    
    if diff_pct < 10:
        print("✅ Difference is < 10%, might be acceptable")
        print("   Could be due to:")
        print("   - Rounding differences in original calculation")
        print("   - Slightly different price data")
        print("   - Different precision in scale factors")
    else:
        print("❌ Difference is > 10%, needs investigation")

if __name__ == "__main__":
    debug_case3()