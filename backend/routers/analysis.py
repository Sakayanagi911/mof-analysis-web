from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import Descriptors  

from models.schemas import FeasibilityRequest, FeasibilityResponse
from models.schemas import EconomicRequest, EconomicResponse
from services.whitebox_model import predict_working_capacity, calculate_wug, calculate_wuv
from services.cost_analysis import run_economic_analysis, get_modulator_concentration_data

# 1. Impor fungsi bawaan Anda agar hitungannya 100% konsisten dengan Notebook
from services.joback import calculate_cp_joback

router = APIRouter()

def get_chem_prop(name: str, is_metal=False):
    """
    Mencari nilai rho (g/mL), Cp (J/mol·K), dan Mr (g/mol) dengan fuzzy matching.
    Sesuai dengan database di cost_analysis.py.
    """
    if not name or name == "-":
        # (density, cp_mol_k, molecular_weight)
        return 1.0, (110.0 if is_metal else 75.0), 100.0
    
    n = name.lower().replace(" ", "").replace("₃", "3").replace("₂", "2").replace("(", "").replace(")", "")
    
    # Format: (rho_g_ml, cp_J_mol_K, mr_g_mol)
    if "dmf" in n: return 0.948, 148.16, 73.09      # DMF: Cp=148.16 J/mol·K, Mr=73.09
    if "hcl" in n: return 1.190, 29.12, 36.46       # HCl: Cp≈29.12 J/mol·K, Mr=36.46
    if "h2o" in n or "water" in n: return 1.000, 75.3, 18.015   # H2O: Cp=75.3 J/mol·K, Mr=18.015
    if "eth" in n or "etoh" in n: return 0.789, 112.4, 46.07    # EtOH: Cp≈112.4 J/mol·K, Mr=46.07
    if "meth" in n or "meoh" in n: return 0.792, 81.1, 32.04    # MeOH: Cp≈81.1 J/mol·K, Mr=32.04
    if "cu" in n: return 1.000, 110.0, 63.55        # Cu: typical metal Cp≈110 J/mol·K
    if "zr" in n: return 1.000, 90.0, 91.22         # Zr: typical Cp≈90 J/mol·K
    if "zn" in n: return 1.000, 100.0, 65.38        # Zn: typical Cp≈100 J/mol·K
    
    return 1.0, (110.0 if is_metal else 75.0), 100.0


def get_energy_scale_factor(solvent_vol: float, additive_vol: float, modulator_vol: float) -> float:
    """
    TIDAK DIGUNAKAN LAGI - Perhitungan murni matematis tanpa scale factor.
    Fungsi ini di-keep untuk backward compatibility tapi selalu return 1.0
    """
    return 1.0


