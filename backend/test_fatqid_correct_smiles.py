#!/usr/bin/env python3
"""
Test FATQID dengan SMILES yang benar
"""

from services.cost_analysis import calculate_energy
from services.joback import calculate_cp_joback

def test_fatqid_correct_smiles():
    """Test dengan SMILES FATQID yang benar"""
    
    # SMILES comparison
    smiles_fatqid = "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O"
    smiles_old = "O=C(O)c1ccc(cc1)C(=O)O"
    
    print("=== COMPARISON: OLD vs NEW SMILES ===")
    print(f"Old SMILES: {smiles_old}")
    print(f"New SMILES: {smiles_fatqid}")
    print()
    
    # Test CP calculation
    try:
        cp_old = calculate_cp_joback(smiles_old)
        print(f"CP Old SMILES: {cp_old:.2f} J/(mol·K)")
    except Exception as e:
        print(f"CP Old SMILES: ERROR - {e}")
    
    try:
        cp_new = calculate_cp_joback(smiles_fatqid)
        print(f"CP New SMILES: {cp_new:.2f} J/(mol·K)")
    except Exception as e:
        print(f"CP New SMILES: ERROR - {e}")
    
    print(f"Target CP: 364.47 J/(mol·K)")
    print()
    
    # Test full energy calculation dengan SMILES baru
    fatqid_params = {
        "smiles": smiles_fatqid,
        "temperature_c": 85.0,
        "reaction_time_h": 24.0,
        "linker_mass_mg": 5.0,
        "metal_mass_mg": 8.0,
        "solvent_name": "DMF",
        "solvent_volume_ml": 2.0,
        "additive_name": "-",
        "additive_volume_ml": 0.0,
        "modulator_name": "HNO3",
        "modulator_volume_ml": 0.05,
        "modulator_concentration": 4.44,
        "metal_name": "CuSO₄·5H₂O",
        "volumetric_wc": 40.0,
        "gravimetric_wc": 5.5,
        "product_mass_mg": 9.12,
        "energy_scale_factor": 1.0
    }
    
    result = calculate_energy(**fatqid_params)
    
    print("=== FATQID RESULTS WITH CORRECT SMILES ===")
    print(f"CP Linker: {result.get('cp_value', 0):.2f} J/(mol·K) (target: 364.47)")
    print(f"Solvent: {result.get('e_sensible_solvent_j', 0):.2f} J (target: 229.74)")
    print(f"Additive: {result.get('e_sensible_additive_j', 0):.2f} J (target: 0.00)")
    print(f"Modulator: {result.get('e_sensible_modulator_j', 0):.2f} J (target: 0.25)")
    print(f"Metal: {result.get('e_sensible_metal_j', 0):.2f} J (target: 0.18)")
    print(f"Linker: {result.get('e_sensible_linker_j', 0):.2f} J (target: 0.33)")
    print(f"Total: {result.get('e_sensible_total_j', 0):.2f} J (target: 230.50)")
    print()
    
    # Check ratios
    cp_actual = result.get("cp_value", 0)
    if cp_actual > 0:
        cp_ratio = cp_actual / 364.47
        print(f"CP Ratio: {cp_ratio:.3f} (1.000 = perfect match)")
        
    total_actual = result.get("e_sensible_total_j", 0)
    total_ratio = total_actual / 230.50
    print(f"Total Energy Ratio: {total_ratio:.3f} (1.000 = perfect match)")
    
    # Status
    if 0.95 <= cp_ratio <= 1.05:
        print("✅ CP LINKER: MATCH!")
    else:
        print("❌ CP LINKER: MISMATCH")
        
    if 0.95 <= total_ratio <= 1.05:
        print("✅ TOTAL ENERGY: MATCH!")
    else:
        print("❌ TOTAL ENERGY: MISMATCH")

if __name__ == "__main__":
    test_fatqid_correct_smiles()