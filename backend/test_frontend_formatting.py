#!/usr/bin/env python3
"""
Test frontend formatting dengan 3 decimal places
"""

from services.cost_analysis import run_economic_analysis

def test_frontend_formatting():
    """
    Test output untuk memastikan frontend akan menampilkan 3 decimal places
    """
    
    print("=== TEST FRONTEND FORMATTING (3 DECIMAL PLACES) ===")
    
    # Use Case 1 parameters
    result = run_economic_analysis(
        metal_name="CuSO₄·5H₂O",
        linker_smiles="C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
        reaction_time=24.0,
        temperature=85.0,
        smiles="C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O",
        product_mass_mg=9.12,
        metal_mass_mg=8.0,
        linker_mass_mg=5.0,
        solvent_name="DMF",
        solvent_volume_ml=2.0,
        additive_name="-",
        additive_volume_ml=0.0,
        modulator_name="HNO3",
        modulator_volume_ml=0.05
    )
    
    print("=== BACKEND OUTPUT (FULL PRECISION) ===")
    print(f"MOF Cost: {result['mof_cost_usd_per_kg']} USD/kg")
    print(f"Storage Cost: {result['storage_cost_usd_per_kg_h2']} USD/kg H2")
    print(f"Q Heat: {result['q_energy_mj']} MJ")
    print(f"Q Loss: {result['q_loss_mj']} MJ")
    print(f"E Stirr: {result['e_stirr_mj']} MJ")
    print(f"E Total: {result['e_total_mj']} MJ")
    print()
    
    print("=== FRONTEND DISPLAY (3 DECIMAL PLACES) ===")
    # Simulate frontend formatting
    mof_cost_display = f"{result['mof_cost_usd_per_kg']:.3f}"
    storage_cost_display = f"{result['storage_cost_usd_per_kg_h2']:.3f}"
    q_heat_display = f"{result['q_energy_mj']:.3f}"
    q_loss_display = f"{result['q_loss_mj']:.3f}"
    e_stirr_display = f"{result['e_stirr_mj']:.3f}"
    e_total_display = f"{result['e_total_mj']:.3f}"
    
    print(f"MOF Cost: {mof_cost_display} USD/kg")
    print(f"Storage Cost: {storage_cost_display} USD/kg H2")
    print(f"Q Heat: {q_heat_display} MJ")
    print(f"Q Loss: {q_loss_display} MJ")
    print(f"E Stirr: {e_stirr_display} MJ")
    print(f"E Total: {e_total_display} MJ")
    print()
    
    print("=== VERIFICATION ===")
    # Check that all displays have exactly 3 decimal places
    displays = [mof_cost_display, storage_cost_display, q_heat_display, 
                q_loss_display, e_stirr_display, e_total_display]
    
    all_correct = True
    for i, display in enumerate(displays):
        if '.' in display:
            decimal_places = len(display.split('.')[1])
            if decimal_places == 3:
                print(f"✅ Display {i+1}: {decimal_places} decimal places")
            else:
                print(f"❌ Display {i+1}: {decimal_places} decimal places (should be 3)")
                all_correct = False
        else:
            print(f"❌ Display {i+1}: No decimal point")
            all_correct = False
    
    if all_correct:
        print("\n✅ All displays have exactly 3 decimal places")
        print("Frontend will show consistent formatting!")
    else:
        print("\n❌ Some displays don't have 3 decimal places")
    
    print("\n=== SAMPLE UI DISPLAY ===")
    print("┌─────────────────────────────────────┐")
    print("│ MOF Production Cost                 │")
    print(f"│ {mof_cost_display:<15} USD/kg          │")
    print("├─────────────────────────────────────┤")
    print("│ Hydrogen Storage Cost               │")
    print(f"│ {storage_cost_display:<15} USD/kg H2       │")
    print("└─────────────────────────────────────┘")
    print()
    print("Energy Metrics:")
    print(f"Q Heat: {q_heat_display} MJ    Q Loss: {q_loss_display} MJ")
    print(f"E Stirr: {e_stirr_display} MJ   E Total: {e_total_display} MJ")

if __name__ == "__main__":
    test_frontend_formatting()