from pydantic import BaseModel
from typing import Optional, Dict, Any

class AnalysisRequest(BaseModel):
    pv: float
    gsa: float
    vsa: float
    lcd: float
    pld: float
    vf: float
    density: float
    metal_name: str
    linker_name: str
    reaction_time: float
    temperature: float

class AnalysisResults(BaseModel):
    gravimetric_h2: float
    volumetric_h2: float
    doe_feasible: bool
    mof_cost: float
    storage_cost: float
    q_energy: float
    q_loss: float
    econ_feasible: bool
    delta_e: float
    rmsd: float
    stability_status: str
    stability_feasible: bool
    is_overall_feasible: bool

class AnalysisResponse(BaseModel):
    status: str
    results: AnalysisResults
