"""
Modul kalkulasi biaya sintesis MOF.
Referensi: old_model/Cost Calculation, MCDM Screening, and Energy Analysis.ipynb
"""

import json
from pathlib import Path
from services.joback import calculate_cp_joback

PRICE_DB_PATH = Path(__file__).parent.parent / "data" / "price_database.json"

# Konstanta feasibility ekonomi
MAX_MOF_COST = 30.0         # USD/kg MOF
MAX_STORAGE_COST = 300.0    # USD/kg H2
MAX_REACTION_TIME = 48.0    # jam
MAX_TEMPERATURE = 180.0     # °C


def load_price_database():
    """Load database harga dari JSON."""
    with open(PRICE_DB_PATH, "r") as f:
        return json.load(f)


def calculate_mof_cost(metal_name: str, linker_name: str,
                        metal_mass_mg: float = 100.0,
                        linker_mass_mg: float = 50.0,
                        product_mass_mg: float = 50.0) -> dict:
    """
    Hitung harga MOF per kg.

    Rumus (dari referensi notebook):
        1. Ambil harga satuan metal (€/g) dan linker (€/g) dari database
        2. Hitung harga bahan: harga = massa × harga_satuan
        3. Terapkan faktor diskon industri:
           scale_factor = (product_mg / 10^7)^ym
        4. Total harga = Σ(harga_bahan × scale_factor)
        5. Konversi ke USD/kg: total / (product_mg / 10^6) × eur_to_usd

    Returns:
        dict: {mof_cost_eur_per_kg, mof_cost_usd_per_kg}
    """
    db = load_price_database()
    eur_to_usd = db["eur_to_usd"]
    ym = db["scale_factors"]["ym"]
    ym_linker = db["scale_factors"]["ym_linker"]
    ind_mass = db["scale_factors"]["industrial_mass_mg"]

    # Lookup harga metal
    metal_price_per_g = db["metals"].get(metal_name, {}).get("price_eur_per_g", 0.01)

    # Lookup harga linker
    linker_price_per_g = db["linkers"].get(linker_name, {}).get("price_eur_per_g", 10.0)

    # Harga bahan mentah
    metal_cost_eur = metal_price_per_g * (metal_mass_mg / 1000.0)
    linker_cost_eur = linker_price_per_g * (linker_mass_mg / 1000.0)

    # Scale factor (diskon produksi massal)
    if product_mass_mg <= 0:
        product_mass_mg = 1.0
    scale = (product_mass_mg / ind_mass) ** ym
    scale_linker = (product_mass_mg / ind_mass) ** ym_linker

    metal_cost_eur *= scale
    linker_cost_eur *= scale_linker

    total_eur = metal_cost_eur + linker_cost_eur

    # Konversi ke per-kg
    product_kg = product_mass_mg / 1e6
    if product_kg > 0:
        mof_cost_eur_per_kg = total_eur / product_kg
    else:
        mof_cost_eur_per_kg = 0.0

    mof_cost_usd_per_kg = mof_cost_eur_per_kg * eur_to_usd

    return {
        "mof_cost_eur_per_kg": round(mof_cost_eur_per_kg, 4),
        "mof_cost_usd_per_kg": round(mof_cost_usd_per_kg, 4)
    }


def calculate_energy(smiles: str, temperature_c: float,
                      reaction_time_h: float) -> dict:
    """
    Hitung Q (energi reaksi) dan Q_loss berdasarkan Cp dari Joback.

    Rumus dasar:
        Cp = Joback(smiles, T)   # dalam J/(mol·K)
        ΔT = T_reaction - T_ambient  (K)
        Q = Cp × ΔT / 1000      # konversi ke kJ/mol
        Q_loss = Q × loss_factor × time_factor

    Args:
        smiles: SMILES string linker
        temperature_c: Temperatur reaksi (°C)
        reaction_time_h: Waktu reaksi (jam)

    Returns:
        dict: {q_energy_kj, q_loss_kj, cp_value}
    """
    T_ambient = 298.15  # Kelvin (25°C)
    T_reaction = temperature_c + 273.15  # Konversi ke Kelvin

    # Hitung Cp pada temperatur reaksi
    cp = calculate_cp_joback(smiles, T=T_reaction)
    if cp is None:
        cp = calculate_cp_joback(smiles, T=T_ambient)
    if cp is None:
        cp = 100.0  # Fallback default Cp

    # Hitung Q
    delta_T = T_reaction - T_ambient
    q_energy_kj = (cp * delta_T) / 1000.0  # Konversi J ke kJ

    # Hitung Q_loss (asumsi: loss factor proporsional terhadap waktu)
    # Semakin lama reaksi, semakin besar heat loss
    loss_factor = 0.15  # 15% heat loss per cycle (asumsi sederhana)
    time_factor = reaction_time_h / 24.0  # Normalisasi ke 1 hari
    q_loss_kj = q_energy_kj * loss_factor * time_factor

    return {
        "q_energy_kj": round(q_energy_kj, 4),
        "q_loss_kj": round(q_loss_kj, 4),
        "cp_value": round(cp, 4)
    }


def calculate_storage_cost(mof_cost_usd_per_kg: float,
                            gravimetric_wc: float) -> float:
    """
    Hitung biaya penyimpanan H₂ per kg.

    Rumus (dari referensi):
        Storage Cost = MOF Price (USD/kg) / (WC_grav / 100)

    Args:
        mof_cost_usd_per_kg: Harga MOF dalam USD/kg
        gravimetric_wc: Working Capacity Gravimetrik dalam wt.%

    Returns:
        float: Biaya penyimpanan dalam USD/kg H₂
    """
    if gravimetric_wc <= 0:
        return float('inf')
    return round(mof_cost_usd_per_kg / (gravimetric_wc / 100.0), 4)


def run_economic_analysis(metal_name: str, linker_name: str,
                           reaction_time: float, temperature: float,
                           smiles: str, gravimetric_wc: float = 5.0) -> dict:
    """
    Jalankan analisis ekonomi lengkap.

    Returns:
        dict lengkap dengan semua output ekonomi + feasibility
    """
    # 1. Hitung harga MOF
    cost_result = calculate_mof_cost(metal_name, linker_name)
    mof_cost = cost_result["mof_cost_usd_per_kg"]

    # 2. Hitung biaya penyimpanan
    storage_cost = calculate_storage_cost(mof_cost, gravimetric_wc)

    # 3. Hitung energi
    energy_result = calculate_energy(smiles, temperature, reaction_time)

    # 4. Cek feasibility
    is_feasible = (
        mof_cost <= MAX_MOF_COST and
        storage_cost <= MAX_STORAGE_COST and
        reaction_time <= MAX_REACTION_TIME and
        temperature <= MAX_TEMPERATURE
    )

    return {
        "mof_cost_usd_per_kg": mof_cost,
        "storage_cost_usd_per_kg_h2": storage_cost,
        "q_energy_kj": energy_result["q_energy_kj"],
        "q_loss_kj": energy_result["q_loss_kj"],
        "is_feasible": is_feasible,
        "feasibility_details": {
            "mof_cost_ok": mof_cost <= MAX_MOF_COST,
            "storage_cost_ok": storage_cost <= MAX_STORAGE_COST,
            "time_ok": reaction_time <= MAX_REACTION_TIME,
            "temperature_ok": temperature <= MAX_TEMPERATURE
        }
    }
