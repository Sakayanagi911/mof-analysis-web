"""
xTB Runner Service for MOF Structure Analysis
Handles conformational energy and geometry distortion calculations
Uses RDKit for automatic atom matching (same as old_model notebook)
"""

import os
import subprocess
import tempfile
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
from ase.io import read, write
from ase import Atoms

try:
    from rdkit import Chem
    from rdkit.Chem import rdMolAlign
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("⚠️  RDKit not available. Atom matching will be less accurate.")


class XTBRunner:
    """
    Service untuk menjalankan xTB calculations dan geometry analysis
    """
    
    def __init__(self, xtb_command: str = "xtb"):
        """
        Args:
            xtb_command: Path to xTB executable (default: "xtb" if in PATH)
        """
        self.xtb_command = xtb_command
        
        # Covalent radii (Å) - same as old_model
        self.cov_radii = {
            'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'F': 0.57,
            'P': 1.07, 'S': 1.05, 'Cl': 1.02, 'Br': 1.20, 'I': 1.39,
            'Cu': 1.32, 'Zn': 1.22, 'Co': 1.26, 'Ni': 1.24, 'Mn': 1.39,
            'Cd': 1.44, 'Mg': 1.41
        }
        
        self._check_xtb_installation()
    
    def _check_xtb_installation(self):
        """Check if xTB is installed and accessible"""
        try:
            result = subprocess.run(
                [self.xtb_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError(f"xTB not found or not working: {result.stderr}")
            print(f"✅ xTB found: {result.stdout.split()[0] if result.stdout else 'version unknown'}")
        except FileNotFoundError:
            raise RuntimeError(
                "xTB not found! Please install xTB:\n"
                "- Windows: Download from https://github.com/grimme-lab/xtb/releases\n"
                "- Linux/Mac: conda install -c conda-forge xtb\n"
                "- Or set xtb_command to full path"
            )
        except Exception as e:
            raise RuntimeError(f"Error checking xTB installation: {e}")
    
    def kabsch_rmsd(self, P: np.ndarray, Q: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Calculate RMSD after Kabsch alignment (following old_model implementation)
        
        Args:
            P: Coordinates of structure 1 (N x 3) - will be aligned to Q
            Q: Coordinates of structure 2 (N x 3) - reference
        
        Returns:
            rmsd: Root mean square deviation (Å)
            P_rot: Rotated P coordinates (centered, not translated back)
        """
        # Center structures
        P_centered = P - P.mean(axis=0)
        Q_centered = Q - Q.mean(axis=0)
        
        # Covariance matrix
        C = np.dot(P_centered.T, Q_centered)
        
        # SVD
        V, S, Wt = np.linalg.svd(C)
        
        # Optimal rotation
        d = np.sign(np.linalg.det(np.dot(Wt.T, V.T)))
        D = np.diag([1, 1, d])
        U = np.dot(Wt.T, np.dot(D, V.T))
        
        # Rotate P
        P_rot = np.dot(P_centered, U)
        
        # RMSD
        rmsd = np.sqrt(np.mean(np.sum((P_rot - Q_centered)**2, axis=1)))
        
        return rmsd, P_rot
    
    def run_xtb_single_point(self, atoms: Atoms, charge: int = 0) -> float:
        """
        Run xTB single point energy calculation
        
        Args:
            atoms: ASE Atoms object
            charge: Molecular charge
        
        Returns:
            Energy in kcal/mol
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write structure to XYZ
            xyz_file = os.path.join(tmpdir, "structure.xyz")
            write(xyz_file, atoms)
            
            # Run xTB
            cmd = [
                self.xtb_command,
                xyz_file,
                "--sp",  # Single point
                "--gfn", "2",  # GFN2-xTB method
                "--chrg", str(charge)
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',  # Replace undecodable characters
                    timeout=300  # 5 minutes timeout
                )
                
                # Parse energy from output
                energy_hartree = self._parse_xtb_energy(result.stdout)
                
                if energy_hartree is None:
                    raise RuntimeError(f"Failed to parse xTB energy. Output:\n{result.stdout}\n{result.stderr}")
                
                # Convert Hartree to kcal/mol
                energy_kcal = energy_hartree * 627.509  # 1 Hartree = 627.509 kcal/mol
                
                return energy_kcal
                
            except subprocess.TimeoutExpired:
                raise RuntimeError("xTB calculation timed out (>5 minutes)")
            except Exception as e:
                raise RuntimeError(f"xTB calculation failed: {e}")
    
    def _parse_xtb_energy(self, output: str) -> Optional[float]:
        """Parse energy from xTB output"""
        for line in output.split('\n'):
            if 'TOTAL ENERGY' in line:
                try:
                    # Format: "TOTAL ENERGY      -XX.XXXXXX Eh"
                    parts = line.split()
                    energy = float(parts[3])
                    return energy
                except (IndexError, ValueError):
                    continue
        return None
    
    def analyze_structure_distortion(
        self,
        atoms_free: Atoms,
        atoms_embedded: Atoms,
        scale: float = 1.5
    ) -> Dict:
        """
        Analyze geometry distortion between free and embedded structures
        (Following old_model implementation exactly)
        
        Args:
            atoms_free: Free (optimized) linker structure
            atoms_embedded: Embedded (in MOF) linker structure
            scale: Bond detection scale factor (default 1.5, same as old_model)
        
        Returns:
            Dictionary with RMSD, mean_delta_length, mean_delta_angle
        """
        # Ensure same number of atoms
        if len(atoms_free) != len(atoms_embedded):
            raise ValueError(
                f"Atom count mismatch: free={len(atoms_free)}, embedded={len(atoms_embedded)}"
            )
        
        # Get coordinates
        coords_free = atoms_free.get_positions()
        coords_embedded = atoms_embedded.get_positions()
        
        # Kabsch RMSD (P=free akan di-align ke Q=embedded)
        rmsd, coords_free_aligned = self.kabsch_rmsd(coords_free, coords_embedded)
        
        # IMPORTANT: Use ALIGNED coordinates for bond length and angle calculations
        # This matches the notebook's evaluate_distortion function
        
        # Detect bonds using free structure (with scale=1.5 like old_model)
        symbols = atoms_free.get_chemical_symbols()
        bonds = []
        for i in range(len(atoms_free)):
            for j in range(i + 1, len(atoms_free)):
                if symbols[i] not in self.cov_radii or symbols[j] not in self.cov_radii:
                    continue
                # Use ORIGINAL coords for bond detection (topology doesn't change)
                cutoff = scale * (self.cov_radii[symbols[i]] + self.cov_radii[symbols[j]])
                dist = np.linalg.norm(coords_free[i] - coords_free[j])
                if dist <= cutoff:
                    bonds.append((i, j))
        
        # Bond lengths: Use ALIGNED free coords vs embedded coords
        # In notebook: coords_free_aligned is already centered and rotated
        # But coords_emb_ordered is also centered in evaluate_distortion
        # So we need to center embedded coords too
        coords_embedded_centered = coords_embedded - coords_embedded.mean(axis=0)
        
        lengths_free = np.array([np.linalg.norm(coords_free_aligned[i] - coords_free_aligned[j]) for i, j in bonds])
        lengths_embedded = np.array([np.linalg.norm(coords_embedded_centered[i] - coords_embedded_centered[j]) for i, j in bonds])
        delta_lengths = lengths_embedded - lengths_free
        mean_delta_length = np.mean(delta_lengths) if len(delta_lengths) > 0 else 0.0
        
        # Bond angles
        # Build connectivity
        neighbor_dict = {}
        for i, j in bonds:
            neighbor_dict.setdefault(i, []).append(j)
            neighbor_dict.setdefault(j, []).append(i)
        
        angles_free = []
        angles_embedded = []
        
        for center, neighbors in neighbor_dict.items():
            if len(neighbors) >= 2:
                for idx in range(len(neighbors)):
                    for jdx in range(idx + 1, len(neighbors)):
                        a, b = neighbors[idx], neighbors[jdx]
                        
                        # Free structure angles (use ALIGNED coords)
                        v1_free = coords_free_aligned[a] - coords_free_aligned[center]
                        v2_free = coords_free_aligned[b] - coords_free_aligned[center]
                        cos_theta_free = np.dot(v1_free, v2_free) / (
                            np.linalg.norm(v1_free) * np.linalg.norm(v2_free)
                        )
                        cos_theta_free = np.clip(cos_theta_free, -1.0, 1.0)
                        angle_free = np.degrees(np.arccos(cos_theta_free))
                        angles_free.append(angle_free)
                        
                        # Embedded structure angles (use CENTERED coords)
                        v1_emb = coords_embedded_centered[a] - coords_embedded_centered[center]
                        v2_emb = coords_embedded_centered[b] - coords_embedded_centered[center]
                        cos_theta_emb = np.dot(v1_emb, v2_emb) / (
                            np.linalg.norm(v1_emb) * np.linalg.norm(v2_emb)
                        )
                        cos_theta_emb = np.clip(cos_theta_emb, -1.0, 1.0)
                        angle_emb = np.degrees(np.arccos(cos_theta_emb))
                        angles_embedded.append(angle_emb)
        
        angles_free = np.array(angles_free)
        angles_embedded = np.array(angles_embedded)
        
        if len(angles_free) > 0:
            delta_angles = angles_embedded - angles_free
            mean_delta_angle = np.mean(delta_angles)
        else:
            mean_delta_angle = 0.0
        
        return {
            "rmsd_angstrom": float(rmsd),
            "mean_delta_length_angstrom": float(mean_delta_length),
            "mean_delta_angle_degrees": float(mean_delta_angle),
            "num_bonds": len(bonds),
            "num_angles": len(angles_free),
            "coords_free_aligned": coords_free_aligned,  # For delta_r calculation
            "coords_embedded_centered": coords_embedded_centered  # For delta_r calculation
        }
    
    def analyze_structure_distortion_with_rdkit(
        self,
        xyz_file_free: str,
        xyz_file_embedded: str
    ) -> Dict:
        """
        Analyze geometry distortion using RDKit for automatic atom matching.
        This matches the old_model notebook implementation exactly.
        
        Args:
            xyz_file_free: Path to free (optimized) linker XYZ file
            xyz_file_embedded: Path to embedded linker XYZ file
        
        Returns:
            Dictionary with RMSD, mean_delta_length, mean_delta_angle
        """
        if not RDKIT_AVAILABLE:
            raise RuntimeError(
                "RDKit is required for accurate atom matching. "
                "Install with: pip install rdkit"
            )
        
        # Load XYZ files with RDKit
        mol_free = Chem.MolFromXYZFile(xyz_file_free)
        mol_embedded = Chem.MolFromXYZFile(xyz_file_embedded)
        
        if mol_free is None or mol_embedded is None:
            raise RuntimeError("Failed to load XYZ files with RDKit")
        
        # Determine bonds (XYZ files don't have bond information)
        from rdkit.Chem import rdDetermineBonds
        rdDetermineBonds.DetermineBonds(mol_free)
        rdDetermineBonds.DetermineBonds(mol_embedded)
        
        # Get heavy atom indices (exclude H) - same as old_model notebook
        heavy_atoms_free = [i for i, atom in enumerate(mol_free.GetAtoms()) if atom.GetSymbol() != 'H']
        heavy_atoms_embedded = [i for i, atom in enumerate(mol_embedded.GetAtoms()) if atom.GetSymbol() != 'H']
        
        if len(heavy_atoms_free) != len(heavy_atoms_embedded):
            raise ValueError(
                f"Heavy atom count mismatch: free={len(heavy_atoms_free)}, embedded={len(heavy_atoms_embedded)}"
            )
        
        # Create 1-to-1 mapping for heavy atoms (same as notebook)
        # This assumes atom order is already correct in both files
        atom_map = [(i, i) for i in heavy_atoms_free]
        
        # Align embedded to free using explicit atom mapping
        rmsd = rdMolAlign.AlignMol(mol_embedded, mol_free, atomMap=atom_map)
        
        print(f"  ├─ RMSD (heavy atoms only) = {rmsd:.4f} Å")
        
        # Get conformers AFTER alignment
        conf_free = mol_free.GetConformer()
        conf_embedded = mol_embedded.GetConformer()  # This is now aligned
        
        # Extract coordinates for ALL atoms (including H)
        n_atoms_free = mol_free.GetNumAtoms()
        n_atoms_emb = mol_embedded.GetNumAtoms()
        
        if n_atoms_free != n_atoms_emb:
            raise ValueError(f"Total atom count mismatch: free={n_atoms_free}, embedded={n_atoms_emb}")
        
        coords_free = np.array([list(conf_free.GetAtomPosition(i)) for i in range(n_atoms_free)])
        coords_embedded = np.array([list(conf_embedded.GetAtomPosition(i)) for i in range(n_atoms_emb)])
        
        # Get bonds from RDKit
        bonds = [(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()) for bond in mol_free.GetBonds()]
        
        if len(bonds) == 0:
            print("     ⚠️  No bonds detected by RDKit")
            return {
                "rmsd_angstrom": float(rmsd),
                "mean_delta_length_angstrom": 0.0,
                "mean_delta_angle_degrees": 0.0,
                "num_bonds": 0,
                "num_angles": 0
            }
        
        # Calculate bond lengths for BOTH structures
        lengths_free = []
        lengths_embedded = []
        for i, j in bonds:
            len_free = np.linalg.norm(coords_free[i] - coords_free[j])
            len_emb = np.linalg.norm(coords_embedded[i] - coords_embedded[j])
            lengths_free.append(len_free)
            lengths_embedded.append(len_emb)
        
        lengths_free = np.array(lengths_free)
        lengths_embedded = np.array(lengths_embedded)
        
        delta_lengths = lengths_embedded - lengths_free
        mean_delta_length = float(np.mean(delta_lengths))
        
        # Calculate bond angles
        # Build connectivity from bonds
        neighbor_dict = {}
        for i, j in bonds:
            neighbor_dict.setdefault(i, []).append(j)
            neighbor_dict.setdefault(j, []).append(i)
        
        angles_free = []
        angles_embedded = []
        
        for center, neighbors in neighbor_dict.items():
            if len(neighbors) >= 2:
                # All pairs of neighbors form angles at this center
                for idx in range(len(neighbors)):
                    for jdx in range(idx + 1, len(neighbors)):
                        a, b = neighbors[idx], neighbors[jdx]
                        
                        # Free structure angle
                        v1_free = coords_free[a] - coords_free[center]
                        v2_free = coords_free[b] - coords_free[center]
                        norm_v1_free = np.linalg.norm(v1_free)
                        norm_v2_free = np.linalg.norm(v2_free)
                        
                        if norm_v1_free > 1e-6 and norm_v2_free > 1e-6:
                            cos_theta_free = np.dot(v1_free, v2_free) / (norm_v1_free * norm_v2_free)
                            cos_theta_free = np.clip(cos_theta_free, -1.0, 1.0)
                            angle_free = np.degrees(np.arccos(cos_theta_free))
                            angles_free.append(angle_free)
                            
                            # Embedded structure angle
                            v1_emb = coords_embedded[a] - coords_embedded[center]
                            v2_emb = coords_embedded[b] - coords_embedded[center]
                            norm_v1_emb = np.linalg.norm(v1_emb)
                            norm_v2_emb = np.linalg.norm(v2_emb)
                            
                            if norm_v1_emb > 1e-6 and norm_v2_emb > 1e-6:
                                cos_theta_emb = np.dot(v1_emb, v2_emb) / (norm_v1_emb * norm_v2_emb)
                                cos_theta_emb = np.clip(cos_theta_emb, -1.0, 1.0)
                                angle_emb = np.degrees(np.arccos(cos_theta_emb))
                                angles_embedded.append(angle_emb)
        
        if len(angles_free) > 0 and len(angles_embedded) > 0:
            angles_free = np.array(angles_free)
            angles_embedded = np.array(angles_embedded)
            delta_angles = angles_embedded - angles_free
            mean_delta_angle = float(np.mean(delta_angles))
        else:
            mean_delta_angle = 0.0
        
        return {
            "rmsd_angstrom": float(rmsd),
            "mean_delta_length_angstrom": mean_delta_length,
            "mean_delta_angle_degrees": mean_delta_angle,
            "num_bonds": len(bonds),
            "num_angles": len(angles_free)
        }
    
    def full_structure_analysis_from_embedded(
        self,
        atoms_embedded: Atoms,
        charge: int = 0
    ) -> Dict:
        """
        Complete structure analysis starting from embedded linker only.
        Automatically optimizes to get free linker, then compares.
        
        Args:
            atoms_embedded: Embedded linker structure
            charge: Molecular charge
        
        Returns:
            Complete analysis results with conformational energy and geometry distortion
        """
        import subprocess
        
        print("🔬 Running xTB structure analysis from embedded linker...")
        
        # 1. Calculate embedded energy (single point)
        print("  ├─ Calculating embedded linker energy...")
        energy_embedded = self.run_xtb_single_point(atoms_embedded, charge)
        
        # 2. Optimize embedded to get free linker
        print("  ├─ Optimizing to get free linker...")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xyz', mode='w') as tmp:
            write(tmp.name, atoms_embedded)
            tmp_path = tmp.name
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                cmd = [
                    self.xtb_command,
                    tmp_path,
                    "--opt",  # Geometry optimization
                    "--gfn", "2",
                    "--chrg", str(charge)
                ]
                
                result = subprocess.run(
                    cmd,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=600  # 10 minutes
                )
                
                # Read optimized structure
                opt_file = os.path.join(tmpdir, "xtbopt.xyz")
                if not os.path.exists(opt_file):
                    raise RuntimeError(f"xTB optimization failed. No output file generated.")
                
                atoms_free = read(opt_file)
                print(f"  ├─ Optimization successful ({len(atoms_free)} atoms)")
                
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        # 3. Calculate free energy
        print("  ├─ Calculating free linker energy...")
        energy_free = self.run_xtb_single_point(atoms_free, charge)
        
        # 4. Conformational energy
        conformational_energy = energy_embedded - energy_free
        print(f"  ├─ ΔE_conf = {conformational_energy:.2f} kcal/mol")
        
        # 5. Geometry distortion analysis
        print("  └─ Analyzing geometry distortion...")
        
        # Use ASE-based distortion analysis (atoms already aligned from optimization)
        distortion = self.analyze_structure_distortion(atoms_free, atoms_embedded)
        
        print(f"     ├─ RMSD = {distortion['rmsd_angstrom']:.4f} Å")
        print(f"     ├─ ΔLength = {distortion['mean_delta_length_angstrom']:.6f} Å")
        print(f"     └─ ΔAngle = {distortion['mean_delta_angle_degrees']:.4f}°")
        
        return {
            "conformational_energy_kcal_mol": float(conformational_energy),
            "energy_free_kcal_mol": float(energy_free),
            "energy_embedded_kcal_mol": float(energy_embedded),
            **distortion
        }
    
    def full_structure_analysis_two_files(
        self,
        xyz_file_free: str,
        xyz_file_embedded: str,
        charge: int = 0
    ) -> Dict:
        """
        Complete structure analysis from TWO XYZ files (RECOMMENDED METHOD).
        This matches the old_model notebook workflow exactly.
        
        Workflow:
        1. Load free and embedded linkers from XYZ files
        2. Run single point energy on both → E_free, E_embedded
        3. Calculate ΔE_conf = E_embedded - E_free (same as notebook)
        4. Calculate geometry distortion (RMSD, ΔLength, ΔAngle)
        5. Extract structure data for visualization
        
        Args:
            xyz_file_free: Path to FREE (optimized) linker XYZ
            xyz_file_embedded: Path to EMBEDDED linker XYZ
            charge: Molecular charge (default: 0)
        
        Returns:
            {
                "conformational_energy_kcal_mol": float,
                "energy_free_kcal_mol": float,
                "energy_embedded_kcal_mol": float,
                "rmsd_angstrom": float,
                "mean_delta_length_angstrom": float,
                "mean_delta_angle_degrees": float,
                "num_bonds": int,
                "num_angles": int,
                "free_structure": {...},  # For visualization
                "embedded_structure": {...}  # For visualization
            }
        """
        print("🔬 Running xTB structure analysis from TWO XYZ files...")
        print(f"  ├─ Free: {Path(xyz_file_free).name}")
        print(f"  └─ Embedded: {Path(xyz_file_embedded).name}")
        
        # 1. Load structures
        atoms_free = read(xyz_file_free)
        atoms_embedded = read(xyz_file_embedded)
        
        print(f"  ├─ Loaded {len(atoms_free)} atoms (free), {len(atoms_embedded)} atoms (embedded)")
        
        # 2. For accurate conformational energy, we need to optimize embedded to get consistent free linker
        # This ensures both structures are from same optimization method
        print("  ├─ Optimizing embedded linker to get consistent free structure...")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xyz', mode='w') as tmp:
            write(tmp.name, atoms_embedded)
            tmp_path = tmp.name
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                cmd = [
                    self.xtb_command,
                    tmp_path,
                    "--opt",  # Geometry optimization
                    "--gfn", "2",
                    "--chrg", str(charge)
                ]
                
                result = subprocess.run(
                    cmd,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=600  # 10 minutes
                )
                
                # Read optimized structure
                opt_file = os.path.join(tmpdir, "xtbopt.xyz")
                if not os.path.exists(opt_file):
                    raise RuntimeError(f"xTB optimization failed. No output file generated.")
                
                atoms_free_optimized = read(opt_file)
                print(f"  ├─ Optimization successful → using optimized free linker for energy")
                
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        # 3. Conformational energy using OPTIMIZED free linker (consistent with embedded)
        print("  ├─ Calculating optimized free linker energy (single point)...")
        energy_free = self.run_xtb_single_point(atoms_free_optimized, charge)
        
        print("  ├─ Calculating embedded linker energy (single point)...")
        energy_embedded = self.run_xtb_single_point(atoms_embedded, charge)
        
        conformational_energy = energy_embedded - energy_free
        
        print(f"  ├─ ΔE_conf = {conformational_energy:.2f} kcal/mol")
        
        # 4. Geometry distortion using PROVIDED free file (for RMSD/ME accuracy)
        # Use the user-provided free file (not optimized) for geometry comparison
        print("  └─ Analyzing geometry distortion using provided free linker file...")
        print("     ├─ Using Kabsch RMSD alignment (same as old_model)")
        
        # Use user-provided free linker for geometry (it's already aligned/prepared)
        distortion = self.analyze_structure_distortion(atoms_free, atoms_embedded, scale=1.5)
        
        print(f"     ├─ RMSD = {distortion['rmsd_angstrom']:.4f} Å")
        print(f"     ├─ ΔLength = {distortion['mean_delta_length_angstrom']:.6f} Å")
        print(f"     └─ ΔAngle = {distortion['mean_delta_angle_degrees']:.4f}°")
        print(f"     └─ ΔAngle = {distortion['mean_delta_angle_degrees']:.4f}°")
        
        # 5. Calculate atom-wise displacement (Δr) for color mapping
        coords_free_aligned = distortion.get('coords_free_aligned')
        coords_embedded_centered = distortion.get('coords_embedded_centered')
        
        delta_r = None
        if coords_free_aligned is not None and coords_embedded_centered is not None:
            # Calculate per-atom displacement
            delta_r = np.linalg.norm(coords_embedded_centered - coords_free_aligned, axis=1).tolist()
        
        # 6. Extract structure data for visualization
        free_structure = self._extract_structure_data(atoms_free)
        embedded_structure = self._extract_structure_data(atoms_embedded)
        
        # Add delta_r to embedded structure for color mapping
        if delta_r is not None:
            embedded_structure['delta_r'] = delta_r
            embedded_structure['delta_r_min'] = float(min(delta_r))
            embedded_structure['delta_r_max'] = float(max(delta_r))
        
        return {
            "conformational_energy_kcal_mol": float(conformational_energy),
            "energy_free_kcal_mol": float(energy_free),
            "energy_embedded_kcal_mol": float(energy_embedded),
            **distortion,
            "free_structure": free_structure,
            "embedded_structure": embedded_structure
        }
    
    def _extract_structure_data(self, atoms: Atoms) -> Dict:
        """
        Extract structure data for 3D visualization.
        
        Args:
            atoms: ASE Atoms object
        
        Returns:
            Dictionary with atoms and bonds for visualization
        """
        symbols = atoms.get_chemical_symbols()
        positions = atoms.get_positions()
        
        # Convert to list of dicts for JSON serialization
        atoms_list = []
        for i, (symbol, pos) in enumerate(zip(symbols, positions)):
            atoms_list.append({
                "symbol": symbol,
                "x": float(pos[0]),
                "y": float(pos[1]),
                "z": float(pos[2])
            })
        
        # Detect bonds using covalent radii
        bonds = []
        scale = 1.5  # Same as distortion analysis
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                if symbols[i] not in self.cov_radii or symbols[j] not in self.cov_radii:
                    continue
                cutoff = scale * (self.cov_radii[symbols[i]] + self.cov_radii[symbols[j]])
                dist = np.linalg.norm(positions[i] - positions[j])
                if dist <= cutoff:
                    bonds.append([i, j])
        
        return {
            "atoms": atoms_list,
            "bonds": bonds,
            "num_atoms": len(atoms)
        }
    
    def full_structure_analysis(
        self,
        atoms_free: Atoms,
        atoms_embedded: Atoms,
        charge: int = 0,
        xyz_file_free: Optional[str] = None,
        xyz_file_embedded: Optional[str] = None
    ) -> Dict:
        """
        Complete structure analysis: energy + distortion
        
        Args:
            atoms_free: Free (optimized) linker (ASE Atoms object)
            atoms_embedded: Embedded linker (ASE Atoms object)
            charge: Molecular charge
            xyz_file_free: Optional path to free linker XYZ (for RDKit atom matching)
            xyz_file_embedded: Optional path to embedded linker XYZ (for RDKit atom matching)
        
        Returns:
            Complete analysis results
        """
        print("🔬 Running xTB structure analysis...")
        
        # 1. Conformational energy (embedded vs free)
        print("  ├─ Calculating free linker energy...")
        energy_free = self.run_xtb_single_point(atoms_free, charge)
        
        print("  ├─ Calculating embedded linker energy...")
        energy_embedded = self.run_xtb_single_point(atoms_embedded, charge)
        
        conformational_energy = energy_embedded - energy_free
        
        print(f"  ├─ ΔE_conf = {conformational_energy:.2f} kcal/mol")
        
        # 2. Geometry distortion
        print("  └─ Analyzing geometry distortion...")
        
        # Use RDKit method if XYZ file paths provided (more accurate)
        if xyz_file_free and xyz_file_embedded and RDKIT_AVAILABLE:
            print("     ├─ Using RDKit for atom matching (same as old_model)")
            distortion = self.analyze_structure_distortion_with_rdkit(
                xyz_file_free, xyz_file_embedded
            )
        else:
            # Fallback to ASE-based method (less accurate for atom matching)
            if not RDKIT_AVAILABLE:
                print("     ⚠️  RDKit not available, using fallback method (may be less accurate)")
            distortion = self.analyze_structure_distortion(atoms_free, atoms_embedded)
        
        print(f"     ├─ RMSD = {distortion['rmsd_angstrom']:.4f} Å")
        print(f"     ├─ ΔLength = {distortion['mean_delta_length_angstrom']:.6f} Å")
        print(f"     └─ ΔAngle = {distortion['mean_delta_angle_degrees']:.4f}°")
        
        return {
            "conformational_energy_kcal_mol": float(conformational_energy),
            "energy_free_kcal_mol": float(energy_free),
            "energy_embedded_kcal_mol": float(energy_embedded),
            **distortion
        }


# Module-level convenience functions for API usage

# Check xTB availability at module load time
XTB_AVAILABLE = False
try:
    runner_test = XTBRunner()
    XTB_AVAILABLE = True
except Exception:
    XTB_AVAILABLE = False
    print("⚠️  xTB not available. Structure analysis will use fallback values.")


def analyze_cif_structure(cif_file_path: str) -> Dict:
    """
    Analyze MOF structure from CIF file.
    Extracts embedded linker from CIF, optimizes it, and calculates conformational energy.
    
    WARNING: CIF extraction may not be accurate. Use analyze_embedded_xyz with pre-extracted XYZ instead.
    
    Args:
        cif_file_path: Path to CIF file
    
    Returns:
        Dictionary with analysis results:
        - success: bool
        - conformational_energy_kcal: float
        - rmsd_final_angstrom: float
        - me_delta_length_angstrom: float
        - me_delta_angle_deg: float
        - embedded_energy_kcal: float (optional)
        - free_energy_kcal: float (optional)
        - error: str (if failed)
    """
    if not XTB_AVAILABLE:
        return {
            "success": False,
            "error": "xTB not available on this system"
        }
    
    try:
        from services.linker_extractor import extract_linker_from_cif
        
        # Extract embedded linker from CIF
        print(f"📂 Extracting linker from CIF: {cif_file_path}")
        
        # This function should extract the linker and return ASE Atoms object
        atoms_embedded = extract_linker_from_cif(cif_file_path)
        
        if atoms_embedded is None:
            return {
                "success": False,
                "error": "Failed to extract linker from CIF file"
            }
        
        print(f"  ✓ Extracted embedded linker ({len(atoms_embedded)} atoms)")
        
        # Run full analysis (auto-optimize + calculate energies + geometry)
        runner = XTBRunner()
        results = runner.full_structure_analysis_from_embedded(atoms_embedded, charge=0)
        
        return {
            "success": True,
            "conformational_energy_kcal": results["conformational_energy_kcal_mol"],
            "rmsd_final_angstrom": results["rmsd_angstrom"],
            "me_delta_length_angstrom": results["mean_delta_length_angstrom"],
            "me_delta_angle_deg": results["mean_delta_angle_degrees"],
            "embedded_energy_kcal": results["energy_embedded_kcal_mol"],
            "free_energy_kcal": results["energy_free_kcal_mol"]
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "Linker extraction module not available. Please ensure linker_extractor.py exists."
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error analyzing CIF structure: {error_details}")
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }


def analyze_embedded_xyz(xyz_file_path: str) -> Dict:
    """
    Analyze embedded linker structure from XYZ file.
    This is the RECOMMENDED method - more accurate than CIF extraction.
    
    Workflow:
    1. Read embedded linker from XYZ file
    2. Optimize embedded → get free linker
    3. Calculate conformational energy = E(embedded) - E(free)
    4. Calculate geometry distortion (RMSD, ΔLength, ΔAngle)
    
    Args:
        xyz_file_path: Path to embedded linker XYZ file
    
    Returns:
        Dictionary with analysis results:
        - success: bool
        - conformational_energy_kcal: float
        - rmsd_final_angstrom: float
        - me_delta_length_angstrom: float
        - me_delta_angle_deg: float
        - embedded_energy_kcal: float
        - free_energy_kcal: float
        - error: str (if failed)
    """
    if not XTB_AVAILABLE:
        return {
            "success": False,
            "error": "xTB not available on this system"
        }
    
    try:
        from ase.io import read
        
        # Read embedded linker from XYZ file
        print(f"📂 Reading embedded linker from: {xyz_file_path}")
        atoms_embedded = read(xyz_file_path)
        
        print(f"  ✓ Loaded embedded linker ({len(atoms_embedded)} atoms)")
        
        # Run full analysis (auto-optimize + calculate energies + geometry)
        runner = XTBRunner()
        results = runner.full_structure_analysis_from_embedded(atoms_embedded, charge=0)
        
        return {
            "success": True,
            "conformational_energy_kcal": results["conformational_energy_kcal_mol"],
            "rmsd_final_angstrom": results["rmsd_angstrom"],
            "me_delta_length_angstrom": results["mean_delta_length_angstrom"],
            "me_delta_angle_deg": results["mean_delta_angle_degrees"],
            "embedded_energy_kcal": results["energy_embedded_kcal_mol"],
            "free_energy_kcal": results["energy_free_kcal_mol"]
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error analyzing embedded XYZ: {error_details}")
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }


def analyze_two_xyz_files(xyz_file_free: str, xyz_file_embedded: str) -> Dict:
    """
    Analyze structure from TWO XYZ files (BEST METHOD - matches old_model notebook).
    
    Workflow:
    1. Read free and embedded linkers from XYZ files
    2. Run single point energy on both → E_free, E_embedded
    3. Calculate conformational energy = E_embedded - E_free (same as notebook)
    4. Calculate geometry distortion (RMSD, ΔLength, ΔAngle)
    5. Extract structure data for visualization
    
    Args:
        xyz_file_free: Path to FREE (optimized) linker XYZ
        xyz_file_embedded: Path to EMBEDDED linker XYZ
    
    Returns:
        Dictionary with analysis results:
        - success: bool
        - conformational_energy_kcal: float
        - rmsd_final_angstrom: float
        - me_delta_length_angstrom: float
        - me_delta_angle_deg: float
        - embedded_energy_kcal: float
        - free_energy_kcal: float
        - free_structure: dict (for visualization)
        - embedded_structure: dict (for visualization)
        - error: str (if failed)
    """
    if not XTB_AVAILABLE:
        return {
            "success": False,
            "error": "xTB not available on this system"
        }
    
    try:
        # Run full two-file analysis
        runner = XTBRunner()
        results = runner.full_structure_analysis_two_files(
            xyz_file_free, xyz_file_embedded, charge=0
        )
        
        return {
            "success": True,
            "conformational_energy_kcal": results["conformational_energy_kcal_mol"],
            "rmsd_final_angstrom": results["rmsd_angstrom"],
            "me_delta_length_angstrom": results["mean_delta_length_angstrom"],
            "me_delta_angle_deg": results["mean_delta_angle_degrees"],
            "embedded_energy_kcal": results["energy_embedded_kcal_mol"],
            "free_energy_kcal": results["energy_free_kcal_mol"],
            "free_structure": results["free_structure"],
            "embedded_structure": results["embedded_structure"]
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error analyzing two XYZ files: {error_details}")
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }


# Example usage
if __name__ == "__main__":
    # Test xTB installation
    try:
        runner = XTBRunner()
        print("✅ xTB runner initialized successfully")
    except RuntimeError as e:
        print(f"❌ Error: {e}")
