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
    # Simpan file
    path = f"uploads/{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Logika dummy
    is_feasible = (pv > 0.5 and temperature < 180)
    
    return {
        "status": "success",
        "results": {
            "gravimetric_h2": 6.8 if pv > 0.6 else 3.4,
            "volumetric_h2": 44.2 if pv > 0.6 else 21.0,
            "mof_cost_usd_kg": 18.5 if temperature < 150 else 48.0,
            "stability_status": "Sangat Stabil" if is_feasible else "Tidak Stabil",
            "is_feasible": is_feasible
        }
    }