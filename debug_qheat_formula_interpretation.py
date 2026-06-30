#!/usr/bin/env python3
"""
Debug Qheat Formula Interpretation
Analisis formula teman untuk menemukan interpretasi yang benar
"""

def debug_formula_interpretation():
    print("=== DEBUG QHEAT FORMULA INTERPRETATION ===\n")
    
    # FATQID data
    total_sensible_j = 230.50
    heat_eff = 0.75
    product_mg = 9.12
    uptake_vol = 43.38  # g/L
    uptake_grav = 13.11  # %
    expected_qheat = 0.53810  # MJ
    teman_result = 1.85  # MJ yang teman dapat
    
    print("📋 ANALYSIS OF FORMULA COMPONENTS:")
    print(f"Formula: Qheat = total sensible energy / (heat eff × Vreactor)")
    print(f"Vreactor = 1.2 × (product/1000) / (uptake vol / (uptake grav × 100))")
    print()
    
    # === INTERPRETASI 1: Uptake density calculation ===
    print("🔍 INTERPRETATION 1: Uptake Density Calculation")
    
    # Formula asli dari physics: Density = volumetric_wc / (gravimetric_wc / 100)
    # Tapi formula teman: uptake vol / (uptake grav × 100)
    
    density_physics = uptake_vol / (uptake_grav / 100.0)  # Standard MOF density
    density_teman = uptake_vol / (uptake_grav * 100.0)   # Teman's formula
    
    print(f"Standard MOF density: {uptake_vol} / ({uptake_grav} / 100) = {density_physics:.2f} g/L")
    print(f"Teman's formula: {uptake_vol} / ({uptake_grav} × 100) = {density_teman:.6f} g/L")
    print()
    
    # === INTERPRETASI 2: Vreactor calculation ===
    print("🔍 INTERPRETATION 2: Vreactor Calculation")
    
    product_g = product_mg / 1000.0
    
    # Standard: V_MOF = mass / density, V_reactor = 1.2 × V_MOF
    v_mof_standard = product_g / density_physics
    v_reactor_standard = 1.2 * v_mof_standard
    
    # Teman's formula: V_reactor = 1.2 × product_g / density_teman  
    v_reactor_teman = 1.2 * product_g / density_teman
    
    print(f"Standard calculation:")
    print(f"   V_MOF = {product_g:.6f} / {density_physics:.2f} = {v_mof_standard:.9f} L")
    print(f"   V_reactor = 1.2 × {v_mof_standard:.9f} = {v_reactor_standard:.9f} L")
    print()
    
    print(f"Teman's calculation:")
    print(f"   V_reactor = 1.2 × {product_g:.6f} / {density_teman:.6f} = {v_reactor_teman:.6f} L")
    print()
    
    # === INTERPRETASI 3: Qheat calculation ===
    print("🔍 INTERPRETATION 3: Qheat Calculation")
    
    # Different unit interpretations
    qheat_standard = total_sensible_j / (heat_eff * v_reactor_standard) / 1e6  # Convert to MJ
    qheat_teman_v = total_sensible_j / (heat_eff * v_reactor_teman) / 1e6  # Convert to MJ
    
    # Maybe different unit in formula?
    qheat_j_per_l = total_sensible_j / (heat_eff * v_reactor_teman)  # J/L
    qheat_mj_per_1000l = qheat_j_per_l * 1000 / 1e6  # MJ/1000L
    
    print(f"Different Qheat interpretations:")
    print(f"   Standard: {total_sensible_j} / ({heat_eff} × {v_reactor_standard:.9f}) / 1e6 = {qheat_standard:.5f} MJ")
    print(f"   Teman V_reactor: {total_sensible_j} / ({heat_eff} × {v_reactor_teman:.6f}) / 1e6 = {qheat_teman_v:.5f} MJ")
    print(f"   As J/L then MJ/1000L: {qheat_j_per_l:.2f} J/L → {qheat_mj_per_1000l:.5f} MJ/1000L")
    print()
    
    # === MENCARI YANG MENDEKATI 1.85 ===
    print("🎯 FINDING MATCH FOR TEMAN'S 1.85 MJ:")
    
    results = [
        ("Standard calculation", qheat_standard),
        ("Teman V_reactor", qheat_teman_v),
        ("MJ/1000L interpretation", qheat_mj_per_1000l)
    ]
    
    for name, result in results:
        error_vs_expected = abs(result - expected_qheat) / expected_qheat * 100
        error_vs_teman = abs(result - teman_result) / teman_result * 100
        
        print(f"{name}:")
        print(f"   Result: {result:.5f} MJ")
        print(f"   Error vs expected (0.538): {error_vs_expected:.1f}%")
        print(f"   Error vs teman (1.85): {error_vs_teman:.1f}%")
        
        if error_vs_teman < 10:
            print("   ✅ MATCHES TEMAN'S CALCULATION!")
        elif error_vs_expected < 10:
            print("   ✅ MATCHES EXPECTED VALUE!")
        else:
            print("   ❌ No close match")
        print()
    
    # === ALTERNATIVE: Maybe different total sensible energy? ===
    print("🔍 ALTERNATIVE: Different Total Sensible Energy?")
    
    # What total sensible energy would give 1.85 with expected formula?
    required_e_sens_for_185 = teman_result * heat_eff * v_reactor_standard * 1e6
    required_e_sens_for_538 = expected_qheat * heat_eff * v_reactor_standard * 1e6
    
    print(f"Required E_sens for 1.85 MJ: {required_e_sens_for_185:.0f} J")
    print(f"Required E_sens for 0.538 MJ: {required_e_sens_for_538:.0f} J") 
    print(f"Our calculated E_sens: {total_sensible_j:.1f} J")
    print()
    
    ratio_185 = required_e_sens_for_185 / total_sensible_j
    ratio_538 = required_e_sens_for_538 / total_sensible_j
    
    print(f"E_sens ratio for 1.85: {ratio_185:.2f}x")
    print(f"E_sens ratio for 0.538: {ratio_538:.2f}x")
    print()
    
    # === RECOMMENDATION ===
    print("🎯 RECOMMENDATION:")
    print("Teman bilang 'kayaknya ada yang salah' - kemungkinan:")
    print("1. Ada perbedaan interpretasi formula Vreactor")
    print("2. Ada perbedaan dalam total sensible energy calculation") 
    print("3. Ada missing conversion factor")
    print()
    print("💡 SUGGESTED ACTION:")
    print("Implementasi formula teman persis seperti yang diberikan,")
    print("tapi adjustable untuk handle different interpretations.")
    print("Biar bisa switch between:")
    print("- Standard physics calculation (untuk accuracy)")
    print("- Teman's exact formula (untuk consistency dengan model asli)")

if __name__ == "__main__":
    debug_formula_interpretation()