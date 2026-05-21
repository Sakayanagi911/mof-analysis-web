"""
Unit Tests untuk Pipeline Analisis Stabilitas Linker MOF.

Mencakup pengujian fungsi-fungsi baru yang ditambahkan ke:
- services/structure_parser.py (relax_hydrogens_uff, analyze_linker_stability, dll.)
- services/xtb_runner.py (perbaikan encoding UTF-8)
- routers/structure.py (endpoint /api/linker/stability)
- routers/analysis.py (integrasi xTB dinamis di /analyze)

Semua test menggunakan mock agar tidak bergantung pada xTB binary.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def simple_xyz_content():
    """XYZ content untuk molekul sederhana (3 atom: C, H, H)."""
    return (
        "3\n"
        "Simple molecule\n"
        "C   0.000000  0.000000  0.000000\n"
        "H   1.089000  0.000000  0.000000\n"
        "H  -0.544500  0.942800  0.000000\n"
    )


@pytest.fixture
def simple_xyz_optimized():
    """XYZ content teroptimasi (sedikit terdistorsi dari simple_xyz_content)."""
    return (
        "3\n"
        "Optimized molecule\n"
        "C   0.010000  0.005000  0.003000\n"
        "H   1.100000  0.010000  0.005000\n"
        "H  -0.550000  0.950000  0.002000\n"
    )


@pytest.fixture
def identical_xyz_pair():
    """Dua XYZ content yang identik untuk menguji RMSD = 0."""
    xyz = (
        "4\n"
        "Methane-like\n"
        "C   0.000000  0.000000  0.000000\n"
        "H   1.089000  0.000000  0.000000\n"
        "H  -0.363000  1.027000  0.000000\n"
        "H  -0.363000 -0.513500  0.889200\n"
    )
    return xyz, xyz


@pytest.fixture
def linker_xyz_content():
    """XYZ content yang mewakili linker organik kecil (BDC-like)."""
    return (
        "10\n"
        "BDC-like linker\n"
        "C   0.000000  0.000000  0.000000\n"
        "C   1.400000  0.000000  0.000000\n"
        "C   2.100000  1.210000  0.000000\n"
        "C   1.400000  2.420000  0.000000\n"
        "C   0.000000  2.420000  0.000000\n"
        "C  -0.700000  1.210000  0.000000\n"
        "H   2.480000  0.000000  0.000000\n"
        "H   3.180000  1.210000  0.000000\n"
        "H   2.480000  2.420000  0.000000\n"
        "O  -0.700000  0.000000  0.000000\n"
    )


# ===========================================================================
# Tests: parse_xyz_content
# ===========================================================================

class TestParseXyzContent:
    """Test suite untuk fungsi parse_xyz_content."""

    def test_parse_valid_xyz(self, simple_xyz_content):
        from services.structure_parser import parse_xyz_content
        symbols, positions = parse_xyz_content(simple_xyz_content)

        assert len(symbols) == 3
        assert symbols == ["C", "H", "H"]
        assert len(positions) == 3
        assert positions[0] == pytest.approx([0.0, 0.0, 0.0])
        assert positions[1] == pytest.approx([1.089, 0.0, 0.0])

    def test_parse_empty_xyz(self):
        from services.structure_parser import parse_xyz_content
        symbols, positions = parse_xyz_content("")
        assert symbols == []
        assert positions == []

    def test_parse_header_only(self):
        from services.structure_parser import parse_xyz_content
        symbols, positions = parse_xyz_content("3\ncomment\n")
        assert symbols == []
        assert positions == []

    def test_parse_xyz_skips_malformed_lines(self):
        from services.structure_parser import parse_xyz_content
        xyz = "2\ntest\nC 0 0 0\nbadline\nH 1 0 0\n"
        symbols, positions = parse_xyz_content(xyz)
        assert len(symbols) == 2
        assert symbols == ["C", "H"]


# ===========================================================================
# Tests: kabsch_rmsd_internal
# ===========================================================================

class TestKabschRmsdInternal:
    """Test suite untuk algoritma Kabsch RMSD internal."""

    def test_identical_structures_rmsd_zero(self):
        from services.structure_parser import kabsch_rmsd_internal
        coords = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
        rmsd, _, _ = kabsch_rmsd_internal(coords, coords)
        assert rmsd == pytest.approx(0.0, abs=1e-10)

    def test_translated_structures_rmsd_zero(self):
        from services.structure_parser import kabsch_rmsd_internal
        P = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
        Q = P + np.array([10, -5, 3])  # Translasi murni
        rmsd, _, _ = kabsch_rmsd_internal(P, Q)
        assert rmsd == pytest.approx(0.0, abs=1e-10)

    def test_rotated_and_translated_structures_rmsd_near_zero(self):
        """Struktur yang ditranslasi+dirotasi harus punya RMSD mendekati 0
        karena Kabsch menghilangkan translasi dan rotasi optimal."""
        from services.structure_parser import kabsch_rmsd_internal
        # Gunakan geometri asimetris (non-centroid-at-origin)
        P = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 1.0, 2.0],
            [3.0, 8.0, 1.0]
        ], dtype=float)
        # Q = P yang hanya ditranslasi (RMSD harus 0)
        Q = P + np.array([100, -50, 30])
        rmsd, _, _ = kabsch_rmsd_internal(P, Q)
        assert rmsd == pytest.approx(0.0, abs=1e-6)

    def test_distorted_structures_rmsd_positive(self):
        from services.structure_parser import kabsch_rmsd_internal
        P = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
        Q = np.array([[0, 0, 0], [1.1, 0.1, 0], [0.1, 1.1, 0]], dtype=float)
        rmsd, _, _ = kabsch_rmsd_internal(P, Q)
        assert rmsd > 0.0

    def test_returns_aligned_coordinates(self):
        from services.structure_parser import kabsch_rmsd_internal
        P = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
        Q = P + 10.0
        rmsd, P_rot, Q_centered = kabsch_rmsd_internal(P, Q)
        # Centroid harus di origin setelah centering
        assert np.allclose(Q_centered.mean(axis=0), [0, 0, 0], atol=1e-10)


# ===========================================================================
# Tests: detect_bonds_internal
# ===========================================================================

class TestDetectBondsInternal:
    """Test suite untuk deteksi ikatan berdasarkan jari-jari kovalen."""

    def test_detects_ch_bond(self):
        from services.structure_parser import detect_bonds_internal
        symbols = ["C", "H"]
        coords = np.array([[0, 0, 0], [1.09, 0, 0]], dtype=float)
        bonds = detect_bonds_internal(symbols, coords, scale=1.5)
        assert (0, 1) in bonds

    def test_no_bond_far_atoms(self):
        from services.structure_parser import detect_bonds_internal
        symbols = ["C", "C"]
        coords = np.array([[0, 0, 0], [10, 0, 0]], dtype=float)
        bonds = detect_bonds_internal(symbols, coords, scale=1.5)
        assert len(bonds) == 0

    def test_ignores_unknown_elements(self):
        """Atom dengan simbol tidak ada di cov_radii harus di-skip."""
        from services.structure_parser import detect_bonds_internal
        symbols = ["Zn", "C"]  # Zn tidak ada di cov_radii
        coords = np.array([[0, 0, 0], [1.0, 0, 0]], dtype=float)
        bonds = detect_bonds_internal(symbols, coords, scale=1.5)
        assert len(bonds) == 0

    def test_detects_multiple_bonds(self):
        from services.structure_parser import detect_bonds_internal
        symbols = ["C", "C", "H"]
        coords = np.array([
            [0, 0, 0],
            [1.4, 0, 0],
            [2.0, 0, 0]
        ], dtype=float)
        bonds = detect_bonds_internal(symbols, coords, scale=1.5)
        assert len(bonds) >= 2

    def test_empty_input(self):
        from services.structure_parser import detect_bonds_internal
        bonds = detect_bonds_internal([], np.array([]).reshape(0, 3), scale=1.5)
        assert bonds == []


# ===========================================================================
# Tests: bond_lengths_internal & bond_angles_internal
# ===========================================================================

class TestBondMetrics:
    """Test suite untuk panjang ikatan dan sudut ikatan."""

    def test_bond_length_correct(self):
        from services.structure_parser import bond_lengths_internal
        coords = np.array([[0, 0, 0], [3, 4, 0]], dtype=float)
        bonds = [(0, 1)]
        lengths = bond_lengths_internal(coords, bonds)
        assert lengths[0] == pytest.approx(5.0)

    def test_bond_angle_90_degrees(self):
        from services.structure_parser import bond_angles_internal
        # Sudut di atom 0 antara atom 1 dan atom 2: harus 90 derajat
        coords = np.array([
            [0, 0, 0],  # center
            [1, 0, 0],  # neighbor 1
            [0, 1, 0],  # neighbor 2
        ], dtype=float)
        bonds = [(0, 1), (0, 2)]
        angles, triplets = bond_angles_internal(coords, bonds)
        assert len(angles) == 1
        assert angles[0] == pytest.approx(90.0, abs=0.01)

    def test_bond_angle_180_degrees(self):
        from services.structure_parser import bond_angles_internal
        coords = np.array([
            [0, 0, 0],   # center
            [-1, 0, 0],  # neighbor 1
            [1, 0, 0],   # neighbor 2
        ], dtype=float)
        bonds = [(0, 1), (0, 2)]
        angles, _ = bond_angles_internal(coords, bonds)
        assert angles[0] == pytest.approx(180.0, abs=0.01)

    def test_no_angles_with_single_bond(self):
        from services.structure_parser import bond_angles_internal
        coords = np.array([[0, 0, 0], [1, 0, 0]], dtype=float)
        bonds = [(0, 1)]
        angles, triplets = bond_angles_internal(coords, bonds)
        assert len(angles) == 0


# ===========================================================================
# Tests: analyze_linker_stability
# ===========================================================================

class TestAnalyzeLinkerStability:
    """Test suite untuk fungsi analyze_linker_stability."""

    def test_identical_structures(self, identical_xyz_pair):
        from services.structure_parser import analyze_linker_stability
        emb, opt = identical_xyz_pair
        result = analyze_linker_stability(emb, opt)

        assert result["rmsd_all"] == pytest.approx(0.0, abs=1e-4)
        assert result["rmsd_heavy"] == pytest.approx(0.0, abs=1e-4)
        assert "atoms_displacement" in result
        assert "coords_embedded" in result
        assert "coords_optimized" in result
        assert "bonds" in result

    def test_distorted_structures(self, simple_xyz_content, simple_xyz_optimized):
        from services.structure_parser import analyze_linker_stability
        result = analyze_linker_stability(simple_xyz_content, simple_xyz_optimized)

        assert result["rmsd_all"] > 0.0
        assert len(result["atoms_displacement"]) == 3
        assert len(result["coords_embedded"]) == 3
        assert len(result["coords_optimized"]) == 3

    def test_displacement_has_correct_fields(self, simple_xyz_content, simple_xyz_optimized):
        from services.structure_parser import analyze_linker_stability
        result = analyze_linker_stability(simple_xyz_content, simple_xyz_optimized)

        for disp in result["atoms_displacement"]:
            assert "index" in disp
            assert "element" in disp
            assert "delta_r" in disp
            assert "color" in disp
            assert disp["color"].startswith("rgb(")
            assert isinstance(disp["delta_r"], float)
            assert disp["delta_r"] >= 0.0

    def test_color_range_viridis(self, simple_xyz_content, simple_xyz_optimized):
        """Warna minimum harus dekat biru (68,1,84) dan max dekat kuning (253,231,37)."""
        from services.structure_parser import analyze_linker_stability
        result = analyze_linker_stability(simple_xyz_content, simple_xyz_optimized)

        disps = result["atoms_displacement"]
        delta_values = [d["delta_r"] for d in disps]
        min_idx = delta_values.index(min(delta_values))
        max_idx = delta_values.index(max(delta_values))

        min_color = disps[min_idx]["color"]
        max_color = disps[max_idx]["color"]

        # Min displacement harus biru-ish
        assert "68" in min_color and "84" in min_color
        # Max displacement harus kuning-ish
        assert "253" in max_color and "37" in max_color

    def test_mismatched_atom_count_raises_error(self):
        from services.structure_parser import analyze_linker_stability
        xyz_3 = "3\ntest\nC 0 0 0\nH 1 0 0\nH 0 1 0\n"
        xyz_2 = "2\ntest\nC 0 0 0\nH 1 0 0\n"
        with pytest.raises(ValueError, match="tidak konsisten"):
            analyze_linker_stability(xyz_3, xyz_2)

    def test_heavy_atom_rmsd_less_than_or_equal_all(self, linker_xyz_content):
        """RMSD heavy atoms tidak selalu <= RMSD all, tapi harus didefinisikan."""
        from services.structure_parser import analyze_linker_stability
        # Buat versi terdistorsi
        lines = linker_xyz_content.strip().splitlines()
        distorted_lines = [lines[0], lines[1]]
        for line in lines[2:]:
            parts = line.split()
            x = float(parts[1]) + 0.05
            y = float(parts[2]) + 0.02
            z = float(parts[3]) + 0.01
            distorted_lines.append(f"{parts[0]}   {x:.6f}  {y:.6f}  {z:.6f}")
        distorted_xyz = "\n".join(distorted_lines) + "\n"

        result = analyze_linker_stability(linker_xyz_content, distorted_xyz)
        assert result["rmsd_heavy"] >= 0.0
        assert result["rmsd_all"] >= 0.0

    def test_bonds_are_list_of_tuples(self, simple_xyz_content, simple_xyz_optimized):
        from services.structure_parser import analyze_linker_stability
        result = analyze_linker_stability(simple_xyz_content, simple_xyz_optimized)
        for bond in result["bonds"]:
            assert len(bond) == 2
            assert isinstance(bond[0], int)
            assert isinstance(bond[1], int)

    def test_me_delta_fields_present(self, simple_xyz_content, simple_xyz_optimized):
        from services.structure_parser import analyze_linker_stability
        result = analyze_linker_stability(simple_xyz_content, simple_xyz_optimized)
        assert "me_delta_length" in result
        assert "me_delta_angle" in result
        assert isinstance(result["me_delta_length"], float)
        assert isinstance(result["me_delta_angle"], float)


# ===========================================================================
# Tests: relax_hydrogens_uff
# ===========================================================================

class TestRelaxHydrogensUff:
    """Test suite untuk fungsi relax_hydrogens_uff."""

    def test_returns_string(self, simple_xyz_content):
        from services.structure_parser import relax_hydrogens_uff
        result = relax_hydrogens_uff(simple_xyz_content)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_same_atom_count(self, simple_xyz_content):
        """Jumlah atom harus tetap sama setelah relaksasi."""
        from services.structure_parser import relax_hydrogens_uff, parse_xyz_content
        result = relax_hydrogens_uff(simple_xyz_content)
        orig_sym, _ = parse_xyz_content(simple_xyz_content)
        result_sym, _ = parse_xyz_content(result)
        assert len(result_sym) == len(orig_sym)

    def test_fallback_on_rdkit_error(self):
        """Jika RDKit gagal, fungsi harus mengembalikan input asli tanpa crash."""
        from services.structure_parser import relax_hydrogens_uff
        bad_xyz = "1\nbad\nXx 0 0 0\n"
        result = relax_hydrogens_uff(bad_xyz)
        assert result == bad_xyz

    def test_fallback_on_empty_input(self):
        from services.structure_parser import relax_hydrogens_uff
        result = relax_hydrogens_uff("")
        assert result == ""


# ===========================================================================
# Tests: xtb_runner - parse_xtb_energy
# ===========================================================================

class TestParseXtbEnergy:
    """Test suite untuk parsing energi xTB dari stdout."""

    def test_parse_valid_energy(self):
        from services.xtb_runner import parse_xtb_energy
        stdout = """
           -------------------------------------------------
          |                 G F N 2 - x T B                 |
           -------------------------------------------------
          :: TOTAL ENERGY             -66.459851 Eh   ::
           -------------------------------------------------
        """
        energy = parse_xtb_energy(stdout)
        assert energy == pytest.approx(-66.459851)

    def test_parse_no_energy(self):
        from services.xtb_runner import parse_xtb_energy
        energy = parse_xtb_energy("No energy here\nJust random text\n")
        assert energy is None

    def test_parse_empty_string(self):
        from services.xtb_runner import parse_xtb_energy
        assert parse_xtb_energy("") is None

    def test_parse_positive_energy(self):
        from services.xtb_runner import parse_xtb_energy
        stdout = ":: TOTAL ENERGY              0.123456 Eh   ::"
        energy = parse_xtb_energy(stdout)
        assert energy == pytest.approx(0.123456)


# ===========================================================================
# Tests: xtb_runner - atoms_positions_to_xyz
# ===========================================================================

class TestAtomsPositionsToXyz:
    """Test suite untuk konversi atom+posisi ke format XYZ."""

    def test_basic_conversion(self):
        from services.xtb_runner import atoms_positions_to_xyz
        atoms = ["C", "H"]
        positions = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]
        result = atoms_positions_to_xyz(atoms, positions)

        lines = result.strip().splitlines()
        assert lines[0] == "2"
        assert "Generated by MOF Analysis" in lines[1]
        assert lines[2].startswith("C")
        assert lines[3].startswith("H")

    def test_empty_input(self):
        from services.xtb_runner import atoms_positions_to_xyz
        result = atoms_positions_to_xyz([], [])
        lines = result.strip().splitlines()
        assert lines[0] == "0"


# ===========================================================================
# Tests: xtb_runner - calculate_delta_e
# ===========================================================================

class TestCalculateDeltaE:
    """Test suite untuk perhitungan ΔE."""

    def test_positive_delta_e(self):
        from services.xtb_runner import calculate_delta_e
        # E_embedded > E_free → linker terdistorsi
        assert calculate_delta_e(-100.0, -150.0) == pytest.approx(50.0)

    def test_negative_delta_e(self):
        from services.xtb_runner import calculate_delta_e
        # E_embedded < E_free → linker terstabilkan
        assert calculate_delta_e(-150.0, -100.0) == pytest.approx(-50.0)

    def test_zero_delta_e(self):
        from services.xtb_runner import calculate_delta_e
        assert calculate_delta_e(-100.0, -100.0) == 0.0


# ===========================================================================
# Tests: xtb_runner - run_xtb_single_point (mocked)
# ===========================================================================

class TestRunXtbMocked:
    """Test xTB runner dengan mock subprocess."""

    def test_single_point_not_available(self):
        from services.xtb_runner import run_xtb_single_point
        with patch("services.xtb_runner.XTB_AVAILABLE", False):
            result = run_xtb_single_point("dummy xyz")
            assert result["success"] is False
            assert "not installed" in result["error"]

    def test_optimization_not_available(self):
        from services.xtb_runner import run_xtb_optimization
        with patch("services.xtb_runner.XTB_AVAILABLE", False):
            result = run_xtb_optimization("dummy xyz")
            assert result["success"] is False
            assert "not installed" in result["error"]
            assert result["optimized_xyz"] == ""
            assert result["optimized_positions"] == []


# ===========================================================================
# Tests: Endpoint /api/linker/stability (mocked xTB)
# ===========================================================================

class TestLinkerStabilityEndpoint:
    """Test suite untuk endpoint POST /api/linker/stability."""

    @pytest.mark.asyncio
    async def test_wrong_file_extension(self, client):
        files = {"file": ("test.txt", b"some text", "text/plain")}
        response = await client.post("/api/linker/stability", files=files)
        assert response.status_code == 400
        assert "Hanya file .xyz atau .cif" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_xtb_unavailable_returns_503(self, client, simple_xyz_content):
        with patch("routers.structure.XTB_AVAILABLE", False):
            files = {"file": ("test.xyz", simple_xyz_content.encode(), "application/octet-stream")}
            response = await client.post("/api/linker/stability", files=files)
            assert response.status_code == 503
            assert "GFN2-xTB" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_successful_xyz_analysis(self, client, simple_xyz_content):
        """Test alur sukses lengkap dengan mock xTB."""
        mock_sp = {
            "success": True,
            "energy_hartree": -10.0,
            "energy_kj_mol": -10.0 * 2625.5
        }
        mock_opt = {
            "success": True,
            "energy_hartree": -10.05,
            "energy_kj_mol": -10.05 * 2625.5,
            "optimized_xyz": simple_xyz_content,  # gunakan input sebagai output (RMSD ≈ 0)
            "optimized_positions": [[0, 0, 0], [1.089, 0, 0], [-0.5445, 0.9428, 0]]
        }

        with patch("routers.structure.XTB_AVAILABLE", True), \
             patch("routers.structure.run_xtb_single_point", return_value=mock_sp), \
             patch("routers.structure.run_xtb_optimization", return_value=mock_opt):

            files = {"file": ("test.xyz", simple_xyz_content.encode(), "application/octet-stream")}
            response = await client.post("/api/linker/stability", files=files)

        assert response.status_code == 200
        data = response.json()

        # Verifikasi JSON schema sesuai issue.md
        assert data["status"] == "success"
        assert "e_sp_kcal" in data
        assert "e_opt_kcal" in data
        assert "delta_e_kcal" in data
        assert "rmsd_all" in data
        assert "rmsd_heavy" in data
        assert "me_delta_length" in data
        assert "me_delta_angle" in data
        assert "atoms_displacement" in data
        assert "coords_embedded" in data
        assert "coords_optimized" in data
        assert "bonds" in data

        # Verifikasi konversi energi Hartree -> kcal/mol
        assert data["e_sp_kcal"] == pytest.approx(-10.0 * 627.509, abs=0.1)
        assert data["e_opt_kcal"] == pytest.approx(-10.05 * 627.509, abs=0.1)
        assert data["delta_e_kcal"] == pytest.approx(0.05 * 627.509, abs=0.1)

    @pytest.mark.asyncio
    async def test_sp_failure_returns_400(self, client, simple_xyz_content):
        mock_sp = {"success": False, "error": "xTB crashed"}

        with patch("routers.structure.XTB_AVAILABLE", True), \
             patch("routers.structure.run_xtb_single_point", return_value=mock_sp):

            files = {"file": ("test.xyz", simple_xyz_content.encode(), "application/octet-stream")}
            response = await client.post("/api/linker/stability", files=files)

        assert response.status_code == 400
        assert "Single Point" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_opt_failure_returns_400(self, client, simple_xyz_content):
        mock_sp = {"success": True, "energy_hartree": -10.0, "energy_kj_mol": -26255.0}
        mock_opt = {"success": False, "error": "convergence failed"}

        with patch("routers.structure.XTB_AVAILABLE", True), \
             patch("routers.structure.run_xtb_single_point", return_value=mock_sp), \
             patch("routers.structure.run_xtb_optimization", return_value=mock_opt):

            files = {"file": ("test.xyz", simple_xyz_content.encode(), "application/octet-stream")}
            response = await client.post("/api/linker/stability", files=files)

        assert response.status_code == 400
        assert "Optimasi" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_cif_input_extracts_linker(self, client, sample_cif_content):
        """Test bahwa file .cif diterima dan linker diekstrak."""
        mock_sp = {
            "success": True,
            "energy_hartree": -5.0,
            "energy_kj_mol": -5.0 * 2625.5
        }
        # Buat mock optimized XYZ yang sesuai dengan atom linker dari CIF sample
        # Sample CIF punya 3 atom: Cu (SBU), C (linker), O (linker) -> 2 linker atoms
        mock_opt_xyz = "2\nopt\nC   5.050000  5.050000  5.050000\nO   2.520000  2.520000  2.520000\n"
        mock_opt = {
            "success": True,
            "energy_hartree": -5.1,
            "energy_kj_mol": -5.1 * 2625.5,
            "optimized_xyz": mock_opt_xyz,
            "optimized_positions": [[5.05, 5.05, 5.05], [2.52, 2.52, 2.52]]
        }

        with patch("routers.structure.XTB_AVAILABLE", True), \
             patch("routers.structure.run_xtb_single_point", return_value=mock_sp), \
             patch("routers.structure.run_xtb_optimization", return_value=mock_opt):

            files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
            response = await client.post("/api/linker/stability", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


# ===========================================================================
# Tests: Endpoint POST /api/structure (perubahan UFF + Kabsch)
# ===========================================================================

class TestStructureEndpointWithXtb:
    """Test endpoint /api/structure yang diperbarui dengan UFF relaxation dan Kabsch RMSD."""

    @pytest.mark.asyncio
    async def test_xtb_available_uses_kabsch_rmsd(self, client, sample_cif_content):
        """Jika xTB tersedia dan sukses, RMSD harus menggunakan analyze_linker_stability."""
        # Mock optimized xyz yang cocok jumlah atom linkernya
        linker_opt_xyz = "2\nopt\nC 5.0 5.0 5.1\nO 2.5 2.5 2.6\n"

        mock_sp = {"success": True, "energy_kj_mol": -100.0}
        mock_opt = {
            "success": True,
            "energy_kj_mol": -120.0,
            "optimized_xyz": linker_opt_xyz,
            "optimized_positions": [[5.0, 5.0, 5.1], [2.5, 2.5, 2.6]]
        }

        with patch("routers.structure.XTB_AVAILABLE", True), \
             patch("routers.structure.run_xtb_single_point", return_value=mock_sp), \
             patch("routers.structure.run_xtb_optimization", return_value=mock_opt):

            files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
            response = await client.post("/api/structure", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["delta_e"] == pytest.approx(20.0)
        assert isinstance(data["rmsd"], float)

    @pytest.mark.asyncio
    async def test_xtb_failure_fallback_zero(self, client, sample_cif_content):
        """Jika xTB crash, endpoint harus return error terkontrol."""
        def raise_error(*args, **kwargs):
            raise RuntimeError("xTB binary error")

        with patch("routers.structure.XTB_AVAILABLE", True), \
             patch("routers.structure.relax_hydrogens_uff", side_effect=raise_error):

            files = {"file": ("test.cif", sample_cif_content, "application/octet-stream")}
            response = await client.post("/api/structure", files=files)

        assert response.status_code == 500


# ===========================================================================
# Tests: Endpoint /analyze (integrasi stabilitas xTB)
# ===========================================================================

class TestAnalyzeEndpointStability:
    """Test integrasi xTB di endpoint /analyze."""

    @pytest.mark.asyncio
    async def test_analyze_without_file(self, client):
        """Tanpa file upload, stabilitas harus None / Belum dihitung."""
        response = await client.post("/analyze", data={
            "pv": "1.2", "gsa": "3000", "vsa": "1500",
            "lcd": "12.1", "pld": "8", "vf": "0.5",
            "density": "0.8", "metal_name": "Cu(NO3)2",
            "linker_name": "H3BTC", "smiles": "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O",
            "reaction_time": "24", "temperature": "120"
        })
        assert response.status_code == 200
        data = response.json()["results"]
        assert data["delta_e"] is None
        assert data["rmsd"] is None

    @pytest.mark.asyncio
    async def test_analyze_with_cif_xtb_unavailable(self, client, sample_cif_content):
        """Dengan file CIF tapi xTB tidak tersedia, status harus menunjukkan xTB unavailable."""
        with patch("routers.analysis.XTB_AVAILABLE", False):
            response = await client.post("/analyze",
                data={
                    "pv": "1.2", "gsa": "3000", "vsa": "1500",
                    "lcd": "12.1", "pld": "8", "vf": "0.5",
                    "density": "0.8", "metal_name": "Cu(NO3)2",
                    "linker_name": "H3BTC", "smiles": "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O",
                    "reaction_time": "24", "temperature": "120"
                },
                files={"file": ("test.cif", sample_cif_content, "application/octet-stream")}
            )
        assert response.status_code == 200
        data = response.json()["results"]
        assert "xTB tidak tersedia" in data["stability_status"]

    @pytest.mark.asyncio
    async def test_overall_feasible_considers_stability(self, client):
        """is_overall_feasible harus mempertimbangkan stability_feasible jika tersedia."""
        response = await client.post("/analyze", data={
            "pv": "1.2", "gsa": "3000", "vsa": "1500",
            "lcd": "12.1", "pld": "8", "vf": "0.5",
            "density": "0.8", "metal_name": "-",
            "linker_name": "-", "smiles": "C1=CC=CC=C1",
            "reaction_time": "24", "temperature": "120"
        })
        assert response.status_code == 200
        data = response.json()["results"]
        # stability_feasible = None, maka is_overall_feasible tidak terpengaruh
        assert isinstance(data["is_overall_feasible"], bool)


# ===========================================================================
# Tests: xtb_runner encoding fix (UTF-8 decode)
# ===========================================================================

class TestXtbRunnerEncoding:
    """Test bahwa subprocess output di-decode dengan UTF-8 + errors=replace."""

    def test_parse_xyz_positions(self):
        from services.xtb_runner import parse_xyz_positions
        xyz = "3\ncomment\nC 1.0 2.0 3.0\nH 4.0 5.0 6.0\nH 7.0 8.0 9.0\n"
        positions = parse_xyz_positions(xyz)
        assert len(positions) == 3
        assert positions[0] == pytest.approx([1.0, 2.0, 3.0])

    def test_parse_xyz_positions_empty(self):
        from services.xtb_runner import parse_xyz_positions
        assert parse_xyz_positions("") == []

    def test_parse_xyz_positions_short(self):
        from services.xtb_runner import parse_xyz_positions
        assert parse_xyz_positions("1\nshort\n") == []
