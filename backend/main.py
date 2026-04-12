from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json, os
import uvicorn

# Import routers sesuai struktur folder kamu
from routers import analysis, visualization, structure

app = FastAPI(title="MOF Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        return {"error": "File not found", "metals": {}, "linkers": {}}
    except Exception as e:
        return {"error": str(e), "metals": {}, "linkers": {}}