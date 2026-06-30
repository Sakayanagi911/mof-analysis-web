#!/usr/bin/env python3
"""
Detailed Accuracy Table with Percentage Errors
"""

import sys
sys.path.append(r'e:\Project\mof-analysis-web\backend')

from services.cost_analysis import run_economic_analysis

def generate_detailed_accuracy():
    print("=== DETAILED ACCURACY TABLE WITH PERCENTAGE ERRORS ===\n")
    
    # Use case data
    use_cases = [
        {
            'name': 'FATQID',
            'params': {
                'metal_name': 'CuSO₄·5H₂O',
                'linker_smiles': "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
                'reaction_time': 24.0, 'temperature': 85.0,
                'smiles': "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
                'gravimetric_wc': 13.11, 'volumetric_wc': 43.38, 'product_mass_mg': 9.12,
                'metal_mass_mg': 8.0, 'linker_mass_mg': 5.0,
                'solvent_name': 'DMF', 'solvent_volume_ml': 2.0,
                'modulator_name': 'HNO3', 'modulator_volume_ml': 0.05, 'modulator_concentration': 4.44
            },
            'expected': {'cp_linker': 364.47, 'e_solvent': 229.74, 'e_additive': 0.00, 'e_modulator': 0.25, 'e_metal': 0.18, 'e_linker': 0.33, 'e_total': 230.50, 'qheat_mj': 0.53810, 'e_tot_mj': 24.70082, 'qloss_mj': 22.83034, 'estirr_mj': 1.33238}
        },
        {
            'name': 'NAWXER',
            'params': {
                'metal_name': 'Zn(NO₃)₂·6H₂O',
                'linker_smiles': "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1",
                'reaction_time': 24.0, 'temperature': 85.0,
                'smiles': "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1",
                'gravimetric_wc': 12.87, 'volumetric_wc': 44.72, 'product_mass_mg': 3.785,
                'metal_mass_mg': 10.0, 'linker_mass_mg': 4.0,
                'solvent_name': 'DMF', 'solvent_volume_ml': 1.0,
                'additive_name': 'EtOH', 'additive_volume_ml': 0.5,
                'modulator_name': 'HNO3', 'modulator_volume_ml': 0.15, 'modulator_concentration': 11.98
            },
            'expected': {'cp_linker': 586.17, 'e_solvent': 114.87, 'e_additive': 57.77, 'e_modulator': 2.03, 'e_metal': 0.19, 'e_linker': 0.25, 'e_total': 175.11, 'qheat_mj': 0.77531, 'e_tot_mj': 24.88310, 'qloss_mj': 22.83034, 'estirr_mj': 1.27746}
        },
        {
            'name': 'VOLPET',
            'params': {
                'metal_name': 'Zn(NO₃)₂·6H₂O',
                'linker_smiles': "S1C(=CC=C1C(=O)O)C(=O)O",
                'reaction_time': 48.0, 'temperature': 120.0,
                'smiles': "S1C(=CC=C1C(=O)O)C(=O)O",
                'gravimetric_wc': 8.17, 'volumetric_wc': 44.62, 'product_mass_mg': 52.3,
                'metal_mass_mg': 119.0, 'linker_mass_mg': 52.0,
                'solvent_name': 'DMF', 'solvent_volume_ml': 4.0,
                'additive_name': 'MeCN', 'additive_volume_ml': 1.0, 'modulator_concentration': 100.0
            },
            'expected': {'cp_linker': 181.99, 'e_solvent': 727.51, 'e_additive': 176.11, 'e_modulator': 0.00, 'e_metal': 3.61, 'e_linker': 5.19, 'e_total': 912.41, 'qheat_mj': 2.09129, 'e_tot_mj': 77.03891, 'qloss_mj': 72.29606, 'estirr_mj': 2.65155}
        },
        {
            'name': 'YAVWUQ',
            'params': {
                'metal_name': 'Cu(NO₃)₂·2.5H₂O',
                'linker_smiles': "C(=O)O",
                'reaction_time': 96.0, 'temperature': 70.0,
                'smiles': "C(=O)O",
                'gravimetric_wc': 10.68, 'volumetric_wc': 44.77, 'product_mass_mg': 17.13,
                'metal_mass_mg': 15.0, 'linker_mass_mg': 5.0,
                'solvent_name': 'DMF', 'solvent_volume_ml': 1.5,
                'modulator_name': 'HCl', 'modulator_volume_ml': 0.02, 'modulator_concentration': 18.54
            },
            'expected': {'cp_linker': 41.29, 'e_solvent': 129.23, 'e_additive': 0.00, 'e_modulator': 0.43, 'e_metal': 0.30, 'e_linker': 0.02, 'e_total': 129.99, 'qheat_mj': 0.17503, 'e_tot_mj': 74.03639, 'qloss_mj': 68.49101, 'estirr_mj': 5.37036}
        },
        {
            'name': 'YUGLES',
            'params': {
                'metal_name': 'Cu(NO₃)₂·3H₂O',
                'linker_smiles': "C(#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O",
                'reaction_time': 24.0, 'temperature': 65.0,
                'smiles': "C(#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O",
                'gravimetric_wc': 8.69, 'volumetric_wc': 49.55, 'product_mass_mg': 6.3,
                'metal_mass_mg': 15.0, 'linker_mass_mg': 5.0,
                'solvent_name': 'DMF', 'solvent_volume_ml': 0.2,
                'additive_name': 'DMSO', 'additive_volume_ml': 0.2,
                'modulator_name': 'HNO3', 'modulator_volume_ml': 0.06, 'modulator_concentration': 4.44
            },
            'expected': {'cp_linker': 345.59, 'e_solvent': 15.00, 'e_additive': 16.72, 'e_modulator': 0.20, 'e_metal': 0.26, 'e_linker': 0.19, 'e_total': 32.69, 'qheat_mj': 0.00445, 'e_tot_mj': 16.73215, 'qloss_mj': 15.22022, 'estirr_mj': 1.50748}
        }
    ]
    
    print("🧪 Running calculations...")
    
    # Run calculations
    results = []
    for case in use_cases:
        try:
            result = run_economic_analysis(**case['params'])
            energy_details = result.get('energy_details', {})
            
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
                'name': case['name'],
                'expected': case['expected'],
                'actual': actual
            })
        except Exception as e:
            print(f"❌ Error in {case['name']}: {e}")
    
    # Generate detailed table
    print("\n" + "="*180)
    print("📊 DETAILED ACCURACY TABLE WITH PERCENTAGE ERRORS")
    print("="*180)
    
    # Header
    header = f"{'Metric':<20} {'Type':<10}"
    for result in results:
        header += f" {result['name']:<25}"
    print(header)
    print("-" * 180)
    
    metrics = [
        ('Cp linker (J/mol·K)', 'cp_linker', 'Corrected'),
        ('Solvent (J)', 'e_solvent', 'Real'),
        ('Additive (J)', 'e_additive', 'Real'),
        ('Modulator (J)', 'e_modulator', 'Akal-akalan'),
        ('Metal (J)', 'e_metal', 'Corrected'),
        ('Linker (J)', 'e_linker', 'Corrected'),
        ('Total Sensible (J)', 'e_total', 'Mixed'),
        ('Qheat (MJ)', 'qheat_mj', 'Akal-akalan'),
        ('E_tot (MJ)', 'e_tot_mj', 'Mixed'),
        ('Qloss (MJ)', 'qloss_mj', 'Real'),
        ('Estirr (MJ)', 'estirr_mj', 'Real')
    ]
    
    accuracy_stats = {result['name']: {'perfect': 0, 'good': 0, 'bad': 0, 'total': 0} for result in results}
    
    for metric_name, metric_key, calc_type in metrics:
        row = f"{metric_name:<20} {calc_type:<10}"
        
        for result in results:
            expected = result['expected'].get(metric_key, 0)
            actual = result['actual'].get(metric_key, 0)
            
            if expected == 0 and actual == 0:
                error_pct = 0.0
                status = "✅"
                category = 'perfect'
            elif expected == 0:
                error_pct = float('inf') if actual != 0 else 0.0
                status = "❌" if actual != 0 else "✅"
                category = 'bad' if actual != 0 else 'perfect'
            else:
                error_pct = abs(actual - expected) / expected * 100
                if error_pct < 1:
                    status = "✅"
                    category = 'perfect'
                elif error_pct < 5:
                    status = "⚠️"
                    category = 'good'
                else:
                    status = "❌"
                    category = 'bad'
            
            accuracy_stats[result['name']][category] += 1
            accuracy_stats[result['name']]['total'] += 1
            
            if metric_key == 'cp_linker':
                display = f"{actual:.1f}({error_pct:.1f}%){status}"
            elif 'mj' in metric_key:
                display = f"{actual:.3f}({error_pct:.1f}%){status}"
            else:
                display = f"{actual:.2f}({error_pct:.1f}%){status}"
            
            row += f" {display:<24}"
        
        print(row)
    
    print("-" * 180)
    
    # Accuracy summary
    print("\n" + "="*120)
    print("📈 ACCURACY SUMMARY BY MOF")
    print("="*120)
    
    print(f"{'MOF':<10} {'Perfect (<1%)':<15} {'Good (1-5%)':<15} {'Bad (>5%)':<15} {'Overall Score':<15}")
    print("-" * 120)
    
    for result in results:
        name = result['name']
        stats = accuracy_stats[name]
        
        perfect_pct = (stats['perfect'] / stats['total']) * 100
        good_pct = (stats['good'] / stats['total']) * 100
        bad_pct = (stats['bad'] / stats['total']) * 100
        
        overall_score = perfect_pct + (good_pct * 0.7)  # Weight good as 70%
        
        print(f"{name:<10} {stats['perfect']}/{stats['total']} ({perfect_pct:.0f}%){' ':<6} {stats['good']}/{stats['total']} ({good_pct:.0f}%){' ':<7} {stats['bad']}/{stats['total']} ({bad_pct:.0f}%){' ':<8} {overall_score:.1f}%")
    
    print("-" * 120)
    
    # Calculation type accuracy
    print("\n" + "="*100)
    print("🔍 ACCURACY BY CALCULATION TYPE")
    print("="*100)
    
    calc_type_stats = {}
    
    for metric_name, metric_key, calc_type in metrics:
        if calc_type not in calc_type_stats:
            calc_type_stats[calc_type] = {'perfect': 0, 'good': 0, 'bad': 0, 'total': 0}
        
        for result in results:
            expected = result['expected'].get(metric_key, 0)
            actual = result['actual'].get(metric_key, 0)
            
            if expected == 0 and actual == 0:
                error_pct = 0.0
                category = 'perfect'
            elif expected == 0:
                category = 'bad' if actual != 0 else 'perfect'
            else:
                error_pct = abs(actual - expected) / expected * 100
                if error_pct < 1:
                    category = 'perfect'
                elif error_pct < 5:
                    category = 'good'
                else:
                    category = 'bad'
            
            calc_type_stats[calc_type][category] += 1
            calc_type_stats[calc_type]['total'] += 1
    
    print(f"{'Type':<15} {'Perfect (<1%)':<15} {'Good (1-5%)':<15} {'Bad (>5%)':<15} {'Score':<10}")
    print("-" * 100)
    
    for calc_type, stats in calc_type_stats.items():
        perfect_pct = (stats['perfect'] / stats['total']) * 100
        good_pct = (stats['good'] / stats['total']) * 100
        bad_pct = (stats['bad'] / stats['total']) * 100
        score = perfect_pct + (good_pct * 0.7)
        
        print(f"{calc_type:<15} {stats['perfect']}/{stats['total']} ({perfect_pct:.0f}%){' ':<6} {stats['good']}/{stats['total']} ({good_pct:.0f}%){' ':<7} {stats['bad']}/{stats['total']} ({bad_pct:.0f}%){' ':<8} {score:.1f}%")
    
    print("\n🎯 LEGEND:")
    print("✅ Perfect: <1% error  |  ⚠️ Good: 1-5% error  |  ❌ Bad: >5% error")
    print("\n📝 CALCULATION TYPES:")
    print("Real: Pure physics/chemistry formulas")
    print("Corrected: Real formulas + MW corrections from original model") 
    print("Mixed: Combination of real and corrected components")
    print("Akal-akalan: Empirical corrections or missing formula confirmation")

if __name__ == "__main__":
    generate_detailed_accuracy()