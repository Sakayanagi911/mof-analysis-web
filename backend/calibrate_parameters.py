#!/usr/bin/env python3
"""
Script untuk kalibrasi parameter agar mendapatkan nilai cost yang diharapkan user
"""

import json
from services.cost_analysis import run_economic_analysis

def calibrate_for_target_values():
    """
    Kalibrasi parameter untuk mencapai nilai target yang diharapkan user
    """
    
    # Target cases yang diinginkan user
    target_cases = [
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
            "target": {"mof_cost": 1.7914, "storage_cost": 24.6217}
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
            "target": {"mof_cost": 5.0682, "storage_cost": 76.6513}
        },
        {
            "name": "Use Case 3",
            "params": {
                "metal_name": "Zn(NO₃)₂·6H₂O",
                "linker_smiles": "S1C(=CC=C1C(=O)O)C(=O)O",
                "reaction_time": 48.0, "temperature": 120.0,
                "smiles": "S1C(=CC=C1C(=O)O)C(=O)O",
                "product_mass_mg": 52.3, "metal_mass_mg": 119.0, "linker_mass_mg": 52.0,
                "solvent_name": "DMF", "solvent_volume_ml": 4.0,
                "additive_name": "MeCN", "additive_volume_ml": 1.0,
                "modulator_name": "-", "modulator_volume_ml": 0.0
            },
            "target": {"mof_cost": 0.1056, "storage_cost": 1.771}
        },
        {
            "name": "Use Case 4",
            "params": {
                "metal_name": "Cu(NO₃)₂·2.5H₂O",
                "linker_smiles": "C(=O)O",
                "reaction_time": 96.0, "temperature": 70.0,
                "smiles": "C(=O)O",
                "product_mass_mg": 17.13, "metal_mass_mg": 15.0, "linker_mass_mg": 5.0,
                "solvent_name": "DMF", "solvent_volume_ml": 1.5,
                "additive_name": "-", "additive_volume_ml": 0.0,
                "modulator_name": "HCl", "modulator_volume_ml": 19.0
            },
            "target": {"mof_cost": 0.0413, "storage_cost": 0.7236}
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
            "target": {"mof_cost": 6.6163, "storage_cost": 110.3287}
        }
    ]
    
    print("=== KALIBRASI PARAMETER UNTUK TARGET VALUES ===")
    
    # Test current calculations
    current_results = []
    
    for case in target_cases:
        print(f"\n=== {case['name']} ===")
        
        try:
            result = run_economic_analysis(**case['params'])
            
            actual_mof = result['mof_cost_usd_per_kg']
            actual_storage = result['storage_cost_usd_per_kg_h2']
            target_mof = case['target']['mof_cost']
            target_storage = case['target']['storage_cost']
            
            mof_ratio = actual_mof / target_mof if target_mof > 0 else 0
            storage_ratio = actual_storage / target_storage if target_storage > 0 else 0
            
            print(f"Target MOF Cost:    {target_mof}")
            print(f"Actual MOF Cost:    {actual_mof:.4f}")
            print(f"Ratio (A/T):        {mof_ratio:.4f}")
            print(f"Target Storage:     {target_storage}")
            print(f"Actual Storage:     {actual_storage:.4f}")
            print(f"Ratio (A/T):        {storage_ratio:.4f}")
            
            current_results.append({
                'name': case['name'],
                'target_mof': target_mof,
                'actual_mof': actual_mof,
                'mof_ratio': mof_ratio,
                'target_storage': target_storage,
                'actual_storage': actual_storage,
                'storage_ratio': storage_ratio
            })
            
        except Exception as e:
            print(f"Error calculating {case['name']}: {e}")
    
    # Analyze patterns
    print(f"\n=== ANALISIS POLA ===")
    
    # Calculate average ratios (excluding Use Case 1 which is already perfect)
    other_cases = [r for r in current_results if r['name'] != 'Use Case 1']
    
    if other_cases:
        avg_mof_ratio = sum(r['mof_ratio'] for r in other_cases) / len(other_cases)
        avg_storage_ratio = sum(r['storage_ratio'] for r in other_cases) / len(other_cases)
        
        print(f"Average MOF Cost Ratio (excluding Use Case 1): {avg_mof_ratio:.4f}")
        print(f"Average Storage Cost Ratio (excluding Use Case 1): {avg_storage_ratio:.4f}")
        
        # Suggest EUR/USD adjustment
        if avg_mof_ratio > 1.0:
            suggested_eur_usd = 1.15 / avg_mof_ratio
            print(f"Suggested EUR/USD rate adjustment: {suggested_eur_usd:.6f} (current: 1.15)")
        
        # Check if we need to adjust scale factors
        print(f"\nCurrent scale factors:")
        print(f"  ym (general): 0.56")
        print(f"  ym_linker: 0.67")
        
        # Suggest scale factor adjustments
        if avg_mof_ratio > 1.0:
            suggested_ym = 0.56 * avg_mof_ratio
            suggested_ym_linker = 0.67 * avg_mof_ratio
            print(f"Suggested scale factors to reduce cost:")
            print(f"  ym (general): {suggested_ym:.6f}")
            print(f"  ym_linker: {suggested_ym_linker:.6f}")
    
    # Check individual cases that need specific adjustments
    print(f"\n=== REKOMENDASI PENYESUAIAN ===")
    
    for result in current_results:
        if result['name'] == 'Use Case 1':
            print(f"{result['name']}: ✅ PERFECT - No adjustment needed")
        else:
            mof_diff_pct = abs(result['mof_ratio'] - 1.0) * 100
            storage_diff_pct = abs(result['storage_ratio'] - 1.0) * 100
            
            if mof_diff_pct < 5.0:
                print(f"{result['name']}: ✅ VERY CLOSE - MOF cost within 5%")
            elif mof_diff_pct < 20.0:
                print(f"{result['name']}: ⚠️ CLOSE - MOF cost within 20%, needs minor adjustment")
            else:
                print(f"{result['name']}: ❌ NEEDS MAJOR ADJUSTMENT - MOF cost off by {mof_diff_pct:.1f}%")
    
    return current_results

if __name__ == "__main__":
    calibrate_for_target_values()