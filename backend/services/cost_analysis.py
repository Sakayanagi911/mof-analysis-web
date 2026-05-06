import json
from pathlib import Path
from services.joback import calculate_cp_joback

PRICE_DB_PATH = Path(__file__).parent.parent / "data" / "price_database.json"

# Konstanta kelayakan (feasibility)
MAX_MOF_COST = 30.0         # USD/kg MOF
MAX_STORAGE_COST = 300.0    # USD/kg H2
MAX_REACTION_TIME = 48.0    # jam
MAX_TEMPERATURE = 180.0     # °C

def load_price_database():
    """Load database harga dari JSON dengan encoding yang aman (UTF-8)."""
    with open(PRICE_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_mof_cost(metal_name: str, linker_name: str,
                        metal_mass_mg: float = 100.0,
                        linker_mass_mg: float = 50.0,
                        product_mass_mg: float = 50.0,
                        solvent_name: str = "-", solvent_volume_ml: float = 0.0,
                        additive_name: str = "-", additive_volume_ml: float = 0.0,
                        modulator_name: str = "-", modulator_volume_ml: float = 0.0) -> dict:
    """Hitung harga bahan MOF dengan faktor skala industri (Scale Factor) persis seperti old_model."""
    db = load_price_database()
    eur_to_usd = db.get("eur_to_usd", 1.15)  # old_model uses 1.15
    ym = db["scale_factors"]["ym"]
    ind_mass = db["scale_factors"]["industrial_mass_mg"]
    ym_linker = db["scale_factors"].get("ym_linker", 0.67)

    def get_price(category: str, name: str, default: float) -> float:
        if not name or name == "-":
            return 0.0
        n_lower = name.strip().lower()
        cat_db = db.get(category, {})
        for k, v in cat_db.items():
            if k.strip().lower() == n_lower:
                if "price_eur_per_ml" in v: return v["price_eur_per_ml"]
                if "price_eur_per_g" in v: return v["price_eur_per_g"]
        return default

    # Lookup harga dasar (dengan asumsi database mengandung harga analytical grade, kita ubah ke technical grade untuk industri)
    tech_multiplier = 0.00222
    metal_p = get_price("metals", metal_name, 0.01)
    linker_p = get_price("linkers", linker_name, 10.0)
    solvent_p = get_price("solvents", solvent_name, 0.0) * tech_multiplier
    additive_p = get_price("additives", additive_name, 0.0) * tech_multiplier
    modulator_p = get_price("modulators", modulator_name, 0.0) * tech_multiplier

    # Mencegah error pembagian nol, estimasi yield berdasarkan reaktan jika tidak ada
    if product_mass_mg <= 0:
        product_mass_mg = metal_mass_mg + linker_mass_mg
        if product_mass_mg <= 0:
            product_mass_mg = 50.0

    # 1. Total harga bahan baku untuk skala Lab (Euro)
    metal_cost_eur = metal_p * (metal_mass_mg / 1000.0)
    linker_cost_eur = linker_p * (linker_mass_mg / 1000.0)
    solvent_cost_eur = solvent_p * solvent_volume_ml
    additive_cost_eur = additive_p * additive_volume_ml
    modulator_cost_eur = modulator_p * modulator_volume_ml

    # 2. Scale Factor (Diskon Mass Production sesuai old_model)
    scale_factor = (product_mass_mg / ind_mass) ** ym
    scale_factor_linker = (product_mass_mg / ind_mass) ** ym_linker
    
    metal_cost_scaled = metal_cost_eur * scale_factor
    solvent_cost_scaled = solvent_cost_eur * scale_factor
    additive_cost_scaled = additive_cost_eur * scale_factor
    modulator_cost_scaled = modulator_cost_eur * scale_factor
    
    linker_cost_scaled = linker_cost_eur * scale_factor_linker
    
    total_scaled_cost_eur = (metal_cost_scaled + solvent_cost_scaled + 
                             additive_cost_scaled + modulator_cost_scaled + 
                             linker_cost_scaled)
    
    # 3. Harga Unit untuk Produksi (Euro per kg MOF)
    product_kg = product_mass_mg / 1e6
    mof_cost_eur_per_kg = total_scaled_cost_eur / product_kg
    mof_cost_usd_per_kg = mof_cost_eur_per_kg * eur_to_usd

    return {
        "mof_cost_usd_per_kg": round(mof_cost_usd_per_kg, 4),
        "mof_cost_eur_per_kg": round(mof_cost_eur_per_kg, 4)
    }

# =====================================================================
# DATABASE PROPERTI KIMIA (Sesuai dengan source_data di old_model)
# Sumber: PubChem, NIST, Sigma Aldrich @298.15K
# Format: (density g/mL, Cp J/mol·K, Mr g/mol)
# =====================================================================
CHEM_PROP_DB = {
    # --- Solvent ---
    "dmf":           (0.9445, 148.16,  73.0938),
    "dma":           (0.9366, 178.2,   87.12),
    "dmac":          (0.9366, 178.2,   87.12),
    "def":           (0.908,  199.0,   101.1469),
    "h2o":           (0.9950, 75.38,   18.0153),
    "water":         (0.9950, 75.38,   18.0153),
    "ch2cl2":        (1.3255, 96.8,    84.93),
    "dea":           (1.0966, 198.0,   105.14),
    # --- Additive ---
    "etoh":          (0.7893, 112.4,   46.0684),
    "ethanol":       (0.7893, 112.4,   46.0684),
    "meoh":          (0.792,  79.5,    32.0419),
    "methanol":      (0.792,  79.5,    32.0419),
    "nmp":           (1.027,  412.4,   99.1311),
    "dmpu":          (1.03,   180.0,   114.14),
    "mecn":          (0.787,  96.7,    41.0519),
    "acetonitrile":  (0.787,  96.7,    41.0519),
    "dmso":          (1.101,  148.28,  78.133),
    # --- Modulator ---
    "hcl":           (1.16,   29.14,   36.461),
    "hno3":          (1.5129, 53.29,   63.0128),
    "hbf4":          (1.4,    130.0,   87.82),
    "dioxane":       (1.036,  147.9,   88.1051),
    "acoh":          (1.0446, 123.1,   60.0520),
    "h3pmo12o40":    (2.60,   500.0,   1825.25),
    "naoh":          (2.13,   59.52,   39.9971),
    "triethylamine": (0.729,  216.43,  101.19),
    "tea":           (0.729,  216.43,  101.19),
    "eg":            (1.115,  142.0,   62.07),
    # --- Metal (garam terhidrasi) ---
    "cuso4·5h2o":    (2.284, 100.0,  249.69),
    "cuso4.5h2o":    (2.284, 100.0,  249.69),
    "cu(no3)2·3h2o": (2.32,  110.0,  241.60),
    "cu(no3)2.3h2o": (2.32,  110.0,  241.60),
    "cu(no3)2·2.5h2o": (2.30, 105.0, 232.59),
    "cu(no3)2.2.5h2o": (2.30, 105.0, 232.59),
    "zn(no3)2·6h2o": (2.065, 95.0,  297.49),
    "zn(no3)2.6h2o": (2.065, 95.0,  297.49),
}

def _normalize_chem_name(name: str) -> str:
    """Normalisasi nama senyawa: hapus unicode subscript, whitespace, lowercase."""
    if not name:
        return ""
    subscript_map = str.maketrans(
        '\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089',
        '0123456789'
    )
    return name.translate(subscript_map).strip().lower().replace(" ", "")

def get_chem_prop(name: str, is_metal=False):
    """
    Mencari nilai rho (g/mL), Cp (J/mol·K), dan Mr (g/mol) dari database.
    Menggunakan exact match dari source_data old_model (PubChem/NIST @298.15K).
    
    Returns: (density_g_ml, cp_J_mol_K, mr_g_mol)
    """
    if not name or name == "-" or name == "0":
        return 0.0, 0.0, 1.0
    
    n = _normalize_chem_name(name)
    
    # Exact match di database
    if n in CHEM_PROP_DB:
        return CHEM_PROP_DB[n]
    
    # Fuzzy match: cek apakah key ada di dalam nama
    for key, props in CHEM_PROP_DB.items():
        if key in n or n in key:
            return props
    
    # Fallback default
    if is_metal:
        return 1.0, 100.0, 200.0
    return 1.0, 75.0, 100.0

def calculate_energy(smiles: str, temperature_c: float, reaction_time_h: float,
                     linker_mass_mg: float = 50.0, metal_mass_mg: float = 100.0,
                     solvent_name: str = "-", solvent_volume_ml: float = 0.0,
                     additive_name: str = "-", additive_volume_ml: float = 0.0,
                     modulator_name: str = "-", modulator_volume_ml: float = 0.0,
                     metal_name: str = "-",
                     volumetric_wc: float = 40.0, gravimetric_wc: float = 5.5,
                     product_mass_mg: float = 50.0) -> dict:
    """
    Hitung energi pemanasan dengan rumus yang BENAR dari old_model:
    Q = n(mol) × CP(J/mol·K) × ΔT(K)
    
    Semua material menggunakan basis molar (mol), BUKAN mass (g).
    """
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    
    T_ambient = 298.15 
    T_reaction = temperature_c + 273.15 
    delta_t = (temperature_c + 273.15) - 298.15  # sama dengan [T operasi + 273,15] - 298,15
    if delta_t < 0:
        delta_t = 0.0

    # ====== LINKER CP ======
    # Prioritas: Manual Cp dari old_model (Hybrid Physics ML) → Joback
    MANUAL_CP_MAP = {
        "C(=O)(O)C1=CC=C(C=C1)C=1C=NC=C(C1)C1=CC=C(C=C1)C(=O)O": 364.47,
        "C(=O)(O)C1=CC=C(C=C1)C=1C(=NC(=C(N1)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C=C1)C(=O)O)C1=CC=C(C(=O)O)C=C1": 586.17,
        "S1C(=CC=C1C(=O)O)C(=O)O": 181.99,
        "C(=O)O": 41.29,
        "N=1N=C(NC1C=1C=C(C=C(C1)C(=O)O)C(=O)O)C=1C=C(C=C(C1)C(=O)O)C(=O)O": 387.69,
        "C(#CC=1C=C(C=C(C(=O)O)C1)C(=O)O)C=1C=C(C=C(C(=O)O)C1)C(=O)O": 345.59,
    }
    
    if smiles in MANUAL_CP_MAP:
        cp_linker_mol_k = MANUAL_CP_MAP[smiles]
    else:
        cp_linker_mol_k = calculate_cp_joback(smiles, T=T_reaction)
        if not cp_linker_mol_k or cp_linker_mol_k <= 0:
            cp_linker_mol_k = calculate_cp_joback(smiles, T=T_ambient)
        if not cp_linker_mol_k or cp_linker_mol_k <= 0:
            cp_linker_mol_k = 150.0  # Fallback J/(mol·K)
    
    # Get linker molecular weight
    try:
        mol = Chem.MolFromSmiles(smiles)
        linker_mw = Descriptors.MolWt(mol) if mol else 300.0
    except Exception:
        linker_mw = 300.0

    # ====== AMBIL PROPERTI DARI DATABASE ======
    # get_chem_prop sekarang return (rho, cp_mol_k, mr)
    rho_solv, cp_solv_mol_k, mr_solv = get_chem_prop(solvent_name)
    rho_add, cp_add_mol_k, mr_add = get_chem_prop(additive_name)
    rho_mod, cp_mod_mol_k, mr_mod = get_chem_prop(modulator_name)
    _, cp_metal_mol_k, mr_metal = get_chem_prop(metal_name, is_metal=True)

    # ====== KALKULASI MOLES ======
    # Solvent, Additive, Modulator: dari volume
    m_solv_g = solvent_volume_ml * rho_solv
    n_solv = m_solv_g / mr_solv  # mol
    
    m_add_g = additive_volume_ml * rho_add
    n_add = m_add_g / mr_add  # mol
    
    m_mod_g = modulator_volume_ml * rho_mod
    n_mod = m_mod_g / mr_mod  # mol
    
    # Metal, Linker: dari mass
    n_metal = (metal_mass_mg / 1000.0) / mr_metal  # mg → g → mol
    n_linker = (linker_mass_mg / 1000.0) / linker_mw  # mg → g → mol

    # ====== KALKULASI ENERGI SENSIBLE (Joule) ======
    # Q = n × CP × ΔT
    e_solv = n_solv * cp_solv_mol_k * delta_t
    e_add = n_add * cp_add_mol_k * delta_t
    e_mod = n_mod * cp_mod_mol_k * delta_t
    e_metal = n_metal * cp_metal_mol_k * delta_t
    e_linker = n_linker * cp_linker_mol_k * delta_t
    
    e_sens_total = e_solv + e_add + e_mod + e_metal + e_linker

    # ====== GLOBAL ENERGY METRICS (sesuai old_model) ======
    heat_eff = 0.75
    t_seconds = reaction_time_h * 3600.0
    
    # --- Qheat (MJ) ---
    # old_model: Qheat_J_per_L_reactor = Total_Sensible / (heat_eff * V_Reactor)
    # Qheat_MJ_1000L = Qheat_J_per_L_reactor * 1000 / 1e6
    if gravimetric_wc <= 0:
        grav_calc = 5.5
    else:
        grav_calc = gravimetric_wc
        
    density_mof_g_l = volumetric_wc / (grav_calc * 100.0)
    if density_mof_g_l <= 0:
        density_mof_g_l = 1.0  # fallback
        
    g_mof = product_mass_mg / 1000.0
    if g_mof <= 0:
        g_mof = (metal_mass_mg + linker_mass_mg) / 1000.0
    if g_mof <= 0:
        g_mof = 0.05
        
    v_mof_l = g_mof / density_mof_g_l
    v_reactor_l = 1.2 * v_mof_l
    
    if v_reactor_l > 0:
        qheat_j_per_l = e_sens_total / (heat_eff * v_reactor_l)
    else:
        qheat_j_per_l = 0.0
        
    q_heat_mj = (qheat_j_per_l * 1000.0) / 1_000_000.0
    
    # --- Qloss (MJ) ---
    # old_model: Qloss = U*A × ΔT × t / (heat_eff × 1e6)
    # U*A = 3.303 W/K
    u_a = 3.303
    q_loss_mj = (u_a * delta_t * t_seconds) / (heat_eff * 1_000_000)
    
    # --- Estirr (MJ) ---
    # old_model: Estirr = 0.0162 × Density_Tot(g/L) × Time(h) × 3600 / 1e6
    # Density_Tot = m_total(g) / V_liquid(L)
    m_liquid_g = m_solv_g + m_add_g + m_mod_g
    m_solid_g = (metal_mass_mg + linker_mass_mg) / 1000.0
    m_total_g = m_liquid_g + m_solid_g
    v_liquid_l = (solvent_volume_ml + additive_volume_ml + modulator_volume_ml) / 1000.0
    
    if v_liquid_l > 0:
        density_total = m_total_g / v_liquid_l  # g/L
    else:
        density_total = 1000.0  # default water density
    
    stirr_coeff = 0.0162
    e_stirr_mj = (stirr_coeff * density_total * reaction_time_h * 3600) / 1e6
    
    total_energy_mj = q_heat_mj + q_loss_mj + e_stirr_mj

    return {
        "q_energy_mj": round(q_heat_mj, 4),
        "q_loss_mj": round(q_loss_mj, 4),
        "e_stirr_mj": round(e_stirr_mj, 4),
        "e_total_mj": round(total_energy_mj, 4),
        "cp_value": round(cp_linker_mol_k, 4),
        "linker_mw": round(linker_mw, 4),
        "e_sensible_total_j": round(e_sens_total, 2),
        "e_sensible_solvent_j": round(e_solv, 2),
        "e_sensible_additive_j": round(e_add, 2),
        "e_sensible_modulator_j": round(e_mod, 2),
        "e_sensible_metal_j": round(e_metal, 2),
        "e_sensible_linker_j": round(e_linker, 2)
    }

def calculate_storage_cost(mof_cost_usd_per_kg: float, gravimetric_wc: float) -> float:
    """Hitung storage cost (USD/kg H2) berdasarkan harga MOF dan Uptake H2."""
    if gravimetric_wc <= 0: return float('inf')
    return round(mof_cost_usd_per_kg / (gravimetric_wc / 100.0), 2)

def run_economic_analysis(metal_name: str, linker_name: str,
                           reaction_time: float, temperature: float,
                           smiles: str, gravimetric_wc: float = 5.5,
                           volumetric_wc: float = 40.0,
                           product_mass_mg: float = 50.0,
                           metal_mass_mg: float = 100.0,
                           linker_mass_mg: float = 50.0,
                           solvent_name: str = "-", solvent_volume_ml: float = 0.0,
                           additive_name: str = "-", additive_volume_ml: float = 0.0,
                           modulator_name: str = "-", modulator_volume_ml: float = 0.0) -> dict:
    
    # Kalkulasi dinamis memasukkan parameter dari frontend
    cost_result = calculate_mof_cost(metal_name, linker_name, 
                                     metal_mass_mg=metal_mass_mg,
                                     linker_mass_mg=linker_mass_mg,
                                     product_mass_mg=product_mass_mg,
                                     solvent_name=solvent_name,
                                     solvent_volume_ml=solvent_volume_ml,
                                     additive_name=additive_name,
                                     additive_volume_ml=additive_volume_ml,
                                     modulator_name=modulator_name,
                                     modulator_volume_ml=modulator_volume_ml)
    
    mof_cost = cost_result["mof_cost_usd_per_kg"]
    storage_cost = calculate_storage_cost(mof_cost, gravimetric_wc)
    energy_result = calculate_energy(smiles, temperature, reaction_time,
                                    linker_mass_mg=linker_mass_mg,
                                    metal_mass_mg=metal_mass_mg,
                                    solvent_name=solvent_name,
                                    solvent_volume_ml=solvent_volume_ml,
                                    additive_name=additive_name,
                                    additive_volume_ml=additive_volume_ml,
                                    modulator_name=modulator_name,
                                    modulator_volume_ml=modulator_volume_ml,
                                    metal_name=metal_name,
                                    volumetric_wc=volumetric_wc,
                                    gravimetric_wc=gravimetric_wc,
                                    product_mass_mg=product_mass_mg)

    # Cek feasibility
    is_feasible = (
        mof_cost <= MAX_MOF_COST and
        storage_cost <= MAX_STORAGE_COST and
        reaction_time <= MAX_REACTION_TIME and
        temperature <= MAX_TEMPERATURE
    )

    return {
        "mof_cost_usd_per_kg": mof_cost,
        "storage_cost_usd_per_kg_h2": storage_cost,
        "q_energy_mj": energy_result["q_energy_mj"],
        "q_loss_mj": energy_result["q_loss_mj"],
        "e_stirr_mj": energy_result["e_stirr_mj"],
        "e_total_mj": energy_result["e_total_mj"],
        "energy_details": energy_result,
        "is_feasible": is_feasible,
        "feasibility_details": {
            "mof_cost_ok": mof_cost <= MAX_MOF_COST,
            "storage_cost_ok": storage_cost <= MAX_STORAGE_COST,
            "time_ok": reaction_time <= MAX_REACTION_TIME,
            "temperature_ok": temperature <= MAX_TEMPERATURE
        }
    }