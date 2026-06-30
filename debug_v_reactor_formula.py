#!/usr/bin/env python3
"""
Debug V_Reactor Formula Issue
V_Reactor terlalu kecil, menghasilkan Qheat yang sangat besar

Problem:
- V_MOF = 0.000028 L (28 μL) → V_Reactor = 0.000033 L (33 μL)
- Qheat = E_sens / (heat_eff × V_reactor × 1000) = 9292 MJ (impossible!)

Expected Qheat ~0.5 MJ, jadi ada masalah dengan formula atau interpretasi V_Reactor.
"""

def debug_v_reactor_formula():
    print("=== DEBUG V_REACTOR FORMULA ISSUE ===\n")
    
    # FATQID data
    product_mass_mg = 9.12
    gravimetric_wc = 13.11  # %
    volumetric_wc = 43.38   # g/L
    e_sens_total = 230.50   # J
    heat_eff = 0.75
    expected_qheat = 0.53810  # MJ
    
    print("📋 FATQID CURRENT CALCULATION:")
    
    # Current calculation
    density_mof = volumetric_wc / (gravimetric_wc / 100.0)
    g_mof = product_mass_mg / 1000.0
    v_mof_l = g_mof / density_mof
    v_reactor_l = 1.2 * v_mof_l
    
    print(f"Product mass: {product_mass_mg} mg = {g_mof:.6f} g")
    print(f"Gravimetric WC: {gravimetric_wc}%")
    print(f"Volumetric WC: {volumetric_wc} g/L")
    print(f"MOF density: {density_mof:.2f} g/L")
    print(f"V_MOF: {v_mof_l:.9f} L = {v_mof_l*1e6:.2f} μL")
    print(f"V_Reactor: {v_reactor_l:.9f} L = {v_reactor_l*1e6:.2f} μL")
    print()
    
    # Current Qheat
    qheat_current = e_sens_total / (heat_eff * v_reactor_l * 1000.0)
    print(f"Current Qheat: {e_sens_total:.2f} / ({heat_eff} × {v_reactor_l:.9f} × 1000) = {qheat_current:.2f} MJ")
    print(f"Expected Qheat: {expected_qheat:.5f} MJ")
    print(f"Error: {(qheat_current/expected_qheat-1)*100:.0f}% too high!")
    print()
    
    # === ANALYSIS: What V_Reactor should be? ===
    print("🔍 REVERSE ENGINEERING REQUIRED V_REACTOR:")
    
    # If Qheat = E_sens / (heat_eff × V_reactor × 1000), then:
    # V_reactor = E_sens / (heat_eff × Qheat × 1000)
    required_v_reactor = e_sens_total / (heat_eff * expected_qheat * 1000.0)
    print(f"Required V_reactor: {e_sens_total:.2f} / ({heat_eff} × {expected_qheat:.5f} × 1000) = {required_v_reactor:.6f} L")
    
    # What scale factor would fix this?
    scale_factor = required_v_reactor / v_reactor_l
    print(f"Scale factor needed: {required_v_reactor:.6f} / {v_reactor_l:.9f} = {scale_factor:.0f}x")
    print()
    
    # === HYPOTHESIS TESTING ===
    print("💡 POSSIBLE ISSUES:")
    
    print("1. Unit confusion in formula:")
    print(f"   Maybe Qheat formula should be: E_sens / (heat_eff × V_reactor) without ×1000?")
    qheat_no_1000 = e_sens_total / (heat_eff * v_reactor_l)
    print(f"   Qheat = {e_sens_total:.2f} / ({heat_eff} × {v_reactor_l:.9f}) = {qheat_no_1000:.2f} J = {qheat_no_1000/1e6:.5f} MJ")
    print()
    
    print("2. V_Reactor might be in different units:")
    print(f"   If V_Reactor should be in mL: {v_reactor_l*1000:.6f} mL")
    qheat_ml = e_sens_total / (heat_eff * (v_reactor_l*1000) * 1000.0)
    print(f"   Qheat = {e_sens_total:.2f} / ({heat_eff} × {v_reactor_l*1000:.6f} × 1000) = {qheat_ml:.5f} MJ")
    print()
    
    print("3. Maybe the formula interpretation is wrong:")
    print(f"   Original formula might be different from what we think")
    print(f"   Need to check the exact formula from synthesis parameter file")
    print()
    
    # === CHECK LIQUID VOLUME VS MOF VOLUME ===
    print("📊 VOLUME COMPARISON:")
    v_liquid_ml = 2.0 + 0.05  # DMF + HNO3
    v_liquid_l = v_liquid_ml / 1000.0
    
    print(f"Liquid volume: {v_liquid_ml} mL = {v_liquid_l:.6f} L")
    print(f"MOF volume: {v_mof_l*1000:.6f} mL = {v_mof_l:.9f} L")
    print(f"Reactor volume: {v_reactor_l*1000:.6f} mL = {v_reactor_l:.9f} L")
    print()
    print(f"Liquid volume is {v_liquid_l/v_reactor_l:.0f}x larger than reactor volume!")
    print(f"This suggests V_Reactor calculation might be wrong.")
    print()
    
    # === WHAT IF WE USE LIQUID VOLUME AS REACTOR VOLUME? ===
    print("🧪 HYPOTHESIS: V_Reactor should be based on liquid volume, not MOF volume")
    qheat_liquid = e_sens_total / (heat_eff * v_liquid_l * 1000.0)
    print(f"If V_Reactor = V_Liquid = {v_liquid_l:.6f} L:")
    print(f"Qheat = {e_sens_total:.2f} / ({heat_eff} × {v_liquid_l:.6f} × 1000) = {qheat_liquid:.5f} MJ")
    print(f"Error vs expected: {abs(qheat_liquid-expected_qheat)/expected_qheat*100:.1f}%")
    
    if abs(qheat_liquid - expected_qheat) / expected_qheat < 0.1:
        print("🎯 BINGO! V_Reactor should probably be based on liquid volume!")
    
    print()
    print("🎯 RECOMMENDATION:")
    print("Check the original synthesis parameter file to see:")
    print("1. Exact V_Reactor formula")
    print("2. Whether V_Reactor is based on V_MOF or V_Liquid")
    print("3. Units used in the calculation")

if __name__ == "__main__":
    debug_v_reactor_formula()