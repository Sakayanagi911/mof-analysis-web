from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json, os
import uvicorn

# Import routers sesuai struktur folder kamu
from routers import analysis, visualization, structure

app = FastAPI(title="MOF Analysis API")

cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allow_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, tags=["Analysis"])
app.include_router(visualization.router, prefix="/visualize", tags=["Visualization"])
app.include_router(structure.router, tags=["Structure"])

@app.get("/")
async def root():
    return {"message": "MOF Analysis API is running", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

@app.get("/get-prices")
async def get_prices():
    file_path = os.path.join("data", "price_database.json")
    try:
        # Tambahkan encoding="utf-8" di sini
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Price database tidak ditemukan")
    except Exception:
        raise HTTPException(status_code=500, detail="Gagal memuat price database")

@app.get("/get-smiles-mapping")
async def get_smiles_mapping():
    """
    Endpoint untuk mendapatkan SMILES to Linker Name mapping
    Sekarang sudah digabung dalam price_database.json
    """
    file_path = os.path.join("data", "price_database.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            smiles_data = data.get("smiles_mapping", {})
            return {
                "description": smiles_data.get("description", ""),
                "total_entries": smiles_data.get("total_entries", 0),
                "mapping": smiles_data.get("mapping", {})
            }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Price database tidak ditemukan")
    except Exception:
        raise HTTPException(status_code=500, detail="Gagal memuat smiles mapping")
