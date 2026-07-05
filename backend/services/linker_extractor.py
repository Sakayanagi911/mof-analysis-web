"""
Linker Extractor Service
Extract organic linker from MOF CIF file
"""

import numpy as np
from ase.io import read, write
from ase import Atoms
from typing import List, Tuple, Optional
import tempfile


class LinkerExtractor:
    """Extract organic linker from MOF structure"""
    
    # Common metal elements in MOFs
    METAL_SYMBOLS = {
        'Cu', 'Zn', 'Co', 'Ni', 'Fe', 'Mn', 'Mg', 'Ca', 'Sr', 'Ba',
        'Cd', 'Cr', 'V', 'Ti', 'Zr', 'Hf', 'Al', 'Ga', 'In',
        'Y', 'La', 'Ce', 'Nd', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu'
    }
    
    # Covalent radii for bond detection (Å)
    COVALENT_RADII = {
        'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'F': 0.57,
        'P': 1.07, 'S': 1.05, 'Cl': 1.02, 'Br': 1.20, 'I': 1.39,
        'Cu': 1.32, 'Zn': 1.22, 'Co': 1.26, 'Ni': 1.24, 'Mn': 1.39,
        'Cd': 1.44, 'Mg': 1.41
    }
    
    def __init__(self):
        pass
    
    def is_metal(self, symbol: str) -> bool:
        """Check if atom is a metal"""
        return symbol in self.METAL_SYMBOLS
    
    def detect_bonds(self, atoms: Atoms, scale: float = 1.8) -> List[Tuple[int, int]]:
        """
        Detect bonds between atoms based on covalent radii
        Uses larger scale factor to catch hydrogen bonds
        
        Args:
            atoms: ASE Atoms object
            scale: Scaling factor for bond detection (1.8 to catch all H bonds)
        
        Returns:
            List of bond tuples (i, j)
        """
        symbols = atoms.get_chemical_symbols()
        positions = atoms.get_positions()
        bonds = []
        
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                r_i = self.COVALENT_RADII.get(symbols[i], 1.5)
                r_j = self.COVALENT_RADII.get(symbols[j], 1.5)
                
                # Use scale factor (default 1.8 to catch all H bonds)
                max_dist = scale * (r_i + r_j)
                
                dist = np.linalg.norm(positions[i] - positions[j])
                
                if dist < max_dist:
                    bonds.append((i, j))
        
        return bonds
    
    def find_connected_component(
        self, 
        start_idx: int, 
        bonds: List[Tuple[int, int]], 
        n_atoms: int,
        exclude_metals: bool = True,
        metal_indices: set = None
    ) -> set:
        """
        Find all atoms connected to start_idx via bonds
        
        Args:
            start_idx: Starting atom index
            bonds: List of bonds
            n_atoms: Total number of atoms
            exclude_metals: If True, stop at metal atoms
            metal_indices: Set of metal atom indices
        
        Returns:
            Set of connected atom indices
        """
        if metal_indices is None:
            metal_indices = set()
        
        # Build adjacency list
        adj = {i: [] for i in range(n_atoms)}
        for i, j in bonds:
            adj[i].append(j)
            adj[j].append(i)
        
        # BFS to find connected component
        visited = set()
        queue = [start_idx]
        visited.add(start_idx)
        
        while queue:
            current = queue.pop(0)
            
            for neighbor in adj[current]:
                if neighbor in visited:
                    continue
                
                # Stop at metals if exclude_metals is True
                if exclude_metals and neighbor in metal_indices:
                    continue
                
                visited.add(neighbor)
                queue.append(neighbor)
        
        return visited
    
    def extract_linker(
        self, 
        cif_path: str,
        linker_smiles: Optional[str] = None
    ) -> Tuple[Atoms, dict]:
        """
        Extract organic linker from MOF CIF file
        
        Args:
            cif_path: Path to CIF file
            linker_smiles: Optional SMILES string to help identify linker
        
        Returns:
            Tuple of (linker_atoms, info_dict)
        """
        print(f"📂 Loading CIF file: {cif_path}")
        
        # Load structure
        structure = read(cif_path)
        
        symbols = structure.get_chemical_symbols()
        positions = structure.get_positions()
        
        print(f"  Total atoms: {len(structure)}")
        
        # Identify metal atoms
        metal_indices = set()
        for i, symbol in enumerate(symbols):
            if self.is_metal(symbol):
                metal_indices.add(i)
        
        print(f"  Metal atoms: {len(metal_indices)}")
        
        # Detect bonds
        print(f"  Detecting bonds...")
        bonds = self.detect_bonds(structure)
        print(f"  Bonds detected: {len(bonds)}")
        
        # Find organic clusters (connected components excluding metals)
        print(f"  Finding organic clusters...")
        organic_clusters = []
        visited_global = set()
        
        for i in range(len(structure)):
            if i in visited_global:
                continue
            if i in metal_indices:
                continue
            
            # Find connected organic component
            cluster = self.find_connected_component(
                i, bonds, len(structure), 
                exclude_metals=True,
                metal_indices=metal_indices
            )
            
            if len(cluster) > 3:  # Ignore very small clusters (likely solvent)
                organic_clusters.append(cluster)
                visited_global.update(cluster)
        
        print(f"  Organic clusters found: {len(organic_clusters)}")
        
        if len(organic_clusters) == 0:
            raise ValueError("No organic linker found in structure")
        
        # Find largest cluster (likely the linker)
        largest_cluster = max(organic_clusters, key=len)
        print(f"  Largest cluster: {len(largest_cluster)} atoms")
        
        # Extract linker atoms
        linker_indices = sorted(list(largest_cluster))
        linker_symbols = [symbols[i] for i in linker_indices]
        linker_positions = positions[linker_indices]
        
        # Create linker Atoms object
        linker_atoms = Atoms(
            symbols=linker_symbols,
            positions=linker_positions
        )
        
        # Count atom types
        from collections import Counter
        atom_counts = Counter(linker_symbols)
        
        print(f"\n  ✅ Linker extracted:")
        print(f"     Atoms: {len(linker_atoms)}")
        print(f"     Composition: {dict(atom_counts)}")
        
        info = {
            "n_atoms": len(linker_atoms),
            "composition": dict(atom_counts),
            "n_clusters_found": len(organic_clusters),
            "n_metals": len(metal_indices)
        }
        
        return linker_atoms, info
    
    def extract_and_save(
        self,
        cif_path: str,
        output_xyz_path: str,
        linker_smiles: Optional[str] = None
    ) -> dict:
        """
        Extract linker and save to XYZ file
        
        Args:
            cif_path: Path to CIF file
            output_xyz_path: Path to save XYZ file
            linker_smiles: Optional SMILES for validation
        
        Returns:
            Info dictionary
        """
        linker_atoms, info = self.extract_linker(cif_path, linker_smiles)
        
        # Save to XYZ
        write(output_xyz_path, linker_atoms)
        print(f"  💾 Saved to: {output_xyz_path}")
        
        return info


