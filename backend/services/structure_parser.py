"""
Modul parsing file CIF dan analisis struktur MOF.
Referensi: old_model/Input_for_DFT,_xTB_Conformational_Energy,_and_Geometry_Distortion_Bound_within_the_SBU.ipynb
"""

import math
import uuid
from pathlib import Path

try:
    from ase.io import read as ase_read
    ASE_AVAILABLE = True
except ImportError:
    ASE_AVAILABLE = False


def parse_cif_file(file_content: bytes, filename: str) -> dict:
    """
    Parse file CIF dan ekstrak informasi struktur.

    Args:
        file_content: Konten file CIF dalam bytes
        filename: Nama file asli

    Returns:
        dict: {atoms, positions, n_atoms, cell_params, formula}
    """
    # Simpan ke file temporary dengan nama unik
    upload_dir = Path(__file__).parent.parent / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Buat nama file unik menggunakan UUID untuk menghindari race condition
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    temp_path = upload_dir / unique_name

    try:
        with open(temp_path, "wb") as f:
            f.write(file_content)

        if ASE_AVAILABLE:
            parsed = _parse_with_ase(temp_path)
        else:
            parsed = _parse_manual(file_content, temp_path)

        if parsed["n_atoms"] <= 0 or len(parsed["positions"]) <= 0:
            raise ValueError("File CIF tidak valid atau tidak mengandung data atom")
        return parsed
    finally:
        # Selalu hapus file temporary setelah selesai diproses
        if temp_path.exists():
            temp_path.unlink()


def _parse_with_ase(file_path: Path) -> dict:
    """Parse CIF menggunakan ASE library."""
    try:
        structure = ase_read(str(file_path))

        symbols = structure.get_chemical_symbols()
        positions = structure.get_positions().tolist()

        # Cell parameters
        cell = structure.get_cell()
        cell_lengths = cell.lengths()
        cell_angles = cell.angles()
        cell_params = {
            "a": round(float(cell_lengths[0]), 4),
            "b": round(float(cell_lengths[1]), 4),
            "c": round(float(cell_lengths[2]), 4),
            "alpha": round(float(cell_angles[0]), 4),
            "beta": round(float(cell_angles[1]), 4),
            "gamma": round(float(cell_angles[2]), 4),
        }

        # Chemical formula
        formula = structure.get_chemical_formula()

        return {
            "atoms": symbols,
            "positions": positions,
            "n_atoms": len(symbols),
            "cell_params": cell_params,
            "formula": formula,
            "file_path": str(file_path)
        }
    except Exception as e:
        raise ValueError(f"Gagal membaca file CIF dengan ASE: {str(e)}")


