from pydantic import BaseModel, Field
from typing import Optional


class AnalysisRequest(BaseModel):
    pv: float
    gsa: float
    vsa: float
    lcd: float
    pld: float
    vf: float
    density: float
    metal_name: Optional[str] = "-"
    linker_name: Optional[str] = "-"
    smiles: Optional[str] = "-"
    solvent_name: Optional[str] = "-"
    additive_name: Optional[str] = "-"
    modulator_name: Optional[str] = "-"
    product_mass_mg: Optional[float] = 0.0
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


class FeasibilityRequest(BaseModel):
    density: float = Field(..., gt=0)
    gsa: float = Field(..., ge=0)
    vsa: float = Field(..., ge=0)
    vf: float = Field(..., ge=0, le=1)
    pv: float = Field(..., ge=0)
    lcd: float = Field(..., ge=0)
    pld: float = Field(..., ge=0)
    pressure_bar: Optional[float] = Field(default=None, ge=0)


class FeasibilityResponse(BaseModel):
    status: str
    gravimetric_wc: float
    volumetric_wc: float
    is_feasible: bool
    thresholds: dict


class EconomicRequest(BaseModel):
    metal_name: str = Field(..., min_length=1)
    reaction_time: float = Field(..., gt=0)
    temperature: float = Field(..., gt=0)
    smiles: str = Field(..., min_length=1)
    gravimetric_wc: Optional[float] = Field(default=None, gt=0)
    volumetric_wc: Optional[float] = Field(default=None, gt=0)
    product_mass_mg: Optional[float] = Field(default=50.0, gt=0)
    metal_mass_mg: Optional[float] = Field(default=100.0, gt=0)
    linker_mass_mg: Optional[float] = Field(default=50.0, gt=0)
    solvent_name: Optional[str] = "-"
    solvent_volume_ml: Optional[float] = Field(default=0.0, ge=0)
    additive_name: Optional[str] = "-"
    additive_volume_ml: Optional[float] = Field(default=0.0, ge=0)
    modulator_name: Optional[str] = "-"
    modulator_volume_ml: Optional[float] = Field(default=0.0, ge=0)


class EconomicResponse(BaseModel):
    status: str
    mof_cost_usd_per_kg: float
    storage_cost_usd_per_kg_h2: float
    q_energy_mj: float
    q_loss_mj: float
    e_stirr_mj: float
    e_total_mj: float
    is_feasible: bool
    feasibility_details: dict


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
    delta_e: float
    rmsd: float
    stability_score: float
    stability_status: str
    is_feasible: bool
    structure_3d: dict
    cell_params: dict
    xtb_available: bool = False
