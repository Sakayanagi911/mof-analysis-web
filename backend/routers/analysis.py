from fastapi import APIRouter, UploadFile, File, Form

from models.schemas import FeasibilityRequest, FeasibilityResponse
from services.whitebox_model import predict_working_capacity

router = APIRouter()

@router.post("/analyze")
async def analyze_mof(
    file: UploadFile = File(None),
    pv: float = Form(...), gsa: float = Form(...), vsa: float = Form(...),
    lcd: float = Form(...), pld: float = Form(...), vf: float = Form(...),
    density: float = Form(...), metal_name: str = Form(...),
    linker_name: str = Form(...), reaction_time: float = Form(...),
    temperature: float = Form(...)
):
    """
    Main endpoint for MOF screening and analysis.
    Placeholder response to maintain compatibility with frontend.
    """
    return {
        "status": "success",
        "results": {
            "gravimetric_h2": 0.0,
            "volumetric_h2": 0.0,
            "doe_feasible": False,
            "mof_cost": 0.0,
            "storage_cost": 0.0,
            "q_energy": 0.0,
            "q_loss": 0.0,
            "econ_feasible": False,
            "delta_e": 0.0,
            "rmsd": 0.0,
            "stability_status": "Pending",
            "stability_feasible": False,
            "is_overall_feasible": False
        }
    }


@router.post("/api/feasibility", response_model=FeasibilityResponse)
async def analyze_feasibility(request: FeasibilityRequest):
    """
    Analisis feasibility MOF berdasarkan 7 parameter struktural.
    Menggunakan persamaan polynomial eksplisit (Persamaan 4-1 & 4-2).
    """
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
