import asyncio
import sys
import json
import pytest
from pathlib import Path
from httpx import AsyncClient, ASGITransport

# Tambahkan backend parent directory ke sys.path agar bisa mengimpor main
sys.path.append(str(Path(__file__).parent.parent.resolve()))
from main import app

# Paksa encoding stdout ke UTF-8 agar aman dari error Windows console
sys.stdout.reconfigure(encoding='utf-8')

@pytest.mark.skip(reason="Manual integration test for local CIF file.")
@pytest.mark.asyncio
async def test():
    # Folder test ada di backend/test, jadi induknya (parent) adalah folder backend
    base_dir = Path(__file__).parent.parent.resolve()
    cif_path = base_dir / "uploads" / "zif-8-f.cif"
    
    if not cif_path.exists():
        print(f"[ERROR] File CIF tidak ditemukan di: {cif_path}")
        return
        
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        with open(cif_path, "rb") as f:
            content = f.read()
        files = {"file": ("zif-8-f.cif", content, "application/octet-stream")}
        response = await client.post("/api/structure", files=files)
        print("Status code:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            # Simpan test_structure_result.json di folder parent (backend) agar konsisten
            result_path = base_dir / "test_structure_result.json"
            with open(result_path, "w", encoding="utf-8") as f_out:
                json.dump(data, f_out, indent=2, ensure_ascii=False)
            print(f"Successfully saved response to {result_path}")
            
            # Print highlights
            print("Formula:", data.get("formula"))
            print("N Atoms:", data.get("n_atoms"))
            print("N SBU Atoms:", data.get("n_sbu_atoms"))
            print("N Linker Atoms:", data.get("n_linker_atoms"))
            print("Delta E:", data.get("delta_e"))
            print("RMSD:", data.get("rmsd"))
            print("Stability score:", data.get("stability_score"))
            print("Stability status:", data.get("stability_status"))
            print("Is feasible:", data.get("is_feasible"))
            print("Cell params:", data.get("cell_params"))
            print("XTB Available:", data.get("xtb_available"))
        else:
            print("Error response:", response.text)

if __name__ == "__main__":
    asyncio.run(test())
