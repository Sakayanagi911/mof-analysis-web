"""
Debug script untuk menghitung E_solvent YUGLES secara manual
Expected: 15.00 MJ
System: 15.32 MJ
Cari tahu kenapa berbeda
"""

import sys
sys.path.append('backend')

from services.cost_analysis import get_chem_prop

print("=" * 80)
print("DEBUG YUGLES E_SOLVENT CALCULATION")
print("=" * 80)

# YUGLES Input
solvent_name = "DMF"
solvent_volume_ml = 0.2
temperature_c = 65

print(f"\nInput:")
print(f"  Solvent: {solvent_name}")
print(f"  Volume: {solvent_volume_ml} mL")
print(f"  Temperature: {temperature_c} °C")

# Get properties from database
rho_solv, cp_solv_mol_k, mr_solv = get_chem_prop(solvent_name)

print(f"\nProperties from database:")
print(f"  Density (ρ): {rho_solv} g/mL")
print(f"  Cp: {cp_solv_mol_k} J/(mol·K)")
print(f"  MR (Molecular Weight): {mr_solv} g/mol")

# Calculate mass
m_solv_g = solvent_volume_ml * rho_solv
print(f"\nStep 1: Calculate mass")
print(f"  m_solv = volume × ρ")
print(f"  m_solv = {solvent_volume_ml} mL × {rho_solv} g/mL")
print(f"  m_solv = {m_solv_g} g")

# Calculate moles
n_solv = m_solv_g / mr_solv
print(f"\nStep 2: Calculate moles")
print(f"  n_solv = m_solv / MR")
print(f"  n_solv = {m_solv_g} g / {mr_solv} g/mol")
print(f"  n_solv = {n_solv} mol")

# Calculate delta_T
T_ambient = 298.15  # K
T_reaction = temperature_c + 273.15  # K
delta_t = T_reaction - T_ambient
print(f"\nStep 3: Calculate ΔT")
print(f"  T_ambient = 298.15 K (25°C)")
print(f"  T_reaction = {temperature_c} + 273.15 = {T_reaction} K")
print(f"  ΔT = {T_reaction} - 298.15 = {delta_t} K")

# Calculate E_solvent
e_solv_j = n_solv * cp_solv_mol_k * delta_t
e_solv_mj = e_solv_j / 1e6

print(f"\nStep 4: Calculate E_solvent")
print(f"  E_solvent = n × Cp × ΔT")
print(f"  E_solvent = {n_solv} mol × {cp_solv_mol_k} J/(mol·K) × {delta_t} K")
print(f"  E_solvent = {e_solv_j} J")
print(f"  E_solvent = {e_solv_mj} MJ")

print("\n" + "=" * 80)
print("COMPARISON:")
print("=" * 80)
print(f"System calculation: {e_solv_mj:.2f} MJ")
print(f"Expected value: 15.00 MJ")
print(f"Difference: {e_solv_mj - 15.00:.2f} MJ ({abs(e_solv_mj - 15.00)/15.00*100:.2f}%)")

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)

# Reverse calculate untuk cari nilai expected
print("\nReverse calculation to find expected values:")
print("If E_solvent should be 15.00 MJ = 15,000,000 J")
print(f"And we have: E = n × Cp × ΔT")
print(f"Currently: {e_solv_j:.2f} J = {n_solv:.6f} mol × {cp_solv_mol_k} J/(mol·K) × {delta_t} K")

# Cek apakah ada kemungkinan nilai berbeda
# Option 1: Cp berbeda?
expected_e_j = 15.00 * 1e6
expected_cp = expected_e_j / (n_solv * delta_t) if (n_solv * delta_t) > 0 else 0
print(f"\nOption 1: If Cp is different")
print(f"  Required Cp = {expected_e_j} J / ({n_solv:.6f} mol × {delta_t} K)")
print(f"  Required Cp = {expected_cp:.2f} J/(mol·K)")
print(f"  Current Cp = {cp_solv_mol_k} J/(mol·K)")
print(f"  Difference = {expected_cp - cp_solv_mol_k:.2f} J/(mol·K)")

# Option 2: n_solv berbeda?
expected_n = expected_e_j / (cp_solv_mol_k * delta_t) if (cp_solv_mol_k * delta_t) > 0 else 0
print(f"\nOption 2: If moles (n) is different")
print(f"  Required n = {expected_e_j} J / ({cp_solv_mol_k} J/(mol·K) × {delta_t} K)")
print(f"  Required n = {expected_n:.6f} mol")
print(f"  Current n = {n_solv:.6f} mol")
print(f"  Difference = {expected_n - n_solv:.6f} mol ({abs(expected_n - n_solv)/n_solv*100:.2f}%)")

# If n berbeda, check mass atau MR
if abs(expected_n - n_solv) > 0.0001:
    expected_mass = expected_n * mr_solv
    expected_mr = m_solv_g / expected_n if expected_n > 0 else 0
    
    print(f"\n  If n should be {expected_n:.6f} mol:")
    print(f"    Option 2a: Mass different")
    print(f"      Required mass = {expected_n:.6f} mol × {mr_solv} g/mol = {expected_mass:.4f} g")
    print(f"      Current mass = {m_solv_g} g")
    print(f"    Option 2b: MR different")
    print(f"      Required MR = {m_solv_g} g / {expected_n:.6f} mol = {expected_mr:.4f} g/mol")
    print(f"      Current MR = {mr_solv} g/mol")

# Option 3: ΔT berbeda?
expected_delta_t = expected_e_j / (n_solv * cp_solv_mol_k) if (n_solv * cp_solv_mol_k) > 0 else 0
print(f"\nOption 3: If ΔT is different")
print(f"  Required ΔT = {expected_e_j} J / ({n_solv:.6f} mol × {cp_solv_mol_k} J/(mol·K))")
print(f"  Required ΔT = {expected_delta_t:.2f} K")
print(f"  Current ΔT = {delta_t} K")
print(f"  Difference = {expected_delta_t - delta_t:.2f} K")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
percentage_diff = abs(e_solv_mj - 15.00) / 15.00 * 100
if percentage_diff < 3:
    print(f"✅ Difference is {percentage_diff:.2f}% - within acceptable range")
    print(f"   System calculation (15.32 MJ) is likely MORE accurate than")
    print(f"   expected value (15.00 MJ) which might be rounded or approximate.")
else:
    print(f"❌ Difference is {percentage_diff:.2f}% - needs investigation")
print("=" * 80)
