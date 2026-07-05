from fastapi import APIRouter, UploadFile, File, HTTPException
from services.structure_parser import (
    parse_cif_file, separate_sbu_and_linker,
    calculate_rmsd, calculate_stability_score, prepare_3d_structure_data
)
from services.xtb_runner import XTBRunner
from ase.io import read
import tempfile
import os

router = APIRouter()


@router.post("/api/structure/conformational-energy")
async def calculate_conformational_energy(
    embedded_linker: UploadFile = File(..., description="Embedded linker XYZ file")
):
    """
    Calculate conformational energy from embedded linker only.
    
    Process:
    1. Load embedded linker XYZ
    2. Optimize with xTB to get free linker
    3. Calculate E_conf = E(embedded) - E(free)
    
    Args:
        embedded_linker: XYZ file of linker extracted from MOF
    
    Returns:
        Conformational energy and related metrics
    """
    try:
        # Validate file extension
        if not embedded_linker.filename.endswith('.xyz'):
            raise HTTPException(
                status_code=400,
                detail="Embedded linker file must be in XYZ format"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xyz', mode='wb') as tmp:
            content = await embedded_linker.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Load embedded linker
            atoms_embedded = read(tmp_path)
            
            # Run xTB analysis
            print(f"🔬 Running xTB analysis for: {embedded_linker.filename}")
            xtb = XTBRunner()
            results = xtb.full_structure_analysis_from_embedded(
                atoms_embedded,
                charge=0
            )
            
            print(f"✅ Analysis completed successfully")
            
            return {
                "success": True,
                "filename": embedded_linker.filename,
                "n_atoms": len(atoms_embedded),
                "conformational_energy_kcal_mol": results['conformational_energy_kcal_mol'],
                "energy_free_kcal_mol": results['energy_free_kcal_mol'],
                "energy_embedded_kcal_mol": results['energy_embedded_kcal_mol'],
                "rmsd_angstrom": results['rmsd_angstrom'],
                "mean_delta_length_angstrom": results['mean_delta_length_angstrom'],
                "mean_delta_angle_degrees": results['mean_delta_angle_degrees'],
                "num_bonds": results['num_bonds'],
                "num_angles": results['num_angles'],
                "message": "Conformational energy calculated successfully. Note: Geometry metrics (RMSD, ΔLength, ΔAngle) are approximations."
            }
            
        finally:
            # Cleanup temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"xTB analysis failed: {str(e)}"
        )


@router.post("/api/structure")
async def analyze_structure(file: UploadFile = File(...)):
    """
    Analisis struktur MOF dari file CIF.

    Alur:
    1. Parse file CIF → ekstrak atom & posisi
    2. Pisahkan SBU dan linker
    3. Gabungkan menjadi skor stabilitas
    4. Siapkan data 3D untuk visualisasi
    
    Note: For xTB analysis, use /api/structure/xtb-analysis endpoint
    """
    # Validasi file
    if not file.filename.endswith(".cif"):
        raise HTTPException(status_code=400,
                          detail="Hanya file .cif yang diterima")

    content = await file.read()

    try:
        # 1. Parse CIF
        parsed = parse_cif_file(content, file.filename)

        # 2. Pisahkan SBU dan linker
        separated = separate_sbu_and_linker(
            parsed["atoms"], parsed["positions"]
        )

        # 3. Skor stabilitas (simplified - without xTB for now)
        stability = calculate_stability_score(0.0, 0.0)

        # 4. Data 3D
        structure_3d = prepare_3d_structure_data(
            parsed["atoms"], parsed["positions"]
        )

        return {
            "status": "success",
            "formula": parsed["formula"],
            "n_atoms": parsed["n_atoms"],
            "n_sbu_atoms": separated["sbu_count"],
            "n_linker_atoms": separated["linker_count"],
            "stability_score": stability["stability_score"],
            "stability_status": stability["stability_status"],
            "is_feasible": stability["is_feasible"],
            "structure_3d": structure_3d,
            "cell_params": parsed["cell_params"],
            "message": "For xTB structure analysis, use /api/structure/xtb-analysis endpoint"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                          detail=f"Internal error: {str(e)}")


