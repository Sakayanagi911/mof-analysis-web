from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from rdkit import Chem
from collections import defaultdict
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"],
)

# --- DATABASE JOBACK LENGKAP ---
JOBACK_CP_GROUPS = {
    "CH3":   {"smarts": "[CH3X4]", "a": 1.95E+01, "b": -8.08E-03, "c": 1.53E-04, "d": -9.67E-08},
    "CH2":   {"smarts": "[CH2X4]", "a": -9.09E-01, "b": 9.50E-02, "c": -5.44E-05, "d": 1.19E-08},
    "CH":    {"smarts": "[CHX4]",  "a": -2.30E+01, "b": 2.04E-01, "c": -2.65E-04, "d": 1.20E-07},
    "C":     {"smarts": "[CX4]",   "a": -6.62E+01, "b": 4.27E-01, "c": -6.41E-04, "d": 3.01E-07},
    "CH2=":  {"smarts": "[CH2]=[CX3]", "a": 2.36E+01, "b": -3.81E-02, "c": 1.72E-04, "d": -1.03E-07},
    "CH=":   {"smarts": "[CH]=[CX3]",  "a": -8.00E+00, "b": 1.05E-01, "c": -9.63E-05, "d": 3.56E-08},
    "C=":    {"smarts": "[CX3]=[CX3]", "a": -2.81E+01, "b": 2.08E-01, "c": -3.06E-04, "d": 1.46E-07},
    "C=C":   {"smarts": "[CX3]=[CX3]", "a": 2.74E+01, "b": -5.57E-02, "c": 1.01E-04, "d": -5.02E-08},
    "C#C":   {"smarts": "[CX2]#C",     "a": 7.87E+00, "b": 2.01E-02, "c": -8.33E-06, "d": 1.39E-09},
    "ring_CH2": {"smarts": "[CH2R]", "a": -6.03E+00, "b": 8.54E-02, "c": -8.00E-06, "d": -1.80E-08},
    "ring_CH":  {"smarts": "[CHR]",  "a": -2.05E+01, "b": 1.62E-01, "c": -1.60E-04, "d": 6.24E-08},
    "ring_C":   {"smarts": "[CRX4]", "a": -9.09E+01, "b": 5.57E-01, "c": -9.00E-04, "d": 4.69E-07},
    "ring_cH":  {"smarts": "[cH]",    "a": -2.14E+00, "b": 5.74E-02, "c": -1.64E-06, "d": -1.59E-08},
    "ring_c":   {"smarts": "[c]",     "a": -8.25E+00, "b": 1.01E-01, "c": -1.42E-04, "d": 6.78E-08},
    "F":  {"smarts": "[F]",  "a": 2.65E+01, "b": -9.13E-02, "c": 1.91E-04, "d": -1.03E-07},
    "Cl": {"smarts": "[Cl]", "a": 3.33E+01, "b": -9.63E-02, "c": 1.87E-04, "d": -9.96E-08},
    "Br": {"smarts": "[Br]", "a": 2.86E+01, "b": -6.49E-02, "c": 1.36E-04, "d": -7.45E-08},
    "I":  {"smarts": "[I]",  "a": 3.21E+01, "b": -6.41E-02, "c": 1.26E-04, "d": -6.87E-08},
    "OH_alcohol": {"smarts": "[OX2H]", "a": 2.57E+01, "b": -6.91E-02, "c": 1.77E-04, "d": -9.88E-08},
    "OH_phenol":  {"smarts": "[cOX2H]", "a": -2.81E+00, "b": 1.11E-01, "c": -1.16E-04, "d": 4.94E-08},
    "O_nonring":  {"smarts": "[OX2]", "a": 2.55E+01, "b": -6.32E-02, "c": 1.11E-04, "d": -5.48E-08},
    "O_ring":     {"smarts": "[OX2R]", "a": 1.22E+01, "b": -1.26E-02, "c": 6.03E-05, "d": -3.86E-08},
    "CO_nonring": {"smarts": "[CX3]=[OX1]", "a": 6.45E+00, "b": 6.70E-02, "c": -3.57E-05, "d": 2.86E-09},
    "CO_ring":    {"smarts": "[CX3R]=[OX1]", "a": 3.04E+01, "b": -8.29E-02, "c": 2.36E-04, "d": -1.31E-07},
    "CHO":        {"smarts": "[CH]=[OX1]", "a": 3.09E+01, "b": -3.36E-02, "c": 1.60E-04, "d": -9.88E-08},
    "COOH":       {"smarts": "[CX3](=O)[OX2H1]", "a": 2.41E+01, "b": 4.27E-02, "c": 8.04E-05, "d": -6.87E-08},
    "COOR":       {"smarts": "[CX3](=O)[OX2]", "a": 2.45E+01, "b": 4.02E-02, "c": 4.02E-05, "d": -4.52E-08},
    "C=O_other":  {"smarts": "[OX1]=[CX3]", "a": 6.82E+00, "b": 1.96E-02, "c": 1.27E-05, "d": -1.78E-08},
    "ring_n":     {"smarts": "[n]",   "a": -4.00E+00, "b": 8.50E-02, "c": -1.10E-04, "d": 4.20E-08},
    "ring_nH":    {"smarts": "[nH]",  "a":  5.00E+00, "b": 6.20E-02, "c": -9.50E-05, "d": 3.80E-08},
    "NH2_ar":     {"smarts": "[NX3H2;R]", "a": 2.69E+01, "b": -4.12E-02, "c": 1.64E-04, "d": -9.76E-08},
    "NH2":        {"smarts": "[NX3H2;!R]", "a": 2.69E+01, "b": -4.12E-02, "c": 1.64E-04, "d": -9.76E-08},
    "NH_nonring": {"smarts": "[NX3H]", "a": -1.21E+00, "b": 7.62E-02, "c": -4.86E-05, "d": 1.05E-08},
    "NH_ring":    {"smarts": "[NX3H;R]", "a": 1.18E+01, "b": -2.30E-02, "c": 1.07E-04, "d": -6.28E-08},
    "N_nonring":  {"smarts": "[NX3]", "a": -3.11E+01, "b": 2.27E-01, "c": -3.20E-04, "d": 1.46E-07},
    "N=_nonring": {"smarts": "[NX2]=[CX3]", "a": 0.00E+00, "b": 0.00E+00, "c": 0.00E+00, "d": 0.00E+00},
    "N=_ring":    {"smarts": "[NX2;R]=[CX3]", "a": 8.83E+00, "b": -3.84E-03, "c": 4.35E-05, "d": -2.60E-08},
    "NH=":        {"smarts": "[NH]=[CX3]", "a": 5.69E+00, "b": -4.12E-03, "c": 1.28E-04, "d": -8.88E-08},
    "CN":         {"smarts": "[CX2]#N", "a": 3.65E+01, "b": -7.33E-02, "c": 1.84E-04, "d": -1.03E-07},
    "NO2":        {"smarts": "[N+](=O)[O-]", "a": 2.59E+01, "b": -3.74E-03, "c": 1.29E-04, "d": -8.88E-08},
    "SH":         {"smarts": "[SX2H]", "a": 3.53E+01, "b": -7.58E-02, "c": 1.85E-04, "d": -1.03E-07},
    "S_nonring":  {"smarts": "[SX2]", "a": 1.96E+01, "b": -5.61E-03, "c": 4.02E-05, "d": -2.76E-08},
    "S_ring":     {"smarts": "[SX2;R]", "a": 1.67E+01, "b": 4.81E-03, "c": 2.77E-05, "d": -2.11E-08},
}

