#!/usr/bin/env python3
"""
Debug YUGLES - Cp and E_solvent
================================
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backend.services.cost_analysis import calculate_energy

yugles_params = {
    "smiles": "C(#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O",
    "temperature_c": 65.0,
    "reaction_time_h": 24.0,
    "linker_mass_mg": 5.0,
    "metal_mass_mg": 15.0,
    "solvent_name": "DMF",
    "solvent_volume_ml": 0.2,
    "additive_name": "DMSO",
    "additive_volume_ml": 0.2,
    "modulator_name": "HNO3",
    "modulator_volume_ml": 0.06,
    "modulator_concentration": 4.44,
    "metal_name": "Cu(NO3)2.3H2O",
    "volumetric_wc": 46.18931424,
    "gravimetric_wc": 5.996913544,
    "product_mass_mg": 6.3,
    "energy_scale_factor": 1.0
}

print("="*80)
print("DEBUG YUGLES - Cp Linker and E_Solvent")
print("="*80)
print()

result = calculate_energy(**yugles_params)

print("\nRESULTS:")
print("-"*80)
print(f"Cp Linker:")
print(f"  Expected: 345.59 J/(mol·K)")
print(f"  Actual:   {result['cp_value']:.2f} J/(mol·K)")
print(f"  Diff:     {abs(result['cp_value'] - 345.59):.2f} ({abs(result['cp_value'] - 345.59)/345.59*100:.2f}%)")
print()

print(f"E_Solvent:")
print(f"  Expected: 15.00 J")
print(f"  Actual:   {result['e_sensible_solvent_j']:.2f} J")
print(f"  Diff:     {abs(result['e_sensible_solvent_j'] - 15.00):.2f} ({abs(result['e_sensible_solvent_j'] - 15.00)/15.00*100:.2f}%)")
print()

print(f"Total Sensible Energy:")
print(f"  Expected: 32.69 J")
print(f"  Actual:   {result['e_sensible_total_j']:.2f} J")
print(f"  Diff:     {abs(result['e_sensible_total_j'] - 32.69):.2f}")
print()

# Check if Cp is from hybrid or verified
print("CP SOURCE:")
if result['cp_value'] == 345.59:
    print("  Using VERIFIED Cp (exact match)")
elif abs(result['cp_value'] - 332.01) < 1:
    print("  Using HYBRID Physics-ML Cp")
    print("  (Cp_Joback=304.34 + DeltaCp_student=27.67 = 332.01)")
else:
    print(f"  Unknown source: {result['cp_value']}")
print()

# Manual calculation for E_solvent
from backend.services.cost_analysis import get_chem_prop

rho_solv, cp_solv, mr_solv = get_chem_prop("DMF")
delta_t = 65.0 - 25.0  # Temperature - room temp

print("MANUAL CALCULATION E_SOLVENT:")
print(f"  Solvent: DMF")
print(f"  Volume: {yugles_params['solvent_volume_ml']:.2f} mL")
print(f"  Density: {rho_solv:.4f} g/mL")
print(f"  Mass: {rho_solv * yugles_params['solvent_volume_ml']:.5f} g")
print(f"  Cp (mass): {cp_solv:.2f} J/(mol·K)")
print(f"  Mr: {mr_solv:.4f} g/mol")
print(f"  Delta T: {delta_t:.1f} °C")
print()

# Calculate cp_mass from cp_molar
cp_mass = (cp_solv / mr_solv) * 1000  # J/(kg·K)
m_solv = rho_solv * yugles_params['solvent_volume_ml']
e_solv_manual = (m_solv / 1000) * cp_mass * delta_t

print(f"  cp_mass = (cp_molar / Mr) × 1000")
print(f"  cp_mass = ({cp_solv:.2f} / {mr_solv:.4f}) × 1000")
print(f"  cp_mass = {cp_mass:.2f} J/(kg·K)")
print()
print(f"  E_solvent = (mass/1000) × cp_mass × delta_T")
print(f"  E_solvent = ({m_solv:.5f}/1000) × {cp_mass:.2f} × {delta_t:.1f}")
print(f"  E_solvent = {e_solv_manual:.2f} J")
print()

if abs(e_solv_manual - 15.00) < 1.0:
    print("  Manual calculation MATCHES expected! (15.00 J)")
else:
    print(f"  Manual calculation DIFFERS from expected by {abs(e_solv_manual - 15.00):.2f} J")

print("="*80)
