#!/usr/bin/env python3
"""
Debug V_Reactor calculation by working backwards from expected Qheat
"""

print("=== V_REACTOR ANALYSIS ===")

# Use Case 1 data
total_sensible_1 = 230.50  # J (expected)
qheat_expected_1 = 0.53810  # MJ
heat_eff = 0.75

# Work backwards: Qheat_MJ_1000L = Qheat_J_per_L_reactor * 1000 / 1e6
# So: Qheat_J_per_L_reactor = Qheat_MJ_1000L * 1e6 / 1000 = Qheat_MJ_1000L * 1000
qheat_j_per_l_1 = qheat_expected_1 * 1000  # J/L

# From: Qheat_J_per_L_reactor = Total_Sensible / (heat_eff * V_Reactor)
# So: V_Reactor = Total_Sensible / (heat_eff * Qheat_J_per_L_reactor)
v_reactor_expected_1 = total_sensible_1 / (heat_eff * qheat_j_per_l_1)

print(f"Use Case 1:")
print(f"  Total Sensible: {total_sensible_1} J")
print(f"  Expected Qheat: {qheat_expected_1} MJ")
print(f"  Qheat J/L: {qheat_j_per_l_1} J/L")
print(f"  Expected V_Reactor: {v_reactor_expected_1:.6f} L")

# Use Case 2 data
total_sensible_2 = 175.11  # J (expected)
qheat_expected_2 = 0.77531  # MJ

qheat_j_per_l_2 = qheat_expected_2 * 1000  # J/L
v_reactor_expected_2 = total_sensible_2 / (heat_eff * qheat_j_per_l_2)

print(f"\nUse Case 2:")
print(f"  Total Sensible: {total_sensible_2} J")
print(f"  Expected Qheat: {qheat_expected_2} MJ")
print(f"  Qheat J/L: {qheat_j_per_l_2} J/L")
print(f"  Expected V_Reactor: {v_reactor_expected_2:.6f} L")

# Compare with current calculation
print(f"\nCurrent V_Reactor calculation:")
print(f"  Use Case 1: 0.003075 L")
print(f"  Use Case 2: 0.003975 L")

print(f"\nRatio analysis:")
print(f"  Expected UC1/Current UC1: {v_reactor_expected_1 / 0.003075:.1f}x")
print(f"  Expected UC2/Current UC2: {v_reactor_expected_2 / 0.003975:.1f}x")

# Check if V_Reactor should be based on liquid volume instead
v_liquid_1 = 2.05 / 1000  # 2.0 mL DMF + 0.05 mL HNO3 → L
v_liquid_2 = 2.65 / 1000  # 2.0 mL DMF + 0.5 mL EtOH + 0.15 mL HNO3 → L

print(f"\nLiquid volume comparison:")
print(f"  UC1 liquid volume: {v_liquid_1:.6f} L")
print(f"  UC2 liquid volume: {v_liquid_2:.6f} L")
print(f"  UC1 expected/liquid: {v_reactor_expected_1 / v_liquid_1:.2f}x")
print(f"  UC2 expected/liquid: {v_reactor_expected_2 / v_liquid_2:.2f}x")

# Check if there's a constant V_Reactor
print(f"\nConstant V_Reactor hypothesis:")
print(f"  If V_Reactor = {v_reactor_expected_1:.6f} L for both cases:")
print(f"    UC1 Qheat: {total_sensible_1 / (heat_eff * v_reactor_expected_1) * 1000 / 1e6:.5f} MJ")
print(f"    UC2 Qheat: {total_sensible_2 / (heat_eff * v_reactor_expected_1) * 1000 / 1e6:.5f} MJ")
print(f"    UC2 expected: {qheat_expected_2:.5f} MJ")