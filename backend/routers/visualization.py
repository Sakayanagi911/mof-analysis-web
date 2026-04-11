from fastapi import APIRouter

router = APIRouter()

@router.get("/doe-scatter")
async def get_doe_scatter():
    """Placeholder for DOE scatter plot visualization."""
    return {"message": "DOE scatter plot data will be available here."}

@router.get("/correlation")
async def get_correlation_heatmap():
    """Placeholder for correlation heatmap visualization."""
    return {"message": "Correlation heatmap data will be available here."}
