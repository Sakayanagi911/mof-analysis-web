from fastapi import APIRouter, UploadFile, File, Form
from rdkit import Chem

from models.schemas import FeasibilityRequest, FeasibilityResponse
from models.schemas import EconomicRequest, EconomicResponse
from services.whitebox_model import predict_working_capacity
from services.whitebox_model import calculate_wug, calculate_wuv
from services.cost_analysis import run_economic_analysis
from services.joback import JOBACK_CP_GROUPS, PRIORITY

router = APIRouter()

def calculate_cp_joback_full(smiles: str, temp_c: float):
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return 150.0
    T_K, used_atoms, total_cp = temp_c + 273.15, set(), 0.0
    for name in PRIORITY:
        if name not in JOBACK_CP_GROUPS: continue
        patt = Chem.MolFromSmarts(JOBACK_CP_GROUPS[name]["smarts"])
        if not patt: continue
        for match in mol.GetSubstructMatches(patt):
            if any(a in used_atoms for a in match): continue
            g = JOBACK_CP_GROUPS[name]
            total_cp += (g["a"] - 37.93 + (g["b"] + 0.21) * T_K + 
                        (g["c"] - 3.91e-04) * (T_K**2) + (g["d"] + 2.06e-07) * (T_K**3))
            for a in match: used_atoms.add(a)
    return total_cp if total_cp > 0 else 150.0

@router.post("/analyze")
async def analyze_mof(
    file: UploadFile = File(None),
    pv: float = Form(...), 
    gsa: float = Form(...), 
    vsa: float = Form(...),
    lcd: float = Form(...), 
    pld: float = Form(...), 
    vf: float = Form(...),
    density: float = Form(...), 
    metal_name: str = Form("-"),
    linker_name: str = Form("-"), 
    smiles: str = Form("-"),
    solvent_name: str = Form("-"),    # Input baru
    additive_name: str = Form("-"),   # Input baru
    modulator_name: str = Form("-"),  # Input baru
    product_mass: float = Form(0.0),  # Input baru
    reaction_time: float = Form(...), 
    temperature: float = Form(...)
):
    # 1. Standarisasi Void Fraction
    valid_vf = vf / 100.0 if vf > 1.0 else vf

    # 2. Hitung Kapasitas (Sesuai model Whitebox)
    wug = calculate_wug(
        p=density,     
        GSA=gsa, 
        VSA=vsa, 
        VF=valid_vf, 
        PV=pv, 
        LCD=lcd, 
        PLD=pld
    )
    
    wuv = calculate_wuv(
        p=density,     
        GSA=gsa, 
        VSA=vsa, 
        VF=valid_vf, 
        PV=pv, 
        LCD=lcd, 
        PLD=pld
    )

    # 3. Integrated Energy Fingerprint (Update Sesuai Notebook)
    heat_eff = 0.75  
    delta_t = temperature - 25.0
    t_seconds = reaction_time * 3600.0
    
    cp_val = calculate_cp_joback_full(smiles, temperature)
    
    # Hitung per komponen dalam MJ
    q_heat_mj = (cp_val * delta_t) / (heat_eff * 1_000_000)
    q_loss_mj = (3.303 * delta_t * t_seconds) / (heat_eff * 1_000_000)
    e_stirr_mj = (0.0162 * 1000.0 * t_seconds) / 1_000_000 # Asumsi mass 1kg
    total_energy_mj = q_heat_mj + q_loss_mj + e_stirr_mj

    return {
        "status": "success",
        "results": {
            "gravimetric_h2": round(wug, 3),
            "volumetric_h2": round(wuv, 3),
            "doe_feasible": (wug >= 5.5 and wuv >= 40.0),
            "mof_cost": 25.0,
            "mof_cost_ok": True,
            "storage_cost": round(25.0 / (wug/100), 2) if wug > 0 else 0,
            "storage_cost_ok": True,
            
            # Nilai Energi dalam Mega Joule (MJ)
            "q_energy": round(q_heat_mj, 4), 
            "q_loss": round(q_loss_mj, 4),
            "e_stirr": round(e_stirr_mj, 4),       # Field tambahan
            "total_energy": round(total_energy_mj, 4), # Field tambahan
            
            "reaction_time": reaction_time,
            "time_ok": reaction_time <= 48,
            "temperature": temperature,
            "temp_ok": temperature <= 180,
            "delta_e": 4.2,
            "rmsd": 0.08,
            "stability_status": "Sangat Stabil" if wug > 5.5 else "Stabil",
            "stability_feasible": True,
            "econ_feasible": (reaction_time <= 48 and temperature <= 180),
            "is_overall_feasible": (wug >= 5.5 and wuv >= 40.0 and reaction_time <= 48)
        }
    }

@router.post("/api/feasibility", response_model=FeasibilityResponse)
async def analyze_feasibility(request: FeasibilityRequest):
    try:
        result = predict_working_capacity(
            p=request.p, gsa=request.gsa, vsa=request.vsa,
            vf=request.vf, pv=request.pv,
            lcd=request.lcd, pld=request.pld
        )
        return FeasibilityResponse(
            status="success",
            gravimetric_wc=result["gravimetric_wc"],
            volumetric_wc=result["volumetric_wc"],
            is_feasible=result["is_feasible"],
            thresholds={"gravimetric": 5.5, "volumetric": 40.0}
        )
    except Exception as e:
        return FeasibilityResponse(
            status=f"error: {str(e)}",
            gravimetric_wc=0.0,
            volumetric_wc=0.0,
            is_feasible=False,
            thresholds={"gravimetric": 5.5, "volumetric": 40.0}
        )

@router.post("/api/economic", response_model=EconomicResponse)
async def analyze_economic(request: EconomicRequest):
    try:
        result = run_economic_analysis(
            metal_name=request.metal_name,
            linker_name=request.linker_name,
            reaction_time=request.reaction_time,
            temperature=request.temperature,
            smiles=request.smiles,
            gravimetric_wc=request.gravimetric_wc
        )
        return EconomicResponse(status="success", **result)
    except Exception as e:
        return EconomicResponse(
            status=f"error: {str(e)}",
            mof_cost_usd_per_kg=0.0,
            storage_cost_usd_per_kg_h2=0.0,
            q_energy_kj=0.0,
            q_loss_kj=0.0,
            is_feasible=False,
            feasibility_details={}
        )