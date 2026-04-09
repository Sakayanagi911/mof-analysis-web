from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uvicorn

app = FastAPI()

# Tambahkan CORS agar Next.js bisa memanggil API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pastikan folder uploads ada
if not os.path.exists("uploads"):
    os.makedirs("uploads")

@app.get("/")
def read_root():
    return {"message": "BACKEND KE FRONT END NYA DAH CONNECT YGY"}

# Endpoint utama untuk analisis MOF
@app.post("/analyze")
async def analyze_mof(
    # Poin 3: Upload CIF [cite: 89]
    file: UploadFile = File(...),
    
    # Poin 1: Parameter MOF [cite: 86]
    pv: float = Form(...),
    gsa: float = Form(...),
    vsa: float = Form(...),
    lcd: float = Form(...),
    pld: float = Form(...),
    vf: float = Form(...),
    density: float = Form(...),
    
    # Poin 2: Data Kimia [cite: 87, 88]
    metal_name: str = Form(...),
    linker_name: str = Form(...),
    reaction_time: float = Form(...),
    temperature: float = Form(...),
    smiles: str = Form(...) 
):
    # 1. Simpan file CIF
    path = f"uploads/{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Logika Perhitungan (Contoh Berdasarkan Target DOE) [cite: 93, 94]
    # Di sini nanti Anda panggil fungsi dari repository TRIAXIS-MOF
    is_feasible_h2 = (pv > 0.5) # Contoh logika sederhana
    
    return {
        "status": "success",
        "filename": file.filename,
        "input_summary": {
            "metal": metal_name,
            "linker": linker_name
        },
        "results": {
            "gravimetric_h2": 6.5,  # Target DOE >= 5.5 wt% [cite: 93]
            "volumetric_h2": 42.1,  # Target DOE >= 40 g/L [cite: 94]
            "mof_cost_usd_kg": 12.4, # Target <= 30 USD/kg [cite: 95]
            "stability_status": "Sangat Stabil", # Berdasarkan Delta E [cite: 78]
            "is_feasible": True
        }
    }