@router.post("/analyze")
async def analyze_mof(
    file: UploadFile = File(None),  # DEPRECATED: Use file_embedded instead
    file_free: UploadFile = File(None),      # NEW: Free linker XYZ
    file_embedded: UploadFile = File(None),  # NEW: Embedded linker XYZ
    pv: str = Form("1.2"), 
    gsa: str = Form("3000"), 
    vsa: str = Form("1500"),
    lcd: str = Form("12.1"), 
    pld: str = Form("8"), 
    vf: str = Form("0.5"),
    density: str = Form("0.8"), 
    metal_name: str = Form("-"),
    metal_mass: str = Form("0"),      
    linker_name: str = Form("-"), 
    linker_mass: str = Form("0"),     
    smiles: str = Form("-"),
    solvent_name: str = Form("-"),
    solvent_volume: str = Form("0"),  
    additive_name: str = Form("-"),   
    additive_volume: str = Form("0"), 
    modulator_name: str = Form("-"),  
    modulator_volume: str = Form("0"),
    modulator_concentration: str = Form("100.0"),  # NEW: User input concentration (default 100%)
    product_mass: str = Form("0"),  
    reaction_time: str = Form("24"), 
    temperature: str = Form("120")
):
    # Parser aman - untuk geometric factors, jika kosong atau 0 maka gunakan 0
    def parse_f(val: str, default: float = 0.0) -> float:
        try:
            return float(val) if val and str(val).strip() != "" else default
        except (ValueError, TypeError):
            return default

    # 1. Parsing Form Data - geometric factors tanpa default fallback (gunakan 0)
    f_pv = parse_f(pv, 0.0)
    f_gsa = parse_f(gsa, 0.0)
    f_vsa = parse_f(vsa, 0.0)
    f_lcd = parse_f(lcd, 0.0)
    f_pld = parse_f(pld, 0.0)
    f_density = parse_f(density, 0.0)
    f_vf = parse_f(vf, 0.0)
    valid_vf = f_vf / 100.0 if f_vf > 1.0 else f_vf
    
    f_metal_mass = parse_f(metal_mass, 0.0)
    f_linker_mass = parse_f(linker_mass, 0.0)
    f_solvent_vol = parse_f(solvent_volume, 0.0)
    f_additive_vol = parse_f(additive_volume, 0.0)
    f_modulator_vol = parse_f(modulator_volume, 0.0)
    f_modulator_concentration = parse_f(modulator_concentration, 100.0)  # NEW: Parse concentration
    
    f_product_mass = parse_f(product_mass, 0.0)
    f_reaction_time = parse_f(reaction_time, 24.0)
    f_temperature = parse_f(temperature, 120.0)

    # 2. Hitung Kapasitas & Ekonomi
    # SELALU hitung WUG dan WUV secara dinamis dari input user (untuk display)
    wug = calculate_wug(density=f_density, GSA=f_gsa, VSA=f_vsa, VF=valid_vf, PV=f_pv, LCD=f_lcd, PLD=f_pld)
    wuv = calculate_wuv(density=f_density, GSA=f_gsa, VSA=f_vsa, VF=valid_vf, PV=f_pv, LCD=f_lcd, PLD=f_pld)
    
    # FIXED: Use calculate_mof_cost directly like the test script to avoid parameter modification
    from services.cost_analysis import calculate_mof_cost, calculate_storage_cost, calculate_energy, get_uptake_data
    
    # PENTING: Untuk Top 5 MOFs, SELALU gunakan uptake data dari database
    # Karena data di database sudah melalui perhitungan yang sama dan sudah benar
    uptake_data = get_uptake_data()
    smiles_normalized = smiles.strip() if smiles else ""
    
    # Untuk Top 5 MOFs: WAJIB gunakan database uptake (data sudah benar dari Excel)
    if smiles_normalized in uptake_data:
        uptake_info = uptake_data[smiles_normalized]
        cost_calc_gravimetric = uptake_info.get("gravimetric_wc_percent", wug)
        cost_calc_volumetric = uptake_info.get("volumetric_wc_g_per_l", wuv)
    else:
        # Untuk MOF lain, gunakan calculated values
        cost_calc_gravimetric = wug
        cost_calc_volumetric = wuv
    
    # Calculate MOF cost using exact same method as test script
    cost_result = calculate_mof_cost(
        metal_name=metal_name,
        linker_smiles=smiles,
        metal_mass_mg=f_metal_mass,
        linker_mass_mg=f_linker_mass,
        product_mass_mg=f_product_mass,
        solvent_name=solvent_name,
        solvent_volume_ml=f_solvent_vol,
        additive_name=additive_name if additive_name != "-" else "-",
        additive_volume_ml=f_additive_vol,
        modulator_name=modulator_name if modulator_name != "-" else "-",
        modulator_volume_ml=f_modulator_vol
    )
    
    # Calculate storage cost using appropriate uptake value
    mof_cost = cost_result["mof_cost_usd_per_kg"]
    storage_cost = calculate_storage_cost(mof_cost, cost_calc_gravimetric)
    
    # Calculate energy using appropriate uptake values
    energy_result = calculate_energy(
        smiles=smiles,
        temperature_c=f_temperature,
        reaction_time_h=f_reaction_time,
        linker_mass_mg=f_linker_mass,
        metal_mass_mg=f_metal_mass,
        solvent_name=solvent_name,
        solvent_volume_ml=f_solvent_vol,
        additive_name=additive_name,
        additive_volume_ml=f_additive_vol,
        modulator_name=modulator_name,
        modulator_volume_ml=f_modulator_vol,
        modulator_concentration=f_modulator_concentration,  # Use user input concentration
        metal_name=metal_name,
        volumetric_wc=cost_calc_volumetric,
        gravimetric_wc=cost_calc_gravimetric,
        product_mass_mg=f_product_mass,
        energy_scale_factor=get_energy_scale_factor(f_solvent_vol, f_additive_vol, f_modulator_vol)
    )
    
    # Calculate xTB structure analysis from uploaded file(s)
    # Accepts 3 modes:
    # 1. TWO XYZ files (file_free + file_embedded) - BEST method, matches notebook
    # 2. Single XYZ (file or file_embedded) - Auto-optimize to get free linker
    # 3. CIF file (file) - Auto-extract + optimize
    from services.xtb_runner import XTB_AVAILABLE, analyze_cif_structure, analyze_embedded_xyz, analyze_two_xyz_files
    
    structure_result = {
        "conformational_energy_kcal": 0.0,
        "rmsd_final_angstrom": 0.0,
        "me_delta_length_angstrom": 0.0,
        "me_delta_angle_deg": 0.0,
        "structure_status": "No structure file uploaded",
        "structure_feasible": None,
        "xtb_available": XTB_AVAILABLE,
        "stability_score": "Unknown",
        "stability_level": 0,
        "free_structure": None,
        "embedded_structure": None
    }
    
    # Determine which file(s) were uploaded
    upload_mode = None
    if file_free and file_embedded:
        upload_mode = "two_xyz"
    elif file_embedded or (file and file.filename.endswith('.xyz')):
        upload_mode = "single_xyz"
    elif file and file.filename.endswith('.cif'):
        upload_mode = "cif"
    
    # Analyze structure based on upload mode
    if upload_mode:
        try:
            # Save uploaded file(s) temporarily
            upload_dir = Path(__file__).parent.parent / "data" / "uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            if upload_mode == "two_xyz":
                # Mode 1: TWO XYZ files (best method)
                print(f"📂 Analyzing TWO XYZ files (matches notebook workflow)")
                
                # Save free linker file
                free_content = await file_free.read()
                free_path = upload_dir / file_free.filename
                with open(free_path, "wb") as f:
                    f.write(free_content)
                
                # Save embedded linker file
                embedded_content = await file_embedded.read()
                embedded_path = upload_dir / file_embedded.filename
                with open(embedded_path, "wb") as f:
                    f.write(embedded_content)
                
                if XTB_AVAILABLE:
                    analysis = analyze_two_xyz_files(str(free_path), str(embedded_path))
                else:
                    analysis = {"success": False, "error": "xTB not available"}
                
                # Clean up
                if free_path.exists():
                    free_path.unlink()
                if embedded_path.exists():
                    embedded_path.unlink()
            
            elif upload_mode == "single_xyz":
                # Mode 2: Single XYZ (auto-optimize)
                target_file = file_embedded if file_embedded else file
                
                print(f"📂 Analyzing single XYZ file (auto-optimize): {target_file.filename}")
                
                file_content = await target_file.read()
                file_path = upload_dir / target_file.filename
                with open(file_path, "wb") as f:
                    f.write(file_content)
                
                if XTB_AVAILABLE:
                    analysis = analyze_embedded_xyz(str(file_path))
                else:
                    analysis = {"success": False, "error": "xTB not available"}
                
                # Clean up
                if file_path.exists():
                    file_path.unlink()
            
            else:  # upload_mode == "cif"
                # Mode 3: CIF (auto-extract + optimize)
                print(f"📂 Analyzing CIF file (auto-extract linker): {file.filename}")
                
                file_content = await file.read()
                file_path = upload_dir / file.filename
                with open(file_path, "wb") as f:
                    f.write(file_content)
                
                if XTB_AVAILABLE:
                    analysis = analyze_cif_structure(str(file_path))
                else:
                    analysis = {"success": False, "error": "xTB not available"}
                
                # Clean up
                if file_path.exists():
                    file_path.unlink()
            
            # Process analysis results
            if analysis["success"]:
                delta_e = analysis["conformational_energy_kcal"]
                
                # Determine stability level based on ΔE - Updated ranges
                if delta_e <= 50.0:
                    stability_score = "Very Stable"
                    stability_level = 4
                    structure_feasible = True
                elif 50.0 < delta_e <= 85.0:
                    stability_score = "Stable"
                    stability_level = 3
                    structure_feasible = True
                elif 85.0 < delta_e <= 250.0:
                    stability_score = "Less Stable"
                    stability_level = 2
                    structure_feasible = True  # Changed to True - Less Stable is still feasible
                else:  # delta_e > 250.0
                    stability_score = "Unstable"
                    stability_level = 1
                    structure_feasible = False
                
                structure_result = {
                    "conformational_energy_kcal": delta_e,
                    "rmsd_final_angstrom": analysis["rmsd_final_angstrom"],
                    "me_delta_length_angstrom": analysis["me_delta_length_angstrom"],
                    "me_delta_angle_deg": analysis["me_delta_angle_deg"],
                    "structure_status": f"ΔE = {delta_e:.2f} kcal/mol - {stability_score}",
                    "structure_feasible": structure_feasible,
                    "xtb_available": True,
                    "embedded_energy_kcal": analysis.get("embedded_energy_kcal", 0.0),
                    "free_energy_kcal": analysis.get("free_energy_kcal", 0.0),
                    "stability_score": stability_score,
                    "stability_level": stability_level,
                    "free_structure": analysis.get("free_structure"),
                    "embedded_structure": analysis.get("embedded_structure"),
                    "upload_mode": upload_mode
                }
            else:
                error_msg = analysis.get('error', 'Unknown error')
                structure_result["structure_status"] = f"xTB analysis failed: {error_msg}"
                structure_result["structure_feasible"] = False  # Set to False when analysis fails
                structure_result["upload_mode"] = upload_mode
                
        except Exception as e:
            import traceback
            error_msg = f"File processing error: {str(e)}"
            traceback.print_exc()
            structure_result["structure_status"] = error_msg
            structure_result["structure_feasible"] = False  # Set to False when processing fails
            structure_result["upload_mode"] = upload_mode if upload_mode else "unknown"
    
    # Check feasibility using calculated WUG/WUV (dynamic) for DOE feasibility
    # But use database values for cost feasibility
    MAX_MOF_COST = 30.0
    MAX_STORAGE_COST = 300.0
    is_feasible = (
        mof_cost <= MAX_MOF_COST and
        storage_cost <= MAX_STORAGE_COST and
        f_reaction_time <= 48.0 and
        f_temperature <= 180.0
    )
    
    # Create econ_result structure compatible with existing code
    econ_result = {
        "mof_cost_usd_per_kg": mof_cost,
        "storage_cost_usd_per_kg_h2": storage_cost,
        "q_energy_mj": energy_result["q_energy_mj"],
        "q_loss_mj": energy_result["q_loss_mj"],
        "e_stirr_mj": energy_result["e_stirr_mj"],
        "e_total_mj": energy_result["e_total_mj"],
        "energy_details": energy_result,
        "is_feasible": is_feasible,
        "feasibility_details": {
            "mof_cost_ok": mof_cost <= MAX_MOF_COST,
            "storage_cost_ok": storage_cost <= MAX_STORAGE_COST,
            "time_ok": f_reaction_time <= 48.0,
            "temperature_ok": f_temperature <= 180.0
        }
    }

    # ==========================================
    # 3. AMBIL HASIL ENERGI DARI ECONOMIC ANALYSIS
    # ==========================================
    # Semua perhitungan energi sudah dilakukan di cost_analysis.py
    # Hanya perlu ambil hasilnya dari econ_result
    
    # Untuk menampilkan breakdown sensible heat, ambil dari hasil cost_analysis.py yang lebih akurat
    # (cost_analysis.py sudah punya MANUAL_CP_MAP dan perhitungan yang 100% konsisten)
    energy_details = econ_result.get("energy_details", {})

    return {
        "status": "success",
        "results": {
            # DISPLAY: Gunakan hasil perhitungan dinamis WUG/WUV dari input user
            "gravimetric_h2": round(wug, 3),  # Dynamic calculation from user input
            "volumetric_h2": round(wuv, 3),   # Dynamic calculation from user input
            "doe_feasible": (wug >= 5.5 and wuv >= 40.0),  # Use dynamic values for DOE feasibility
            
            # COST: Gunakan hasil yang sudah diperbaiki (database uptake untuk akurasi)
            "mof_cost": econ_result["mof_cost_usd_per_kg"],
            "mof_cost_ok": econ_result["feasibility_details"]["mof_cost_ok"],
            "storage_cost": econ_result["storage_cost_usd_per_kg_h2"],
            "storage_cost_ok": econ_result["feasibility_details"]["storage_cost_ok"],
            
            # Data Tabel Sensible Heat
            "cp_linker": energy_details.get("cp_value", 0.0),  # CP dalam J/(mol·K)
            "linker_mw": energy_details.get("linker_mw", 0.0),  # Molecular weight dalam g/mol
            "e_sensible_solvent": energy_details.get("e_sensible_solvent_j", 0.0),
            "e_sensible_additive": energy_details.get("e_sensible_additive_j", 0.0),
            "e_sensible_modulator": energy_details.get("e_sensible_modulator_j", 0.0),
            "e_sensible_metal": energy_details.get("e_sensible_metal_j", 0.0),
            "e_sensible_linker": energy_details.get("e_sensible_linker_j", 0.0),
            "e_sensible_total": energy_details.get("e_sensible_total_j", 0.0),

            # Card Heat Metrics (dari cost_analysis.py yang konsisten)
            "q_energy": econ_result["q_energy_mj"], 
            "q_loss": econ_result["q_loss_mj"],
            "e_stirr": econ_result["e_stirr_mj"],       
            "e_tot": econ_result["e_total_mj"], 
            
            "reaction_time": f_reaction_time,
            "time_ok": f_reaction_time <= 48,
            "temperature": f_temperature,
            "temp_ok": f_temperature <= 180,
            
            # Structure analysis dari xTB (4 output yang diminta)
            "conformational_energy_kcal": structure_result["conformational_energy_kcal"],
            "rmsd_final_angstrom": structure_result["rmsd_final_angstrom"],
            "me_delta_length_angstrom": structure_result["me_delta_length_angstrom"],
            "me_delta_angle_deg": structure_result["me_delta_angle_deg"],
            "structure_status": structure_result["structure_status"],
            "structure_feasible": structure_result["structure_feasible"],
            "xtb_available": structure_result["xtb_available"],
            
            # NEW: 3D Structure data for visualization
            "free_structure": structure_result.get("free_structure"),
            "embedded_structure": structure_result.get("embedded_structure"),
            "upload_mode": structure_result.get("upload_mode", "none"),
            "stability_score": structure_result.get("stability_score", "Unknown"),
            "stability_level": structure_result.get("stability_level", 0),
            
            "econ_feasible": econ_result["is_feasible"],
            # Overall feasibility: DOE (dynamic WUG/WUV) + Economic (database-based cost) + Structure
            "is_overall_feasible": (wug >= 5.5 and wuv >= 40.0 and econ_result["is_feasible"] and 
                                  (structure_result["structure_feasible"] if structure_result["structure_feasible"] is not None else True))
        }
    }

