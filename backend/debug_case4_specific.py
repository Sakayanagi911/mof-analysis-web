#!/usr/bin/env python3
"""
Debug spesifik untuk Use Case 4 yang memiliki perbedaan besar
"""

from services.cost_analysis import calculate_mof_cost, load_price_database

def debug_case4():
    """
    Debug Use Case 4 secara detail
    """
    
    print("=== DEBUG USE CASE 4 ===")
    
    # Use Case 4 parameters
    params = {
        "metal_name": "Cu(NO₃)₂·2.5H₂O",
        "linker_smiles": "C(=O)O",
        "product_mass_mg": 17.13, 
        "metal_mass_mg": 15.0, 
        "linker_mass_mg": 5.0,
        "solvent_name": "DMF", 
        "solvent_volume_ml": 1.5,
        "additive_name": "-", 
        "additive_volume_ml": 0.0,
        "modulator_name": "HCl", 
        "modulator_volume_ml": 19.0  # VERY HIGH VOLUME!
    }
    
    target_mof = 0.0413
    target_storage = 0.7236
    
    print("Parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    print(f"\nTarget MOF Cost: {target_mof}")
    print(f"Target Storage Cost: {target_storage}")
    
    # Run calculation with calculate_mof_cost directly
    result = calculate_mof_cost(**params)
    
    actual_mof = result['mof_cost_usd_per_kg']
    
    print(f"\nActual MOF Cost: {actual_mof:.4f}")
    print(f"MOF Cost Ratio: {actual_mof / target_mof:.4f}")
    
    # Analyze cost breakdown
    print(f"\n=== COST BREAKDOWN ===")
    
    raw_costs = result.get('raw_costs', {})
    scaled_costs = result.get('scaled_costs', {})
    scale_factors = result.get('scale_factors', {})
    
    print("Raw costs (EUR):")
    for component, cost in raw_costs.items():
        print(f"  {component}: {cost:.6f}")
    
    print("\nScale factors:")
    for factor, value in scale_factors.items():
        print(f"  {factor}: {value:.6f}")
    
    print("\nScaled costs (EUR):")
    for component, cost in scaled_costs.items():
        print(f"  {component}: {cost:.6f}")
    
    total_scaled_eur = result.get('total_scaled_eur', 0)
    product_kg = result.get('product_kg', 0)
    
    print(f"\nTotal scaled cost (EUR): {total_scaled_eur:.6f}")
    print(f"Product mass (kg): {product_kg:.6f}")
    
    if product_kg > 0:
        print(f"MOF Price (EUR/kg): {total_scaled_eur / product_kg:.4f}")
        print(f"MOF Price (USD/kg): {(total_scaled_eur / product_kg) * 1.15:.4f}")
    
    # Check database prices
    print(f"\n=== DATABASE PRICES ===")
    db = load_price_database()
    
    # Check HCl price
    modulators = db.get('modulators', {})
    hcl_price = None
    for name, data in modulators.items():
        if 'hcl' in name.lower():
            hcl_price = data.get('price_eur_per_ml', 0)
            print(f"HCl ({name}): {hcl_price:.6f} EUR/mL")
            break
    
    if hcl_price and product_kg > 0:
        hcl_raw_cost = hcl_price * 19.0  # 19 mL
        print(f"HCl raw cost (19 mL): {hcl_raw_cost:.6f} EUR")
        
        # Calculate what the HCl price should be to get target cost
        target_total_eur = target_mof * product_kg / 1.15
        print(f"Target total cost (EUR): {target_total_eur:.6f}")
        
        # Current cost without HCl
        other_costs = sum(cost for key, cost in scaled_costs.items() if 'modulator' not in key)
        print(f"Other costs (scaled EUR): {other_costs:.6f}")
        
        # Required HCl cost
        required_hcl_scaled = target_total_eur - other_costs
        print(f"Required HCl cost (scaled EUR): {required_hcl_scaled:.6f}")
        
        # Required HCl price per mL
        scale_factor_general = scale_factors.get('general', 1.0)
        required_hcl_raw = required_hcl_scaled / scale_factor_general
        required_hcl_price_per_ml = required_hcl_raw / 19.0
        
        print(f"Required HCl price per mL: {required_hcl_price_per_ml:.6f} EUR/mL")
        print(f"Current HCl price per mL: {hcl_price:.6f} EUR/mL")
        print(f"Price adjustment factor: {required_hcl_price_per_ml / hcl_price:.6f}")
    
    # Test with different HCl volumes to see the pattern
    print(f"\n=== TESTING DIFFERENT HCl VOLUMES ===")
    test_volumes = [0.1, 0.5, 1.0, 5.0, 10.0, 15.0, 19.0, 25.0]
    
    for vol in test_volumes:
        test_params = params.copy()
        test_params['modulator_volume_ml'] = vol
        
        try:
            test_result = calculate_mof_cost(**test_params)
            test_mof = test_result['mof_cost_usd_per_kg']
            print(f"HCl {vol:4.1f} mL → MOF Cost: {test_mof:.4f} USD/kg")
        except Exception as e:
            print(f"HCl {vol:4.1f} mL → Error: {e}")

if __name__ == "__main__":
    debug_case4()