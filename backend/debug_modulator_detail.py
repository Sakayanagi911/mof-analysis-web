#!/usr/bin/env python3
"""
Debug modulator calculation dengan data lengkap dari notebook
"""

print("=== ANALISIS MODULATOR DETAIL ===")

# Data dari notebook untuk Use Case 1 (HUNCIE)
print("Use Case 1 - Data dari notebook:")
print("  Modulator_Name: HNO3")
print("  Concentration (% or M): 0.65")
print("  Modulator Sol_Volume (mL): 0.03")
print("  Concentration (%w/w): 0.650000")
print("  Modulator_Volume (mL): 0.028676")

# Properti HNO3 dari notebook
rho_hno3 = 1.5129  # g/mL
cp_hno3 = 53.29    # J/mol·K
mr_hno3 = 63.0128  # g/mol
delta_t = 60.0     # K

print(f"\nProperti HNO3:")
print(f"  Density: {rho_hno3} g/mL")
print(f"  Cp: {cp_hno3} J/mol·K")
print(f"  Mr: {mr_hno3} g/mol")
print(f"  Delta T: {delta_t} K")

# Perhitungan dengan volume yang berbeda
volumes_to_test = [0.05, 0.03, 0.028676]
concentrations_to_test = [100.0, 0.65, 6.5]

print(f"\nTesting different volumes and concentrations:")
print(f"Expected energy: 0.25 J")

for vol in volumes_to_test:
    for conc in concentrations_to_test:
        mass_g = vol * rho_hno3
        n_mol = mass_g / mr_hno3
        # Apply concentration factor
        n_effective = n_mol * (conc / 100.0)
        energy_j = n_effective * cp_hno3 * delta_t
        
        print(f"  Vol={vol:7.5f} mL, Conc={conc:5.1f}%: mass={mass_g:.6f}g, n={n_effective:.6f}mol, E={energy_j:.3f}J")

# Cari kombinasi yang tepat untuk 0.25 J
target_energy = 0.25
print(f"\nMencari kombinasi untuk {target_energy} J:")

for vol in volumes_to_test:
    required_n = target_energy / (cp_hno3 * delta_t)
    mass_g = vol * rho_hno3
    n_total = mass_g / mr_hno3
    required_conc = (required_n / n_total) * 100.0
    
    print(f"  Vol={vol:7.5f} mL: required_conc={required_conc:.2f}%")

# Test dengan data Use Case 2
print(f"\n=== Use Case 2 Analysis ===")
print("Expected modulator energy: 2.03 J")
vol_uc2 = 0.15  # mL HNO3
target_energy_uc2 = 2.03

required_n_uc2 = target_energy_uc2 / (cp_hno3 * delta_t)
mass_g_uc2 = vol_uc2 * rho_hno3
n_total_uc2 = mass_g_uc2 / mr_hno3
required_conc_uc2 = (required_n_uc2 / n_total_uc2) * 100.0

print(f"  Vol={vol_uc2} mL: required_conc={required_conc_uc2:.2f}%")

# Analisis apakah ada pola
print(f"\n=== ANALISIS POLA ===")
print(f"UC1: Vol=0.05 mL, Target=0.25 J, Required conc={0.25/(0.05*rho_hno3/mr_hno3*cp_hno3*delta_t)*100:.2f}%")
print(f"UC2: Vol=0.15 mL, Target=2.03 J, Required conc={2.03/(0.15*rho_hno3/mr_hno3*cp_hno3*delta_t)*100:.2f}%")

# Cek apakah menggunakan Modulator_Volume dari notebook
print(f"\n=== MENGGUNAKAN MODULATOR_VOLUME DARI NOTEBOOK ===")
vol_notebook = 0.028676  # dari Modulator_Volume (mL)
mass_notebook = vol_notebook * rho_hno3
n_notebook = mass_notebook / mr_hno3
energy_notebook_100 = n_notebook * cp_hno3 * delta_t
energy_notebook_065 = n_notebook * cp_hno3 * delta_t * (0.65/100.0)

print(f"Modulator_Volume dari notebook: {vol_notebook} mL")
print(f"Energy dengan 100% conc: {energy_notebook_100:.3f} J")
print(f"Energy dengan 0.65% conc: {energy_notebook_065:.3f} J")
print(f"Target: 0.25 J")