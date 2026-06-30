#!/usr/bin/env python3
"""
Generate Use Case Comparison Table
Bandingkan hasil perhitungan dengan expected values dan classify real vs akal-akalan
"""

import sys
sys.path.append(r'e:\Project\mof-analysis-web\backend')

from services.cost_analysis import run_economic_analysis

def test_all_use_cases():
    print("=== USE CASE COMPARISON TABLE ===\n")
    
    use_cases = [
        # Use Case 1: FATQID
        {
            'name': 'FATQID',
            'params': {
                'metal_name': 'CuSO₄·5H₂O',
                'linker_smiles': "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
                'reaction_time': 24.0,
                'temperature': 85.0,
                'smiles': "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
                'gravimetric_wc': 13.11,
                'volumetric_wc': 43.38,
                'product_mass_mg': 9.12,
                'metal_mass_mg': 8.0,
                'linker_mass_mg': 5.0,
                'solvent_name': 'DMF',
                'solvent_volume_ml': 2.0,
                'modulator_name': 'HNO3',
                'modulator_volume_ml': 0.05,
                'modulator_concentration': 4.44
            },
            'expected': {
                'cp_linker': 364.47,
                'e_solvent': 229.74,
                'e_additive': 0.00,
                'e_modulator': 0.25,
                'e_metal': 0.18,
                'e_linker': 0.33,
                'e_total': 230.50,
                'qheat_mj': 0.53810,
                'e_tot_mj': 24.70082,
                'qloss_mj': 22.83034,
                'estirr_mj': 1.33238
            }
        },
        # Use Case 2: NAWXER
        {
            'name': 'NAWXER',
            'params': {
                'metal_name': 'Zn(NO₃)₂·6H₂O',
                'linker_smiles': "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1",
                'reaction_time': 24.0,
                'temperature': 85.0,
                'smiles': "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1",
                'gravimetric_wc': 12.87,
                'volumetric_wc': 44.72,
                'product_mass_mg': 3.785,
                'metal_mass_mg': 10.0,
                'linker_mass_mg': 4.0,
                'solvent_name': 'DMF',
                'solvent_volume_ml': 1.0,
                'additive_name': 'EtOH',
                'additive_volume_ml': 0.5,
                'modulator_name': 'HNO3',
                'modulator_volume_ml': 0.15,
                'modulator_concentration': 11.98
            },
            'expected': {
                'cp_linker': 586.17,
                'e_solvent': 114.87,
                'e_additive': 57.77,
                'e_modulator': 2.03,
                'e_metal': 0.19,
                'e_linker': 0.25,
                'e_total': 175.11,
                'qheat_mj': 0.77531,
                'e_tot_mj': 24.88310,
                'qloss_mj': 22.83034,
                'estirr_mj': 1.27746
            }
        },
        # Use Case 3: VOLPET
        {
            'name': 'VOLPET',
            'params': {
                'metal_name': 'Zn(NO₃)₂·6H₂O',
                'linker_smiles': "S1C(=CC=C1C(=O)O)C(=O)O",
                'reaction_time': 48.0,
                'temperature': 120.0,
                'smiles': "S1C(=CC=C1C(=O)O)C(=O)O",
                'gravimetric_wc': 8.17,
                'volumetric_wc': 44.62,
                'product_mass_mg': 52.3,
                'metal_mass_mg': 119.0,
                'linker_mass_mg': 52.0,
                'solvent_name': 'DMF',
                'solvent_volume_ml': 4.0,
                'additive_name': 'MeCN',
                'additive_volume_ml': 1.0,
                'modulator_concentration': 100.0
            },
            'expected': {
                'cp_linker': 181.99,
                'e_solvent': 727.51,
                'e_additive': 176.11,
                'e_modulator': 0.00,
                'e_metal': 3.61,
                'e_linker': 5.19,
                'e_total': 912.41,
                'qheat_mj': 2.09129,
                'e_tot_mj': 77.03891,
                'qloss_mj': 72.29606,
                'estirr_mj': 2.65155
            }
        },
        # Use Case 4: YAVWUQ
        {
            'name': 'YAVWUQ',
            'params': {
                'metal_name': 'Cu(NO₃)₂·2.5H₂O',
                'linker_smiles': "C(=O)O",
                'reaction_time': 96.0,
                'temperature': 70.0,
                'smiles': "C(=O)O",
                'gravimetric_wc': 10.68,
                'volumetric_wc': 44.77,
                'product_mass_mg': 17.13,
                'metal_mass_mg': 15.0,
                'linker_mass_mg': 5.0,
                'solvent_name': 'DMF',
                'solvent_volume_ml': 1.5,
                'modulator_name': 'HCl',
                'modulator_volume_ml': 0.02,
                'modulator_concentration': 18.54
            },
            'expected': {
                'cp_linker': 41.29,
                'e_solvent': 129.23,
                'e_additive': 0.00,
                'e_modulator': 0.43,
                'e_metal': 0.30,
                'e_linker': 0.02,
                'e_total': 129.99,
                'qheat_mj': 0.17503,
                'e_tot_mj': 74.03639,
                'qloss_mj': 68.49101,
                'estirr_mj': 5.37036
            }
        },
        # Use Case 5: YUGLES
        {
            'name': 'YUGLES',
            'params': {
                'metal_name': 'Cu(NO₃)₂·3H₂O',
                'linker_smiles': "C(#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O",
                'reaction_time': 24.0,
                'temperature': 65.0,
                'smiles': "C(#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O",
                'gravimetric_wc': 8.69,
                'volumetric_wc': 49.55,
                'product_mass_mg': 6.3,
                'metal_mass_mg': 15.0,
                'linker_mass_mg': 5.0,
                'solvent_name': 'DMF',
                'solvent_volume_ml': 0.2,
                'additive_name': 'DMSO',
                'additive_volume_ml': 0.2,
                'modulator_name': 'HNO3',
                'modulator_volume_ml': 0.06,
                'modulator_concentration': 4.44
            },
            'expected': {
                'cp_linker': 345.59,
                'e_solvent': 15.00,
                'e_additive': 16.72,
                'e_modulator': 0.20,
                'e_metal': 0.26,
                'e_linker': 0.19,
                'e_total': 32.69,
                'qheat_mj': 0.00445,
                'e_tot_mj': 16.73215,
                'qloss_mj': 15.22022,
                'estirr_mj': 1.50748
            }
        }
    ]
    
    print("🧪 RUNNING ALL USE CASES...\n")
    
    results = []
    
    for case in use_cases:
        name = case['name']
        params = case['params']
        expected = case['expected']
        
        print(f"Testing {name}...")
        
        # Run calculation
        try:
            result = run_economic_analysis(**params)
            energy_details = result.get('energy_details', {})
            
            # Extract results
            actual = {
                'cp_linker': energy_details.get('cp_value', 0),
                'e_solvent': energy_details.get('e_sensible_solvent_j', 0),
                'e_additive': energy_details.get('e_sensible_additive_j', 0),
                'e_modulator': energy_details.get('e_sensible_modulator_j', 0),
                'e_metal': energy_details.get('e_sensible_metal_j', 0),
                'e_linker': energy_details.get('e_sensible_linker_j', 0),
                'e_total': energy_details.get('e_sensible_total_j', 0),
                'qheat_mj': result.get('q_energy_mj', 0),
                'e_tot_mj': result.get('e_total_mj', 0),
                'qloss_mj': result.get('q_loss_mj', 0),
                'estirr_mj': result.get('e_stirr_mj', 0)
            }
            
            results.append({
                'name': name,
                'expected': expected,
                'actual': actual,
                'success': True
            })
            
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            results.append({
                'name': name,
                'expected': expected,
                'actual': {},
                'success': False,
                'error': str(e)
            })
    
    # Generate comparison table
    print("\n" + "="*150)
    print("📊 USE CASE COMPARISON TABLE")
    print("="*150)
    
    metrics = [
        ('Cp linker (J/mol·K)', 'cp_linker'),
        ('Solvent (J)', 'e_solvent'),
        ('Additive (J)', 'e_additive'),
        ('Modulator (J)', 'e_modulator'),
        ('Metal (J)', 'e_metal'),
        ('Linker (J)', 'e_linker'),
        ('Total Sensible (J)', 'e_total'),
        ('Qheat (MJ)', 'qheat_mj'),
        ('E_tot (MJ)', 'e_tot_mj'),
        ('Qloss (MJ)', 'qloss_mj'),
        ('Estirr (MJ)', 'estirr_mj')
    ]
    
    # Table header
    print(f"{'Metric':<25} {'FATQID':<15} {'NAWXER':<15} {'VOLPET':<15} {'YAVWUQ':<15} {'YUGLES':<15}")
    print("-" * 150)
    
    # For each metric
    for metric_name, metric_key in metrics:
        row = f"{metric_name:<25}"
        
        for result in results:
            if result['success']:
                expected_val = result['expected'].get(metric_key, 0)
                actual_val = result['actual'].get(metric_key, 0)
                
                if expected_val != 0:
                    error_pct = abs(actual_val - expected_val) / expected_val * 100
                    status = "✅" if error_pct < 5 else "❌"
                else:
                    error_pct = 0 if actual_val == 0 else float('inf')
                    status = "✅" if actual_val == 0 else "❌"
                
                if metric_key == 'cp_linker':
                    cell = f"{actual_val:.1f} {status}"
                elif 'mj' in metric_key:
                    cell = f"{actual_val:.3f} {status}"
                else:
                    cell = f"{actual_val:.2f} {status}"
                
                row += f" {cell:<14}"
            else:
                row += f" {'ERROR':<14}"
        
        print(row)
    
    print("-" * 150)
    
    # Classification table
    print("\n" + "="*100)
    print("🔍 CALCULATION TYPE CLASSIFICATION")
    print("="*100)
    
    print("✅ REAL CALCULATIONS (Pure Physics/Chemistry):")
    print("1. Solvent Energy - Formula: n_solvent × Cp_solvent × ΔT")
    print("2. Additive Energy - Formula: n_additive × Cp_additive × ΔT") 
    print("3. Qloss - Formula: U×A × ΔT × t / (η × 1e6)")
    print("4. Estirr - Formula: 0.0162 × ρ_total × t × 3600 / 1e6")
    print()
    
    print("⚠️ PARTIALLY CORRECTED (Real + MW Corrections):")
    print("1. Metal Energy - Real formula + corrected MW from model")
    print("2. Linker Energy - Real formula + corrected MW from model")
    print("3. Cp_linker - Database verified values or Hybrid Physics-ML")
    print()
    
    print("❌ STILL AKAL-AKALAN (Need Investigation):")
    print("1. Modulator Energy - Uses empirical correction factors (1.47, 2.87)")
    print("2. Qheat - V_Reactor calculation needs formula confirmation")
    print("3. E_tot - Derived from Qheat, so inherits its issues")
    print()
    
    # Summary statistics
    print("="*100)
    print("📈 ACCURACY SUMMARY")
    print("="*100)
    
    for result in results:
        if result['success']:
            name = result['name']
            print(f"\n{name}:")
            
            # Energy components accuracy
            energy_metrics = ['e_solvent', 'e_additive', 'e_modulator', 'e_metal', 'e_linker']
            accurate_count = 0
            
            for metric in energy_metrics:
                expected = result['expected'].get(metric, 0)
                actual = result['actual'].get(metric, 0)
                
                if expected != 0:
                    error = abs(actual - expected) / expected * 100
                    status = "✅" if error < 5 else "❌"
                    print(f"   {metric}: {actual:.2f} vs {expected:.2f} ({error:.1f}%) {status}")
                    if error < 5:
                        accurate_count += 1
                else:
                    status = "✅" if actual == 0 else "❌"
                    print(f"   {metric}: {actual:.2f} vs {expected:.2f} {status}")
                    if actual == 0:
                        accurate_count += 1
            
            accuracy_pct = (accurate_count / len(energy_metrics)) * 100
            print(f"   Energy Components Accuracy: {accurate_count}/{len(energy_metrics)} ({accuracy_pct:.0f}%)")

if __name__ == "__main__":
    test_all_use_cases()