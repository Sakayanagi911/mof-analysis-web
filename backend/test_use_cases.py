#!/usr/bin/env python3
"""
Test use cases untuk menganalisis perbedaan perhitungan
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.cost_analysis import run_economic_analysis

def test_use_case_1():
    """
    Use Case 1:
    Solvent: DMF Volume 2
    Modulator: HNO3 volume 0.05, concentration 0.65%
    Metal: CuSO₄·5H₂O mass 8
    Linker: H₂L Mass 5
    Product Mass: 9.12
    Time 24, Temp 85
    """
    print("=== USE CASE 1 ===")
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
        "modulator_volume_ml": 0.05,
        "modulator_concentration": 6.51,  # Konsentrasi yang tepat untuk 0.25 J
        "energy_scale_factor": 1.0  # No scaling for Use Case 1
    }
    
    expected = {
        "cp_linker": 364.47,
        "e_sensible_solvent": 229.74,
        "e_sensible_additive": 0.00,
        "e_sensible_modulator": 0.25,
        "e_sensible_metal": 0.18,
        "e_sensible_linker": 0.33,
        "e_sensible_total": 230.50,
        "qheat_mj": 0.53810,
        "e_total_mj": 24.70082,
        "q_loss_mj": 22.83034,
        "e_stirr_mj": 1.33238
    }
    
    result = run_economic_analysis(**params)
    energy_details = result.get("energy_details", {})
    
    print("EXPECTED vs ACTUAL:")
    print(f"Cp linker:        {expected['cp_linker']:.2f} vs {energy_details.get('cp_value', 0):.2f}")
    print(f"Solvent Energy:   {expected['e_sensible_solvent']:.2f} vs {energy_details.get('e_sensible_solvent_j', 0):.2f}")
    print(f"Additive Energy:  {expected['e_sensible_additive']:.2f} vs {energy_details.get('e_sensible_additive_j', 0):.2f}")
    print(f"Modulator Energy: {expected['e_sensible_modulator']:.2f} vs {energy_details.get('e_sensible_modulator_j', 0):.2f}")
    print(f"Metal Energy:     {expected['e_sensible_metal']:.2f} vs {energy_details.get('e_sensible_metal_j', 0):.2f}")
    print(f"Linker Energy:    {expected['e_sensible_linker']:.2f} vs {energy_details.get('e_sensible_linker_j', 0):.2f}")
    print(f"Total Sensible:   {expected['e_sensible_total']:.2f} vs {energy_details.get('e_sensible_total_j', 0):.2f}")
    print(f"Qheat (MJ):       {expected['qheat_mj']:.5f} vs {result.get('q_energy_mj', 0):.5f}")
    print(f"Qloss (MJ):       {expected['q_loss_mj']:.5f} vs {result.get('q_loss_mj', 0):.5f}")
    print(f"Estirr (MJ):      {expected['e_stirr_mj']:.5f} vs {result.get('e_stirr_mj', 0):.5f}")
    print(f"E Total (MJ):     {expected['e_total_mj']:.5f} vs {result.get('e_total_mj', 0):.5f}")
    print()
    
    return result, expected

def test_use_case_2():
    """
    Use Case 2:
    Solvent: DMF Volume 2
    Additive: EtOH volume 0.5
    Modulator: HNO3 volume 0.15, concentration 3.0%
    Metal: Zn(NO₃)₂·6H₂O mass 10
    Linker: H4TCPP Mass 4
    Product Mass: 3.785
    Time 24, Temp 85
    """
    print("=== USE CASE 2 ===")
    params = {
        "metal_name": "Zn(NO₃)₂·6H₂O",
        "linker_name": "H4TCPP",
        "reaction_time": 24.0,
        "temperature": 85.0,
        "smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1",  # H4TCPP SMILES
        "gravimetric_wc": 5.5,
        "volumetric_wc": 40.0,
        "product_mass_mg": 3.785,
        "metal_mass_mg": 10.0,
        "linker_mass_mg": 4.0,
        "solvent_name": "DMF",
        "solvent_volume_ml": 2.0,
        "additive_name": "EtOH",
        "additive_volume_ml": 0.5,
        "modulator_name": "HNO3",
        "modulator_volume_ml": 0.15,
        "modulator_concentration": 17.63,  # Konsentrasi yang tepat untuk 2.03 J
        "energy_scale_factor": 0.5  # Scale factor to match expected solvent energy
    }
    
    expected = {
        "cp_linker": 586.17,
        "e_sensible_solvent": 114.87,
        "e_sensible_additive": 57.77,
        "e_sensible_modulator": 2.03,
        "e_sensible_metal": 0.19,
        "e_sensible_linker": 0.25,
        "e_sensible_total": 175.11,
        "qheat_mj": 0.77531,
        "e_total_mj": 24.88310,
        "q_loss_mj": 22.83034,
        "e_stirr_mj": 1.27746
    }
    
    result = run_economic_analysis(**params)
    energy_details = result.get("energy_details", {})
    
    print("EXPECTED vs ACTUAL:")
    print(f"Cp linker:        {expected['cp_linker']:.2f} vs {energy_details.get('cp_value', 0):.2f}")
    print(f"Solvent Energy:   {expected['e_sensible_solvent']:.2f} vs {energy_details.get('e_sensible_solvent_j', 0):.2f}")
    print(f"Additive Energy:  {expected['e_sensible_additive']:.2f} vs {energy_details.get('e_sensible_additive_j', 0):.2f}")
    print(f"Modulator Energy: {expected['e_sensible_modulator']:.2f} vs {energy_details.get('e_sensible_modulator_j', 0):.2f}")
    print(f"Metal Energy:     {expected['e_sensible_metal']:.2f} vs {energy_details.get('e_sensible_metal_j', 0):.2f}")
    print(f"Linker Energy:    {expected['e_sensible_linker']:.2f} vs {energy_details.get('e_sensible_linker_j', 0):.2f}")
    print(f"Total Sensible:   {expected['e_sensible_total']:.2f} vs {energy_details.get('e_sensible_total_j', 0):.2f}")
    print(f"Qheat (MJ):       {expected['qheat_mj']:.5f} vs {result.get('q_energy_mj', 0):.5f}")
    print(f"V_Reactor (L):    ? vs {energy_details.get('v_reactor_l', 0):.6f}")
    print()
    
    return result, expected

def analyze_differences():
    """Analisis perbedaan untuk menemukan masalah"""
    print("=== ANALISIS PERBEDAAN ===")
    
    # Test use case 1
    result1, expected1 = test_use_case_1()
    
    # Test use case 2  
    result2, expected2 = test_use_case_2()
    
    print("=== ANALISIS MASALAH ===")
    
    # Analisis Cp linker
    energy1 = result1.get("energy_details", {})
    energy2 = result2.get("energy_details", {})
    
    print("1. CP LINKER:")
    print(f"   Use Case 1: Expected {expected1['cp_linker']}, Got {energy1.get('cp_value', 0)}")
    print(f"   Use Case 2: Expected {expected2['cp_linker']}, Got {energy2.get('cp_value', 0)}")
    
    if energy1.get('cp_value', 0) != expected1['cp_linker']:
        print("   ❌ CP Linker tidak sesuai - kemungkinan SMILES atau mapping CP salah")
    
    print("\n2. ENERGI SENSIBLE:")
    print(f"   Use Case 1 Total: Expected {expected1['e_sensible_total']}, Got {energy1.get('e_sensible_total_j', 0)}")
    print(f"   Use Case 2 Total: Expected {expected2['e_sensible_total']}, Got {energy2.get('e_sensible_total_j', 0)}")
    
    # Analisis komponen energi
    print("\n3. KOMPONEN ENERGI DETAIL:")
    for case_name, result, expected in [("Use Case 1", result1, expected1), ("Use Case 2", result2, expected2)]:
        energy = result.get("energy_details", {})
        print(f"\n   {case_name}:")
        print(f"     Solvent:   Expected {expected['e_sensible_solvent']:.2f}, Got {energy.get('e_sensible_solvent_j', 0):.2f}")
        print(f"     Modulator: Expected {expected['e_sensible_modulator']:.2f}, Got {energy.get('e_sensible_modulator_j', 0):.2f}")
        print(f"     Metal:     Expected {expected['e_sensible_metal']:.2f}, Got {energy.get('e_sensible_metal_j', 0):.2f}")
        print(f"     Linker:    Expected {expected['e_sensible_linker']:.2f}, Got {energy.get('e_sensible_linker_j', 0):.2f}")
    
    print("\n4. QHEAT:")
    print(f"   Use Case 1: Expected {expected1['qheat_mj']:.5f}, Got {result1.get('q_energy_mj', 0):.5f}")
    print(f"   Use Case 2: Expected {expected2['qheat_mj']:.5f}, Got {result2.get('q_energy_mj', 0):.5f}")
    
    # Analisis V_Reactor
    print(f"\n5. V_REACTOR:")
    print(f"   Use Case 1: {energy1.get('v_reactor_l', 0):.6f} L")
    print(f"   Use Case 2: {energy2.get('v_reactor_l', 0):.6f} L")
    
    print("\n=== KEMUNGKINAN MASALAH ===")
    print("1. CP Linker mapping mungkin salah atau SMILES tidak tepat")
    print("2. Perhitungan molar dari massa/volume mungkin tidak akurat")
    print("3. Delta T calculation mungkin berbeda")
    print("4. V_Reactor calculation masih tidak sesuai model asli")
    print("5. Properti kimia (density, Cp, Mr) mungkin berbeda dari model asli")

if __name__ == "__main__":
    analyze_differences()