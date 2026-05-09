#!/usr/bin/env python3
"""
Menambahkan data Uptake (Gravimetric & Volumetric Working Capacity) 
dari Excel Synthesis_Parameter_3.xlsx ke database
"""

import pandas as pd
import json
from pathlib import Path

def add_uptake_to_database():
    """
    Baca data uptake dari Excel dan tambahkan ke price_database.json
    """
    
    # Path files
    excel_path = Path("old_model/Synthesis_Parameter_3.xlsx")
    db_path = Path("data/price_database.json")
    
    print("=== ADDING UPTAKE DATA TO DATABASE ===")
    
    # Load existing database
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)
    
    # Read Excel file
    print(f"Reading Excel: {excel_path}")
    
    try:
        # Read the first sheet (default worksheet)
        df = pd.read_excel(excel_path, sheet_name=0)
        print(f"Excel loaded successfully. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Find uptake columns
        uptake_grav_col = None
        uptake_vol_col = None
        
        for col in df.columns:
            if "uptake" in str(col).lower() and "grav" in str(col).lower():
                uptake_grav_col = col
                print(f"Found Gravimetric Uptake column: {col}")
            elif "uptake" in str(col).lower() and ("vol" in str(col).lower() or "volumetric" in str(col).lower()):
                uptake_vol_col = col
                print(f"Found Volumetric Uptake column: {col}")
        
        if uptake_grav_col is None:
            print("❌ Gravimetric uptake column not found!")
            print("Available columns containing 'uptake':")
            for col in df.columns:
                if "uptake" in str(col).lower():
                    print(f"  - {col}")
            return
        
        # Look for SMILES column to match with our database
        smiles_col = None
        for col in df.columns:
            if "smiles" in str(col).lower():
                smiles_col = col
                print(f"Found SMILES column: {col}")
                break
        
        if smiles_col is None:
            print("❌ SMILES column not found!")
            print("Available columns:")
            for col in df.columns:
                print(f"  - {col}")
            return
        
        # Create uptake mapping
        uptake_data = {}
        
        print(f"\n=== PROCESSING UPTAKE DATA ===")
        
        for idx, row in df.iterrows():
            smiles = row[smiles_col]
            grav_uptake = row[uptake_grav_col]
            vol_uptake = row[uptake_vol_col] if uptake_vol_col else None
            
            # Skip if SMILES is empty or NaN
            if pd.isna(smiles) or str(smiles).strip() == "":
                continue
            
            # Skip if gravimetric uptake is empty or NaN
            if pd.isna(grav_uptake):
                continue
            
            smiles_clean = str(smiles).strip()
            
            uptake_entry = {
                "gravimetric_wc_percent": float(grav_uptake),
            }
            
            if vol_uptake is not None and not pd.isna(vol_uptake):
                uptake_entry["volumetric_wc_g_per_l"] = float(vol_uptake)
            
            uptake_data[smiles_clean] = uptake_entry
            
            print(f"Row {idx+1}: SMILES={smiles_clean[:50]}... Grav={grav_uptake}% Vol={vol_uptake}")
        
        print(f"\n=== SUMMARY ===")
        print(f"Total uptake entries processed: {len(uptake_data)}")
        
        # Add to database
        db["uptake_data"] = uptake_data
        
        # Save updated database
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Database updated successfully!")
        print(f"Added uptake data for {len(uptake_data)} SMILES entries")
        
        # Show some examples
        print(f"\n=== EXAMPLES ===")
        count = 0
        for smiles, data in uptake_data.items():
            if count >= 5:
                break
            print(f"SMILES: {smiles[:60]}...")
            print(f"  Gravimetric WC: {data['gravimetric_wc_percent']}%")
            if 'volumetric_wc_g_per_l' in data:
                print(f"  Volumetric WC: {data['volumetric_wc_g_per_l']} g/L")
            print()
            count += 1
            
    except Exception as e:
        print(f"❌ Error reading Excel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_uptake_to_database()