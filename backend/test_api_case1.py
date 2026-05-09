#!/usr/bin/env python3
"""
Test API endpoint dengan Use Case 1 untuk memastikan gravimetric WC dari database
"""

import requests
import json

def test_api_case1():
    """
    Test API /analyze dengan Use Case 1
    """
    
    # API endpoint
    url = "http://127.0.0.1:8000/analyze"
    
    # Use Case 1 data
    data = {
        "pv": "1.2",
        "gsa": "3000", 
        "vsa": "1500",
        "lcd": "12.1", 
        "pld": "8", 
        "vf": "0.5",
        "density": "0.8",
        "metal_name": "CuSO₄·5H₂O",
        "metal_mass": "8",
        "linker_name": "H₂L",
        "linker_mass": "5",
        "smiles": "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
        "solvent_name": "DMF",
        "solvent_volume": "2",
        "additive_name": "-",
        "additive_volume": "0",
        "modulator_name": "HNO3",
        "modulator_volume": "0.05",
        "product_mass": "9.12",
        "reaction_time": "24",
        "temperature": "85"
    }
    
    print("=== TESTING API ENDPOINT /analyze ===")
    print("Use Case 1 Data:")
    for key, value in data.items():
        print(f"  {key}: {value}")
    print()
    
    try:
        # Make API request
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("=== API RESPONSE ===")
            print(f"Status: {result.get('status')}")
            
            if result.get('status') == 'success':
                results = result.get('results', {})
                
                print("\n=== COST RESULTS ===")
                print(f"MOF Cost: {results.get('mof_cost')} USD/kg")
                print(f"Storage Cost: {results.get('storage_cost')} USD/kg H2")
                
                print("\n=== ENERGY RESULTS ===")
                print(f"Cp Linker: {results.get('cp_linker')} J/mol.K")
                print(f"Solvent Energy: {results.get('e_sensible_solvent')} J")
                print(f"Additive Energy: {results.get('e_sensible_additive')} J")
                print(f"Modulator Energy: {results.get('e_sensible_modulator')} J")
                print(f"Metal Energy: {results.get('e_sensible_metal')} J")
                print(f"Linker Energy: {results.get('e_sensible_linker')} J")
                print(f"Total Sensible: {results.get('e_sensible_total')} J")
                
                print("\n=== HEAT METRICS ===")
                print(f"Qheat: {results.get('q_energy')} MJ")
                print(f"Qloss: {results.get('q_loss')} MJ")
                print(f"Estirr: {results.get('e_stirr')} MJ")
                print(f"E total: {results.get('e_tot')} MJ")
                
                print("\n=== WORKING CAPACITY ===")
                print(f"Gravimetric H2: {results.get('gravimetric_h2')}%")
                print(f"Volumetric H2: {results.get('volumetric_h2')} g/L")
                
                print("\n=== EXPECTED vs ACTUAL ===")
                expected_storage_cost = 24.68  # Based on database gravimetric WC
                actual_storage_cost = results.get('storage_cost', 0)
                
                print(f"Expected Storage Cost: {expected_storage_cost} USD/kg H2")
                print(f"Actual Storage Cost: {actual_storage_cost} USD/kg H2")
                
                if abs(expected_storage_cost - actual_storage_cost) < 1.0:
                    print("✅ Storage cost matches expected (using database gravimetric WC)")
                else:
                    print("❌ Storage cost doesn't match - may still be using whitebox model")
                
            else:
                print(f"❌ API Error: {result}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure backend server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_case1()