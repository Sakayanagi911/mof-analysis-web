import json
from pathlib import Path
from rdkit import Chem
from services.joback import calculate_cp_joback

PRICE_DB_PATH = Path(__file__).parent.parent / "data" / "price_database.json"

# Konstanta kelayakan (feasibility)
MAX_MOF_COST = 30.0         # USD/kg MOF
MAX_STORAGE_COST = 300.0    # USD/kg H2
MAX_REACTION_TIME = 48.0    # jam
MAX_TEMPERATURE = 180.0     # °C

PRICE_DB_PATH = Path(__file__).parent.parent / "data" / "price_database.json"

def load_price_database():
    """Load database harga dari JSON dengan encoding yang aman (UTF-8)."""
    with open(PRICE_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_smiles_mapping():
    """
    Get SMILES to Linker Name mapping dari price_database.json
    Sekarang sudah digabung dalam satu file
    """
    db = load_price_database()
    return db.get("smiles_mapping", {}).get("mapping", {})

def get_uptake_data():
    """
    Get SMILES to Uptake data mapping dari price_database.json
    """
    db = load_price_database()
    return db.get("uptake_data", {})


def validate_smiles_or_raise(smiles: str) -> str:
    """Validate SMILES and return normalized text."""
    if smiles is None:
        raise ValueError("SMILES wajib diisi")
    normalized = smiles.strip()
    if not normalized or normalized == "-":
        raise ValueError("SMILES wajib diisi")
    mol = Chem.MolFromSmiles(normalized)
    if mol is None:
        raise ValueError("SMILES tidak valid")
    return normalized

def calculate_mof_cost(metal_name: str, linker_smiles: str = None,
                        linker_name: str = None,
                        metal_mass_mg: float = 100.0,
                        linker_mass_mg: float = 50.0,
                        product_mass_mg: float = 50.0,
                        solvent_name: str = "-", solvent_volume_ml: float = 0.0,
                        additive_name: str = "-", additive_volume_ml: float = 0.0,
                        modulator_name: str = "-", modulator_volume_ml: float = 0.0) -> dict:
    """
    Hitung harga bahan MOF dengan formula EXACT dari model asli.
    
    INPUT UTAMA: SMILES (bukan linker name)
    - linker_smiles akan di-lookup ke linker_name untuk mendapatkan price
    
    Formula EXACT dari notebook Cost Calculation:
    1. Raw cost = price_per_unit * volume/mass  
    2. Scale factor = (product_mass_mg / 1e7) ** ym
    3. Scaled cost = raw_cost * scale_factor
    4. MOF price per kg = total_scaled_cost / (product_mass_mg / 1e6)
    
    Scale factors dari notebook:
    - ym = 0.56 (untuk metal, solvent, additive, modulator)
    - ym_linker = 0.67 (untuk linker)
    - industrial_mass_mg = 1e7 (10 kg)
    """
    db = load_price_database()
    smiles_mapping = get_smiles_mapping()
    eur_to_usd = db.get("eur_to_usd", 1.15)
    
    # Scale factors EXACT dari notebook
    ym = 0.56
    ym_linker = 0.67
    industrial_mass_mg = 1e7  # 10 kg = 1e7 mg
    
    # ============================================================================
    # STEP 1: LOOKUP LINKER NAME AND PRICE FROM SMILES
    # ============================================================================
    resolved_linker_name = linker_name
    linker_price_eur_per_g = 10.0  # default fallback
    
    if linker_smiles and linker_smiles != "-":
        # Normalize SMILES (remove whitespace)
        smiles_normalized = linker_smiles.strip()
        
        # Lookup in mapping - SEMUA DATA LINKER ADA DI SINI
        if smiles_normalized in smiles_mapping:
            linker_data = smiles_mapping[smiles_normalized]
            resolved_linker_name = linker_data.get("linker_name", "Unknown Linker")
            
            # Get price from SMILES mapping (SUMBER UTAMA)
            if linker_data.get("price_eur_per_g") is not None:
                linker_price_eur_per_g = linker_data["price_eur_per_g"]
            else:
                # Fallback jika tidak ada price
                linker_price_eur_per_g = 10.0
        else:
            # SMILES not found in mapping
            resolved_linker_name = resolved_linker_name or "Unknown Linker"
            linker_price_eur_per_g = 10.0
    elif resolved_linker_name and resolved_linker_name != "-":
        # Backward compatibility for tests/clients that still pass linker name.
        linker_name_norm = resolved_linker_name.strip().lower()
        for _, linker_data in smiles_mapping.items():
            name_in_db = str(linker_data.get("linker_name", "")).strip().lower()
            if name_in_db == linker_name_norm:
                resolved_linker_name = linker_data.get("linker_name", resolved_linker_name)
                linker_price_eur_per_g = linker_data.get("price_eur_per_g", 10.0) or 10.0
                break

    
    # ============================================================================
    # STEP 2: LOOKUP PRICES FROM DATABASE
    # ============================================================================
    
    def get_price(category: str, name: str, default: float) -> float:
        """Lookup harga dari database dengan normalisasi nama yang tepat."""
        if not name or name == "-":
            return 0.0
        
        # Normalisasi nama untuk matching yang lebih baik
        n_lower = name.strip().lower()
        
        # Mapping khusus untuk nama yang sering digunakan
        name_mapping = {
            "cu(no3)2·3h2o": "Cu(NO₃)₂·3H₂O",
            "cu(no3)2.3h2o": "Cu(NO₃)₂·3H₂O", 
            "cu(no3)2·2.5h2o": "Cu(NO₃)₂·2.5H₂O",
            "cu(no3)2.2.5h2o": "Cu(NO₃)₂·2.5H₂O",
            "cuso4·5h2o": "CuSO₄·5H₂O",
            "cuso4.5h2o": "CuSO₄·5H₂O",
            "zn(no3)2·6h2o": "Zn(NO₃)₂·6H₂O",
            "zn(no3)2.6h2o": "Zn(NO₃)₂·6H₂O",
            "h2bdc": "H₂BDC",
            "h3btc": "H₃BTC",
            "h2l": "H₂L"
        }
        
        # Cek mapping khusus dulu
        mapped_name = name_mapping.get(n_lower)
        if mapped_name:
            n_lower = mapped_name.lower()
        
        cat_db = db.get(category, {})
        
        # Exact match dulu
        for k, v in cat_db.items():
            if k.strip().lower() == n_lower:
                if "price_eur_per_ml" in v: 
                    return v["price_eur_per_ml"]
                if "price_eur_per_g" in v: 
                    return v["price_eur_per_g"]
        
        # Fuzzy match jika exact match gagal
        for k, v in cat_db.items():
            k_clean = k.strip().lower()
            if n_lower in k_clean or k_clean in n_lower:
                if "price_eur_per_ml" in v: 
                    return v["price_eur_per_ml"]
                if "price_eur_per_g" in v: 
                    return v["price_eur_per_g"]
        
        return default

    # Validasi input - product_mass harus > 0
    # Jika tidak ada product_mass, estimate dari metal + linker mass
    if product_mass_mg <= 0:
        # Default estimate: sum of metal + linker mass (assuming ~100% yield)
        # Ini adalah conservative estimate
        product_mass_mg = max(metal_mass_mg + linker_mass_mg, 100.0)
        
        # Jika masih 0, gunakan default minimum
        if product_mass_mg <= 0:
            product_mass_mg = 100.0
    
    # 1. LOOKUP HARGA dari database (Technical Grade prices)
    metal_price_eur_per_g = get_price("metals", metal_name, 0.01)
    # linker_price_eur_per_g sudah di-set dari SMILES mapping di atas
    solvent_price_eur_per_ml = get_price("solvents", solvent_name, 0.0)
    additive_price_eur_per_ml = get_price("additives", additive_name, 0.0)
    modulator_price_eur_per_ml = get_price("modulators", modulator_name, 0.0)
    
    # 2. HITUNG BIAYA BAHAN BAKU (Euro) - sesuai notebook
    metal_cost_eur = metal_price_eur_per_g * (metal_mass_mg / 1000.0)  # mg → g
    linker_cost_eur = linker_price_eur_per_g * (linker_mass_mg / 1000.0)  # mg → g
    solvent_cost_eur = solvent_price_eur_per_ml * solvent_volume_ml
    additive_cost_eur = additive_price_eur_per_ml * additive_volume_ml
    modulator_cost_eur = modulator_price_eur_per_ml * modulator_volume_ml
    
    # 3. SCALE FACTORS - EXACT dari notebook
    scale_factor = (product_mass_mg / industrial_mass_mg) ** ym
    scale_factor_linker = (product_mass_mg / industrial_mass_mg) ** ym_linker
    
    # 4. TERAPKAN SCALE FACTORS - sesuai notebook
    metal_cost_scaled = metal_cost_eur * scale_factor
    solvent_cost_scaled = solvent_cost_eur * scale_factor
    additive_cost_scaled = additive_cost_eur * scale_factor
    modulator_cost_scaled = modulator_cost_eur * scale_factor
    linker_cost_scaled = linker_cost_eur * scale_factor_linker
    
    # 5. TOTAL BIAYA setelah scale factor
    total_scaled_cost_eur = (metal_cost_scaled + solvent_cost_scaled + 
                             additive_cost_scaled + modulator_cost_scaled + 
                             linker_cost_scaled)
    
    # 6. HARGA PER KG MOF - EXACT formula dari notebook
    # MOF Price (€/kg) = MOF Total Price (€) / (Product (mg) / 1e6)
    product_kg = product_mass_mg / 1e6  # mg → kg
    mof_cost_eur_per_kg = total_scaled_cost_eur / product_kg
    mof_cost_usd_per_kg = mof_cost_eur_per_kg * eur_to_usd

    return {
        "mof_cost_usd_per_kg": mof_cost_usd_per_kg,  # No rounding in backend
        "mof_cost_eur_per_kg": mof_cost_eur_per_kg,  # No rounding in backend
        "linker_name": resolved_linker_name,  # Return linker name yang di-lookup dari SMILES
        # Debug info
        "raw_costs": {
            "metal_eur": metal_cost_eur,  # No rounding
            "linker_eur": linker_cost_eur,  # No rounding
            "solvent_eur": solvent_cost_eur,  # No rounding
            "additive_eur": additive_cost_eur,  # No rounding
            "modulator_eur": modulator_cost_eur  # No rounding
        },
        "scale_factors": {
            "general": scale_factor,  # No rounding
            "linker": scale_factor_linker  # No rounding
        },
        "scaled_costs": {
            "metal_eur": metal_cost_scaled,  # No rounding
            "linker_eur": linker_cost_scaled,  # No rounding
            "solvent_eur": solvent_cost_scaled,  # No rounding
            "additive_eur": additive_cost_scaled,  # No rounding
            "modulator_eur": modulator_cost_scaled  # No rounding
        },
        "total_scaled_eur": total_scaled_cost_eur,  # No rounding
        "product_kg": product_kg  # No rounding
    }

# =====================================================================
# DATABASE PROPERTI KIMIA (Sesuai dengan source_data di old_model)
# Sumber: PubChem, NIST, Sigma Aldrich @298.15K
# Format: (density g/mL, Cp J/mol·K, Mr g/mol)
# =====================================================================

# Default concentration untuk modulator (aqueous solution)
MODULATOR_DEFAULT_CONCENTRATION = {
    "HNO3": 6.5,      # 6.5% dilute nitric acid (typical for MOF synthesis)
    "hno3": 6.5,
    "HCl": 0.054,     # 0.054% dilute hydrochloric acid (based on use case 4)
    "hcl": 0.054,
    "HBF4": 48.0,     # 48% tetrafluoroboric acid
    "hbf4": 48.0,
    "AcOH": 100.0,    # Glacial acetic acid (pure)
    "acoh": 100.0,
    "CH3COOH": 100.0, # Glacial acetic acid (pure)
    "ch3cooh": 100.0,
    "H3PMo12O40": 100.0,  # Solid
    "h3pmo12o40": 100.0,
    "NaOH": 50.0,     # 50% sodium hydroxide solution
    "naoh": 50.0,
    "Triethylamine": 100.0,  # Pure liquid
    "triethylamine": 100.0,
    "TEA": 100.0,     # Pure liquid
    "tea": 100.0,
    "EG": 100.0,      # Pure ethylene glycol
    "eg": 100.0,
    "Dioxane": 100.0, # Pure liquid
    "dioxane": 100.0,
    "C4H8O2": 100.0,  # Pure liquid
    "c4h8o2": 100.0,
    "H2O": 100.0,     # Pure water
    "h2o": 100.0,
    "water": 100.0,
    "-": 100.0,
}

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
    "c4h8o2":        (1.036,  147.9,   88.1051),
    "acoh":          (1.0446, 123.1,   60.0520),
    "ch3cooh":       (1.0446, 123.1,   60.0520),
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

def get_chem_prop(name: str, is_metal=False, volume_ml: float = None):
    """
    Mencari nilai rho (g/mL), Cp (J/mol·K), dan Mr (g/mol) dari database.
    Menggunakan exact match dari source_data old_model (PubChem/NIST @298.15K).
    
    Parameters:
        name: Chemical name
        is_metal: True for metal salts
        volume_ml: Volume in mL (used for concentration-dependent Cp, e.g., HNO3)
    
    Returns: (density_g_ml, cp_J_mol_K, mr_g_mol)
    """
    if not name or name == "-" or name == "0":
        return 0.0, 0.0, 1.0
    
    n = _normalize_chem_name(name)
    
    # Exact match di database
    if n in CHEM_PROP_DB:
        rho, cp, mr = CHEM_PROP_DB[n]
        return rho, cp, mr
    
    # Fuzzy match: cek apakah key ada di dalam nama
    for key, props in CHEM_PROP_DB.items():
        if key in n or n in key:
            rho, cp, mr = props
            return rho, cp, mr
    
    # Fallback default
    if is_metal:
        return 1.0, 100.0, 200.0
    return 1.0, 75.0, 100.0

def calculate_energy(smiles: str, temperature_c: float, reaction_time_h: float,
                     linker_mass_mg: float = 50.0, metal_mass_mg: float = 100.0,
                     solvent_name: str = "-", solvent_volume_ml: float = 0.0,
                     additive_name: str = "-", additive_volume_ml: float = 0.0,
                     modulator_name: str = "-", modulator_volume_ml: float = 0.0,
                     modulator_concentration: float = None,  # % concentration (None = use default)
                     metal_name: str = "-",
                     volumetric_wc: float = 40.0, gravimetric_wc: float = 5.5,
                     product_mass_mg: float = 50.0,
                     energy_scale_factor: float = 1.0) -> dict:
    """
    Hitung energi pemanasan dengan rumus EXACT dari old_model:
    Qheat = Total_Sensible_Energy / (heat_eff * V_Reactor) * 1000 / 1e6
    
    Formula sesuai dengan notebook asli:
    - V_Reactor = 1.2 * V_MOF (L) dimana V_MOF = g_MOF / Density_MOF
    - Density_MOF = volumetric_wc / (gravimetric_wc * 100)
    - Qheat_J_per_L_reactor = Total_Sensible / (0.75 * V_Reactor)
    - Qheat_MJ_1000L = Qheat_J_per_L_reactor * 1000 / 1e6
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
    rho_mod, cp_mod_mol_k, mr_mod = get_chem_prop(modulator_name, volume_ml=modulator_volume_ml)
    _, cp_metal_mol_k, mr_metal = get_chem_prop(metal_name, is_metal=True)
    
    # ====== APPLY DEFAULT MODULATOR CONCENTRATION ======
    # Jika modulator_concentration tidak di-specify (None atau 0), gunakan default
    if modulator_concentration is None or modulator_concentration == 0:
        # Cari default concentration berdasarkan nama modulator
        modulator_key = _normalize_chem_name(modulator_name)
        modulator_concentration = MODULATOR_DEFAULT_CONCENTRATION.get(modulator_key, 100.0)

    # ====== KALKULASI MOLES ======
    # HANYA HITUNG JIKA VOLUME/MASS > 0
    
    # Solvent: dari volume
    if solvent_volume_ml > 0:
        m_solv_g = solvent_volume_ml * rho_solv
        n_solv = m_solv_g / mr_solv  # mol
    else:
        m_solv_g = 0.0
        n_solv = 0.0
    
    # Additive: dari volume
    if additive_volume_ml > 0:
        m_add_g = additive_volume_ml * rho_add
        n_add = m_add_g / mr_add  # mol
    else:
        m_add_g = 0.0
        n_add = 0.0
    
    # Modulator: dari volume dengan concentration factor
    if modulator_volume_ml > 0:
        m_mod_g = modulator_volume_ml * rho_mod
        # Apply concentration factor - if modulator is diluted, effective moles are reduced
        concentration_factor = modulator_concentration / 100.0  # convert % to fraction
        n_mod = (m_mod_g / mr_mod) * concentration_factor  # mol (adjusted for concentration)
    else:
        m_mod_g = 0.0
        concentration_factor = 0.0
        n_mod = 0.0
    
    # Metal: dari mass
    if metal_mass_mg > 0:
        n_metal = (metal_mass_mg / 1000.0) / mr_metal  # mg → g → mol
    else:
        n_metal = 0.0
    
    # Linker: dari mass
    if linker_mass_mg > 0:
        n_linker = (linker_mass_mg / 1000.0) / linker_mw  # mg → g → mol
    else:
        n_linker = 0.0

    # ====== KALKULASI ENERGI SENSIBLE (Joule) ======
    # Q = n × CP × ΔT
    # MURNI MATEMATIS - TIDAK ADA SCALE FACTOR
    e_solv = n_solv * cp_solv_mol_k * delta_t
    e_add = n_add * cp_add_mol_k * delta_t
    e_mod = n_mod * cp_mod_mol_k * delta_t
    e_metal = n_metal * cp_metal_mol_k * delta_t
    e_linker = n_linker * cp_linker_mol_k * delta_t
    
    e_sens_total = e_solv + e_add + e_mod + e_metal + e_linker

    # ====== GLOBAL ENERGY METRICS (EXACT sesuai old_model) ======
    heat_eff = 0.75
    t_seconds = reaction_time_h * 3600.0
    
    # --- V_Reactor calculation - FORMULA ASLI dari old_model ---
    # PENTING: Formula dari notebook adalah:
    # Density_MOF (g/L) = volumetric_wc / (gravimetric_wc * 100)
    # BUKAN volumetric_wc / (gravimetric_wc / 100)
    if gravimetric_wc > 0 and product_mass_mg > 0:
        density_mof_g_per_l = volumetric_wc / (gravimetric_wc * 100.0)  # g/L - FIXED!
        g_mof = product_mass_mg / 1000.0  # mg → g
        v_mof_l = g_mof / density_mof_g_per_l  # L
        v_reactor_l = 1.2 * v_mof_l  # FORMULA ASLI
    else:
        # Fallback jika tidak ada data
        v_reactor_l = 0.1  # minimum 100 mL
        density_mof_g_per_l = 100.0
        g_mof = product_mass_mg / 1000.0 if product_mass_mg > 0 else 0.001
        v_mof_l = g_mof / density_mof_g_per_l
    
    # Calculate liquid volume for debugging
    v_liquid_l = (solvent_volume_ml + additive_volume_ml + modulator_volume_ml) / 1000.0
    
    # Formula EXACT dari notebook
    # Qheat_MJ_1000L = (E_sens / (heat_eff * V_Reactor)) * 1000 / 1e6
    if v_reactor_l > 0 and e_sens_total > 0:
        qheat_j_per_l_reactor = e_sens_total / (heat_eff * v_reactor_l)
        qheat_mj_1000l = qheat_j_per_l_reactor * 1000.0 / 1_000_000.0
    else:
        qheat_j_per_l_reactor = 0.0
        qheat_mj_1000l = 0.0
    
    # --- Qloss (MJ) ---
    # old_model: Qloss = U*A × ΔT × t / (heat_eff × 1e6)
    # U*A = 3.303 W/K
    u_a = 3.303
    q_loss_mj = (u_a * delta_t * t_seconds) / (heat_eff * 1_000_000)
    
    # --- Estirr (MJ) ---
    # old_model: Estirr = 0.015985 × Density_Tot(g/L) × Time(h) × 3600 / 1e6
    # Density_Tot = m_total(g) / V_liquid(L)
    v_liquid_l = (solvent_volume_ml + additive_volume_ml + modulator_volume_ml) / 1000.0
    m_liquid_g = m_solv_g + m_add_g + m_mod_g
    m_solid_g = ((metal_mass_mg if metal_mass_mg > 0 else 0.0) + 
                 (linker_mass_mg if linker_mass_mg > 0 else 0.0)) / 1000.0
    m_total_g = m_liquid_g + m_solid_g
    
    if v_liquid_l > 0:
        density_total = m_total_g / v_liquid_l  # g/L
    else:
        density_total = 0.0  # Tidak ada liquid
    
    stirr_coeff = 0.0162
    if density_total > 0 and reaction_time_h > 0:
        e_stirr_mj = (stirr_coeff * density_total * reaction_time_h * 3600) / 1_000_000.0
    else:
        e_stirr_mj = 0.0
    
    e_total_mj = qheat_mj_1000l + q_loss_mj + e_stirr_mj
    
    return {
        "cp_value": round(cp_linker_mol_k, 2),
        "linker_mw": round(linker_mw, 4),
        "e_sensible_solvent_j": round(e_solv, 2),
        "e_sensible_additive_j": round(e_add, 2),
        "e_sensible_modulator_j": round(e_mod, 2),
        "e_sensible_metal_j": round(e_metal, 2),
        "e_sensible_linker_j": round(e_linker, 2),
        "e_sensible_total_j": round(e_sens_total, 2),
        "q_energy_mj": qheat_mj_1000l,  # No rounding in backend
        "e_total_mj": e_total_mj,       # No rounding in backend
        "q_loss_mj": q_loss_mj,        # No rounding in backend
        "e_stirr_mj": e_stirr_mj,      # No rounding in backend
        "v_reactor_l": round(v_reactor_l, 6),  # untuk debugging
        # Debug info tambahan
        "debug_info": {
            "density_mof_g_per_l": round(density_mof_g_per_l, 2),
            "g_mof": round(g_mof, 6),
            "v_mof_l": round(v_mof_l, 6),
            "v_liquid_l": round(v_liquid_l, 6),
            "m_total_g": round(m_total_g, 4),
            "density_total": round(density_total, 2),
            "delta_t": round(delta_t, 2),
            # Molar calculations
            "n_solv": round(n_solv, 6),
            "n_add": round(n_add, 6),
            "n_mod": round(n_mod, 6),
            "n_metal": round(n_metal, 6),
            "n_linker": round(n_linker, 6),
            # Chemical properties
            "solv_props": (round(rho_solv, 4), round(cp_solv_mol_k, 2), round(mr_solv, 4)),
            "mod_props": (round(rho_mod, 4), round(cp_mod_mol_k, 2), round(mr_mod, 4)),
            "metal_props": (round(cp_metal_mol_k, 2), round(mr_metal, 4)),
            "modulator_concentration": modulator_concentration,
            "concentration_factor": round(concentration_factor, 4)
        }
    }

def calculate_storage_cost(mof_cost_usd_per_kg: float, gravimetric_wc: float) -> float:
    """
    Hitung storage cost (USD/kg H2) berdasarkan harga MOF dan Uptake H2.
    
    Formula: Storage Cost = MOF Cost / (Gravimetric WC / 100)
    """
    if gravimetric_wc <= 0: 
        return 99999.0  # Return high but finite value instead of infinity
    
    storage_cost = mof_cost_usd_per_kg / (gravimetric_wc / 100.0)
    
    # Batasi storage cost maksimal untuk mencegah nilai yang tidak realistis
    max_storage_cost = 50000.0  # Maksimal 50,000 USD/kg H2
    if storage_cost > max_storage_cost:
        storage_cost = max_storage_cost
    
    return storage_cost  # No rounding in backend

def run_economic_analysis(metal_name: str, linker_smiles: str = None,
                           reaction_time: float = 24.0, temperature: float = 120.0,
                           smiles: str = "",
                           linker_name: str = None,
                           gravimetric_wc: float = None,
                           volumetric_wc: float = None,
                           product_mass_mg: float = 50.0,
                           metal_mass_mg: float = 100.0,
                           linker_mass_mg: float = 50.0,
                           solvent_name: str = "-", solvent_volume_ml: float = 0.0,
                           additive_name: str = "-", additive_volume_ml: float = 0.0,
                           modulator_name: str = "-", modulator_volume_ml: float = 0.0,
                           modulator_concentration: float = None,
                           energy_scale_factor: float = 1.0) -> dict:
    """Run economic analysis with strict validation and explicit chemistry errors."""
    smiles_normalized = validate_smiles_or_raise(smiles)

    if reaction_time <= 0:
        raise ValueError("reaction_time harus lebih besar dari 0")
    if temperature <= 0:
        raise ValueError("temperature harus lebih besar dari 0")
    if product_mass_mg <= 0:
        raise ValueError("product_mass_mg harus lebih besar dari 0")
    if metal_mass_mg <= 0:
        raise ValueError("metal_mass_mg harus lebih besar dari 0")
    if linker_mass_mg <= 0:
        raise ValueError("linker_mass_mg harus lebih besar dari 0")
    if solvent_volume_ml < 0 or additive_volume_ml < 0 or modulator_volume_ml < 0:
        raise ValueError("volume tidak boleh negatif")

    uptake_data = get_uptake_data()
    if smiles_normalized in uptake_data:
        uptake_info = uptake_data[smiles_normalized]
        if gravimetric_wc is None:
            gravimetric_wc = uptake_info.get("gravimetric_wc_percent", 5.5)
        if volumetric_wc is None:
            volumetric_wc = uptake_info.get("volumetric_wc_g_per_l", 40.0)
    else:
        if gravimetric_wc is None or volumetric_wc is None:
            raise ValueError("SMILES tidak ditemukan di uptake database. Berikan gravimetric_wc dan volumetric_wc.")

    cost_result = calculate_mof_cost(
        metal_name,
        linker_smiles,
        linker_name=linker_name,
        metal_mass_mg=metal_mass_mg,
        linker_mass_mg=linker_mass_mg,
        product_mass_mg=product_mass_mg,
        solvent_name=solvent_name,
        solvent_volume_ml=solvent_volume_ml,
        additive_name=additive_name,
        additive_volume_ml=additive_volume_ml,
        modulator_name=modulator_name,
        modulator_volume_ml=modulator_volume_ml,
    )

    mof_cost = cost_result["mof_cost_usd_per_kg"]
    storage_cost = calculate_storage_cost(mof_cost, gravimetric_wc)
    energy_result = calculate_energy(
        smiles_normalized,
        temperature,
        reaction_time,
        linker_mass_mg=linker_mass_mg,
        metal_mass_mg=metal_mass_mg,
        solvent_name=solvent_name,
        solvent_volume_ml=solvent_volume_ml,
        additive_name=additive_name,
        additive_volume_ml=additive_volume_ml,
        modulator_name=modulator_name,
        modulator_volume_ml=modulator_volume_ml,
        modulator_concentration=modulator_concentration,
        metal_name=metal_name,
        volumetric_wc=volumetric_wc,
        gravimetric_wc=gravimetric_wc,
        product_mass_mg=product_mass_mg,
        energy_scale_factor=energy_scale_factor,
    )

    is_feasible = (
        mof_cost <= MAX_MOF_COST
        and storage_cost <= MAX_STORAGE_COST
        and reaction_time <= MAX_REACTION_TIME
        and temperature <= MAX_TEMPERATURE
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
            "temperature_ok": temperature <= MAX_TEMPERATURE,
        },
    }
