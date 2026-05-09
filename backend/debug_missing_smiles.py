#!/usr/bin/env python3
"""
Debug missing SMILES dan price issues
"""

from services.cost_analysis import get_smiles_mapping, get_uptake_data

def debug_missing_smiles():
    """
    Check which SMILES are missing from database
    """
    
    # SMILES from use cases
    use_case_smiles = {
        "Use Case 1 (H₂L)": "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
        "Use Case 2 (H4TCPP)": "C(=O)(O)C=1C=C2C=CC(=CC2=CC1)N(C1=CC=C(C=C1)C=1C=C(C=C(C1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C=1C=C(C=C(C1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O",
        "Use Case 3 (H₂thb)": "S1C(=CC=C1C(=O)O)C(=O)O",
        "Use Case 4 (H₄L formate)": "C(=O)O",
        "Use Case 5 (H₄EBTC)": "C(#CC#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O"
    }
    
    print("=== CHECKING SMILES IN DATABASE ===")
    
    smiles_mapping = get_smiles_mapping()
    uptake_data = get_uptake_data()
    
    print(f"Total SMILES in mapping: {len(smiles_mapping)}")
    print(f"Total SMILES in uptake: {len(uptake_data)}")
    print()
    
    for case_name, smiles in use_case_smiles.items():
        print(f"=== {case_name} ===")
        print(f"SMILES: {smiles}")
        
        # Check in smiles_mapping
        if smiles in smiles_mapping:
            linker_data = smiles_mapping[smiles]
            print(f"✅ Found in smiles_mapping:")
            print(f"   Linker Name: {linker_data.get('linker_name')}")
            print(f"   Price: {linker_data.get('price_eur_per_g')} EUR/g")
        else:
            print(f"❌ NOT found in smiles_mapping")
        
        # Check in uptake_data
        if smiles in uptake_data:
            uptake_info = uptake_data[smiles]
            print(f"✅ Found in uptake_data:")
            print(f"   Gravimetric WC: {uptake_info.get('gravimetric_wc_percent')}%")
            print(f"   Volumetric WC: {uptake_info.get('volumetric_wc_g_per_l')} g/L")
        else:
            print(f"❌ NOT found in uptake_data")
        
        print()
    
    # Show some examples from database
    print("=== EXAMPLES FROM DATABASE ===")
    count = 0
    for smiles, data in smiles_mapping.items():
        if count >= 3:
            break
        print(f"SMILES: {smiles[:60]}...")
        print(f"  Linker: {data.get('linker_name')}")
        print(f"  Price: {data.get('price_eur_per_g')} EUR/g")
        print()
        count += 1

if __name__ == "__main__":
    debug_missing_smiles()