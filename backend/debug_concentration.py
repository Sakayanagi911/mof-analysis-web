#!/usr/bin/env python3
"""
Debug script untuk test modulator concentration
Tidak ada pemaksaan hasil - hanya test perhitungan murni matematis
"""

from services.cost_analysis import calculate_energy

def debug_concentration_effect():
    """
    Debug bagaimana concentration mempengaruhi perhitungan energi
    Test dengan data user yang diberikan
    """
    
    # Base parameters untuk test
    base_params = {
        "smiles": "O=C(O)c1ccc(cc1)C(=O)O",  # Terephthalic acid
        "temperature_c": 85.0,
        "reaction_time_h": 24.0,
        "linker_mass_mg": 5.0,
        "metal_mass_mg": 8.0,
        "solvent_name": "DMF",
        "solvent_volume_ml": 2.0,
        "additive_name": "-",
        "additive_volume_ml": 0.0,
        "modulator_name": "HNO3",
        "modulator_volume_ml": 0.05,
        "metal_name": "CuSO₄·5H₂O",
        "volumetric_wc": 40.0,
        "gravimetric_wc": 5.5,
        "product_mass_mg": 9.12,
        "energy_scale_factor": 1.0
    }
    
    # Test concentration values dari data user
    test_concentrations = [
        ("FATQID", 4.44),
        ("NAWXER", 11.98), 
        ("VOLPET", 100.0),  # No modulator
        ("YAVWUQ", 18.54),
        ("YUGLES", 4.44)
    ]
    
    print("=== DEBUG MODULATOR CONCENTRATION EFFECT ===")
    print("Base parameters:")
    for key, value in base_params.items():
        print(f"  {key}: {value}")
    print()
    
    print("Testing different concentrations:")
    print("Use Case | Concentration | E_Modulator (J) | E_Total (J) | Notes")
    print("-" * 70)
    
    for use_case, concentration in test_concentrations:
        # Update modulator untuk YAVWUQ (HCl instead of HNO3)
        modulator_name = "HCl" if use_case == "YAVWUQ" else "HNO3"
        modulator_volume = 0.0 if use_case == "VOLPET" else 0.05
        
        # Create params copy and update specific values
        params = base_params.copy()
        params["modulator_name"] = modulator_name
        params["modulator_volume_ml"] = modulator_volume
        params["modulator_concentration"] = concentration
        
        result = calculate_energy(**params)
        
        e_modulator = result.get("e_sensible_modulator_j", 0.0)
        e_total = result.get("e_sensible_total_j", 0.0)
        
        notes = ""
        if use_case == "VOLPET":
            notes = "No modulator"
        elif use_case == "YAVWUQ":
            notes = "HCl instead of HNO3"
        
        print(f"{use_case:8} | {concentration:11.2f}% | {e_modulator:13.4f} | {e_total:9.2f} | {notes}")
    
    print()
    print("=== DETAILED CALCULATION FOR FATQID (4.44%) ===")
    
    params_detailed = base_params.copy()
    params_detailed["modulator_concentration"] = 4.44
    result_detailed = calculate_energy(**params_detailed)
    
    print("Energy breakdown:")
    for key, value in result_detailed.items():
        if key.startswith("e_sensible_"):
            print(f"  {key}: {value:.4f} J")
    
    print()
    print("=== COMPARISON: 100% vs 4.44% ===")
    
    params_100 = base_params.copy()
    params_100["modulator_concentration"] = 100.0
    result_100 = calculate_energy(**params_100)
    
    params_444 = base_params.copy()
    params_444["modulator_concentration"] = 4.44
    result_444 = calculate_energy(**params_444)
    
    e_mod_100 = result_100.get("e_sensible_modulator_j", 0.0)
    e_mod_444 = result_444.get("e_sensible_modulator_j", 0.0)
    
    print(f"Modulator energy at 100%: {e_mod_100:.4f} J")
    print(f"Modulator energy at 4.44%: {e_mod_444:.4f} J")
    print(f"Ratio (4.44% / 100%): {e_mod_444/e_mod_100 if e_mod_100 > 0 else 0:.4f}")
    print(f"Expected ratio: {4.44/100:.4f}")
    
    if abs((e_mod_444/e_mod_100) - (4.44/100)) < 0.001:
        print("✅ Concentration calculation is CORRECT")
    else:
        print("❌ Concentration calculation has issues")

if __name__ == "__main__":
    debug_concentration_effect()