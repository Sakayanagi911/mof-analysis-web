from pydantic import BaseModel
from typing import Optional, Dict, Any, List

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


# --- API #1: Feasibility Analysis ---

class FeasibilityRequest(BaseModel):
    p: float        # Tekanan operasi [bar]
    gsa: float      # Gravimetric Surface Area [m²/g]
    vsa: float      # Volumetric Surface Area [m²/cm³]
    vf: float       # Void Fraction [-]
    pv: float       # Pore Volume [cm³/g]
    lcd: float      # Largest Cavity Diameter [Å]
    pld: float      # Pore Limiting Diameter [Å]

class FeasibilityResponse(BaseModel):
    status: str                # "success" atau "error"
    gravimetric_wc: float      # Working Uptake Gravimetrik [wt.%]
    volumetric_wc: float       # Working Uptake Volumetrik [g H₂/L]
    is_feasible: bool          # True jika memenuhi threshold DOE 2025
    thresholds: dict           # {"gravimetric": 5.5, "volumetric": 40.0}


# --- API #2: Economic Analysis ---

class EconomicRequest(BaseModel):
    metal_name: str        # Nama metal precursor
    linker_name: str       # Nama linker
    reaction_time: float   # Waktu reaksi (jam)
    temperature: float     # Temperatur reaksi (°C)
    smiles: str            # SMILES linker
    gravimetric_wc: float = 5.0  # Opsional, dari API #1

class EconomicResponse(BaseModel):
    status: str
    mof_cost_usd_per_kg: float
    storage_cost_usd_per_kg_h2: float
    q_energy_kj: float
    q_loss_kj: float
    is_feasible: bool
    feasibility_details: dict


# --- API #3: Structure Analysis ---

class Atom3D(BaseModel):
    symbol: str
    x: float
    y: float
    z: float

class StructureResponse(BaseModel):
    status: str
    formula: str
    n_atoms: int
    n_sbu_atoms: int
    n_linker_atoms: int
    delta_e: float              # kJ/mol
    rmsd: float                 # Å
    stability_score: float      # skor gabungan
    stability_status: str       # "Sangat stabil" / "Cukup stabil" / "Tidak stabil"
    is_feasible: bool
    structure_3d: dict          # Data untuk rendering 3D
    cell_params: dict           # Parameter unit cell
    xtb_available: bool = False # Apakah xTB tersedia di server
