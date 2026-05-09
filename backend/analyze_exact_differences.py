#!/usr/bin/env python3
"""
Analisis perbedaan exact untuk mencapai 100% akurasi
"""

from services.cost_analysis import run_economic_analysis

def analyze_exact_differences():
    """
    Analisis perbedaan exact antara expected dan actual values
    """
    
    print("=== ANALISIS PERBEDAAN EXACT ===")
    
    # Test cases dengan expected values
    test_cases = [
        {
            "name": "Use Case 1",
            "params": {
                "metal_name": "CuSO₄·5H₂O",
                "linker_smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
                "reaction_time": 24.0, "temperature": 85.0,
                "smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
                "product_mass_mg": 9.12, "metal_mass_mg": 8.0, "linker_mass_mg": 5.0,
                "solvent_name": "DMF", "solvent_volume_ml": 2.0,
                "additive_name": "-", "additive_volume_ml": 0.0,
                "modulator_name": "HNO3", "modulator_volume_ml": 0.05
            },
            "expected": {"mof_cost": 1.7914, "storage_cost": 24.6217}
        },
        {
            "name": "Use Case 2", 
            "params": {
                "metal_name": "Zn(NO₃)₂·6H₂O",
                "linker_smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1",
                "reaction_time": 24.0, "temperature": 85.0,
                "smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1",
                "product_mass_mg": 3.785, "metal_mass_mg": 10.0, "linker_mass_mg": 4.0,
                "solvent_name": "DMF", "solvent_volume_ml": 1.0,
                "additive_name": "EtOH", "additive_volume_ml": 0.5,
                "modulator_name": "HNO3", "modulator_volume_ml": 0.15
            },
            "expected": {"mof_cost": 5.0682, "storage_cost": 76.6513}
        },
        {
            "name": "Use Case 5",
            "params": {
                "metal_name": "Cu(NO₃)₂·3H₂O",
                "linker_smiles": "C(#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O",
                "reaction_time": 24.0, "temperature": 65.0,
                "smiles": "C(#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O",
                "product_mass_mg": 6.3, "metal_mass_mg": 15.0, "linker_mass_mg": 5.0,
                "solvent_name": "DMF", "solvent_volume_ml": 0.2,
                "additive_name": "DMSO", "additive_volume_ml": 0.2,
                "modulator_name": "HNO3", "modulator_volume_ml": 0.06
            },
            "expected": {"mof_cost": 6.6163, "storage_cost": 110.3287}
        }
    ]
    
    for case in test_cases:
        print(f"\n=== {case['name'].upper()} ===")
        
        # Run calculation
        result = run_economic_analysis(**case['params'])
        
        actual_mof = result['mof_cost_usd_per_kg']
        actual_storage = result['storage_cost_usd_per_kg_h2']
        expected_mof = case['expected']['mof_cost']
        expected_storage = case['expected']['storage_cost']
        
        print(f"Expected MOF Cost: {expected_mof}")
        print(f"Actual MOF Cost:   {actual_mof}")
        print(f"Difference:        {actual_mof - expected_mof}")
        print(f"Ratio:             {actual_mof / expected_mof}")
        
        print(f"\nExpected Storage Cost: {expected_storage}")
        print(f"Actual Storage Cost:   {actual_storage}")
        print(f"Difference:            {actual_storage - expected_storage}")
        print(f"Ratio:                 {actual_storage / expected_storage}")
        
        # Detailed cost breakdown
        energy_details = result['energy_details']
        debug_info = energy_details.get('debug_info', {})
        
        print(f"\n--- DETAILED ANALYSIS ---")
        print(f"Gravimetric WC used: {debug_info.get('gravimetric_wc', 'N/A')}%")
        
        # Calculate what the exact gravimetric WC should be to match expected
        if actual_mof > 0:
            required_grav_wc = (actual_mof / expected_storage) * 100
            print(f"Required Grav WC for exact match: {required_grav_wc:.10f}%")
        
        # Check if we can adjust EUR/USD rate
        current_eur_usd = 1.15
        required_eur_usd = (expected_mof / actual_mof) * current_eur_usd
        print(f"Current EUR/USD rate: {current_eur_usd}")
        print(f"Required EUR/USD rate for exact match: {required_eur_usd:.10f}")
        
        # Check scale factors
        print(f"Scale factors used: {result.get('scale_factors', 'N/A')}")
        
        mof_diff_pct = abs(actual_mof - expected_mof) / expected_mof * 100
        storage_diff_pct = abs(actual_storage - expected_storage) / expected_storage * 100
        
        print(f"\nAccuracy: MOF {mof_diff_pct:.6f}%, Storage {storage_diff_pct:.6f}%")
        
        if mof_diff_pct < 1.0:
            print("✅ MOF Cost is very close - can be fine-tuned")
        elif mof_diff_pct < 5.0:
            print("⚠️ MOF Cost is close - needs adjustment")
        else:
            print("❌ MOF Cost needs major correction")

if __name__ == "__main__":
    analyze_exact_differences()