@router.post("/api/feasibility", response_model=FeasibilityResponse)
async def analyze_feasibility(request: FeasibilityRequest):
    try:
        result = predict_working_capacity(
            density=request.p, gsa=request.gsa, vsa=request.vsa,
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
            linker_smiles=request.smiles,  # Changed: use smiles as linker identifier
            reaction_time=request.reaction_time,
            temperature=request.temperature,
            smiles=request.smiles,
            # REMOVED: gravimetric_wc=request.gravimetric_wc,
            # Sekarang akan auto-lookup dari database berdasarkan SMILES
            product_mass_mg=request.product_mass_mg,
            metal_mass_mg=request.metal_mass_mg,
            linker_mass_mg=request.linker_mass_mg,
            solvent_name=request.solvent_name,
            solvent_volume_ml=request.solvent_volume_ml,
            additive_name=request.additive_name,
            additive_volume_ml=request.additive_volume_ml,
            modulator_name=request.modulator_name,
            modulator_volume_ml=request.modulator_volume_ml,
            modulator_concentration=getattr(request, 'modulator_concentration', 100.0),  # Use user input or default 100%
            energy_scale_factor=get_energy_scale_factor(
                request.solvent_volume_ml,
                request.additive_volume_ml,
                request.modulator_volume_ml
            )
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