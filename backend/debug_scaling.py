#!/usr/bin/env python3
"""
Debug the scaling factor for solvent energy
"""

print("=== SCALING FACTOR ANALYSIS ===")

# Use Case data
uc1_data = {
    "solvent_vol": 2.0,
    "additive_vol": 0.0,
    "modulator_vol": 0.05,
    "total_liquid": 2.05,
    "product_mass": 9.12,
    "expected_solvent_energy": 229.74
}

uc2_data = {
    "solvent_vol": 2.0,
    "additive_vol": 0.5,
    "modulator_vol": 0.15,
    "total_liquid": 2.65,
    "product_mass": 3.785,
    "expected_solvent_energy": 114.87
}

print("Use Case 1:")
for key, value in uc1_data.items():
    print(f"  {key}: {value}")

print("\nUse Case 2:")
for key, value in uc2_data.items():
    print(f"  {key}: {value}")

# Calculate ratios
print(f"\nRatios (UC2/UC1):")
print(f"  Solvent volume: {uc2_data['solvent_vol'] / uc1_data['solvent_vol']:.4f}")
print(f"  Total liquid: {uc2_data['total_liquid'] / uc1_data['total_liquid']:.4f}")
print(f"  Product mass: {uc2_data['product_mass'] / uc1_data['product_mass']:.4f}")
print(f"  Expected energy: {uc2_data['expected_solvent_energy'] / uc1_data['expected_solvent_energy']:.4f}")

# Check if energy scales with total liquid volume
total_liquid_ratio = uc2_data['total_liquid'] / uc1_data['total_liquid']
energy_ratio = uc2_data['expected_solvent_energy'] / uc1_data['expected_solvent_energy']

print(f"\nScaling analysis:")
print(f"  Total liquid ratio: {total_liquid_ratio:.4f}")
print(f"  Energy ratio: {energy_ratio:.4f}")
print(f"  Difference: {abs(total_liquid_ratio - energy_ratio):.4f}")

if abs(total_liquid_ratio - energy_ratio) < 0.05:
    print("  ✓ Energy might scale with total liquid volume!")
else:
    print("  ✗ Energy does not scale with total liquid volume")

# Check other possible scaling factors
print(f"\nOther scaling possibilities:")
print(f"  Energy / total_liquid: UC1 = {uc1_data['expected_solvent_energy'] / uc1_data['total_liquid']:.2f}, UC2 = {uc2_data['expected_solvent_energy'] / uc2_data['total_liquid']:.2f}")
print(f"  Energy / product_mass: UC1 = {uc1_data['expected_solvent_energy'] / uc1_data['product_mass']:.2f}, UC2 = {uc2_data['expected_solvent_energy'] / uc2_data['product_mass']:.2f}")

# Check if there's a concentration effect
print(f"\nConcentration effects:")
print(f"  Solvent/Total liquid: UC1 = {uc1_data['solvent_vol'] / uc1_data['total_liquid']:.4f}, UC2 = {uc2_data['solvent_vol'] / uc2_data['total_liquid']:.4f}")

solvent_fraction_1 = uc1_data['solvent_vol'] / uc1_data['total_liquid']
solvent_fraction_2 = uc2_data['solvent_vol'] / uc2_data['total_liquid']
fraction_ratio = solvent_fraction_2 / solvent_fraction_1

print(f"  Solvent fraction ratio: {fraction_ratio:.4f}")
print(f"  Energy ratio: {energy_ratio:.4f}")

if abs(fraction_ratio - energy_ratio) < 0.05:
    print("  ✓ Energy might scale with solvent fraction!")
else:
    print("  ✗ Energy does not scale with solvent fraction")