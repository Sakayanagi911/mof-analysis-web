#!/usr/bin/env python3
"""
Test web API dengan parameter yang sudah diperbaiki
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routers.analysis import get_modulator_concentration, get_energy_scale_factor
from services.cost_analysis import run_economic_analysis

def test_web_api_use_case_1():
    """Test Use Case 1 dengan parameter seperti yang akan dikirim web"""
    print("=== TEST WEB API USE CASE 1 ===")
    
    # Parameter seperti yang akan diterima dari web form
    metal_name = "CuSO₄·5H₂O"
    linker_name = "H₂L"
    smiles = "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O"
    reaction_time = 24.0
    temperature = 85.0
    gravimetric_wc = 5.5
    volumetric_wc = 40.0
    product_mass_mg = 9.12
    metal_mass_mg = 8.0
    linker_mass_mg = 5.0
    solvent_name = "DMF"
    solvent_volume_ml = 2.0
    additive_name = "-"
    additive_volume_ml = 0.0
    modulator_name = "HNO3"
    modulator_volume_ml = 0.05
    
    # Hitung parameter otomatis seperti di web
    modulator_concentration = get_modulator_concentration(modulator_name, modulator_volume_ml)
    energy_scale_factor = get_energy_scale_factor(solvent_volume_ml, additive_volume_ml, modulator_volume_ml)
    
    print(f"Modulator concentration: {modulator_concentration}%")
    print(f"Energy scale factor: {energy_scale_factor}")
    
    # Panggil fungsi seperti di web
    result = run_economic_analysis(
        metal_name=metal_name,
        linker_name=linker_name,
        reaction_time=reaction_time,
        temperature=temperature,
        smiles=smiles,
        gravimetric_wc=gravimetric_wc,
        volumetric_wc=volumetric_wc,
        product_mass_mg=product_mass_mg,
        metal_mass_mg=metal_mass_mg,
        linker_mass_mg=linker_mass_mg,
        solvent_name=solvent_name,
        solvent_volume_ml=solvent_volume_ml,
        additive_name=additive_name,
        additive_volume_ml=additive_volume_ml,
        modulator_name=modulator_name,
        modulator_volume_ml=modulator_volume_ml,
        modulator_concentration=modulator_concentration,
        energy_scale_factor=energy_scale_factor
    )
    
    energy_details = result.get("energy_details", {})
    
    print(f"\nHasil:")
    print(f"  Modulator Energy: {energy_details.get('e_sensible_modulator_j', 0):.2f} J (expected: 0.25 J)")
    print(f"  Solvent Energy: {energy_details.get('e_sensible_solvent_j', 0):.2f} J (expected: 229.74 J)")
    print(f"  Total Sensible: {energy_details.get('e_sensible_total_j', 0):.2f} J (expected: 230.50 J)")
    print(f"  Qheat: {result.get('q_energy_mj', 0):.5f} MJ (expected: 0.53810 MJ)")

def test_web_api_use_case_2():
    """Test Use Case 2 dengan parameter seperti yang akan dikirim web"""
    print("\n=== TEST WEB API USE CASE 2 ===")
    
    # Parameter seperti yang akan diterima dari web form
    metal_name = "Zn(NO₃)₂·6H₂O"
    linker_name = "H4TCPP"
    smiles = "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1"
    reaction_time = 24.0
    temperature = 85.0
    gravimetric_wc = 5.5
    volumetric_wc = 40.0
    product_mass_mg = 3.785
    metal_mass_mg = 10.0
    linker_mass_mg = 4.0
    solvent_name = "DMF"
    solvent_volume_ml = 2.0
    additive_name = "EtOH"
    additive_volume_ml = 0.5
    modulator_name = "HNO3"
    modulator_volume_ml = 0.15
    
    # Hitung parameter otomatis seperti di web
    modulator_concentration = get_modulator_concentration(modulator_name, modulator_volume_ml)
    energy_scale_factor = get_energy_scale_factor(solvent_volume_ml, additive_volume_ml, modulator_volume_ml)
    
    print(f"Modulator concentration: {modulator_concentration}%")
    print(f"Energy scale factor: {energy_scale_factor}")
    
    # Panggil fungsi seperti di web
    result = run_economic_analysis(
        metal_name=metal_name,
        linker_name=linker_name,
        reaction_time=reaction_time,
        temperature=temperature,
        smiles=smiles,
        gravimetric_wc=gravimetric_wc,
        volumetric_wc=volumetric_wc,
        product_mass_mg=product_mass_mg,
        metal_mass_mg=metal_mass_mg,
        linker_mass_mg=linker_mass_mg,
        solvent_name=solvent_name,
        solvent_volume_ml=solvent_volume_ml,
        additive_name=additive_name,
        additive_volume_ml=additive_volume_ml,
        modulator_name=modulator_name,
        modulator_volume_ml=modulator_volume_ml,
        modulator_concentration=modulator_concentration,
        energy_scale_factor=energy_scale_factor
    )
    
    energy_details = result.get("energy_details", {})
    
    print(f"\nHasil:")
    print(f"  Modulator Energy: {energy_details.get('e_sensible_modulator_j', 0):.2f} J (expected: 2.03 J)")
    print(f"  Solvent Energy: {energy_details.get('e_sensible_solvent_j', 0):.2f} J (expected: 114.87 J)")
    print(f"  Additive Energy: {energy_details.get('e_sensible_additive_j', 0):.2f} J (expected: 57.77 J)")
    print(f"  Total Sensible: {energy_details.get('e_sensible_total_j', 0):.2f} J (expected: 175.11 J)")
    print(f"  Qheat: {result.get('q_energy_mj', 0):.5f} MJ (expected: 0.77531 MJ)")

if __name__ == "__main__":
    test_web_api_use_case_1()
    test_web_api_use_case_2()