from fastapi import APIRouter, UploadFile, File, HTTPException
from services.structure_parser import (
    parse_cif_file, separate_sbu_and_linker,
    calculate_rmsd, calculate_stability_score, prepare_3d_structure_data
)
from services.xtb_runner import (
    XTB_AVAILABLE, run_xtb_single_point,
    run_xtb_optimization, calculate_delta_e,
    atoms_positions_to_xyz
)

router = APIRouter()


@router.post("/api/structure")
async def analyze_structure(file: UploadFile = File(...)):
    """
    Analisis struktur MOF dari file CIF.

    Alur:
    1. Parse file CIF → ekstrak atom & posisi
    2. Pisahkan SBU dan linker
    3. Hitung energi linker (embedded vs free) via xTB (jika tersedia)
    4. Hitung RMSD distorsi geometri (jika xTB tersedia)
    5. Gabungkan menjadi skor stabilitas
    6. Siapkan data 3D untuk visualisasi
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

        # 3 & 4. Hitung energi dan RMSD via xTB (jika tersedia)
        delta_e = 0.0
        rmsd = 0.0

        if XTB_AVAILABLE and separated["linker_count"] > 0:
            # Konversi linker positions ke XYZ
            linker_xyz = atoms_positions_to_xyz(
                separated["linker_atoms"], separated["linker_positions"]
            )

            # Single point energy (embedded geometry)
            sp_result = run_xtb_single_point(linker_xyz)

            # Optimization (free geometry)
            opt_result = run_xtb_optimization(linker_xyz)

            if sp_result["success"] and opt_result["success"]:
                delta_e = calculate_delta_e(
                    sp_result["energy_kj_mol"],
                    opt_result["energy_kj_mol"]
                )

                # RMSD antara embedded dan optimized geometry
                if opt_result["optimized_positions"]:
                    rmsd = calculate_rmsd(
                        separated["linker_positions"],
                        opt_result["optimized_positions"]
                    )

        # 5. Skor stabilitas
        stability = calculate_stability_score(delta_e, rmsd)

        # 6. Data 3D
        structure_3d = prepare_3d_structure_data(
            parsed["atoms"], parsed["positions"]
        )

        return {
            "status": "success",
            "formula": parsed["formula"],
            "n_atoms": parsed["n_atoms"],
            "n_sbu_atoms": separated["sbu_count"],
            "n_linker_atoms": separated["linker_count"],
            "delta_e": delta_e,
            "rmsd": rmsd,
            "stability_score": stability["stability_score"],
            "stability_status": stability["stability_status"],
            "is_feasible": stability["is_feasible"],
            "structure_3d": structure_3d,
            "cell_params": parsed["cell_params"],
            "xtb_available": XTB_AVAILABLE
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
