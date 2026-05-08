#!/usr/bin/env python3
"""
Debug modulator calculation specifically
"""

# Manual calculation for HNO3
volume_ml = 0.05
rho_hno3 = 1.5129  # g/mL from notebook
mr_hno3 = 63.0128  # g/mol from notebook
cp_hno3 = 53.29    # J/mol·K from notebook

# Mass calculation
mass_g = volume_ml * rho_hno3
print(f"HNO3 mass: {volume_ml} mL × {rho_hno3} g/mL = {mass_g:.6f} g")

# Molar calculation
n_mol = mass_g / mr_hno3
print(f"HNO3 moles: {mass_g:.6f} g / {mr_hno3} g/mol = {n_mol:.6f} mol")

# Energy calculation
delta_t = 60.0  # K (85°C - 25°C)
energy_j = n_mol * cp_hno3 * delta_t
print(f"HNO3 energy: {n_mol:.6f} mol × {cp_hno3} J/mol·K × {delta_t} K = {energy_j:.2f} J")

print(f"\nExpected: 0.25 J")
print(f"Calculated: {energy_j:.2f} J")
print(f"Ratio: {energy_j / 0.25:.1f}x too high")

# What should the values be for 0.25 J?
print(f"\nFor 0.25 J energy:")
print(f"Required moles: {0.25 / (cp_hno3 * delta_t):.6f} mol")
print(f"Required mass: {0.25 / (cp_hno3 * delta_t) * mr_hno3:.6f} g")
print(f"Required volume: {0.25 / (cp_hno3 * delta_t) * mr_hno3 / rho_hno3:.6f} mL")

# Check if there's a concentration issue
print(f"\nPossible concentration factor:")
print(f"If HNO3 is diluted, effective concentration = {0.25 / energy_j:.4f}")
print(f"This would be {0.25 / energy_j * 100:.1f}% concentration")