# Convenience function for API usage
def extract_linker_from_cif(cif_path: str) -> Optional[Atoms]:
    """
    Extract organic linker from MOF CIF file (convenience function for API)
    
    Args:
        cif_path: Path to CIF file
    
    Returns:
        ASE Atoms object of the extracted linker, or None if extraction fails
    """
    try:
        extractor = LinkerExtractor()
        linker_atoms, info = extractor.extract_linker(cif_path)
        return linker_atoms
    except Exception as e:
        print(f"❌ Linker extraction failed: {e}")
        return None


# Test function
if __name__ == "__main__":
    extractor = LinkerExtractor()
    
    # Test with VOLPET (smallest structure)
    print("="*70)
    print("Testing Linker Extraction: VOLPET")
    print("="*70)
    
    try:
        linker, info = extractor.extract_linker(
            "old_model/TOP 3_VOLPET_Unit Cell.cif"
        )
        
        print(f"\n✅ Extraction successful!")
        print(f"   Expected: 15 atoms (from VOLPET_Linker_Embed_After_UFF.xyz)")
        print(f"   Extracted: {info['n_atoms']} atoms")
        
        if info['n_atoms'] == 15:
            print(f"   Status: ✅ PERFECT MATCH!")
        else:
            print(f"   Status: ⚠️  Different atom count")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
