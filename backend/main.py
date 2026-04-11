from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import routers
from routers import analysis, visualization, structure

app = FastAPI(title="MOF Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
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
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)