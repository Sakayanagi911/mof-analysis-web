import numpy as np
from rdkit import Chem
from collections import defaultdict

# =====================================================================
# JOBACK METHOD DATABASE (Sesuai dengan Hybrid Physics ML Notebook)
# =====================================================================

JOBACK_CP_GROUPS = {
     # --- Non-ring increments ---
    "CH3":   {"smarts": "[CH3X4]", "a": 1.95E+01, "b": -8.08E-03, "c": 1.53E-04, "d": -9.67E-08},
    "CH2":   {"smarts": "[CH2X4]", "a": -9.09E-01, "b": 9.50E-02, "c": -5.44E-05, "d": 1.19E-08},
    "CH":    {"smarts": "[CHX4]",  "a": -2.30E+01, "b": 2.04E-01, "c": -2.65E-04, "d": 1.20E-07},
    "C":     {"smarts": "[CX4]",   "a": -6.62E+01, "b": 4.27E-01, "c": -6.41E-04, "d": 3.01E-07},
    "CH2=":  {"smarts": "[CH2]=[CX3]", "a": 2.36E+01, "b": -3.81E-02, "c": 1.72E-04, "d": -1.03E-07},
    "CH=":   {"smarts": "[CH]=[CX3]",  "a": -8.00E+00, "b": 1.05E-01, "c": -9.63E-05, "d": 3.56E-08},
    "C=":    {"smarts": "[CX3](=[CX3])([!#1])", "a": -2.81E+01, "b": 2.08E-01, "c": -3.06E-04, "d": 1.46E-07},
    "C=C":   {"smarts": "[CX3]=[CX3]", "a": 2.74E+01, "b": -5.57E-02, "c": 1.01E-04, "d": -5.02E-08},
    "C#C":   {"smarts": "[CX2]#C",     "a": 7.87E+00, "b": 2.01E-02, "c": -8.33E-06, "d": 1.39E-09},

     # --- Ring increments ---
    "ring_CH2": {"smarts": "[CH2R]", "a": -6.03E+00, "b": 8.54E-02, "c": -8.00E-06, "d": -1.80E-08},
    "ring_CH":  {"smarts": "[CHR]",  "a": -2.05E+01, "b": 1.62E-01, "c": -1.60E-04, "d": 6.24E-08},
    "ring_C":   {"smarts": "[CRX4]", "a": -9.09E+01, "b": 5.57E-01, "c": -9.00E-04, "d": 4.69E-07},
    "ring_cH":  {"smarts": "[cH]",    "a": -2.14E+00, "b": 5.74E-02, "c": -1.64E-06, "d": -1.59E-08},
    "ring_c":   {"smarts": "[c]",     "a": -8.25E+00, "b": 1.01E-01, "c": -1.42E-04, "d": 6.78E-08},

     # --- Halogen increments ---
    "F":  {"smarts": "[F]",  "a": 2.65E+01, "b": -9.13E-02, "c": 1.91E-04, "d": -1.03E-07},
    "Cl": {"smarts": "[Cl]", "a": 3.33E+01, "b": -9.63E-02, "c": 1.87E-04, "d": -9.96E-08},
    "Br": {"smarts": "[Br]", "a": 2.86E+01, "b": -6.49E-02, "c": 1.36E-04, "d": -7.45E-08},
    "I":  {"smarts": "[I]",  "a": 3.21E+01, "b": -6.41E-02, "c": 1.26E-04, "d": -6.87E-08},

     # --- Oxygen increments ---
    "OH_alcohol": {"smarts": "[OX2H]", "a": 2.57E+01, "b": -6.91E-02, "c": 1.77E-04, "d": -9.88E-08},
    "OH_phenol":  {"smarts": "[cOX2H]", "a": -2.81E+00, "b": 1.11E-01, "c": -1.16E-04, "d": 4.94E-08},
    "O_nonring":  {"smarts": "[OX2]", "a": 2.55E+01, "b": -6.32E-02, "c": 1.11E-04, "d": -5.48E-08},
    "O_ring":     {"smarts": "[OX2R0]", "a": 1.22E+01, "b": -1.26E-02, "c": 6.03E-05, "d": -3.86E-08},
    "CO_nonring": {"smarts": "[CX3]=[OX1]", "a": 6.45E+00, "b": 6.70E-02, "c": -3.57E-05, "d": 2.86E-09},
    "CO_ring":    {"smarts": "[CX3R]=[OX1]", "a": 3.04E+01, "b": -8.29E-02, "c": 2.36E-04, "d": -1.31E-07},
    "CHO":        {"smarts": "[CH]=[OX1]", "a": 3.09E+01, "b": -3.36E-02, "c": 1.60E-04, "d": -9.88E-08},
    "COOH":       {"smarts": "[CX3](=O)[OX2H1]", "a": 2.41E+01, "b": 4.27E-02, "c": 8.04E-05, "d": -6.87E-08},
    "COOR":       {"smarts": "[CX3](=O)[OX2]", "a": 2.45E+01, "b": 4.02E-02, "c": 4.02E-05, "d": -4.52E-08},
    "C=O_other":  {"smarts": "[OX1]=[CX3]", "a": 6.82E+00, "b": 1.96E-02, "c": 1.27E-05, "d": -1.78E-08},

     # --- Aromatic Nitrogen ---
     "ring_n":  {"smarts": "[n]",   "a": -4.00E+00, "b": 8.50E-02, "c": -1.10E-04, "d": 4.20E-08},
     "ring_nH": {"smarts": "[nH]",  "a":  5.00E+00, "b": 6.20E-02, "c": -9.50E-05, "d": 3.80E-08},
     "NH2_ar": {"smarts": "[NX3H2;R]", "a": 2.69E+01, "b": -4.12E-02, "c": 1.64E-04, "d": -9.76E-08},

     # --- Nitrogen increments ---
     "NH2":        {"smarts": "[NX3H2;!R]", "a": 2.69E+01, "b": -4.12E-02, "c": 1.64E-04, "d": -9.76E-08},
     "NH_nonring": {"smarts": "[NX3H]", "a": -1.21E+00, "b": 7.62E-02, "c": -4.86E-05, "d": 1.05E-08},
     "NH_ring":    {"smarts": "[NX3H;R]", "a": 1.18E+01, "b": -2.30E-02, "c": 1.07E-04, "d": -6.28E-08},
     "N_nonring":  {"smarts": "[NX3]", "a": -3.11E+01, "b": 2.27E-01, "c": -3.20E-04, "d": 1.46E-07},
     "N=_nonring": {"smarts": "[NX2]=[CX3]", "a": 0.00E+00, "b": 0.00E+00, "c": 0.00E+00, "d": 0.00E+00},
     "N=_ring":    {"smarts": "[NX2;R]=[CX3]", "a": 8.83E+00, "b": -3.84E-03, "c": 4.35E-05, "d": -2.60E-08},
     "NH=":        {"smarts": "[NH]=[CX3]", "a": 5.69E+00, "b": -4.12E-03, "c": 1.28E-04, "d": -8.88E-08},
     "CN":         {"smarts": "[CX2]#N", "a": 3.65E+01, "b": -7.33E-02, "c": 1.84E-04, "d": -1.03E-07},
     "NO2":        {"smarts": "[N+](=O)[O-]", "a": 2.59E+01, "b": -3.74E-03, "c": 1.29E-04, "d": -8.88E-08},

     # --- Sulfur increments ---
    "SH":         {"smarts": "[SX2H]", "a": 3.53E+01, "b": -7.58E-02, "c": 1.85E-04, "d": -1.03E-07},
    "S_nonring":  {"smarts": "[SX2]", "a": 1.96E+01, "b": -5.61E-03, "c": 4.02E-05, "d": -2.76E-08},
    "S_ring":     {"smarts": "[SX2;R]", "a": 1.67E+01, "b": 4.81E-03, "c": 2.77E-05, "d": -2.11E-08},
}

