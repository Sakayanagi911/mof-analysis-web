"""
Modul Joback Group Contribution untuk menghitung Cp dari SMILES.
Referensi: old_model/Hybrid Physics ML for Residual Heat Capacity Prediction.ipynb

Metode Joback menggunakan kontribusi gugus fungsional untuk mengestimasi
Heat Capacity (Cp) dari molekul berdasarkan struktur SMILES-nya.
"""

try:
    from rdkit import Chem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


# Definisi gugus Joback dengan koefisien a, b, c, d
# Cp(T) = Σ (n_i × (a_i + b_i*T + c_i*T² + d_i*T³))  [J/(mol·K)]
# T dalam Kelvin

JOBACK_CP_GROUPS = {
    # Nama Gugus: {smarts, a, b, c, d}
    # ---- Grup Non-Ring ----
    "-CH3":     {"smarts": "[CX4H3]",  "a": 19.5,  "b": -8.08e-3, "c": 1.53e-4,  "d": -9.67e-8},
    "-CH2-":    {"smarts": "[CX4H2;!r]",  "a": -0.909,"b": 9.50e-2,  "c": -5.44e-5, "d": 1.19e-8},
    ">CH-":     {"smarts": "[CX4H1;!r]",  "a": -23.0, "b": 2.04e-1,  "c": -2.65e-4, "d": 1.20e-7},
    ">C<":      {"smarts": "[CX4H0;!r]",  "a": -66.2, "b": 4.27e-1,  "c": -6.41e-4, "d": 3.01e-7},
    "=CH2":     {"smarts": "[CX3H2]=[CX3]", "a": 23.6,  "b": -3.81e-2, "c": 1.72e-4,  "d": -1.03e-7},
    "=CH-":     {"smarts": "[CX3H1;!r]=[CX3]", "a": -8.0,  "b": 1.05e-1,  "c": -9.63e-5, "d": 3.56e-8},
    "=C<":      {"smarts": "[CX3H0;!r](=[CX3])", "a": -28.1, "b": 2.08e-1,  "c": -3.06e-4, "d": 1.46e-7},
    "-OH (alcohol)": {"smarts": "[OX2H][CX4]", "a": 25.7,  "b": -6.91e-2, "c": 1.77e-4,  "d": -9.88e-8},
    "-OH (phenol)":  {"smarts": "[OX2H][c]",    "a": -2.81, "b": 1.11e-1,  "c": -1.16e-4, "d": 4.94e-8},
    "-O- (non-ring)":{"smarts": "[OX2H0;!r]","a": 25.5,  "b": -6.32e-2, "c": 1.11e-4,  "d": -5.48e-8},
    ">C=O (non-ring)":{"smarts":"[CX3H0;!r](=O)", "a": 6.45, "b": 6.70e-2, "c": -3.57e-5, "d": 2.86e-9},
    "-CHO (aldehyde)":{"smarts":"[CX3H1](=O)", "a": 30.9, "b": -3.36e-2, "c": 1.60e-4,  "d": -9.88e-8},
    "-COOH":    {"smarts": "[CX3](=O)[OX2H]", "a": 24.1,  "b": 4.27e-2,  "c": 8.04e-5,  "d": -6.87e-8},
    "-COO- (ester)": {"smarts": "[CX3](=O)[OX2H0]", "a": 24.5, "b": 4.02e-2, "c": 4.02e-5, "d": -4.52e-8},
    "-NH2":     {"smarts": "[NX3H2]",  "a": 26.9,  "b": -4.12e-2, "c": 1.64e-4,  "d": -9.76e-8},
    ">NH (non-ring)":{"smarts": "[NX3H1;!r]", "a": -1.21, "b": 7.62e-2, "c": -4.86e-5, "d": 1.05e-8},
    "-N= (non-ring)":{"smarts": "[NX2;!r]",   "a": 11.8,  "b": -2.30e-2, "c": 1.07e-4,  "d": -6.28e-8},
    "-F":       {"smarts": "[FX1]",    "a": 26.5,  "b": -9.13e-2, "c": 1.91e-4,  "d": -1.03e-7},
    "-Cl":      {"smarts": "[ClX1]",   "a": 33.3,  "b": -9.63e-2, "c": 1.87e-4,  "d": -9.96e-8},
    "-Br":      {"smarts": "[BrX1]",   "a": 28.6,  "b": -6.49e-2, "c": 1.36e-4,  "d": -7.45e-8},
    "-I":       {"smarts": "[IX1]",    "a": 32.1,  "b": -6.41e-2, "c": 1.26e-4,  "d": -6.87e-8},
    # ---- Grup Ring ----
    "-CH2- (ring)":  {"smarts": "[CX4H2;r]",  "a": -6.03, "b": 8.54e-2,  "c": -8.00e-6, "d": -1.80e-8},
    ">CH- (ring)":   {"smarts": "[CX4H1;r]",  "a": -20.7, "b": 1.54e-1,  "c": -1.54e-4, "d": 5.13e-8},
    ">C< (ring)":    {"smarts": "[CX4H0;r]",  "a": -90.9, "b": 5.57e-1,  "c": -9.00e-4, "d": 4.69e-7},
    "=CH- (ring)":   {"smarts": "[cX3H1]",    "a": -2.14, "b": 5.74e-2,  "c": -1.64e-6, "d": -1.59e-8},
    "=C< (ring)":    {"smarts": "[cX3H0]",    "a": -8.25, "b": 1.01e-1,  "c": -1.42e-4, "d": 6.78e-8},
    "-O- (ring)":    {"smarts": "[OX2H0;r]",  "a": 12.2,  "b": -1.26e-2, "c": 6.03e-5,  "d": -3.86e-8},
    ">C=O (ring)":   {"smarts": "[CX3H0;r](=O)", "a": -2.81, "b": 8.11e-2, "c": -4.86e-5, "d": 1.05e-8},
    "-NH- (ring)":   {"smarts": "[NX3H1;r]",  "a": 8.83,  "b": -3.84e-3, "c": 4.35e-5,  "d": -2.60e-8},
    "-N= (ring)":    {"smarts": "[nX2]",       "a": 5.69,  "b": -4.12e-3, "c": 1.28e-5,  "d": -8.88e-9},
    "-S- (ring)":    {"smarts": "[SX2;r]",     "a": 6.45,  "b": 6.70e-2,  "c": -3.57e-5, "d": 2.86e-9},

    
}

