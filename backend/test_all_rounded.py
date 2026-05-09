#!/usr/bin/env python3
"""
Test semua 5 use cases dengan output yang dibulatkan 4 decimal places
"""

from services.cost_analysis import run_economic_analysis

def test_all_rounded():
    """
    Test semua 5 use cases dengan output rounded ke 4 decimal places
    """
    
    print("=== ALL USE CASES - ROUNDED OUTPUT (4 DECIMAL PLACES) ===")
    
    use_cases = [
        {
            "name": "Use Case 1",
            "solvent_name": "DMF", "solvent_volume_ml": 2.0,
            "additive_name": "-", "additive_volume_ml": 0.0,
            "modulator_name": "HNO3", "modulator_volume_ml": 0.05,
            "metal_name": "CuSO₄·5H₂O", "metal_mass_mg": 8.0,
            "smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
            "linker_mass_mg": 5.0, "product_mass_mg": 9.12,
            "reaction_time_h": 24.0, "temperature_c": 85.0,
            "expected_mof_cost": 1.7914, "expected_storage_cost": 24.6217
        },
        {
            "name": "Use Case 2",
            "solvent_name": "DMF", "solvent_volume_ml": 1.0,
            "additive_name": "EtOH", "additive_volume_ml": 0.5,
            "modulator_name": "HNO3", "modulator_volume_ml": 0.15,
            "metal_name": "Zn(NO₃)₂·6H₂O", "metal_mass_mg": 10.0,
            "smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1",
            "linker_mass_mg": 4.0, "product_mass_mg": 3.785,
            "reaction_time_h": 24.0, "temperature_c": 85.0,
            "expected_mof_cost": 5.0682, "expected_storage_cost": 76.6513
        },
        {
            "name": "Use Case 3",
            "solvent_name": "DMF", "solvent_volume_ml": 4.0,
            "additive_name": "MeCN", "additive_volume_ml": 1.0,
            "modulator_name": "-", "modulator_volume_ml": 0.0,
            "metal_name": "Zn(NO₃)₂·6H₂O", "metal_mass_mg": 119.0,
            "smiles": "S1C(=CC=C1C(=O)O)C(=O)O",
            "linker_mass_mg": 52.0, "product_mass_mg": 52.3,
            "reaction_time_h": 48.0, "temperature_c": 120.0,
            "expected_mof_cost": 0.1056, "expected_storage_cost": 1.771
        },
        {
            "name": "Use Case 4",
            "solvent_name": "DMF", "solvent_volume_ml": 1.5,
            "additive_name": "-", "additive_volume_ml": 0.0,
            "modulator_name": "HCl", "modulator_volume_ml": 19.0,
            "metal_name": "Cu(NO₃)₂·2.5H₂O", "metal_mass_mg": 15.0,
            "smiles": "C(=O)O",
            "linker_mass_mg": 5.0, "product_mass_mg": 17.13,
            "reaction_time_h": 96.0, "temperature_c": 70.0,
            "expected_mof_cost": 0.0413, "expected_storage_cost": 0.7236
        },
        {
            "name": "Use Case 5",
            "solvent_name": "DMF", "solvent_volume_ml": 0.2,
            "additive_name": "DMSO", "additive_volume_ml": 0.2,
            "modulator_name": "HNO3", "modulator_volume_ml": 0.06,
            "metal_name": "Cu(NO₃)₂·3H₂O", "metal_mass_mg": 15.0,
            "smiles": "C(#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O",
            "linker_mass_mg": 5.0, "product_mass_mg": 6.3,
            "reaction_time_h": 24.0, "temperature_c": 65.0,
            "expected_mof_cost": 6.6163, "expected_storage_cost": 110.3287
        }
    ]
    
    results = []
    
    for case in use_cases:
        print(f"=== {case['name'].upper()} ===")
        
        try:
            result = run_economic_analysis(
                metal_name=case['metal_name'],
                linker_smiles=case['smiles'],
                reaction_time=case['reaction_time_h'],
                temperature=case['temperature_c'],
                smiles=case['smiles'],
                product_mass_mg=case['product_mass_mg'],
                metal_mass_mg=case['metal_mass_mg'],
                linker_mass_mg=case['linker_mass_mg'],
                solvent_name=case['solvent_name'],
                solvent_volume_ml=case['solvent_volume_ml'],
                additive_name=case['additive_name'],
                additive_volume_ml=case['additive_volume_ml'],
                modulator_name=case['modulator_name'],
                modulator_volume_ml=case['modulator_volume_ml']
            )
            
            mof_cost = result['mof_cost_usd_per_kg']
            storage_cost = result['storage_cost_usd_per_kg_h2']
            
            print(f"Expected: {case['expected_mof_cost']} USD/kg MOF, {case['expected_storage_cost']} USD/kg H2")
            print(f"Actual:   {mof_cost} USD/kg MOF, {storage_cost} USD/kg H2")
            
            # Check decimal places
            mof_decimals = len(str(mof_cost).split('.')[1]) if '.' in str(mof_cost) else 0
            storage_decimals = len(str(storage_cost).split('.')[1]) if '.' in str(storage_cost) else 0
            
            print(f"Decimal places: MOF={mof_decimals}, Storage={storage_decimals}")
            
            # Calculate differences
            mof_diff_pct = abs(mof_cost - case['expected_mof_cost']) / case['expected_mof_cost'] * 100
            storage_diff_pct = abs(storage_cost - case['expected_storage_cost']) / case['expected_storage_cost'] * 100
            
            mof_status = "✅" if mof_diff_pct < 5 else "❌"
            storage_status = "✅" if storage_diff_pct < 5 else "❌"
            
            print(f"Accuracy: MOF {mof_diff_pct:.2f}% {mof_status}, Storage {storage_diff_pct:.2f}% {storage_status}")
            
            results.append({
                "case": case['name'],
                "mof_cost": mof_cost,
                "storage_cost": storage_cost,
                "mof_decimals": mof_decimals,
                "storage_decimals": storage_decimals,
                "mof_ok": mof_diff_pct < 5,
                "storage_ok": storage_diff_pct < 5
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"case": case['name'], "error": str(e)})
        
        print()
    
    # Summary
    print("=== SUMMARY ===")
    print("| Case | MOF Cost | Storage Cost | Decimals | Status |")
    print("|------|----------|--------------|----------|--------|")
    
    for result in results:
        if 'error' in result:
            print(f"| {result['case']} | ERROR | ERROR | - | ❌ |")
        else:
            mof_status = "✅" if result['mof_ok'] else "❌"
            storage_status = "✅" if result['storage_ok'] else "❌"
            overall_status = "✅" if result['mof_ok'] and result['storage_ok'] else "❌"
            decimals_ok = "✅" if result['mof_decimals'] <= 4 and result['storage_decimals'] <= 4 else "❌"
            print(f"| {result['case']} | {mof_status} | {storage_status} | {decimals_ok} ({result['mof_decimals']},{result['storage_decimals']}) | {overall_status} |")
    
    # Check decimal places consistency
    valid_results = [r for r in results if 'error' not in r]
    all_decimals_ok = all(r['mof_decimals'] <= 4 and r['storage_decimals'] <= 4 for r in valid_results)
    
    print()
    if all_decimals_ok:
        print("✅ All outputs have ≤ 4 decimal places")
    else:
        print("❌ Some outputs have > 4 decimal places")
    
    accuracy_count = len([r for r in valid_results if r['mof_ok'] and r['storage_ok']])
    print(f"Overall accuracy: {accuracy_count}/{len(valid_results)} cases")

if __name__ == "__main__":
    test_all_rounded()