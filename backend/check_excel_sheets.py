#!/usr/bin/env python3
"""
Check sheet names in Excel file
"""

import pandas as pd
from pathlib import Path

def check_excel_sheets():
    excel_path = Path("old_model/Synthesis_Parameter_3.xlsx")
    
    print(f"Checking sheets in: {excel_path}")
    
    try:
        # Read Excel file to get sheet names
        excel_file = pd.ExcelFile(excel_path)
        sheet_names = excel_file.sheet_names
        
        print(f"Found {len(sheet_names)} sheets:")
        for i, sheet in enumerate(sheet_names):
            print(f"  {i+1}. {sheet}")
        
        # Try to read first few rows of each sheet to understand structure
        for sheet in sheet_names:
            print(f"\n=== SHEET: {sheet} ===")
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet, nrows=5)
                print(f"Shape: {df.shape}")
                print("Columns:")
                for col in df.columns:
                    print(f"  - {col}")
                    
                # Look for uptake columns
                uptake_cols = [col for col in df.columns if "uptake" in str(col).lower()]
                if uptake_cols:
                    print(f"UPTAKE COLUMNS FOUND: {uptake_cols}")
                    
            except Exception as e:
                print(f"Error reading sheet {sheet}: {e}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_excel_sheets()