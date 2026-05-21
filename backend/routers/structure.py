from fastapi import APIRouter, UploadFile, File, HTTPException
from services.structure_parser import (
    parse_cif_file, separate_sbu_and_linker,
    calculate_rmsd, calculate_stability_score, prepare_3d_structure_data,
    relax_hydrogens_uff, analyze_linker_stability
)
from services.xtb_runner import (
    XTB_AVAILABLE, run_xtb_single_point,
    run_xtb_optimization, calculate_delta_e,
    atoms_positions_to_xyz
)

router = APIRouter()
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post("/api/structure")
async def analyze_structure(file: UploadFile = File(...)):
    """
    Analisis struktur MOF dari file CIF.

    Alur:
    1. Parse file CIF → ekstrak atom & posisi
    2. Pisahkan SBU dan linker
    3. Hitung energi linker (embedded vs free) via xTB setelah relaksasi hidrogen UFF
    4. Hitung RMSD distorsi geometri terselaraskan dengan Kabsch
    5. Gabungkan menjadi skor stabilitas
    6. Siapkan data 3D untuk visualisasi
    """
    # Validasi file
    if not file.filename.endswith(".cif"):
        raise HTTPException(status_code=400,
                          detail="Hanya file .cif yang diterima")

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Ukuran file melebihi batas 5 MB")

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
        stability_failure = False

        if XTB_AVAILABLE and separated["linker_count"] > 0:
            # Konversi linker positions ke XYZ
            linker_xyz = atoms_positions_to_xyz(
                separated["linker_atoms"], separated["linker_positions"]
            )

            # Relaksasi atom H (heavy atoms di-fix)
            relaxed_xyz = relax_hydrogens_uff(linker_xyz)

            # Single point energy (embedded geometry)
            sp_result = run_xtb_single_point(relaxed_xyz)
            if not sp_result["success"]:
                stability_failure = True

            # Optimization (free geometry)
            opt_result = run_xtb_optimization(relaxed_xyz)
            if not opt_result["success"]:
                stability_failure = True

            if not stability_failure:
                # Selisih energi konformasi (kJ/mol)
                delta_e = calculate_delta_e(
                    sp_result["energy_kj_mol"],
                    opt_result["energy_kj_mol"]
                )

                # Gunakan RMSD Kabsch terselaraskan dari analyze_linker_stability
                analysis = analyze_linker_stability(relaxed_xyz, opt_result["optimized_xyz"])
                rmsd = analysis["rmsd_all"]

        # 5. Skor stabilitas
        if stability_failure:
            stability = {
                "stability_score": 999.0,
                "stability_status": "Tidak stabil",
                "is_feasible": False,
            }
        else:
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


@router.post("/api/linker/stability")
async def analyze_linker_stability_endpoint(file: UploadFile = File(...)):
    """
    Endpoint untuk menganalisis stabilitas konformasi linker dan distorsi geometri.
    Menerima file .xyz atau .cif, melakukan relaksasi UFF dan perhitungan xTB,
    dan mengembalikan data perbandingan lengkap.
    """
    if not (file.filename.endswith(".xyz") or file.filename.endswith(".cif")):
        raise HTTPException(status_code=400, detail="Hanya file .xyz atau .cif yang diterima")

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Ukuran file melebihi batas 5 MB")

    try:
        # Tentukan content XYZ awal
        if file.filename.endswith(".xyz"):
            xyz_content = content.decode("utf-8", errors="replace")
        else:
            # Parse CIF
            parsed = parse_cif_file(content, file.filename)
            separated = separate_sbu_and_linker(parsed["atoms"], parsed["positions"])
            if separated["linker_count"] > 0:
                xyz_content = atoms_positions_to_xyz(separated["linker_atoms"], separated["linker_positions"])
            else:
                xyz_content = atoms_positions_to_xyz(parsed["atoms"], parsed["positions"])

        if not XTB_AVAILABLE:
            raise HTTPException(status_code=503, detail="Layanan GFN2-xTB tidak tersedia di server lokal.")

        # 1. Relaksasi H (UFF dengan heavy atoms fixed)
        relaxed_xyz = relax_hydrogens_uff(xyz_content)

        # 2. Perhitungan xTB Single Point
        sp_result = run_xtb_single_point(relaxed_xyz)
        if not sp_result["success"]:
            raise ValueError(f"Perhitungan Single Point xTB gagal: {sp_result.get('error')}")

        # 3. Perhitungan xTB Geometry Optimization
        opt_result = run_xtb_optimization(relaxed_xyz)
        if not opt_result["success"]:
            raise ValueError(f"Optimasi Geometri xTB gagal: {opt_result.get('error')}")

        # 4. Ambil energi dalam Hartree dan konversi ke kcal/mol (1 Hartree = 627.509 kcal/mol)
        e_sp_hartree = sp_result["energy_hartree"]
        e_opt_hartree = opt_result["energy_hartree"]

        e_sp_kcal = e_sp_hartree * 627.509
        e_opt_kcal = e_opt_hartree * 627.509
        delta_e_kcal = (e_sp_hartree - e_opt_hartree) * 627.509

        # 5. Analisis distorsi geometri dan alignment Kabsch
        analysis = analyze_linker_stability(relaxed_xyz, opt_result["optimized_xyz"])

        return {
            "status": "success",
            "e_sp_kcal": round(e_sp_kcal, 4),
            "e_opt_kcal": round(e_opt_kcal, 4),
            "delta_e_kcal": round(delta_e_kcal, 4),
            "rmsd_all": analysis["rmsd_all"],
            "rmsd_heavy": analysis["rmsd_heavy"],
            "me_delta_length": analysis["me_delta_length"],
            "me_delta_angle": analysis["me_delta_angle"],
            "atoms_displacement": analysis["atoms_displacement"],
            "coords_embedded": analysis["coords_embedded"],
            "coords_optimized": analysis["coords_optimized"],
            "bonds": analysis["bonds"]
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


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
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Ukuran file melebihi batas 5 MB")

    try:
        parsed = parse_cif_file(content, file.filename)

        # Return raw CIF content + parsed atoms
        return {
            "status": "success",
            "structure_3d": prepare_3d_structure_data(
                parsed["atoms"], parsed["positions"]
            ),
            "formula": parsed["formula"],
            "cell_params": parsed["cell_params"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