# COMPILE SMARTS
joback_patterns = {}
for name, info in JOBACK_CP_GROUPS.items():
    joback_patterns[name] = Chem.MolFromSmarts(info["smarts"])

def count_joback_groups_no_overlap(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    used_atoms = set()
    counts = {}
    atom_hits = defaultdict(list)

    # PRIORITY ORDER (Persis sesuai Notebook Hybrid Physics ML)
    priority = [
   "COOH","COOR","CHO","CO_nonring",
   "OH_phenol","OH_alcohol",

   "ring_nH","ring_n",
   "NH2_ar","NH_ring","NH2","NH_nonring","N_nonring",

   "ring_cH","ring_c","ring_CH2","ring_CH","ring_C",
   "CH3","CH2","CH","C",
   "CH2=","CH=","C=","C=C","C#C",
   "F","Cl","Br","I",
   "CN",
   "SH","S_nonring"
    ]

    for name in priority:
        patt = joback_patterns.get(name)
        if patt is None:
            continue

        matches = mol.GetSubstructMatches(patt)
        for match in matches:
            if any(a in used_atoms for a in match):
                continue

            counts[name] = counts.get(name, 0) + 1
            for a in match:
                used_atoms.add(a)
                atom_hits[a].append(name)

    return counts

def calculate_cp_joback(smiles: str, T: float = 298.15):
    """
    Menghitung kapasitas panas ideal gas (Cp) menggunakan metode Joback.
    Rumus: Cp = (Σ nᵢ·aᵢ − 37.93) + (Σ nᵢ·bᵢ + 0.210)·T
              + (Σ nᵢ·cᵢ − 3.91×10⁻⁴)·T² + (Σ nᵢ·dᵢ + 2.06×10⁻⁷)·T³
    
    Konstanta universal (-37.93, +0.21, -3.91e-4, +2.06e-7) diterapkan SEKALI
    ke total sum, BUKAN per-grup.
    Ref: Reid, Prausnitz & Poling, "Properties of Gases and Liquids"
    
    Returns:
        float: Cp dalam J/(mol·K)
    """
    res = count_joback_groups_no_overlap(smiles)
    if res is None:
        return 150.0  # Fallback

    counts = res
    if len(counts) == 0:
        return 150.0  # Fallback

    # Akumulasi kontribusi grup terlebih dahulu
    sum_a, sum_b, sum_c, sum_d = 0.0, 0.0, 0.0, 0.0
    for g, n in counts.items():
        if g in JOBACK_CP_GROUPS and n > 0:
            grp = JOBACK_CP_GROUPS[g]
            sum_a += n * grp["a"]
            sum_b += n * grp["b"]
            sum_c += n * grp["c"]
            sum_d += n * grp["d"]

    # Konstanta universal diterapkan per grup, sesuai dengan notebook old_model
    Cp = 0.0
    for g, n in counts.items():
        if g in JOBACK_CP_GROUPS and n > 0:
            grp = JOBACK_CP_GROUPS[g]
            Cp += n * (
                grp["a"] - 37.93
                + (grp["b"] + 0.210) * T
                + (grp["c"] - 3.91e-04) * T**2
                + (grp["d"] + 2.06e-07) * T**3
            )

    return Cp if Cp > 0 else 150.0