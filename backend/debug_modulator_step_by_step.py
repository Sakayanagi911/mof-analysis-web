#!/usr/bin/env python3
"""
Debug modulator calculation step by step
"""

from services.cost_analysis import get_chem_prop

def debug_modulator_step_by_step():
    """Debug modulator calculation manually"""
    
    print("=== MODULATOR CALCULATION DEBUG ===")
    
    # Test case: HNO3 0.05mL at 4.44%
    modulator_name = "HNO3"
    modulator_volume_ml = 0.05
    modulator_concentration = 4.44
    temperature_c = 85.0
    
    print(f"Input:")
    print(f"  Modulator: {modulator_name}")
    print(f"  Volume: {modulator_volume_ml} mL")
    print(f"  Concentration: {modulator_concentration}%")
    print(f"  Temperature: {temperature_c}°C")
    print()
    
    # Get properties
    rho_mod, cp_mod_mol_k, mr_mod = get_chem_prop(modulator_name)
    print(f"Properties from database:")
    print(f"  Density (rho): {rho_mod} g/mL")
    print(f"  Heat capacity (Cp): {cp_mod_mol_k} J/(mol·K)")
    print(f"  Molecular weight (Mr): {mr_mod} g/mol")
    print()
    
    # Step-by-step calculation
    print("Step-by-step calculation:")
    
    # Step 1: Mass calculation
    m_mod_g = modulator_volume_ml * rho_mod
    print(f"1. Mass = Volume × Density")
    print(f"   Mass = {modulator_volume_ml} mL × {rho_mod} g/mL = {m_mod_g} g")
    
    # Step 2: Concentration factor
    concentration_factor = modulator_concentration / 100.0
    print(f"2. Concentration factor = {modulator_concentration}% / 100 = {concentration_factor}")
    
    # Step 3: Effective mass (with concentration)
    effective_mass_g = m_mod_g * concentration_factor
    print(f"3. Effective mass = {m_mod_g} g × {concentration_factor} = {effective_mass_g} g")
    
    # Step 4: Moles calculation
    n_mod = effective_mass_g / mr_mod
    print(f"4. Moles = Effective mass / Molecular weight")
    print(f"   Moles = {effective_mass_g} g / {mr_mod} g/mol = {n_mod} mol")
    
    # Step 5: Temperature difference
    delta_t = temperature_c - 25.0
    print(f"5. ΔT = {temperature_c}°C - 25°C = {delta_t} K")
    
    # Step 6: Energy calculation
    e_mod = n_mod * cp_mod_mol_k * delta_t
    print(f"6. Energy = Moles × Cp × ΔT")
    print(f"   Energy = {n_mod} mol × {cp_mod_mol_k} J/(mol·K) × {delta_t} K = {e_mod} J")
    print()
    
    print(f"FINAL RESULT: {e_mod:.4f} J")
    
    # Compare with expected manual calculation
    print("\n=== COMPARISON WITH EXPECTED ===")
    
    # Expected calculation (from debug output earlier)
    expected_mass = 0.002642  # g
    expected_moles = 0.041927  # mol
    expected_energy = 73.2543  # J
    
    print(f"Expected mass: {expected_mass} g")
    print(f"Actual mass: {effective_mass_g} g")
    print(f"Ratio: {effective_mass_g/expected_mass if expected_mass > 0 else 0:.3f}")
    print()
    
    print(f"Expected moles: {expected_moles} mol")
    print(f"Actual moles: {n_mod} mol")
    print(f"Ratio: {n_mod/expected_moles if expected_moles > 0 else 0:.3f}")
    print()
    
    print(f"Expected energy: {expected_energy} J")
    print(f"Actual energy: {e_mod} J")
    print(f"Ratio: {e_mod/expected_energy if expected_energy > 0 else 0:.3f}")

if __name__ == "__main__":
    debug_modulator_step_by_step()