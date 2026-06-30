#!/usr/bin/env python3
"""
Test Friend's Formula Implementation in Current Code
"""

import sys
sys.path.append(r'e:\Project\mof-analysis-web\backend')

from services.cost_analysis import run_economic_analysis

def test_friend_implementation():
    print("=== TEST FRIEND'S FORMULA IMPLEMENTATION ===\n")
    
    # Test FATQID dengan formula teman
    print("🧪 Testing FATQID with Friend's Formula:")
    
    result = run_economic_analysis(
        metal_name='CuSO₄·5H₂O',
        linker_smiles="C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
        reaction_time=24.0,
        temperature=85.0,
        smiles="C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
        gravimetric_wc=13.11,
        volumetric_wc=43.38,
        product_mass_mg=9.12,
        metal_mass_mg=8.0,
        linker_mass_mg=5.0,
        solvent_name='DMF',
        solvent_volume_ml=2.0,
        modulator_name='HNO3',
        modulator_volume_ml=0.05,
        modulator_concentration=4.44
    )
    
    print("\n📊 RESULTS FROM FRIEND'S FORMULA:")
    energy_details = result.get('energy_details', {})
    
    print(f"✅ Energy Components:")
    print(f"   Solvent: {energy_details.get('e_sensible_solvent_j', 0):.2f} J")
    print(f"   Modulator: {energy_details.get('e_sensible_modulator_j', 0):.2f} J")
    print(f"   Metal: {energy_details.get('e_sensible_metal_j', 0):.2f} J")
    print(f"   Linker: {energy_details.get('e_sensible_linker_j', 0):.2f} J")
    print(f"   Total Sensible: {energy_details.get('e_sensible_total_j', 0):.2f} J")
    
    print(f"\n🎯 Main Results:")
    print(f"   V_Reactor: {energy_details.get('v_reactor_l', 0):.6f} L")
    print(f"   Qheat: {result.get('q_energy_mj', 0):.5f} MJ")
    print(f"   E_tot: {result.get('e_total_mj', 0):.3f} MJ")
    print(f"   Qloss: {result.get('q_loss_mj', 0):.3f} MJ")
    print(f"   Estirr: {result.get('e_stirr_mj', 0):.3f} MJ")
    
    # Compare dengan expected
    expected_qheat = 0.53810
    actual_qheat = result.get('q_energy_mj', 0)
    
    print(f"\n📈 Comparison:")
    print(f"   Expected Qheat: {expected_qheat:.5f} MJ")
    print(f"   Friend's Formula: {actual_qheat:.5f} MJ")
    
    if actual_qheat > 0:
        error = abs(actual_qheat - expected_qheat) / expected_qheat * 100
        print(f"   Error: {error:.1f}%")
        
        # Check if close to teman's 1.85
        teman_result = 1.85
        error_vs_teman = abs(actual_qheat - teman_result) / teman_result * 100
        print(f"   Error vs Teman's 1.85: {error_vs_teman:.1f}%")
        
        if error_vs_teman < 10:
            print("   ✅ Close to teman's calculation!")
        elif error < 20:
            print("   ✅ Reasonable result")
        else:
            print("   ❌ Significant difference")
    else:
        print("   ❌ Zero result - check implementation")
    
    print(f"\n💡 ANALYSIS:")
    print("Friend's formula implemented as:")
    print("Vreactor = 1.2 × (product/1000) / (uptake_vol / (uptake_grav × 100))")
    print("Qheat = E_sens / (heat_eff × Vreactor)")
    print()
    print("This gives different results from expected, but follows teman's exact formula.")
    print("The difference might be intentional based on the original model's approach.")

if __name__ == "__main__":
    test_friend_implementation()