def _parse_manual(file_content: bytes, file_path: Path) -> dict:
    """
    Fallback parser: parse CIF secara manual tanpa ASE.
    Mendukung format CIF standar dengan _atom_site loop.
    """
    text = file_content.decode("utf-8", errors="replace")
    lines = text.splitlines()

    cell_params = {"a": 0, "b": 0, "c": 0, "alpha": 90, "beta": 90, "gamma": 90}
    atoms = []
    positions = []
    formula = ""

    # Extract cell parameters
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("_cell_length_a"):
            cell_params["a"] = _extract_cif_number(line_stripped)
        elif line_stripped.startswith("_cell_length_b"):
            cell_params["b"] = _extract_cif_number(line_stripped)
        elif line_stripped.startswith("_cell_length_c"):
            cell_params["c"] = _extract_cif_number(line_stripped)
        elif line_stripped.startswith("_cell_angle_alpha"):
            cell_params["alpha"] = _extract_cif_number(line_stripped)
        elif line_stripped.startswith("_cell_angle_beta"):
            cell_params["beta"] = _extract_cif_number(line_stripped)
        elif line_stripped.startswith("_cell_angle_gamma"):
            cell_params["gamma"] = _extract_cif_number(line_stripped)
        elif line_stripped.startswith("_chemical_formula_sum"):
            parts = line_stripped.split(None, 1)
            if len(parts) > 1:
                formula = parts[1].strip().strip("'\"")

    # Extract atom sites from loop_
    atom_site_labels = []
    in_atom_loop = False
    reading_headers = False
    label_col = -1
    type_col = -1
    x_col = -1
    y_col = -1
    z_col = -1

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line == "loop_":
            # Check if next lines contain _atom_site
            if i + 1 < len(lines) and "_atom_site" in lines[i + 1]:
                in_atom_loop = True
                reading_headers = True
                atom_site_labels = []
                i += 1
                continue

        if in_atom_loop and reading_headers:
            if line.startswith("_atom_site"):
                col_idx = len(atom_site_labels)
                atom_site_labels.append(line)
                if "_atom_site_type_symbol" in line:
                    type_col = col_idx
                elif "_atom_site_label" in line and label_col == -1:
                    label_col = col_idx
                if "_atom_site_fract_x" in line:
                    x_col = col_idx
                elif "_atom_site_fract_y" in line:
                    y_col = col_idx
                elif "_atom_site_fract_z" in line:
                    z_col = col_idx
                elif "_atom_site_Cartn_x" in line:
                    x_col = col_idx
                elif "_atom_site_Cartn_y" in line:
                    y_col = col_idx
                elif "_atom_site_Cartn_z" in line:
                    z_col = col_idx
            else:
                reading_headers = False
                # Now parse data lines

        if in_atom_loop and not reading_headers:
            if not line or line.startswith("loop_") or line.startswith("_") or line.startswith("#"):
                in_atom_loop = False
                i += 1
                continue

            parts = line.split()
            if len(parts) >= len(atom_site_labels):
                # Determine atom symbol
                symbol_col = type_col if type_col >= 0 else label_col
                if symbol_col >= 0 and symbol_col < len(parts):
                    symbol = parts[symbol_col]
                    # Clean symbol: remove digits, keep only letters
                    clean_symbol = ''.join(c for c in symbol if c.isalpha())
                    if clean_symbol:
                        atoms.append(clean_symbol)

                        # Extract coordinates
                        if x_col >= 0 and y_col >= 0 and z_col >= 0:
                            try:
                                x = _extract_cif_number_from_str(parts[x_col])
                                y = _extract_cif_number_from_str(parts[y_col])
                                z = _extract_cif_number_from_str(parts[z_col])

                                # Check if fractional coordinates
                                if any("_atom_site_fract" in lbl for lbl in atom_site_labels):
                                    # Convert fractional to Cartesian
                                    x_cart, y_cart, z_cart = _frac_to_cart(
                                        x, y, z, cell_params
                                    )
                                    positions.append([x_cart, y_cart, z_cart])
                                else:
                                    positions.append([x, y, z])
                            except (ValueError, IndexError):
                                pass

        i += 1

    if not formula and atoms:
        # Generate formula from atom counts
        from collections import Counter
        counts = Counter(atoms)
        formula = ''.join(f"{el}{cnt}" if cnt > 1 else el
                         for el, cnt in sorted(counts.items()))

    return {
        "atoms": atoms,
        "positions": positions,
        "n_atoms": len(atoms),
        "cell_params": cell_params,
        "formula": formula,
        "file_path": str(file_path)
    }



def _extract_cif_number(line: str) -> float:
    """Extract numeric value from a CIF parameter line like '_cell_length_a 12.345(6)'."""
    parts = line.split()
    if len(parts) >= 2:
        return _extract_cif_number_from_str(parts[-1])
    return 0.0


def _extract_cif_number_from_str(s: str) -> float:
    """Extract number from CIF string, removing uncertainty in parentheses."""
    # Remove uncertainty notation like '12.345(6)' → '12.345'
    idx = s.find('(')
    if idx >= 0:
        s = s[:idx]
    return float(s)


def _frac_to_cart(x_frac, y_frac, z_frac, cell_params):
    """Convert fractional coordinates to Cartesian coordinates."""
    a = cell_params["a"]
    b = cell_params["b"]
    c = cell_params["c"]
    alpha = math.radians(cell_params["alpha"])
    beta = math.radians(cell_params["beta"])
    gamma = math.radians(cell_params["gamma"])

    cos_alpha = math.cos(alpha)
    cos_beta = math.cos(beta)
    cos_gamma = math.cos(gamma)
    sin_gamma = math.sin(gamma)

    volume_factor = math.sqrt(
        1 - cos_alpha**2 - cos_beta**2 - cos_gamma**2
        + 2 * cos_alpha * cos_beta * cos_gamma
    )

    x = a * x_frac + b * cos_gamma * y_frac + c * cos_beta * z_frac
    y = b * sin_gamma * y_frac + c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma * z_frac
    z = c * volume_factor / sin_gamma * z_frac

    return round(x, 6), round(y, 6), round(z, 6)


