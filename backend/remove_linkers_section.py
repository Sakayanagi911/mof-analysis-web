#!/usr/bin/env python3
"""
Script untuk menghapus bagian 'linkers' dari price_database.json
karena semua data linker sudah ada di smiles_mapping
"""

import json
import os

def remove_linkers_section():
    file_path = os.path.join("data", "price_database.json")
    
    # Load database
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Check current structure
    print("Current sections:")
    for key in data.keys():
        if key == "linkers":
            print(f"  - {key}: {len(data[key])} entries (WILL BE REMOVED)")
        elif key == "smiles_mapping":
            print(f"  - {key}: {len(data[key].get('mapping', {}))} entries (KEEP)")
        else:
            print(f"  - {key}: {type(data[key])}")
    
    # Remove linkers section
    if "linkers" in data:
        linkers_count = len(data["linkers"])
        del data["linkers"]
        print(f"\n✅ Removed 'linkers' section with {linkers_count} entries")
    else:
        print("\n⚠️ 'linkers' section not found")
    
    # Verify smiles_mapping exists
    if "smiles_mapping" in data and "mapping" in data["smiles_mapping"]:
        smiles_count = len(data["smiles_mapping"]["mapping"])
        print(f"✅ 'smiles_mapping' section exists with {smiles_count} entries")
    else:
        print("❌ 'smiles_mapping' section missing!")
        return
    
    # Save updated database
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Database updated successfully!")
    print(f"File: {file_path}")
    
    # Show final structure
    print("\nFinal sections:")
    for key in data.keys():
        if key == "smiles_mapping":
            print(f"  - {key}: {len(data[key].get('mapping', {}))} entries")
        else:
            print(f"  - {key}: {type(data[key])}")

if __name__ == "__main__":
    remove_linkers_section()