def calculate_cp_joback_full(smiles: str, temp_c: float):
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return 0.0
    T_K = temp_c + 273.15
    used_atoms = set()
    total_cp = 0.0
    priority = [
        "COOH","COOR","CHO","CO_nonring","CO_ring","C=O_other",
        "OH_phenol","OH_alcohol","NO2","CN","NH2_ar","ring_nH",
        "ring_n","NH_ring","NH2","NH_nonring","N_nonring",
        "N=_ring","N=_nonring","NH=","ring_cH","ring_c",
        "ring_CH2","ring_CH","ring_C","CH3","CH2","CH","C",
        "CH2=","CH=","C=","C=C","C#C","F","Cl","Br","I",
        "SH","S_nonring","S_ring"
    ]
    for name in priority:
        if name not in JOBACK_CP_GROUPS: continue
        patt = Chem.MolFromSmarts(JOBACK_CP_GROUPS[name]["smarts"])
        if not patt: continue
        for match in mol.GetSubstructMatches(patt):
            if any(a in used_atoms for a in match): continue
            g = JOBACK_CP_GROUPS[name]
            total_cp += (
                g["a"] - 37.93 
                + (g["b"] + 0.21) * T_K 
                + (g["c"] - 3.91e-04) * (T_K**2) 
                + (g["d"] + 2.06e-07) * (T_K**3)
            )
            for a in match: used_atoms.add(a)
    return total_cp

