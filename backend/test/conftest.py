import pytest
import pytest_asyncio
import sys
import os
from httpx import AsyncClient

# Ensure backend directory is in path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest_asyncio.fixture
async def client():
    """
    Async client for FastAPI testing using httpx.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def sample_cif_content():
    """
    Minimal valid CIF content for testing.
    """
    return (
        "data_test_mof\n"
        "_cell_length_a 10.0000\n"
        "_cell_length_b 10.0000\n"
        "_cell_length_c 10.0000\n"
        "_cell_angle_alpha 90.0000\n"
        "_cell_angle_beta 90.0000\n"
        "_cell_angle_gamma 90.0000\n"
        "loop_\n"
        "_atom_site_label\n"
        "_atom_site_type_symbol\n"
        "_atom_site_fract_x\n"
        "_atom_site_fract_y\n"
        "_atom_site_fract_z\n"
        "Cu1 Cu 0.00000 0.00000 0.00000\n"
        "C1  C  0.50000 0.50000 0.50000\n"
        "O1  O  0.25000 0.25000 0.25000\n"
    ).encode("utf-8")

@pytest.fixture
def invalid_cif_content():
    """
    Invalid CIF content for testing error handling.
    """
    return b"this is not a valid cif file"

@pytest.fixture
def sample_feasibility_payload():
    """
    Standard valid payload for /api/feasibility.
    """
    return {
        "p": 5.0,
        "gsa": 3500.0,
        "vsa": 1800.0,
        "vf": 0.75,
        "pv": 1.25,
        "lcd": 15.0,
        "pld": 10.0
    }

@pytest.fixture
def sample_economic_payload():
    """
    Standard valid payload for /api/economic.
    """
    return {
        "metal_name": "Cu(NO3)2",
        "linker_name": "H3BTC",
        "reaction_time": 24.0,
        "temperature": 120.0,
        "smiles": "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O",
        "gravimetric_wc": 8.5
    }

@pytest.fixture
def sample_analyze_form_data():
    """
    Standard valid form data for /analyze.
    """
    return {
        "pv": 1.25,
        "gsa": 3500.0,
        "vsa": 1800.0,
        "lcd": 15.0,
        "pld": 10.0,
        "vf": 0.75,
        "density": 0.8,
        "metal_name": "Cu(NO3)2",
        "linker_name": "H3BTC",
        "reaction_time": 24.0,
        "temperature": 120.0
    }
