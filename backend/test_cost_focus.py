#!/usr/bin/env python3
"""
Test fokus ke cost calculation dengan SMILES yang sudah diperbaiki
"""

from services.cost_analysis import calculate_mof_cost, get_smiles_mapping, get_uptake_data

def test_cost_focus():
    """
    Test cost calculation untuk semua 5 use cases dengan SMILES yang benar
    """
    
    print("=== FOCUS TEST: COST CALCULATION ONLY ===")
    print("Expected cost outputs:")
    print("Use Case 1: 1.7914 MOF Price (USD/kg), 24.6217 H2 Storage Cost (USD/kg H2)")
    print("Use Case 2: 5.0682 MOF Price (USD/kg), 76.6513 H2 Storage Cost (USD/kg H2)")
    print("Use Case 3: 0.1056 MOF Price (USD/kg), 1.771 H2 Storage Cost (USD/kg H2)")
    print("Use Case 4: 0.0413 MOF Price (USD/kg), 0.7236 H2 Storage Cost (USD/kg H2)")
    print("Use Case 5: 6.6163 MOF Price (USD/kg), 110.3287 H2 Storage Cost (USD/kg H2)")
    print()
    
    # Updated use cases dengan SMILES yang benar
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
            "smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",  # H₂L
            "linker_mass_mg": 5.0,
            "product_mass_mg": 9.12,
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
            "smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1",  # H4TCPP (updated)
            "linker_mass_mg": 4.0,
            "product_mass_mg": 3.785,
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
            "smiles": "S1C(=CC=C1C(=O)O)C(=O)O",  # H₂thb
            "linker_mass_mg": 52.0,
            "product_mass_mg": 52.3,
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
            "smiles": "C(=O)O",  # H₄L (formate)
            "linker_mass_mg": 5.0,
            "product_mass_mg": 17.13,
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
            "smiles": "C(#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O",  # H₄EBTC
            "linker_mass_mg": 5.0,
            "product_mass_mg": 6.3,
            "expected_mof_cost": 6.6163,
            "expected_storage_cost": 110.3287
        }
    ]
    
    # Check SMILES availability first
    print("=== CHECKING SMILES AVAILABILITY ===")
    smiles_mapping = get_smiles_mapping()
    uptake_data = get_uptake_data()
    
    for case in use_cases:
        smiles = case['smiles']
        print(f"{case['name']}: SMILES = {smiles[:50]}...")
        
        in_mapping = smiles in smiles_mapping
        in_uptake = smiles in uptake_data
        
        print(f"  In smiles_mapping: {'✅' if in_mapping else '❌'}")
        print(f"  In uptake_data: {'✅' if in_uptake else '❌'}")
        
        if in_mapping:
            linker_data = smiles_mapping[smiles]
            print(f"  Linker Name: {linker_data.get('linker_name')}")
            print(f"  Price: {linker_data.get('price_eur_per_g')} EUR/g")
        
        if in_uptake:
            uptake_info = uptake_data[smiles]
            print(f"  Gravimetric WC: {uptake_info.get('gravimetric_wc_percent')}%")
        
        print()
    
    print("=== COST CALCULATION RESULTS ===")
    
    results = []
    
    for case in use_cases:
        print(f"=== {case['name'].upper()} ===")
        
        try:
            # Calculate MOF cost
            cost_result = calculate_mof_cost(
                metal_name=case['metal_name'],
                linker_smiles=case['smiles'],
                metal_mass_mg=case['metal_mass_mg'],
                linker_mass_mg=case['linker_mass_mg'],
                product_mass_mg=case['product_mass_mg'],
                solvent_name=case['solvent_name'],
                solvent_volume_ml=case['solvent_volume_ml'],
                additive_name=case['additive_name'],
                additive_volume_ml=case['additive_volume_ml'],
                modulator_name=case['modulator_name'],
                modulator_volume_ml=case['modulator_volume_ml']
            )
            
            mof_cost = cost_result['mof_cost_usd_per_kg']
            
            # Calculate storage cost using uptake from database
            smiles = case['smiles']
            if smiles in uptake_data:
                uptake_info = uptake_data[smiles]
                gravimetric_wc = uptake_info.get('gravimetric_wc_percent', 5.5)
            else:
                gravimetric_wc = 5.5  # default
            
            storage_cost = mof_cost / (gravimetric_wc / 100.0)
            
            print(f"Expected MOF Cost: {case['expected_mof_cost']} USD/kg")
            print(f"Actual MOF Cost: {mof_cost} USD/kg")
            print(f"Expected Storage Cost: {case['expected_storage_cost']} USD/kg H2")
            print(f"Actual Storage Cost: {storage_cost:.4f} USD/kg H2")
            print(f"Gravimetric WC used: {gravimetric_wc}%")
            
            # Calculate differences
            mof_diff = abs(mof_cost - case['expected_mof_cost'])
            mof_pct_diff = (mof_diff / case['expected_mof_cost'] * 100) if case['expected_mof_cost'] != 0 else 0
            
            storage_diff = abs(storage_cost - case['expected_storage_cost'])
            storage_pct_diff = (storage_diff / case['expected_storage_cost'] * 100) if case['expected_storage_cost'] != 0 else 0
            
            mof_status = "✅" if mof_pct_diff < 5 else "❌"
            storage_status = "✅" if storage_pct_diff < 5 else "❌"
            
            print(f"MOF Cost Diff: {mof_pct_diff:.2f}% {mof_status}")
            print(f"Storage Cost Diff: {storage_pct_diff:.2f}% {storage_status}")
            
            # Show detailed cost breakdown
            print("\nCost Breakdown:")
            print(f"  Raw costs: {cost_result['raw_costs']}")
            print(f"  Scale factors: {cost_result['scale_factors']}")
            print(f"  Scaled costs: {cost_result['scaled_costs']}")
            print(f"  Total scaled EUR: {cost_result['total_scaled_eur']}")
            print(f"  Product kg: {cost_result['product_kg']}")
            
            results.append({
                "case": case['name'],
                "mof_expected": case['expected_mof_cost'],
                "mof_actual": mof_cost,
                "mof_diff_pct": mof_pct_diff,
                "mof_ok": mof_pct_diff < 5,
                "storage_expected": case['expected_storage_cost'],
                "storage_actual": storage_cost,
                "storage_diff_pct": storage_pct_diff,
                "storage_ok": storage_pct_diff < 5,
                "gravimetric_wc": gravimetric_wc
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
    print("| Case | MOF Cost | Storage Cost | Grav WC | Status |")
    print("|------|----------|--------------|---------|--------|")
    
    total_cases = len([r for r in results if 'error' not in r])
    mof_ok_count = len([r for r in results if 'error' not in r and r['mof_ok']])
    storage_ok_count = len([r for r in results if 'error' not in r and r['storage_ok']])
    
    for result in results:
        if 'error' in result:
            print(f"| {result['case']} | ERROR | ERROR | - | ❌ |")
        else:
            mof_status = "✅" if result['mof_ok'] else "❌"
            storage_status = "✅" if result['storage_ok'] else "❌"
            overall_status = "✅" if result['mof_ok'] and result['storage_ok'] else "❌"
            print(f"| {result['case']} | {mof_status} ({result['mof_diff_pct']:.1f}%) | {storage_status} ({result['storage_diff_pct']:.1f}%) | {result['gravimetric_wc']:.2f}% | {overall_status} |")
    
    print()
    print(f"MOF Cost Accuracy: {mof_ok_count}/{total_cases} cases within 5%")
    print(f"Storage Cost Accuracy: {storage_ok_count}/{total_cases} cases within 5%")
    print(f"Overall Success Rate: {min(mof_ok_count, storage_ok_count)}/{total_cases} cases")

if __name__ == "__main__":
    test_cost_focus()