def separate_sbu_and_linker(atoms: list, positions: list) -> dict:
    """
    Pisahkan SBU (metal cluster) dan linker (organik) dari struktur MOF.

    Logika sederhana:
    - Metal atoms (Cu, Zn, Zr, Al, Fe, Cr, Co, Ni, Mn, dll) → SBU
    - Non-metal (C, H, N, O, S, dll) → Linker

    CATATAN: Ini adalah pendekatan simplifikasi. Dalam kenyataannya,
    pemisahan SBU-linker membutuhkan analisis topologi yang lebih kompleks.

    Returns:
        dict: {sbu_atoms, sbu_positions, linker_atoms, linker_positions}
    """
    METAL_SYMBOLS = {
        "Li", "Be", "Na", "Mg", "Al", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe",
        "Co", "Ni", "Cu", "Zn", "Ga", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Ru", "Rh",
        "Pd", "Ag", "Cd", "In", "Sn", "Cs", "Ba", "La", "Ce", "Hf", "Ta", "W", "Re",
        "Os", "Ir", "Pt", "Au", "Pb", "Bi"
    }

    sbu_atoms, sbu_positions = [], []
    linker_atoms, linker_positions = [], []

    for atom, pos in zip(atoms, positions):
        if atom in METAL_SYMBOLS:
            sbu_atoms.append(atom)
            sbu_positions.append(pos)
        else:
            linker_atoms.append(atom)
            linker_positions.append(pos)

    return {
        "sbu_atoms": sbu_atoms,
        "sbu_positions": sbu_positions,
        "sbu_count": len(sbu_atoms),
        "linker_atoms": linker_atoms,
        "linker_positions": linker_positions,
        "linker_count": len(linker_atoms)
    }


def calculate_rmsd(positions_1: list, positions_2: list) -> float:
    """
    Hitung RMSD antara dua set posisi atom menggunakan Kabsch algorithm
    (optimal rotation alignment).

    Args:
        positions_1: Posisi atom set 1 [[x,y,z], ...]
        positions_2: Posisi atom set 2 [[x,y,z], ...]

    Returns:
        float: RMSD dalam Ångström
    """
    import numpy as np
    
    if len(positions_1) != len(positions_2):
        raise ValueError("Jumlah atom tidak sama untuk RMSD calculation")

    n = len(positions_1)
    if n == 0:
        return 0.0

    P = np.array(positions_1)
    Q = np.array(positions_2)

    # Center the structures
    P_centered = P - P.mean(axis=0)
    Q_centered = Q - Q.mean(axis=0)

    # Covariance matrix
    C = np.dot(P_centered.T, Q_centered)

    # SVD
    U, S, Vt = np.linalg.svd(C)
    
    # Rotation matrix
    R = np.dot(U, Vt)
    
    # Handle reflection
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = np.dot(U, Vt)

    # Rotate P
    P_rot = np.dot(P_centered, R)

    # Calculate RMSD
    rmsd = np.sqrt(np.mean(np.sum((P_rot - Q_centered)**2, axis=1)))
    
    return round(float(rmsd), 4)


def calculate_stability_score(delta_e: float, rmsd: float) -> dict:
    """
    Hitung skor stabilitas gabungan dan tentukan status.

    Skor = kombinasi delta_e dan RMSD (weighted).

    Interpretasi:
        < 5    → Sangat stabil
        5-15   → Cukup stabil
        > 15   → Tidak stabil

    Args:
        delta_e: Selisih energi (kJ/mol)
        rmsd: RMSD (Å)

    Returns:
        dict: {stability_score, stability_status, is_feasible}
    """
    # Skor gabungan: utamakan delta_e, RMSD sebagai faktor koreksi
    # Bobot: 70% dari delta_e, 30% dari RMSD (dikonversi ke skala serupa)
    stability_score = abs(delta_e) * 0.7 + (rmsd * 10) * 0.3

    if stability_score < 5:
        status = "Sangat stabil"
        is_feasible = True
    elif stability_score <= 15:
        status = "Cukup stabil"
        is_feasible = True
    else:
        status = "Tidak stabil"
        is_feasible = False

    return {
        "stability_score": round(stability_score, 4),
        "stability_status": status,
        "is_feasible": is_feasible
    }


