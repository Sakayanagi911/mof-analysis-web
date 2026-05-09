#!/usr/bin/env python3
"""
Script untuk mencari case-case spesifik yang sesuai dengan parameter sintesis user
"""

import pandas as pd
from services.cost_analysis import run_economic_analysis

def find_matching_synthesis_cases():
    """
    Mencari case-case berdasarkan parameter sintesis yang sesuai dengan use case user
    """
    
    # Load Excel file
    excel_path = "old_model/Synthesis_Parameter_3.xlsx"
    
    try:
        # Read all sheets
        syn1 = pd.read_excel(excel_path, sheet_name=0).fillna(0)
        print(f"Loaded {len(syn1)} rows from Excel")
        
        # User's expected cases dengan parameter sintesis
        user_cases = [
            {
                "name": "Use Case 1",
                "params": {
                    "solvent": "DMF", "solvent_vol": 2.0,
                    "modulator": "HNO3", "modulator_vol": 0.05,
                    "metal": "CuSO₄·5H₂O", "metal_mass": 8.0,
                    "linker_mass": 5.0, "product_mass": 9.12,
                    "temp": 85.0, "time": 24.0
                },
                "expected": {"mof_cost": 1.7914, "storage_cost": 24.6217}
            },
            {
                "name": "Use Case 2", 
                "params": {
                    "solvent": "DMF", "solvent_vol": 1.0,
                    "additive": "EtOH", "additive_vol": 0.5,
                    "modulator": "HNO3", "modulator_vol": 0.15,
                    "metal": "Zn(NO₃)₂·6H₂O", "metal_mass": 10.0,
                    "linker_mass": 4.0, "product_mass": 3.785,
                    "temp": 85.0, "time": 24.0
                },
                "expected": {"mof_cost": 5.0682, "storage_cost": 76.6513}
            },
            {
                "name": "Use Case 3",
                "params": {
                    "solvent": "DMF", "solvent_vol": 4.0,
                    "additive": "MeCN", "additive_vol": 1.0,
                    "metal": "Zn(NO₃)₂·6H₂O", "metal_mass": 119.0,
                    "linker_mass": 52.0, "product_mass": 52.3,
                    "temp": 120.0, "time": 48.0
                },
                "expected": {"mof_cost": 0.1056, "storage_cost": 1.771}
            },
            {
                "name": "Use Case 4",
                "params": {
                    "solvent": "DMF", "solvent_vol": 1.5,
                    "modulator": "HCl", "modulator_vol": 19.0,
                    "metal": "Cu(NO₃)₂·2.5H₂O", "metal_mass": 15.0,
                    "linker_mass": 5.0, "product_mass": 17.13,
                    "temp": 70.0, "time": 96.0
                },
                "expected": {"mof_cost": 0.0413, "storage_cost": 0.7236}
            },
            {
                "name": "Use Case 5",
                "params": {
                    "solvent": "DMF", "solvent_vol": 0.2,
                    "additive": "DMSO", "additive_vol": 0.2,
                    "modulator": "HNO3", "modulator_vol": 0.06,
                    "metal": "Cu(NO₃)₂·3H₂O", "metal_mass": 15.0,
                    "linker_mass": 5.0, "product_mass": 6.3,
                    "temp": 65.0, "time": 24.0
                },
                "expected": {"mof_cost": 6.6163, "storage_cost": 110.3287}
            }
        ]
        
        print("\n=== MENCARI CASE BERDASARKAN PARAMETER SINTESIS ===")
        
        for case in user_cases:
            print(f"\n=== {case['name']} ===")
            params = case['params']
            
            # Create filter conditions
            conditions = []
            
            # Temperature (±5°C tolerance)
            if 'temp' in params:
                temp_condition = (
                    (syn1['Temperature (oC)'] >= params['temp'] - 5) & 
                    (syn1['Temperature (oC)'] <= params['temp'] + 5)
                )
                conditions.append(temp_condition)
                print(f"Looking for Temperature: {params['temp']}°C (±5°C)")
            
            # Time (±10h tolerance)
            if 'time' in params:
                time_condition = (
                    (syn1['Time (h)'] >= params['time'] - 10) & 
                    (syn1['Time (h)'] <= params['time'] + 10)
                )
                conditions.append(time_condition)
                print(f"Looking for Time: {params['time']}h (±10h)")
            
            # Solvent
            if 'solvent' in params:
                solvent_condition = syn1['Solvent_Name'].str.contains(params['solvent'], case=False, na=False)
                conditions.append(solvent_condition)
                print(f"Looking for Solvent: {params['solvent']}")
            
            # Metal (partial match)
            if 'metal' in params:
                metal_name = params['metal']
                # Try different variations
                metal_variations = [
                    metal_name,
                    metal_name.replace('₄', '4').replace('₃', '3').replace('₂', '2'),
                    metal_name.replace('·', '.').replace('₄', '4').replace('₃', '3').replace('₂', '2')
                ]
                
                metal_condition = False
                for variation in metal_variations:
                    metal_condition = metal_condition | syn1['Metal_Name'].str.contains(variation, case=False, na=False)
                
                conditions.append(metal_condition)
                print(f"Looking for Metal: {params['metal']}")
            
            # Apply all conditions
            if conditions:
                final_condition = conditions[0]
                for condition in conditions[1:]:
                    final_condition = final_condition & condition
                
                matching_rows = syn1[final_condition]
                
                if len(matching_rows) > 0:
                    print(f"Found {len(matching_rows)} potentially matching rows:")
                    
                    for idx, row in matching_rows.head(3).iterrows():  # Show top 3 matches
                        print(f"\n  Row {idx} - {row['MOF_Name']}:")
                        print(f"    Temperature: {row['Temperature (oC)']}°C")
                        print(f"    Time: {row['Time (h)']}h")
                        print(f"    Product: {row['Product (mg)']}mg")
                        print(f"    Metal: {row['Metal_Name']} - {row['Metal_Mass (mg)']}mg")
                        print(f"    Solvent: {row['Solvent_Name']} - {row['Solvent_Volume (mL)']}mL")
                        
                        if row['Additive_Name'] and row['Additive_Name'] != '0':
                            print(f"    Additive: {row['Additive_Name']} - {row['Additive_Volume (mL)']}mL")
                        
                        if row['Modulator_Name'] and row['Modulator_Name'] != '0':
                            print(f"    Modulator: {row['Modulator_Name']} - {row['Modulator_Volume (mL)']}mL")
                        
                        print(f"    SMILES: {row['SMILES1']}")
                        print(f"    Gravimetric WC: {row['Uptake Grav - Working Cap [%wt]']}%")
                        
                        # Test calculation with this data
                        try:
                            result = run_economic_analysis(
                                metal_name=row['Metal_Name'],
                                linker_smiles=row['SMILES1'],
                                reaction_time=row['Time (h)'],
                                temperature=row['Temperature (oC)'],
                                smiles=row['SMILES1'],
                                product_mass_mg=row['Product (mg)'],
                                metal_mass_mg=row['Metal_Mass (mg)'],
                                linker_mass_mg=row['Linker1_Mass (mg)'],
                                solvent_name=row['Solvent_Name'],
                                solvent_volume_ml=row['Solvent_Volume (mL)'],
                                additive_name=row['Additive_Name'] if row['Additive_Name'] != '0' else '-',
                                additive_volume_ml=row['Additive_Volume (mL)'] if row['Additive_Name'] != '0' else 0.0,
                                modulator_name=row['Modulator_Name'] if row['Modulator_Name'] != '0' else '-',
                                modulator_volume_ml=row['Modulator_Volume (mL)'] if row['Modulator_Name'] != '0' else 0.0
                            )
                            
                            actual_mof = result['mof_cost_usd_per_kg']
                            actual_storage = result['storage_cost_usd_per_kg_h2']
                            expected_mof = case['expected']['mof_cost']
                            expected_storage = case['expected']['storage_cost']
                            
                            print(f"    CALCULATION RESULT:")
                            print(f"      Expected MOF Cost: {expected_mof}")
                            print(f"      Actual MOF Cost:   {actual_mof:.4f}")
                            print(f"      Difference:        {abs(actual_mof - expected_mof):.4f}")
                            print(f"      Expected Storage:  {expected_storage}")
                            print(f"      Actual Storage:    {actual_storage:.4f}")
                            print(f"      Difference:        {abs(actual_storage - expected_storage):.4f}")
                            
                        except Exception as e:
                            print(f"    CALCULATION ERROR: {e}")
                
                else:
                    print("No matching rows found")
            else:
                print("No search conditions specified")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    find_matching_synthesis_cases()