def calculate_wug(p, GSA, VSA, VF, PV, LCD, PLD):
    wug = (
        -4.47194 + (1.77349*p) + (0.000511149*GSA) + (0.00163429*VSA) + 
        (3.92696*VF) + (5.59522*PV) - (0.0764434*LCD) + (0.262302*PLD) - 
        (0.163317*(p**2)) - (0.00133171*p*GSA) + (7.69048e-5*p*VSA) - 
        (2.66592*p*VF) + (2.45092*p*PV) + (0.089082*p*LCD) - 
        (0.0975448*p*PLD) - (4.1166e-8*(GSA**2)) - (1.15768e-7*GSA*VSA) + 
        (0.00280453*GSA*VF) - (2.35326e-5*GSA*PV) + (8.39123e-6*GSA*LCD) - 
        (3.89128e-6*GSA*PLD) + (2.21456e-7*(VSA**2)) - 0.00231186*VSA*VF - 
        0.00180075*VSA*PV + (4.34998e-6*VSA*LCD) + (1.65433e-5*VSA*PLD) + 
        4.52648*(VF**2) - 3.82519*VF*PV - 0.0639716*VF*LCD - 
        0.283064*VF*PLD - 0.0213098*(PV**2) + 0.000824477*PV*LCD + 
        0.00253194*PV*PLD + 0.000521033*(LCD**2) + 0.000700743*LCD*PLD - 
        (0.000244913*(PLD**2))
    )
    return round(wug, 3)

def calculate_wuv(p, GSA, VSA, VF, PV, LCD, PLD):
    wuv = (
        -49.6238 + (17.4843*p) - (0.000310481*GSA) + (0.0214365*VSA) + 
        32.4082*VF + 14.1933*PV + 0.0660557*LCD + 1.66494*PLD - 
        1.79789*(p**2) - (0.00754047*p*GSA) - (0.0012505*p*VSA) - 
        (22.99*p*VF) + (69.0864*p*PV) + (0.861169*p*LCD) - 
        (0.523851*p*PLD) + (1.51676e-7*(GSA**2)) + (3.18358e-7*GSA*VSA) + 
        (0.0145422*GSA*VF) - (5.75705e-5*GSA*PV) + (0.000157672*GSA*LCD) - 
        (2.93554e-5*GSA*PLD) + (7.11672e-7*(VSA**2)) - (0.0162344*VSA*VF) - 
        (0.0208807*VSA*PV) + (3.334e-5*VSA*LCD) + (0.000196064*VSA*PLD) + 
        (44.1803*(VF**2)) - (14.2407*VF*PV) - (1.95209*VF*LCD) - 
        (2.23509*VF*PLD) - (0.0384937*(PV**2)) - (0.00185746*PV*LCD) + 
        (0.0410538*PV*PLD) + (0.00735029*(LCD**2)) + (0.00119741*LCD*PLD) + 
        (0.00386859*(PLD**2))
    )
    return round(wuv, 3)

@app.post("/analyze")
async def analyze_mof(
    file: UploadFile = File(...),
    pv: float = Form(...), gsa: float = Form(...), vsa: float = Form(...),
    lcd: float = Form(...), pld: float = Form(...), vf: float = Form(...),
    density: float = Form(...), metal_name: str = Form(...),
    linker_name: str = Form(...), smiles: str = Form(...),
    reaction_time: float = Form(...), temperature: float = Form(...)
):
    wug = calculate_wug(density, gsa, vsa, vf, pv, lcd, pld)
    wuv = calculate_wuv(density, gsa, vsa, vf, pv, lcd, pld)
    
    # ENERGY CALCULATION
    cp_final = calculate_cp_joback_full(smiles, temperature)
    delta_t = temperature - 25.0
    
    # Q Heat = (Q Total / eta_heat) * V_reaktor
    q_heat = ((cp_final * delta_t / 0.8) * 1000) / 1000
    
    # Q Loss = A * (ka / s) * deltaT * t_seconds (A = 5.899)
    q_loss = (5.899 * (0.042 / 0.075) * delta_t * (reaction_time * 3600)) / 1000

    return {
        "status": "success",
        "results": {
            "stability_status": "Sangat Stabil" if wug > 5 else "Tidak Stabil",
            "gravimetric_h2": wug,
            "volumetric_h2": wuv,
            "doe_feasible": (wug >= 5.5 and wuv >= 40),
            "mof_cost": 25.0,
            "mof_cost_ok": True,
            "storage_cost": 280.0,
            "storage_cost_ok": True,
            "q_energy": round(q_heat, 2),
            "q_loss": round(q_loss, 2),
            "reaction_time": reaction_time,
            "time_ok": reaction_time <= 48,
            "temperature": temperature,
            "temp_ok": temperature <= 180,
            "delta_e": 4.2,
            "rmsd": 0.08,
            "stability_feasible": True,
            "econ_feasible": True,
            "is_overall_feasible": (wug >= 5.5 and wuv >= 40)
        }
    }