def prepare_3d_structure_data(atoms: list, positions: list) -> dict:
    """
    Siapkan data untuk visualisasi 3D di frontend.

    Format yang dihasilkan kompatibel dengan 3Dmol.js atau NGL Viewer.

    Returns:
        dict: {atoms: [{symbol, x, y, z}, ...], n_atoms: int}
    """
    atom_data = []
    for symbol, pos in zip(atoms, positions):
        atom_data.append({
            "symbol": symbol,
            "x": round(pos[0], 6),
            "y": round(pos[1], 6),
            "z": round(pos[2], 6)
        })

    return {
        "atoms": atom_data,
        "n_atoms": len(atom_data)
    }


def relax_hydrogens_uff(xyz_content: str) -> str:
    """
    Menerima xyz_content, mendeteksi ikatan dengan RDKit,
    melakukan relaksasi UFF pada atom H dengan heavy atoms fixed,
    dan mengembalikan xyz_content baru hasil relaksasi.
    Jika terjadi kesalahan (misal RDKit tidak bisa menebak valensi),
    fungsi ini akan mengembalikan xyz_content asli sebagai fallback.
    """
    import tempfile
    import os
    from rdkit import Chem
    from rdkit.Chem import rdDetermineBonds, AllChem

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_xyz = os.path.join(tmpdir, "temp.xyz")
            with open(temp_xyz, "w") as f:
                f.write(xyz_content)
            
            raw_mol = Chem.MolFromXYZFile(temp_xyz)
            if raw_mol is None:
                return xyz_content
            
            mol = Chem.Mol(raw_mol)
            rdDetermineBonds.DetermineBonds(mol, charge=0)
            
            ff = AllChem.UFFGetMoleculeForceField(mol)
            if ff:
                for i, atom in enumerate(mol.GetAtoms()):
                    if atom.GetSymbol() != "H":
                        ff.AddFixedPoint(i)
                ff.Minimize(maxIts=500)
            
            return Chem.MolToXYZBlock(mol)
    except Exception as e:
        print(f"[Warning] RDKit UFF hydrogen relaxation failed, using raw coordinates: {e}")
        return xyz_content


def parse_xyz_content(xyz_content: str):
    """Parse simbol dan koordinat dari string blok XYZ."""
    lines = xyz_content.strip().splitlines()
    if len(lines) < 3:
        return [], []
    symbols = []
    positions = []
    for line in lines[2:]:
        parts = line.split()
        if len(parts) >= 4:
            symbols.append(parts[0])
            positions.append([float(parts[1]), float(parts[2]), float(parts[3])])
    return symbols, positions


def kabsch_rmsd_internal(P, Q):
    """Algoritma Kabsch untuk perataan optimal dan RMSD."""
    import numpy as np
    P_centered = P - P.mean(axis=0)
    Q_centered = Q - Q.mean(axis=0)
    C = np.dot(P_centered.T, Q_centered)
    V, S, Wt = np.linalg.svd(C)
    d = np.sign(np.linalg.det(np.dot(Wt.T, V.T)))
    D = np.diag([1, 1, d])
    U = np.dot(Wt.T, np.dot(D, V.T))
    P_rot = np.dot(P_centered, U)
    rmsd = np.sqrt(np.mean(np.sum((P_rot - Q_centered)**2, axis=1)))
    return rmsd, P_rot, Q_centered


def detect_bonds_internal(symbols, coords, scale=1.5):
    """Mendeteksi ikatan berdasarkan jari-jari kovalen."""
    import numpy as np
    from itertools import combinations
    cov_radii = {
        'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'F': 0.57,
        'P': 1.07, 'S': 1.05, 'Cl': 1.02, 'Br': 1.20, 'I': 1.39
    }
    bonds = []
    N = len(symbols)
    for i, j in combinations(range(N), 2):
        if symbols[i] not in cov_radii or symbols[j] not in cov_radii:
            continue
        cutoff = scale * (cov_radii[symbols[i]] + cov_radii[symbols[j]])
        dist = np.linalg.norm(coords[i] - coords[j])
        if dist <= cutoff:
            bonds.append((i, j))
    return bonds


def bond_lengths_internal(coords, bonds):
    """Menghitung panjang ikatan untuk daftar ikatan."""
    import numpy as np
    return np.array([np.linalg.norm(coords[i] - coords[j]) for i, j in bonds])


