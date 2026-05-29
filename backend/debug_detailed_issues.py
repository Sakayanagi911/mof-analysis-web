#!/usr/bin/env python3
"""
Debug detailed issues dari verification results
"""

from services.cost_analysis import calculate_energy
from services.joback import calculate_cp_joback

def debug_cp_linker_issue():
    """Debug kenapa CP Linker selalu rendah"""
    
    print("=== DEBUG CP LINKER ISSUE ===")
    
    # Test SMILES untuk setiap use case
    smiles_list = [
        ("FATQID", "O=C(O)c1ccc(cc1)C(=O)O"),
        ("NAWXER", "O=C(O)c1cc(C(=O)O)cc(c1)C(=O)O"),
        ("HUNCIE", "O=C(O)c1ccc2cc(C(=O)O)ccc2c1"),
        ("YAVWUQ", "O=C(O)c1cc(cc(c1)C(=O)O)C(=O)O"),
        ("YUGLES", "O=C(O)c1cc(C(=O)O)cc(c1)C(=O)O")
    ]
    
    for name, smiles in smiles_list:
        try:
            cp_result = calculate_cp_joback(smiles)
            print(f"{name:8}: SMILES={smiles}")
            print(f"         CP calculated = {cp_result:.2f} J/(mol·K)")
            print(f"         Target = {364.47 if name == 'FATQID' else 586.17} J/(mol·K)")
            print()
        except Exception as e:
            print(f"{name:8}: ERROR - {e}")
            print()

def debug_modulator_concentration():
    """Debug modulator concentration calculations"""
    
    print("=== DEBUG MODULATOR CONCENTRATION ===")
    
    test_cases = [
        ("HNO3 4.44%", "HNO3", 0.05, 4.44),
        ("HNO3 11.98%", "HNO3", 0.15, 11.98),
        ("HNO3 0.65%", "HNO3", 0.03, 0.65),
        ("HCl 6.0%", "HCl", 0.020, 6.0),
        ("HNO3 4.44% (YUGLES)", "HNO3", 0.15, 4.44)
    ]
    
    base_params = {
        "smiles": "O=C(O)c1ccc(cc1)C(=O)O",
        "temperature_c": 85.0,
        "reaction_time_h": 24.0,
        "linker_mass_mg": 5.0,
        "metal_mass_mg": 8.0,
        "solvent_name": "DMF",
        "solvent_volume_ml": 2.0,
        "additive_name": "-",
        "additive_volume_ml": 0.0,
        "metal_name": "CuSO₄·5H₂O",
        "volumetric_wc": 40.0,
        "gravimetric_wc": 5.5,
        "product_mass_mg": 9.12,
        "energy_scale_factor": 1.0
    }
    
    for name, mod_name, mod_vol, mod_conc in test_cases:
        params = base_params.copy()
        params.update({
            "modulator_name": mod_name,
            "modulator_volume_ml": mod_vol,
            "modulator_concentration": mod_conc
        })
        
        result = calculate_energy(**params)
        e_mod = result.get("e_sensible_modulator_j", 0.0)
        
        print(f"{name:20}: {e_mod:.4f} J")
        
        # Manual calculation check
        from rdkit import Chem
        from rdkit.Chem import Descriptors
        
        # Get modulator properties
        if mod_name == "HNO3":
            rho, cp_mol_k, mr = 1.190, 29.12, 63.01  # HNO3 properties
        elif mod_name == "HCl":
            rho, cp_mol_k, mr = 1.190, 29.12, 36.46  # HCl properties
        else:
            rho, cp_mol_k, mr = 1.0, 75.0, 100.0
        
        if mod_vol > 0:
            mass_g = mod_vol * rho * (mod_conc / 100.0)
            moles = mass_g / mr * 1000  # Convert to mol
            delta_t = 85.0 - 25.0  # Temperature difference
            e_manual = moles * cp_mol_k * delta_t
            
            print(f"                     Manual calc: {e_manual:.4f} J (mass={mass_g:.6f}g, moles={moles:.6f})")
        print()

def debug_solvent_volume_issue():
    """Debug kenapa Use Case 3&4 solvent energy tinggi, Use Case 5 rendah"""
    
    print("=== DEBUG SOLVENT VOLUME ISSUE ===")
    
    test_cases = [
        ("DMF 1mL (UC2)", "DMF", 1.0, 114.87),
        ("DMF 1mL (UC3)", "DMF", 1.0, 86.15),
        ("DMF 1mL (UC4)", "DMF", 1.0, 86.15),
        ("DMA 1mL (UC5)", "DMA", 1.0, 172.43)
    ]
    
    base_params = {
        "smiles": "O=C(O)c1cc(C(=O)O)cc(c1)C(=O)O",
        "temperature_c": 85.0,
        "reaction_time_h": 24.0,
        "linker_mass_mg": 4.0,
        "metal_mass_mg": 10.0,
        "additive_name": "-",
        "additive_volume_ml": 0.0,
        "modulator_name": "HNO3",
        "modulator_volume_ml": 0.15,
        "modulator_concentration": 11.98,
        "metal_name": "Zn(NO₃)₂·6H₂O",
        "volumetric_wc": 40.0,
        "gravimetric_wc": 5.5,
        "product_mass_mg": 3.785,
        "energy_scale_factor": 1.0
    }
    
    for name, solv_name, solv_vol, target in test_cases:
        params = base_params.copy()
        params.update({
            "solvent_name": solv_name,
            "solvent_volume_ml": solv_vol
        })
        
        result = calculate_energy(**params)
        e_solv = result.get("e_sensible_solvent_j", 0.0)
        ratio = e_solv / target if target > 0 else 0
        
        print(f"{name:15}: {e_solv:.2f} J vs {target:.2f} J (ratio: {ratio:.3f})")

if __name__ == "__main__":
    debug_cp_linker_issue()
    debug_modulator_concentration()
    debug_solvent_volume_issue()