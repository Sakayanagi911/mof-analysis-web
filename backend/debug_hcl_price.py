#!/usr/bin/env python3
"""
Debug HCl price issue in Use Case 4
"""

from services.cost_analysis import load_price_database

def debug_hcl_price():
    """
    Debug HCl price yang mungkin terlalu tinggi
    """
    
    print("=== DEBUG HCl PRICE ISSUE ===")
    
    # Load database
    db = load_price_database()
    
    # Check HCl in modulators
    modulators = db.get("modulators", {})
    
    print("HCl entries in modulators:")
    for key, value in modulators.items():
        if "hcl" in key.lower():
            print(f"  {key}: {value}")
    
    print()
    
    # Calculate Use Case 4 modulator cost manually
    modulator_volume_ml = 19.0
    
    if "HCl" in modulators:
        hcl_price = modulators["HCl"]["price_eur_per_ml"]
        modulator_cost = hcl_price * modulator_volume_ml
        
        print(f"HCl price: {hcl_price} EUR/mL")
        print(f"Volume: {modulator_volume_ml} mL")
        print(f"Raw modulator cost: {modulator_cost} EUR")
        print()
        
        # Compare with other components
        print("=== COST COMPARISON ===")
        
        # Typical linker cost for Use Case 4
        linker_price = 0.0182  # EUR/g (formic acid)
        linker_mass_g = 5.0 / 1000.0  # 5 mg
        linker_cost = linker_price * linker_mass_g
        
        print(f"Linker cost: {linker_cost} EUR")
        print(f"Modulator cost: {modulator_cost} EUR")
        print(f"Modulator/Linker ratio: {modulator_cost/linker_cost:.1f}x")
        
        if modulator_cost > linker_cost * 10:
            print("⚠️  Modulator cost is much higher than linker cost!")
            print("   This suggests HCl price might be too high")
        
        # Check if 19 mL is realistic
        print(f"\n=== VOLUME ANALYSIS ===")
        print(f"HCl volume: {modulator_volume_ml} mL")
        print("This is equivalent to:")
        print(f"  - {modulator_volume_ml/1000:.3f} L")
        print(f"  - {modulator_volume_ml} cm³")
        
        if modulator_volume_ml > 10:
            print("⚠️  Very large modulator volume!")
            print("   Typical modulator volumes are 0.05-0.5 mL")
            print("   19 mL seems unusually large")
        
        # Suggest potential fixes
        print(f"\n=== POTENTIAL FIXES ===")
        
        # Option 1: Lower HCl price
        target_modulator_cost = linker_cost * 2  # 2x linker cost seems reasonable
        suggested_hcl_price = target_modulator_cost / modulator_volume_ml
        print(f"1. Lower HCl price to {suggested_hcl_price:.6f} EUR/mL")
        print(f"   (would make modulator cost = {target_modulator_cost:.6f} EUR)")
        
        # Option 2: Check if volume is correct
        print(f"2. Verify if 19 mL volume is correct in original data")
        print(f"   Maybe it should be 1.9 mL or 0.19 mL?")
        
        # Option 3: Check concentration
        print(f"3. Check if HCl concentration affects the calculation")
        print(f"   Maybe it's diluted HCl, not concentrated")

if __name__ == "__main__":
    debug_hcl_price()