def bond_angles_internal(coords, bonds):
    """Menghitung sudut ikatan untuk semua triplet."""
    import numpy as np
    angles = []
    triplets = []
    neighbor_dict = {}
    for i, j in bonds:
        neighbor_dict.setdefault(i, []).append(j)
        neighbor_dict.setdefault(j, []).append(i)
    for center, neighbors in neighbor_dict.items():
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                a, b = neighbors[i], neighbors[j]
                v1 = coords[a] - coords[center]
                v2 = coords[b] - coords[center]
                cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_theta = np.clip(cos_theta, -1.0, 1.0)
                theta = np.arccos(cos_theta) * 180 / np.pi
                angles.append(theta)
                triplets.append((a, center, b))
    return np.array(angles), triplets


def analyze_linker_stability(embedded_xyz_content: str, optimized_xyz_content: str) -> dict:
    """
    Analisis stabilitas linker MOF dengan membandingkan koordinat embedded
    dan optimized.
    """
    import numpy as np
    
    sym_emb, coord_emb = parse_xyz_content(embedded_xyz_content)
    sym_free, coord_free = parse_xyz_content(optimized_xyz_content)
    
    if len(sym_emb) != len(sym_free):
        raise ValueError("Jumlah atom tidak konsisten antar struktur")
        
    coords_emb_arr = np.array(coord_emb)
    coords_free_arr = np.array(coord_free)
    
    # RMSD All
    rmsd_all, coord_free_aligned, coord_emb_centered = kabsch_rmsd_internal(coords_free_arr, coords_emb_arr)
    
    # RMSD Heavy
    heavy_idx = [i for i, sym in enumerate(sym_free) if sym != "H"]
    if len(heavy_idx) > 0:
        rmsd_heavy, _, _ = kabsch_rmsd_internal(coords_free_arr[heavy_idx], coords_emb_arr[heavy_idx])
    else:
        rmsd_heavy = rmsd_all
        
    # Deteksi ikatan & hitung deviasi
    bonds = detect_bonds_internal(sym_free, coords_free_arr, scale=1.5)
    
    lengths_free = bond_lengths_internal(coords_free_arr, bonds)
    lengths_emb = bond_lengths_internal(coords_emb_arr, bonds)
    delta_lengths = lengths_emb - lengths_free
    me_delta_length = float(np.mean(delta_lengths)) if len(delta_lengths) > 0 else 0.0
    
    angles_free, triplets = bond_angles_internal(coords_free_arr, bonds)
    angles_emb, _ = bond_angles_internal(coords_emb_arr, bonds)
    delta_angles = angles_emb - angles_free
    me_delta_angle = float(np.mean(delta_angles)) if len(delta_angles) > 0 else 0.0
    
    # Centering untuk visualisasi 3D
    coords_free_centered = coord_free_aligned - coord_free_aligned.mean(axis=0)
    coords_emb_centered_zero = coord_emb_centered - coord_emb_centered.mean(axis=0)
    
    delta_r = np.linalg.norm(coords_emb_centered_zero - coords_free_centered, axis=1)
    
    delta_min = float(delta_r.min()) if len(delta_r) > 0 else 0.0
    delta_max = float(delta_r.max()) if len(delta_r) > 0 else 0.0
    
    # Map ke warna gradien Viridis (Biru -> Teal -> Kuning)
    displacements = []
    for i, (sym, dr) in enumerate(zip(sym_free, delta_r)):
        val_norm = (dr - delta_min) / (delta_max - delta_min) if delta_max > delta_min else 0.0
        r = int(68 + val_norm * (253 - 68))
        g = int(1 + val_norm * (231 - 1))
        b = int(84 + val_norm * (37 - 84))
        
        displacements.append({
            "index": i,
            "element": sym,
            "delta_r": round(float(dr), 4),
            "color": f"rgb({r},{g},{b})"
        })
        
    return {
        "rmsd_all": round(float(rmsd_all), 4),
        "rmsd_heavy": round(float(rmsd_heavy), 4),
        "me_delta_length": round(me_delta_length, 6),
        "me_delta_angle": round(me_delta_angle, 4),
        "atoms_displacement": displacements,
        "coords_embedded": coords_emb_centered_zero.tolist(),
        "coords_optimized": coords_free_centered.tolist(),
        "bonds": bonds
    }
