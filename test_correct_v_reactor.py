#!/usr/bin/env python3
"""
Test Correct V_Reactor Formula
V_Reactor = 1.2 * V_MOF sesuai model asli
"""

import sys
sys.path.append(r'e:\Project\mof-analysis-web\backend')

from services.cost_analysis import calculate_energy

def test_correct_v_reactor():
    print("=== TEST CORRECT V_REACTOR FORMULA ===\n")
    print("Formula: V_Reactor = 1.2 * V_MOF")
    print("V_MOF = Product Mass (g) / MOF Density (g/L)")
    print("MOF Density = Volumetric WC / (Gravimetric WC / 100)")
    print()
    
    # Test FATQID
    print("📋 FATQID Use Case:")
    result = calculate_energy(
        smiles="C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
        temperature_c=85.0,
        reaction_time_h=24.0,
        linker_mass_mg=5.0,
        metal_mass_mg=8.0,
        solvent_name="DMF",
        solvent_volume_ml=2.0,
        modulator_name="HNO3",
        modulator_volume_ml=0.05,
        modulator_concentration=4.44,
        metal_name="CuSO₄·5H₂O",
        volumetric_wc=43.38,  # From uptake database
        gravimetric_wc=13.11,  # From uptake database  
        product_mass_mg=9.12,
        energy_scale_factor=1.0
    )
    
    print(f"✅ FATQID Results:")
    print(f"   V_Reactor: {result.get('v_reactor_l', 0):.6f} L")
    print(f"   Qheat: {result.get('q_energy_mj', 0):.5f} MJ")
    print(f"   Expected Qheat: 0.53810 MJ")
    
    qheat_error = abs(result.get('q_energy_mj', 0) - 0.53810) / 0.53810 * 100
    print(f"   Qheat Error: {qheat_error:.1f}%")
    print()
    
    # Test NAWXER
    print("📋 NAWXER Use Case:")
    result2 = calculate_energy(
        smiles="C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1",
        temperature_c=85.0,
        reaction_time_h=24.0,
        linker_mass_mg=4.0,
        metal_mass_mg=10.0,
        solvent_name="DMF",
        solvent_volume_ml=1.0,
        additive_name="EtOH",
        additive_volume_ml=0.5,
        modulator_name="HNO3", 
        modulator_volume_ml=0.15,
        modulator_concentration=11.98,
        metal_name="Zn(NO₃)₂·6H₂O",
        volumetric_wc=44.72,  # From uptake database
        gravimetric_wc=12.87,  # From uptake database
        product_mass_mg=3.785,
        energy_scale_factor=1.0
    )
    
    print(f"✅ NAWXER Results:")
    print(f"   V_Reactor: {result2.get('v_reactor_l', 0):.6f} L")
    print(f"   Qheat: {result2.get('q_energy_mj', 0):.5f} MJ")
    print(f"   Expected Qheat: 0.77531 MJ")
    
    qheat_error2 = abs(result2.get('q_energy_mj', 0) - 0.77531) / 0.77531 * 100
    print(f"   Qheat Error: {qheat_error2:.1f}%")
    print()
    
    # Debug V_reactor values
    print("🔍 V_REACTOR ANALYSIS:")
    debug1 = result.get('debug_info', {})
    debug2 = result2.get('debug_info', {})
    
    print(f"FATQID:")
    print(f"   Product: {debug1.get('g_mof', 0)*1000:.2f} mg")
    print(f"   MOF Density: {debug1.get('density_mof_g_per_l', 0):.2f} g/L") 
    print(f"   V_MOF: {debug1.get('v_mof_l', 0):.6f} L")
    print(f"   V_Reactor: {result.get('v_reactor_l', 0):.6f} L")
    
    print(f"\nNAWXER:")
    print(f"   Product: {debug2.get('g_mof', 0)*1000:.2f} mg")
    print(f"   MOF Density: {debug2.get('density_mof_g_per_l', 0):.2f} g/L")
    print(f"   V_MOF: {debug2.get('v_mof_l', 0):.6f} L") 
    print(f"   V_Reactor: {result2.get('v_reactor_l', 0):.6f} L")
    
    print()
    print("📊 SUMMARY:")
    if qheat_error < 10 and qheat_error2 < 10:
        print("✅ V_Reactor formula is working correctly!")
        print("✅ Qheat calculations now more accurate with dynamic V_Reactor")
    else:
        print("❌ Still need adjustment - check formula or additional terms")

if __name__ == "__main__":
    test_correct_v_reactor()