#!/usr/bin/env python3
"""
Debug script untuk menganalisis perhitungan energi
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.cost_analysis import run_economic_analysis

def debug_use_case_1():
    """Debug Use Case 1 dengan detail lengkap"""
    print("=== DEBUG USE CASE 1 ===")
    params = {
        "metal_name": "CuSO₄·5H₂O",
        "linker_name": "H₂L",
        "reaction_time": 24.0,
        "temperature": 85.0,
        "smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",  # H₂L SMILES
        "gravimetric_wc": 5.5,
        "volumetric_wc": 40.0,
        "product_mass_mg": 9.12,
        "metal_mass_mg": 8.0,
        "linker_mass_mg": 5.0,
        "solvent_name": "DMF",
        "solvent_volume_ml": 2.0,
        "additive_name": "-",
        "additive_volume_ml": 0.0,
        "modulator_name": "HNO3",
        "modulator_volume_ml": 0.05
    }
    
    result = run_economic_analysis(**params)
    energy_details = result.get("energy_details", {})
    debug_info = energy_details.get("debug_info", {})
    
    print("INPUT PARAMETERS:")
    print(f"  Product Mass: {params['product_mass_mg']} mg")
    print(f"  Gravimetric WC: {params['gravimetric_wc']} %")
    print(f"  Volumetric WC: {params['volumetric_wc']} g/L")
    print(f"  Solvent: {params['solvent_name']} {params['solvent_volume_ml']} mL")
    print(f"  Modulator: {params['modulator_name']} {params['modulator_volume_ml']} mL")
    print(f"  Temperature: {params['temperature']} °C")
    
    print("\nDEBUG CALCULATIONS:")
    print(f"  Density MOF: {debug_info.get('density_mof_g_per_l', 0):.2f} g/L")
    print(f"  g_MOF: {debug_info.get('g_mof', 0):.6f} g")
    print(f"  V_MOF: {debug_info.get('v_mof_l', 0):.6f} L")
    print(f"  V_Reactor: {energy_details.get('v_reactor_l', 0):.6f} L")
    print(f"  V_Liquid: {debug_info.get('v_liquid_l', 0):.6f} L")
    print(f"  Delta T: {debug_info.get('delta_t', 0):.2f} K")
    
    print("\nMOLAR CALCULATIONS:")
    print(f"  n_solvent: {debug_info.get('n_solv', 0):.6f} mol")
    print(f"  n_modulator: {debug_info.get('n_mod', 0):.6f} mol")
    print(f"  n_metal: {debug_info.get('n_metal', 0):.6f} mol")
    print(f"  n_linker: {debug_info.get('n_linker', 0):.6f} mol")
    
    print("\nCHEMICAL PROPERTIES:")
    solv_props = debug_info.get('solv_props', (0, 0, 0))
    mod_props = debug_info.get('mod_props', (0, 0, 0))
    metal_props = debug_info.get('metal_props', (0, 0))
    print(f"  Solvent (rho, Cp, Mr): {solv_props}")
    print(f"  Modulator (rho, Cp, Mr): {mod_props}")
    print(f"  Metal (Cp, Mr): {metal_props}")
    
    print("\nENERGY RESULTS:")
    print(f"  Solvent Energy: {energy_details.get('e_sensible_solvent_j', 0):.2f} J")
    print(f"  Modulator Energy: {energy_details.get('e_sensible_modulator_j', 0):.2f} J")
    print(f"  Metal Energy: {energy_details.get('e_sensible_metal_j', 0):.2f} J")
    print(f"  Linker Energy: {energy_details.get('e_sensible_linker_j', 0):.2f} J")
    print(f"  Total Sensible: {energy_details.get('e_sensible_total_j', 0):.2f} J")
    print(f"  Qheat: {result.get('q_energy_mj', 0):.5f} MJ")
    
    print("\nEXPECTED VALUES:")
    print("  Solvent Energy: 229.74 J")
    print("  Modulator Energy: 0.25 J")
    print("  Metal Energy: 0.18 J")
    print("  Linker Energy: 0.33 J")
    print("  Total Sensible: 230.50 J")
    print("  Qheat: 0.53810 MJ")
    
    # Manual calculation check
    print("\nMANUAL CALCULATION CHECK:")
    
    # Expected density MOF calculation
    expected_density_mof = 40.0 / (5.5 / 100.0)  # volumetric_wc / (gravimetric_wc / 100)
    expected_g_mof = 9.12 / 1000.0  # mg to g
    expected_v_mof = expected_g_mof / expected_density_mof
    expected_v_reactor = 1.2 * expected_v_mof
    
    print(f"  Expected Density MOF: {expected_density_mof:.2f} g/L")
    print(f"  Expected g_MOF: {expected_g_mof:.6f} g")
    print(f"  Expected V_MOF: {expected_v_mof:.6f} L")
    print(f"  Expected V_Reactor: {expected_v_reactor:.6f} L")
    
    # Expected Qheat calculation
    expected_qheat_j_per_l = 230.50 / (0.75 * expected_v_reactor)
    expected_qheat_mj = expected_qheat_j_per_l * 1000 / 1e6
    print(f"  Expected Qheat J/L: {expected_qheat_j_per_l:.2f}")
    print(f"  Expected Qheat MJ: {expected_qheat_mj:.5f}")

if __name__ == "__main__":
    debug_use_case_1()