@router.post("/api/structure/3d-view")
async def get_3d_view(file: UploadFile = File(...)):
    """
    Endpoint khusus untuk mendapatkan data 3D dari file CIF.
    Mengembalikan data atom yang bisa langsung dirender oleh 3Dmol.js
    atau NGL Viewer di frontend.
    """
    if not file.filename.endswith(".cif"):
        raise HTTPException(status_code=400,
                          detail="Hanya file .cif yang diterima")

    content = await file.read()

    try:
        parsed = parse_cif_file(content, file.filename)

        # Return raw CIF content + parsed atoms
        return {
            "status": "success",
            "cif_content": content.decode("utf-8", errors="replace"),
            "structure_3d": prepare_3d_structure_data(
                parsed["atoms"], parsed["positions"]
            ),
            "formula": parsed["formula"],
            "cell_params": parsed["cell_params"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/structure/xtb-analysis")
async def xtb_structure_analysis(
    free_linker: UploadFile = File(..., description="Free (optimized) linker XYZ file"),
    embedded_linker: UploadFile = File(..., description="Embedded linker XYZ file")
):
    """
    Perform xTB structure analysis comparing free vs embedded linker.
    
    User uploads 2 files:
    - free_linker: XYZ file of optimized free linker
    - embedded_linker: XYZ file of embedded linker (extracted from MOF)
    
    Returns:
    - conformational_energy_kcal_mol: Energy difference (embedded - free)
    - rmsd_angstrom: Root mean square deviation after alignment
    - mean_delta_length_angstrom: Average bond length change
    - mean_delta_angle_degrees: Average bond angle change
    """
    try:
        # Validate file extensions
        if not free_linker.filename.endswith('.xyz'):
            raise HTTPException(
                status_code=400,
                detail="Free linker file must be in XYZ format"
            )
        if not embedded_linker.filename.endswith('.xyz'):
            raise HTTPException(
                status_code=400,
                detail="Embedded linker file must be in XYZ format"
            )
        
        # Initialize xTB runner
        xtb = XTBRunner()
        
        # Save uploaded files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xyz', mode='wb') as tmp_free:
            content_free = await free_linker.read()
            tmp_free.write(content_free)
            tmp_free_path = tmp_free.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xyz', mode='wb') as tmp_emb:
            content_emb = await embedded_linker.read()
            tmp_emb.write(content_emb)
            tmp_emb_path = tmp_emb.name
        
        try:
            # Load structures using ASE
            atoms_free = read(tmp_free_path)
            atoms_embedded = read(tmp_emb_path)
            
            # Validate atom counts
            if len(atoms_free) != len(atoms_embedded):
                raise HTTPException(
                    status_code=400,
                    detail=f"Atom count mismatch: free={len(atoms_free)}, embedded={len(atoms_embedded)}"
                )
            
            # Run full xTB analysis
            print(f"🔬 Starting xTB analysis: {free_linker.filename} vs {embedded_linker.filename}")
            results = xtb.full_structure_analysis(
                atoms_free=atoms_free,
                atoms_embedded=atoms_embedded,
                charge=0
            )
            
            print(f"✅ xTB analysis completed successfully")
            
            return {
                "success": True,
                "results": results,
                "files": {
                    "free_linker": free_linker.filename,
                    "embedded_linker": embedded_linker.filename
                },
                "message": "xTB structure analysis completed successfully"
            }
            
        finally:
            # Cleanup temporary files
            if os.path.exists(tmp_free_path):
                os.unlink(tmp_free_path)
            if os.path.exists(tmp_emb_path):
                os.unlink(tmp_emb_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"xTB analysis failed: {str(e)}"
        )
