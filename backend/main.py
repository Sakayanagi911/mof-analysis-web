from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_wug(p, GSA, VSA, VF, PV, LCD, PLD):
    # Persamaan (4-1) Working Uptake Gravimetric sesuai gambar
    wug = (
        -4.47194 + (1.77349 * p) + (0.000511149 * GSA) + (0.00163429 * VSA) + 
        (3.92696 * VF) + (5.59522 * PV) - (0.0764434 * LCD) + (0.262302 * PLD) - 
        (0.163317 * (p**2)) - (0.00133171 * p * GSA) + (7.69048e-5 * p * VSA) - 
        (2.66592 * p * VF) + (2.45092 * p * PV) + (0.089082 * p * LCD) - 
        (0.0975448 * p * PLD) - (4.1166e-8 * (GSA**2)) - (1.15768e-7 * GSA * VSA) + 
        (0.00280453 * GSA * VF) - (2.35326e-5 * GSA * PV) + (8.39123e-6 * GSA * LCD) - 
        (3.89128e-6 * GSA * PLD) + (2.21456e-7 * (VSA**2)) - (0.00231186 * VSA * VF) - 
        (0.00180075 * VSA * PV) + (4.34998e-6 * VSA * LCD) + (1.65433e-5 * VSA * PLD) + 
        (4.52648 * (VF**2)) - (3.82519 * VF * PV) - (0.0639716 * VF * LCD) - 
        (0.283064 * VF * PLD) - (0.0213098 * (PV**2)) + (0.000824477 * PV * LCD) + 
        (0.00253194 * PV * PLD) + (0.000521033 * (LCD**2)) + (0.000700743 * LCD * PLD) - 
        (0.000244913 * (PLD**2))
    )
    return round(wug, 3)

def calculate_wuv(p, GSA, VSA, VF, PV, LCD, PLD):
    # Persamaan (4-2) Working Uptake Volumetric sesuai gambar
    wuv = (
        -49.6238 + (17.4843 * p) - (0.000310481 * GSA) + (0.0214365 * VSA) + 
        (32.4082 * VF) + (14.1933 * PV) + (0.0660557 * LCD) + (1.66494 * PLD) - 
        (1.79789 * (p**2)) - (0.00754047 * p * GSA) - (0.0012505 * p * VSA) - 
        (22.99 * p * VF) + (69.0864 * p * PV) + (0.861169 * p * LCD) - 
        (0.523851 * p * PLD) + (1.51676e-7 * (GSA**2)) + (3.18358e-7 * GSA * VSA) + 
        (0.0145422 * GSA * VF) - (5.75705e-5 * GSA * PV) + (0.000157672 * GSA * LCD) - 
        (2.93554e-5 * GSA * PLD) + (7.11672e-7 * (VSA**2)) - (0.0162344 * VSA * VF) - 
        (0.0208807 * VSA * PV) + (3.334e-5 * VSA * LCD) + (0.000196064 * VSA * PLD) + 
        (44.1803 * (VF**2)) - (14.2407 * VF * PV) - (1.95209 * VF * LCD) - 
        (2.23509 * VF * PLD) - (0.0384937 * (PV**2)) - (0.00185746 * PV * LCD) + 
        (0.0410538 * PV * PLD) + (0.00735029 * (LCD**2)) + (0.00119741 * LCD * PLD) + 
        (0.00386859 * (PLD**2))
    )
    return round(wuv, 3)

@app.post("/analyze")
async def analyze_mof(
    file: UploadFile = File(...),
    pv: float = Form(...), gsa: float = Form(...), vsa: float = Form(...),
    lcd: float = Form(...), pld: float = Form(...), vf: float = Form(...),
    density: float = Form(...), metal_name: str = Form(...),
    linker_name: str = Form(...), reaction_time: float = Form(...),
    temperature: float = Form(...)
):
    # Hitung nilai nyata berdasarkan rumus gambar
    wug = calculate_wug(density, gsa, vsa, vf, pv, lcd, pld)
    wuv = calculate_wuv(density, gsa, vsa, vf, pv, lcd, pld)

    # Judgment DOE Target
    doe_passed = (wug >= 5.5 and wuv >= 40)
    
    # Placeholder Analisis Ekonomi (Bisa disesuaikan rumusnya nanti)
    mof_cost = round(15 + (temperature * 0.1), 2)
    econ_passed = mof_cost <= 30

    return {
        "status": "success",
        "results": {
            "gravimetric_h2": wug,
            "volumetric_h2": wuv,
            "doe_feasible": doe_passed,
            "mof_cost": mof_cost,
            "storage_cost": 2.5,
            "q_energy": 4.8,
            "q_loss": 1.1,
            "econ_feasible": econ_passed,
            "delta_e": 4.1,
            "rmsd": 0.05,
            "stability_status": "Sangat Stabil" if wug > 4 else "Stabil",
            "stability_feasible": True,
            "is_overall_feasible": doe_passed and econ_passed
        }
    }