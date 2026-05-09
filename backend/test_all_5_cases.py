#!/usr/bin/env python3
"""
Test semua 5 use cases dengan expected output terbaru
"""

from services.cost_analysis import run_economic_analysis

def test_all_5_cases():
    """
    Test semua 5 use cases dengan expected output yang diberikan user
    """
    
    print("=== TESTING ALL 5 USE CASES ===")
    print("Expected outputs:")
    print("Use Case 1: 1.7914 MOF Price (USD/kg), 24.6217 H2 Storage Cost (USD/kg H2)")
    print("Use Case 2: 5.0682 MOF Price (USD/kg), 76.6513 H2 Storage Cost (USD/kg H2)")
    print("Use Case 3: 0.1056 MOF Price (USD/kg), 1.771 H2 Storage Cost (USD/kg H2)")
    print("Use Case 4: 0.0413 MOF Price (USD/kg), 0.7236 H2 Storage Cost (USD/kg H2)")
    print("Use Case 5: 6.6163 MOF Price (USD/kg), 110.3287 H2 Storage Cost (USD/kg H2)")
    print()
    
    # Define all use cases
    use_cases = [
        {
            "name": "Use Case 1",
            "solvent_name": "DMF",
            "solvent_volume_ml": 2.0,
            "additive_name": "-",
            "additive_volume_ml": 0.0,
            "modulator_name": "HNO3",
            "modulator_volume_ml": 0.05,
            "metal_name": "CuSO₄·5H₂O",
            "metal_mass_mg": 8.0,
            "linker_smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",  # H₂L
            "linker_mass_mg": 5.0,
            "product_mass_mg": 9.12,
            "reaction_time_h": 24.0,
            "temperature_c": 85.0,
            "expected_mof_cost": 1.7914,
            "expected_storage_cost": 24.6217
        },
        {
            "name": "Use Case 2",
            "solvent_name": "DMF",
            "solvent_volume_ml": 1.0,
            "additive_name": "EtOH",
            "additive_volume_ml": 0.5,
            "modulator_name": "HNO3",
            "modulator_volume_ml": 0.15,
            "metal_name": "Zn(NO₃)₂·6H₂O",
            "metal_mass_mg": 10.0,
            "linker_smiles": "C(=O)(O)C=1C=C2C=CC(=CC2=CC1)N(C1=CC=C(C=C1)C=1C=C(C=C(C1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C=1C=C(C=C(C1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O",  # H4TCPP
            "linker_mass_mg": 4.0,
            "product_mass_mg": 3.785,
            "reaction_time_h": 24.0,
            "temperature_c": 85.0,
            "expected_mof_cost": 5.0682,
            "expected_storage_cost": 76.6513
        },
        {
            "name": "Use Case 3",
            "solvent_name": "DMF",
            "solvent_volume_ml": 4.0,
            "additive_name": "MeCN",
            "additive_volume_ml": 1.0,
            "modulator_name": "-",
            "modulator_volume_ml": 0.0,
            "metal_name": "Zn(NO₃)₂·6H₂O",
            "metal_mass_mg": 119.0,
            "linker_smiles": "S1C(=CC=C1C(=O)O)C(=O)O",  # H₂thb
            "linker_mass_mg": 52.0,
            "product_mass_mg": 52.3,
            "reaction_time_h": 48.0,
            "temperature_c": 120.0,
            "expected_mof_cost": 0.1056,
            "expected_storage_cost": 1.771
        },
        {
            "name": "Use Case 4",
            "solvent_name": "DMF",
            "solvent_volume_ml": 1.5,
            "additive_name": "-",
            "additive_volume_ml": 0.0,
            "modulator_name": "HCl",
            "modulator_volume_ml": 19.0,
            "metal_name": "Cu(NO₃)₂·2.5H₂O",
            "metal_mass_mg": 15.0,
            "linker_smiles": "C(=O)O",  # H₄L (formate)
            "linker_mass_mg": 5.0,
            "product_mass_mg": 17.13,
            "reaction_time_h": 96.0,
            "temperature_c": 70.0,
            "expected_mof_cost": 0.0413,
            "expected_storage_cost": 0.7236
        },
        {
            "name": "Use Case 5",
            "solvent_name": "DMF",
            "solvent_volume_ml": 0.2,
            "additive_name": "DMSO",
            "additive_volume_ml": 0.2,
            "modulator_name": "HNO3",
            "modulator_volume_ml": 0.06,
            "metal_name": "Cu(NO₃)₂·3H₂O",
            "metal_mass_mg": 15.0,
            "linker_smiles": "C(#CC#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O",  # H₄EBTC
            "linker_mass_mg": 5.0,
            "product_mass_mg": 6.3,
            "reaction_time_h": 24.0,
            "temperature_c": 65.0,
            "expected_mof_cost": 6.6163,
            "expected_storage_cost": 110.3287
        }
    ]
    
    results = []
    
    for i, case in enumerate(use_cases, 1):
        print(f"=== {case['name'].upper()} ===")
        print(f"Solvent: {case['solvent_name']} {case['solvent_volume_ml']} mL")
        if case['additive_name'] != "-":
            print(f"Additive: {case['additive_name']} {case['additive_volume_ml']} mL")
        if case['modulator_name'] != "-":
            print(f"Modulator: {case['modulator_name']} {case['modulator_volume_ml']} mL")
        print(f"Metal: {case['metal_name']} {case['metal_mass_mg']} mg")
        print(f"Linker: {case['linker_mass_mg']} mg")
        print(f"Product: {case['product_mass_mg']} mg")
        print(f"Time: {case['reaction_time_h']} h, Temp: {case['temperature_c']} °C")
        
        try:
            # Run economic analysis
            result = run_economic_analysis(
                metal_name=case['metal_name'],
                linker_smiles=case['linker_smiles'],
                reaction_time=case['reaction_time_h'],
                temperature=case['temperature_c'],
                smiles=case['linker_smiles'],
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
            
            actual_mof_cost = result['mof_cost_usd_per_kg']
            actual_storage_cost = result['storage_cost_usd_per_kg_h2']
            
            print(f"Expected MOF Cost: {case['expected_mof_cost']} USD/kg")
            print(f"Actual MOF Cost: {actual_mof_cost} USD/kg")
            
            print(f"Expected Storage Cost: {case['expected_storage_cost']} USD/kg H2")
            print(f"Actual Storage Cost: {actual_storage_cost} USD/kg H2")
            
            # Calculate differences
            mof_diff = abs(actual_mof_cost - case['expected_mof_cost'])
            mof_pct_diff = (mof_diff / case['expected_mof_cost'] * 100) if case['expected_mof_cost'] != 0 else 0
            
            storage_diff = abs(actual_storage_cost - case['expected_storage_cost'])
            storage_pct_diff = (storage_diff / case['expected_storage_cost'] * 100) if case['expected_storage_cost'] != 0 else 0
            
            mof_status = "✅" if mof_pct_diff < 5 else "❌"
            storage_status = "✅" if storage_pct_diff < 5 else "❌"
            
            print(f"MOF Cost Diff: {mof_pct_diff:.2f}% {mof_status}")
            print(f"Storage Cost Diff: {storage_pct_diff:.2f}% {storage_status}")
            
            results.append({
                "case": case['name'],
                "mof_expected": case['expected_mof_cost'],
                "mof_actual": actual_mof_cost,
                "mof_diff_pct": mof_pct_diff,
                "mof_ok": mof_pct_diff < 5,
                "storage_expected": case['expected_storage_cost'],
                "storage_actual": actual_storage_cost,
                "storage_diff_pct": storage_pct_diff,
                "storage_ok": storage_pct_diff < 5
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "case": case['name'],
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("=== SUMMARY ===")
    print("| Case | MOF Cost | Storage Cost | Status |")
    print("|------|----------|--------------|--------|")
    
    total_cases = len([r for r in results if 'error' not in r])
    mof_ok_count = len([r for r in results if 'error' not in r and r['mof_ok']])
    storage_ok_count = len([r for r in results if 'error' not in r and r['storage_ok']])
    
    for result in results:
        if 'error' in result:
            print(f"| {result['case']} | ERROR | ERROR | ❌ |")
        else:
            mof_status = "✅" if result['mof_ok'] else "❌"
            storage_status = "✅" if result['storage_ok'] else "❌"
            overall_status = "✅" if result['mof_ok'] and result['storage_ok'] else "❌"
            print(f"| {result['case']} | {mof_status} ({result['mof_diff_pct']:.1f}%) | {storage_status} ({result['storage_diff_pct']:.1f}%) | {overall_status} |")
    
    print()
    print(f"MOF Cost Accuracy: {mof_ok_count}/{total_cases} cases within 5%")
    print(f"Storage Cost Accuracy: {storage_ok_count}/{total_cases} cases within 5%")
    print(f"Overall Success Rate: {min(mof_ok_count, storage_ok_count)}/{total_cases} cases")

if __name__ == "__main__":
    test_all_5_cases()