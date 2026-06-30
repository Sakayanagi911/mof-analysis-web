#!/usr/bin/env python3
"""
Test Friend's Qheat Formula
Formula: Qheat = total sensible energy / (heat eff × Vreactor)
Vreactor = 1.2 × (product/1000) / (uptake vol / (uptake grav × 100))
"""

def test_friend_formula():
    print("=== TEST FRIEND'S QHEAT FORMULA ===\n")
    
    print("📋 FORMULA DARI TEMAN:")
    print("Qheat (MJ/1000 L) = total sensible energy (J) / (heat eff × Vreactor)")
    print("Vreactor = 1.2 × (product/1000) / (uptake vol / (uptake grav × 100))")
    print()
    
    # FATQID test case
    print("🧪 TEST FATQID:")
    
    # Data FATQID
    total_sensible_j = 230.50  # J (dari hasil perhitungan energy components)
    heat_eff = 0.75
    product_mg = 9.12  # mg
    uptake_vol = 43.38  # g/L (volumetric_wc)
    uptake_grav = 13.11  # % (gravimetric_wc)
    expected_qheat = 0.53810  # MJ
    
    print(f"Data:")
    print(f"   Total sensible energy: {total_sensible_j} J")
    print(f"   Heat efficiency: {heat_eff}")
    print(f"   Product mass: {product_mg} mg")
    print(f"   Uptake volumetric: {uptake_vol} g/L")
    print(f"   Uptake gravimetric: {uptake_grav} %")
    print(f"   Expected Qheat: {expected_qheat} MJ")
    print()
    
    # Step 1: Hitung Vreactor
    print("📊 STEP 1: Calculate Vreactor")
    
    # Vreactor = 1.2 × (product/1000) / (uptake vol / (uptake grav × 100))
    product_g = product_mg / 1000.0  # mg → g
    uptake_density = uptake_vol / (uptake_grav * 100 / 100)  # g/L / (% as fraction)
    # Wait, ini sepertinya uptake_vol / (uptake_grav / 100)
    uptake_density_corrected = uptake_vol / (uptake_grav / 100)  # g/L / fraction
    
    vreactor_formula1 = 1.2 * product_g / (uptake_vol / (uptake_grav * 100))
    vreactor_formula2 = 1.2 * product_g / (uptake_vol / (uptake_grav / 100))
    
    print(f"Product: {product_mg} mg = {product_g:.6f} g")
    print(f"Uptake density calculation options:")
    print(f"   Formula 1: uptake_vol / (uptake_grav * 100) = {uptake_vol} / ({uptake_grav} * 100) = {uptake_vol / (uptake_grav * 100):.6f}")
    print(f"   Formula 2: uptake_vol / (uptake_grav / 100) = {uptake_vol} / ({uptake_grav} / 100) = {uptake_vol / (uptake_grav / 100):.6f}")
    print()
    
    print(f"Vreactor calculations:")
    print(f"   Formula 1: 1.2 × {product_g:.6f} / {uptake_vol / (uptake_grav * 100):.6f} = {vreactor_formula1:.6f} L")
    print(f"   Formula 2: 1.2 × {product_g:.6f} / {uptake_vol / (uptake_grav / 100):.6f} = {vreactor_formula2:.6f} L")
    print()
    
    # Step 2: Hitung Qheat untuk kedua formula
    print("📊 STEP 2: Calculate Qheat")
    
    qheat1 = total_sensible_j / (heat_eff * vreactor_formula1)  # MJ? atau perlu /1e6?
    qheat2 = total_sensible_j / (heat_eff * vreactor_formula2)
    
    # Convert ke MJ
    qheat1_mj = qheat1 / 1e6
    qheat2_mj = qheat2 / 1e6
    
    print(f"Qheat calculations:")
    print(f"   Formula 1: {total_sensible_j} / ({heat_eff} × {vreactor_formula1:.6f}) = {qheat1:.2f} J = {qheat1_mj:.5f} MJ")
    print(f"   Formula 2: {total_sensible_j} / ({heat_eff} × {vreactor_formula2:.6f}) = {qheat2:.2f} J = {qheat2_mj:.5f} MJ")
    print()
    
    # Compare dengan expected
    print("📊 STEP 3: Compare with expected")
    print(f"Expected: {expected_qheat:.5f} MJ")
    print()
    
    error1 = abs(qheat1_mj - expected_qheat) / expected_qheat * 100
    error2 = abs(qheat2_mj - expected_qheat) / expected_qheat * 100
    
    print(f"Errors:")
    print(f"   Formula 1: {error1:.1f}% {'✅' if error1 < 10 else '❌'}")
    print(f"   Formula 2: {error2:.1f}% {'✅' if error2 < 10 else '❌'}")
    print()
    
    # Cek mana yang lebih dekat
    if error1 < error2:
        best_formula = "Formula 1"
        best_vreactor = vreactor_formula1
        best_qheat = qheat1_mj
        best_error = error1
    else:
        best_formula = "Formula 2"  
        best_vreactor = vreactor_formula2
        best_qheat = qheat2_mj
        best_error = error2
    
    print(f"🎯 BEST RESULT: {best_formula}")
    print(f"   Vreactor: {best_vreactor:.6f} L")
    print(f"   Qheat: {best_qheat:.5f} MJ")
    print(f"   Error: {best_error:.1f}%")
    print()
    
    # Debug: Cek apakah ada missing conversion factor
    print("🔍 DEBUG: Missing conversion factors?")
    
    # What if we need × 1000 somewhere for MJ/1000L?
    qheat_with_1000 = total_sensible_j / (heat_eff * best_vreactor * 1000)  # /1000 for per 1000L
    qheat_with_1000_mj = qheat_with_1000 / 1e3  # Convert to MJ
    
    print(f"With ×1000 factor: {qheat_with_1000:.2f} J = {qheat_with_1000_mj:.5f} MJ")
    error_1000 = abs(qheat_with_1000_mj - expected_qheat) / expected_qheat * 100
    print(f"Error with ×1000: {error_1000:.1f}% {'✅' if error_1000 < 10 else '❌'}")
    print()
    
    # Reverse engineering: what Vreactor gives correct result?
    print("🔄 REVERSE ENGINEERING:")
    required_vreactor = total_sensible_j / (heat_eff * expected_qheat * 1e6)
    print(f"Required Vreactor for exact match: {required_vreactor:.6f} L")
    
    # What factor would fix the best formula?
    correction_factor = required_vreactor / best_vreactor
    print(f"Correction factor needed: {correction_factor:.3f}")
    print()
    
    # Test teman's calculation that gave 1.85
    print("🧪 TEMAN'S CALCULATION (got 1.85):")
    print("If teman got 1.85 instead of 0.53, let's see what they might have calculated...")
    
    # Maybe they used different formula or units
    teman_result = 1.85
    ratio_to_expected = teman_result / expected_qheat
    print(f"Teman result: {teman_result} MJ")
    print(f"Ratio to expected: {ratio_to_expected:.2f}x higher")
    
    # Check if any of our calculations match 1.85
    if abs(qheat1_mj - teman_result) < 0.1:
        print("✅ Formula 1 matches teman's calculation!")
    elif abs(qheat2_mj - teman_result) < 0.1:
        print("✅ Formula 2 matches teman's calculation!")
    elif abs(qheat_with_1000_mj - teman_result) < 0.1:
        print("✅ ×1000 version matches teman's calculation!")
    else:
        print("❓ Teman might be using different parameters or formula")

if __name__ == "__main__":
    test_friend_formula()