#!/usr/bin/env python3
"""
Debug solvent energy calculation
"""

# Use Case 1: DMF 2.0 mL, Expected 229.74 J
# Use Case 2: DMF 2.0 mL, Expected 114.87 J

# Both use same solvent and volume, but different expected energies
# This suggests there might be a scaling factor or different calculation

print("=== SOLVENT ENERGY ANALYSIS ===")

# DMF properties from notebook
rho_dmf = 0.9445  # g/mL
cp_dmf = 148.16   # J/mol·K  
mr_dmf = 73.0938  # g/mol

volume_ml = 2.0
delta_t = 60.0  # K (85°C - 25°C)

# Standard calculation
mass_g = volume_ml * rho_dmf
n_mol = mass_g / mr_dmf
energy_j = n_mol * cp_dmf * delta_t

print(f"Standard calculation:")
print(f"  Volume: {volume_ml} mL")
print(f"  Mass: {mass_g:.4f} g")
print(f"  Moles: {n_mol:.6f} mol")
print(f"  Energy: {energy_j:.2f} J")

print(f"\nExpected values:")
print(f"  Use Case 1: 229.74 J")
print(f"  Use Case 2: 114.87 J")

print(f"\nRatio analysis:")
print(f"  UC1/Calculated: {229.74 / energy_j:.4f}")
print(f"  UC2/Calculated: {114.87 / energy_j:.4f}")
print(f"  UC2/UC1: {114.87 / 229.74:.4f}")

# Check if there's a product mass scaling factor
product_mass_1 = 9.12   # mg
product_mass_2 = 3.785  # mg

print(f"\nProduct mass scaling:")
print(f"  UC1 product: {product_mass_1} mg")
print(f"  UC2 product: {product_mass_2} mg")
print(f"  Mass ratio UC2/UC1: {product_mass_2 / product_mass_1:.4f}")
print(f"  Energy ratio UC2/UC1: {114.87 / 229.74:.4f}")

if abs((product_mass_2 / product_mass_1) - (114.87 / 229.74)) < 0.01:
    print("  ✓ Energy scales with product mass!")
else:
    print("  ✗ Energy does not scale with product mass")

# Check other possible scaling factors
print(f"\nOther possible factors:")
print(f"  If energy scales with sqrt(product_mass): {(product_mass_2 / product_mass_1)**0.5:.4f}")
print(f"  If energy scales with product_mass^2: {(product_mass_2 / product_mass_1)**2:.4f}")