#!/usr/bin/env python3
"""
Debug detail untuk menemukan masalah spesifik
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.cost_analysis import get_chem_prop

def debug_chemical_properties():
    """Debug properti kimia yang digunakan"""
    
    print("=== DEBUG PROPERTI KIMIA ===")
    
    # Test properti untuk Use Case 1
    print("USE CASE 1:")
    print("DMF:", get_chem_prop("DMF"))
    print("HNO3:", get_chem_prop("HNO3"))
    print("CuSO₄·5H₂O:", get_chem_prop("CuSO₄·5H₂O", is_metal=True))
    
    print("\nUSE CASE 2:")
    print("DMF:", get_chem_prop("DMF"))
    print("EtOH:", get_chem_prop("EtOH"))
    print("HNO3:", get_chem_prop("HNO3"))
    print("Zn(NO₃)₂·6H₂O:", get_chem_prop("Zn(NO₃)₂·6H₂O", is_metal=True))

def debug_molar_calculation():
    """Debug perhitungan molar"""
    
    print("\n=== DEBUG PERHITUNGAN MOLAR ===")
    
    # Use Case 1 parameters
    solvent_volume_ml = 2.0
    modulator_volume_ml = 0.05
    metal_mass_mg = 8.0
    linker_mass_mg = 5.0
    temperature_c = 85.0
    
    # Get properties
    rho_solv, cp_solv_mol_k, mr_solv = get_chem_prop("DMF")
    rho_mod, cp_mod_mol_k, mr_mod = get_chem_prop("HNO3")
    _, cp_metal_mol_k, mr_metal = get_chem_prop("CuSO₄·5H₂O", is_metal=True)
    
    print("USE CASE 1 CALCULATION:")
    print(f"DMF: rho={rho_solv}, cp={cp_solv_mol_k}, mr={mr_solv}")
    print(f"HNO3: rho={rho_mod}, cp={cp_mod_mol_k}, mr={mr_mod}")
    print(f"CuSO₄·5H₂O: cp={cp_metal_mol_k}, mr={mr_metal}")
    
    # Calculate moles
    m_solv_g = solvent_volume_ml * rho_solv
    n_solv = m_solv_g / mr_solv
    print(f"Solvent: {solvent_volume_ml} mL * {rho_solv} g/mL = {m_solv_g} g")
    print(f"Solvent moles: {m_solv_g} g / {mr_solv} g/mol = {n_solv} mol")
    
    m_mod_g = modulator_volume_ml * rho_mod
    n_mod = m_mod_g / mr_mod
    print(f"Modulator: {modulator_volume_ml} mL * {rho_mod} g/mL = {m_mod_g} g")
    print(f"Modulator moles: {m_mod_g} g / {mr_mod} g/mol = {n_mod} mol")
    
    n_metal = (metal_mass_mg / 1000.0) / mr_metal
    print(f"Metal moles: {metal_mass_mg/1000.0} g / {mr_metal} g/mol = {n_metal} mol")
    
    # Calculate delta T
    delta_t = (temperature_c + 273.15) - 298.15
    print(f"Delta T: ({temperature_c} + 273.15) - 298.15 = {delta_t} K")
    
    # Calculate energies
    e_solv = n_solv * cp_solv_mol_k * delta_t
    e_mod = n_mod * cp_mod_mol_k * delta_t
    e_metal = n_metal * cp_metal_mol_k * delta_t
    
    print(f"Solvent energy: {n_solv} * {cp_solv_mol_k} * {delta_t} = {e_solv} J")
    print(f"Modulator energy: {n_mod} * {cp_mod_mol_k} * {delta_t} = {e_mod} J")
    print(f"Metal energy: {n_metal} * {cp_metal_mol_k} * {delta_t} = {e_metal} J")
    
    print(f"\nEXPECTED vs CALCULATED:")
    print(f"Solvent: 229.74 vs {e_solv:.2f}")
    print(f"Modulator: 0.25 vs {e_mod:.2f}")
    print(f"Metal: 0.18 vs {e_metal:.2f}")

def debug_v_reactor():
    """Debug perhitungan V_Reactor"""
    
    print("\n=== DEBUG V_REACTOR ===")
    
    # Use Case 1
    solvent_volume_ml = 2.0
    modulator_volume_ml = 0.05
    metal_mass_mg = 8.0
    linker_mass_mg = 5.0
    
    # Current calculation
    rho_solv, _, _ = get_chem_prop("DMF")
    rho_mod, _, _ = get_chem_prop("HNO3")
    
    m_solv_g = solvent_volume_ml * rho_solv
    m_mod_g = modulator_volume_ml * rho_mod
    m_solid_g = (metal_mass_mg + linker_mass_mg) / 1000.0
    m_total_g = m_solv_g + m_mod_g + m_solid_g
    
    v_liquid_l = (solvent_volume_ml + modulator_volume_ml) / 1000.0
    
    print(f"Liquid volume: ({solvent_volume_ml} + {modulator_volume_ml}) / 1000 = {v_liquid_l} L")
    print(f"Total mass: {m_solv_g} + {m_mod_g} + {m_solid_g} = {m_total_g} g")
    
    # Current V_Reactor calculation
    if v_liquid_l > 0:
        v_reactor_l = v_liquid_l * 3.0
    else:
        v_reactor_l = (m_total_g / 1000.0) * 3.0
    
    if v_reactor_l < 0.1:
        v_reactor_l = 0.1
    elif v_reactor_l > 10.0:
        v_reactor_l = 10.0
        
    print(f"V_Reactor (current): {v_reactor_l} L")
    
    # Expected Qheat calculation
    e_sens_total = 230.50  # Expected from use case 1
    heat_eff = 0.75
    expected_qheat = 0.53810  # MJ/1000L
    
    # Reverse calculate expected V_Reactor
    # qheat_mj_1000l = (e_sens_total / (heat_eff * v_reactor_l)) * 1000 / 1e6
    # expected_qheat = (e_sens_total / (heat_eff * v_reactor_expected)) * 1000 / 1e6
    # v_reactor_expected = (e_sens_total * 1000) / (expected_qheat * heat_eff * 1e6)
    
    v_reactor_expected = (e_sens_total * 1000) / (expected_qheat * heat_eff * 1e6)
    print(f"V_Reactor (expected): {v_reactor_expected:.6f} L")
    print(f"Ratio: {v_reactor_l / v_reactor_expected:.2f}x too small")

if __name__ == "__main__":
    debug_chemical_properties()
    debug_molar_calculation()
    debug_v_reactor()