# Lookup table Cp untuk SMILES umum linker MOF (fallback jika rdkit tidak tersedia)
# Nilai Cp pada 298.15 K dalam J/(mol·K)
KNOWN_CP_VALUES = {
    "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O": 186.0,    # H3BTC (Trimesic acid)
    "OC(=O)c1ccc(cc1)C(O)=O": 144.0,               # H2BDC (Terephthalic acid)
    "Oc1cc(O)c(cc1C(O)=O)C(O)=O": 170.0,            # H4DOBDC
    "OC(=O)c1ccc(-c2ccc(cc2)C(O)=O)cc1": 220.0,     # BPDC
}


def count_joback_groups(smiles: str) -> dict:
    """
    Hitung jumlah masing-masing gugus Joback pada molekul.

    Args:
        smiles: String SMILES dari molekul

    Returns:
        dict: {nama_gugus: jumlah}
    """
    if not RDKIT_AVAILABLE:
        raise ImportError("rdkit tidak tersedia untuk analisis SMILES")

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"SMILES tidak valid: {smiles}")

    # Tambah hidrogen eksplisit agar match pattern lebih akurat
    mol = Chem.AddHs(mol)

    counts = {}
    used_atoms = set()

    # Urutkan berdasarkan spesifisitas (grup yang lebih spesifik dulu)
    for name, info in JOBACK_CP_GROUPS.items():
        patt = Chem.MolFromSmarts(info["smarts"])
        if patt is None:
            continue
        matches = mol.GetSubstructMatches(patt)
        n = 0
        for match in matches:
            # Hindari double-counting: cek apakah atom utama sudah terpakai
            primary = match[0]
            if primary not in used_atoms:
                n += 1
                used_atoms.add(primary)
        if n > 0:
            counts[name] = n

    return counts

# --- LIST PRIORITY (Penting untuk Import) ---
PRIORITY = [
    "COOH","COOR","CHO","CO_nonring","CO_ring","C=O_other",
    "OH_phenol","OH_alcohol",
    "NO2","CN","NH2_ar","ring_nH","ring_n","NH_ring","NH2","NH_nonring","N_nonring","N=_ring","N=_nonring","NH=",
    "ring_cH","ring_c","ring_CH2","ring_CH","ring_C",
    "CH3","CH2","CH","C","CH2=","CH=","C=","C=C","C#C",
    "F","Cl","Br","I",
    "SH","S_nonring","S_ring"
]

def calculate_cp_joback(smiles: str, T: float = 298.15) -> float:
    """
    Hitung Cp (Heat Capacity) pada temperatur T menggunakan metode Joback.

    Cp(T) = Σ n_i × (a_i + b_i×T + c_i×T² + d_i×T³)

    Jika rdkit tidak tersedia, gunakan lookup table untuk SMILES yang dikenal.

    Args:
        smiles: String SMILES
        T: Temperatur dalam Kelvin (default 298.15 K)

    Returns:
        float: Cp dalam J/(mol·K), atau None jika gagal
    """
    # Coba gunakan rdkit terlebih dahulu
    if RDKIT_AVAILABLE:
        try:
            counts = count_joback_groups(smiles)
        except (ValueError, Exception):
            # Fallback ke lookup table
            return KNOWN_CP_VALUES.get(smiles)

        Cp = 0.0
        for group_name, n in counts.items():
            if group_name in JOBACK_CP_GROUPS and n > 0:
                info = JOBACK_CP_GROUPS[group_name]
                a, b, c, d = info["a"], info["b"], info["c"], info["d"]
                Cp += n * (a + b*T + c*T**2 + d*T**3)

        return Cp if Cp > 0 else None

    # Fallback: gunakan lookup table jika rdkit tidak tersedia
    base_cp = KNOWN_CP_VALUES.get(smiles)
    if base_cp is not None:
        # Skalakan Cp sederhana berdasarkan rasio temperatur
        # (approximasi kasar tanpa rdkit)
        T_ref = 298.15
        return base_cp * (T / T_ref) ** 0.3

    return None
