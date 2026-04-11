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

if not os.path.exists("uploads"):
    os.makedirs("uploads")

@app.post("/analyze")
async def analyze_mof(
    file: UploadFile = File(...),
    pv: float = Form(...),
    gsa: float = Form(...),
    vsa: float = Form(...),
    lcd: float = Form(...),
    pld: float = Form(...),
    vf: float = Form(...),
    density: float = Form(...),
    metal_name: str = Form(...),
    linker_name: str = Form(...),
    reaction_time: float = Form(...),
    temperature: float = Form(...)
):
    # Logika dummy untuk simulasi Judgment
    # 1. Parameter MOF (Working Capacity)
    grav_h2 = 6.2  # Contoh hasil
    vol_h2 = 45.0  # Contoh hasil
    is_doe_ok = (grav_h2 >= 5.5 and vol_h2 >= 40)

    # 2. Ekonomi
    mof_cost = 15.5
    storage_cost = 2.4
    q_energy = 4.5
    q_loss = 1.2
    is_econ_ok = (mof_cost <= 30)

    # 3. Struktur (Stabilitas)
    delta_e = 4.2
    rmsd = 0.08
    is_stability_ok = (delta_e < 5.0)

    return {
        "status": "success",
        "results": {
            # Output Poin 1
            "gravimetric_h2": grav_h2,
            "volumetric_h2": vol_h2,
            "doe_feasible": is_doe_ok,
            
            # Output Poin 2
            "mof_cost": mof_cost,
            "storage_cost": storage_cost,
            "q_energy": q_energy,
            "q_loss": q_loss,
            "econ_feasible": is_econ_ok,
            
            # Output Poin 3
            "delta_e": delta_e,
            "rmsd": rmsd,
            "stability_status": "Sangat Stabil" if is_stability_ok else "Tidak Stabil",
            "stability_feasible": is_stability_ok,
            
            # Final Verdict
            "is_overall_feasible": is_doe_ok and is_econ_ok and is_stability_ok
        }
    }