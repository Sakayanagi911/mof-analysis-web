#!/usr/bin/env python3
"""
Test script untuk verify FATQID default values
"""

from services.cost_analysis import calculate_energy

def test_fatqid_defaults():
    """Test dengan FATQID default values"""
    
    fatqid_params = {
        "smiles": "O=C(O)c1ccc(cc1)C(=O)O",
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
        "modulator_concentration": 4.44,
        "metal_name": "CuSO₄·5H₂O",
        "volumetric_wc": 40.0,
        "gravimetric_wc": 5.5,
        "product_mass_mg": 9.12,
        "energy_scale_factor": 1.0
    }
    
    print("=== TESTING FATQID DEFAULT VALUES ===")
    print("Parameters:")
    for key, value in fatqid_params.items():
        print(f"  {key}: {value}")
    
    result = calculate_energy(**fatqid_params)
    
    print("\nEnergy Results:")
    print(f"  Solvent: {result.get('e_sensible_solvent_j', 0):.4f} J")
    print(f"  Additive: {result.get('e_sensible_additive_j', 0):.4f} J")
    print(f"  Modulator: {result.get('e_sensible_modulator_j', 0):.4f} J")
    print(f"  Metal: {result.get('e_sensible_metal_j', 0):.4f} J")
    print(f"  Linker: {result.get('e_sensible_linker_j', 0):.4f} J")
    print(f"  Total: {result.get('e_sensible_total_j', 0):.4f} J")
    
    print(f"\nOther Results:")
    print(f"  Q Energy: {result.get('q_energy_mj', 0):.6f} MJ")
    print(f"  Q Loss: {result.get('q_loss_mj', 0):.6f} MJ")
    print(f"  E Stirr: {result.get('e_stirr_mj', 0):.6f} MJ")
    print(f"  E Total: {result.get('e_total_mj', 0):.6f} MJ")

if __name__ == "__main__":
    test_fatqid_defaults()