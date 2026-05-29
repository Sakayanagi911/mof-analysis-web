#!/usr/bin/env python3
"""
Comprehensive verification untuk semua 5 use cases
Tidak ada pemaksaan hasil - hanya perhitungan murni matematis
"""

from services.cost_analysis import calculate_energy

def verify_all_use_cases():
    """
    Verify semua 5 use cases dengan input dan target yang spesifik
    Bandingkan dengan target tanpa memaksa hasil
    """
    
    # Data lengkap untuk 5 use cases
    use_cases = {
        "Use Case 1 - FATQID": {
            "input": {
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
            },
            "target": {
                "cp_linker": 364.47,
                "e_sensible_solvent": 229.74,
                "e_sensible_additive": 0.0,
                "e_sensible_modulator": 0.25,
                "e_sensible_metal": 0.18,
                "e_sensible_linker": 0.33,
                "e_sensible_total": 230.50
            }
        },
        
        "Use Case 2 - NAWXER": {
            "input": {
                "smiles": "O=C(O)c1cc(C(=O)O)cc(c1)C(=O)O",
                "temperature_c": 85.0,
                "reaction_time_h": 24.0,
                "linker_mass_mg": 4.0,
                "metal_mass_mg": 10.0,
                "solvent_name": "DMF",
                "solvent_volume_ml": 1.0,
                "additive_name": "EtOH",
                "additive_volume_ml": 0.5,
                "modulator_name": "HNO3",
                "modulator_volume_ml": 0.15,
                "modulator_concentration": 11.98,
                "metal_name": "Zn(NO₃)₂·6H₂O",
                "volumetric_wc": 40.0,
                "gravimetric_wc": 5.5,
                "product_mass_mg": 3.785,
                "energy_scale_factor": 1.0
            },
            "target": {
                "cp_linker": 586.17,
                "e_sensible_solvent": 114.87,
                "e_sensible_additive": 57.77,
                "e_sensible_modulator": 2.03,
                "e_sensible_metal": 0.19,
                "e_sensible_linker": 0.25,
                "e_sensible_total": 175.11
            }
        },
        
        "Use Case 3 - HUNCIE": {
            "input": {
                "smiles": "O=C(O)c1ccc2cc(C(=O)O)ccc2c1",
                "temperature_c": 85.0,
                "reaction_time_h": 24.0,
                "linker_mass_mg": 4.0,
                "metal_mass_mg": 10.0,
                "solvent_name": "DMF",
                "solvent_volume_ml": 1.0,
                "additive_name": "-",
                "additive_volume_ml": 0.0,
                "modulator_name": "HNO3",
                "modulator_volume_ml": 0.03,
                "modulator_concentration": 0.65,  # Dari Excel: 0.03mL → 0.65%
                "metal_name": "Zn(NO₃)₂·6H₂O",
                "volumetric_wc": 40.0,
                "gravimetric_wc": 5.5,
                "product_mass_mg": 3.785,
                "energy_scale_factor": 1.0
            },
            "target": {
                "cp_linker": 586.17,
                "e_sensible_solvent": 86.15,
                "e_sensible_additive": 0.0,
                "e_sensible_modulator": 0.11,
                "e_sensible_metal": 0.19,
                "e_sensible_linker": 0.25,
                "e_sensible_total": 86.70
            }
        },
        
        "Use Case 4 - YAVWUQ": {
            "input": {
                "smiles": "O=C(O)c1cc(cc(c1)C(=O)O)C(=O)O",
                "temperature_c": 85.0,
                "reaction_time_h": 24.0,
                "linker_mass_mg": 4.0,
                "metal_mass_mg": 10.0,
                "solvent_name": "DMF",
                "solvent_volume_ml": 1.0,
                "additive_name": "-",
                "additive_volume_ml": 0.0,
                "modulator_name": "HCl",
                "modulator_volume_ml": 0.020,
                "modulator_concentration": 6.0,  # Dari Excel: 0.020mL → 6.0%
                "metal_name": "Zn(NO₃)₂·6H₂O",
                "volumetric_wc": 40.0,
                "gravimetric_wc": 5.5,
                "product_mass_mg": 3.785,
                "energy_scale_factor": 1.0
            },
            "target": {
                "cp_linker": 586.17,
                "e_sensible_solvent": 86.15,
                "e_sensible_additive": 0.0,
                "e_sensible_modulator": 0.11,
                "e_sensible_metal": 0.19,
                "e_sensible_linker": 0.25,
                "e_sensible_total": 86.70
            }
        },
        
        "Use Case 5 - YUGLES": {
            "input": {
                "smiles": "O=C(O)c1cc(C(=O)O)cc(c1)C(=O)O",
                "temperature_c": 85.0,
                "reaction_time_h": 24.0,
                "linker_mass_mg": 4.0,
                "metal_mass_mg": 10.0,
                "solvent_name": "DMA",
                "solvent_volume_ml": 1.0,
                "additive_name": "EtOH",
                "additive_volume_ml": 0.5,
                "modulator_name": "HNO3",
                "modulator_volume_ml": 0.15,
                "modulator_concentration": 4.44,
                "metal_name": "Zn(NO₃)₂·6H₂O",
                "volumetric_wc": 40.0,
                "gravimetric_wc": 5.5,
                "product_mass_mg": 3.785,
                "energy_scale_factor": 1.0
            },
            "target": {
                "cp_linker": 586.17,
                "e_sensible_solvent": 172.43,
                "e_sensible_additive": 115.54,
                "e_sensible_modulator": 2.03,
                "e_sensible_metal": 0.19,
                "e_sensible_linker": 0.25,
                "e_sensible_total": 290.44
            }
        }
    }
    
    print("=" * 80)
    print("COMPREHENSIVE VERIFICATION - ALL 5 USE CASES")
    print("Tidak ada pemaksaan hasil - hanya perhitungan murni matematis")
    print("=" * 80)
    
    for case_name, case_data in use_cases.items():
        print(f"\n{case_name}")
        print("-" * 60)
        
        # Input summary
        inp = case_data["input"]
        print(f"Input: {inp['solvent_name']} {inp['solvent_volume_ml']}mL", end="")
        if inp['additive_volume_ml'] > 0:
            print(f", {inp['additive_name']} {inp['additive_volume_ml']}mL", end="")
        if inp['modulator_volume_ml'] > 0:
            print(f", {inp['modulator_name']} {inp['modulator_volume_ml']}mL ({inp['modulator_concentration']}%)", end="")
        print(f", {inp['metal_name']} {inp['metal_mass_mg']}mg, Linker {inp['linker_mass_mg']}mg")
        
        # Calculate
        result = calculate_energy(**inp)
        target = case_data["target"]
        
        # Compare results
        print("\nComponent Analysis:")
        components = [
            ("CP Linker", "cp_value", "cp_linker"),
            ("Solvent", "e_sensible_solvent_j", "e_sensible_solvent"),
            ("Additive", "e_sensible_additive_j", "e_sensible_additive"),
            ("Modulator", "e_sensible_modulator_j", "e_sensible_modulator"),
            ("Metal", "e_sensible_metal_j", "e_sensible_metal"),
            ("Linker", "e_sensible_linker_j", "e_sensible_linker"),
            ("Total", "e_sensible_total_j", "e_sensible_total")
        ]
        
        for comp_name, result_key, target_key in components:
            actual = result.get(result_key, 0.0)
            expected = target[target_key]
            
            if expected > 0:
                ratio = actual / expected
                match_status = "✅" if 0.95 <= ratio <= 1.05 else "❌"
                print(f"  {comp_name:10}: {actual:8.2f} vs {expected:8.2f} (ratio: {ratio:.3f}) {match_status}")
            else:
                match_status = "✅" if actual == 0 else "❌"
                print(f"  {comp_name:10}: {actual:8.2f} vs {expected:8.2f} {match_status}")
        
        # Overall assessment
        total_actual = result.get("e_sensible_total_j", 0.0)
        total_expected = target["e_sensible_total"]
        total_ratio = total_actual / total_expected if total_expected > 0 else 0
        
        if 0.95 <= total_ratio <= 1.05:
            print(f"\n🎯 OVERALL: MATCH (ratio: {total_ratio:.3f})")
        else:
            print(f"\n⚠️  OVERALL: MISMATCH (ratio: {total_ratio:.3f})")
            
            # Identify potential issues
            if total_ratio > 1.2:
                print("   → Calculated values too high - check formula or data")
            elif total_ratio < 0.8:
                print("   → Calculated values too low - check concentration or volume")
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("- ✅ = Match (within 5% tolerance)")
    print("- ❌ = Mismatch (outside 5% tolerance)")
    print("- Semua perhitungan berdasarkan formula murni tanpa pemaksaan")
    print("=" * 80)

if __name__ == "__main__":
    verify_all_use_cases()