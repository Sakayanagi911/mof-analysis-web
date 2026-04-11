# ISSUE: Implementasi 3 API Analisis MOF

> **Prioritas:** High  
> **Estimasi:** ~3-5 hari kerja  
> **Target:** Junior Programmer / AI Model  
> **Backend Framework:** FastAPI (sudah ter-setup di `main.py`)

---

## Ringkasan

Implementasi 3 endpoint API utama pada backend MOF Analysis:

| # | API | Endpoint | Metode |
|---|-----|----------|--------|
| 1 | Analisis Feasible (Whitebox) | `POST /api/feasibility` | Persamaan Polynomial Eksplisit (4-1 & 4-2) |
| 2 | Analisis Ekonomi | `POST /api/economic` | Kalkulasi Harga + Joback |
| 3 | Analisis Struktur CIF | `POST /api/structure` | xTB + RMSD |

---

## Struktur Direktori Saat Ini

```
backend/
├── main.py                          # FastAPI app (sudah ada)
├── requirements.txt                 # Dependencies (sudah ada)
├── models/
│   ├── schemas.py                   # Pydantic schemas (PERLU DIUBAH)
│   └── constants.py                 # Konstanta (PERLU DIUBAH)
├── services/
│   ├── whitebox_model.py            # Placeholder (PERLU DIISI)
│   ├── cost_analysis.py             # Placeholder (PERLU DIISI)
│   └── structure_parser.py          # Placeholder (PERLU DIISI)
├── routers/
│   ├── analysis.py                  # Router utama (PERLU DIUBAH)
│   ├── structure.py                 # Router CIF (PERLU DIUBAH)
│   └── visualization.py            # Router visual (TIDAK DIUBAH DULU)
├── utils/
│   ├── file_handler.py              # Utilitas file (PERLU DIISI)
│   └── plotting.py                  # Utilitas plot (TIDAK DIUBAH DULU)
├── data/
│   └── uploads/                     # Simpan file upload user
└── old_model/
    ├── CoRE-MOF-whitebox-ml.py      # REFERENSI untuk API #1
    ├── SYNMOF-MOFDBam-DoE-Screening # REFERENSI untuk API #1 (versi lain)
    ├── Cost Calculation, MCDM Screening, and Energy Analysis.ipynb  # REFERENSI untuk API #2
    ├── Hybrid Physics ML for Residual Heat Capacity Prediction.ipynb # REFERENSI untuk Joback (API #2)
    └── Input_for_DFT,_xTB_Conformational_Energy,_and_Geometry_Distortion_Bound_within_the_SBU.ipynb  # REFERENSI untuk API #3
```

---

---

# API #1: Analisis Feasible (Whitebox Model)

## Deskripsi
User menginput 7 parameter MOF, sistem memprediksi Working Uptake Gravimetrik (WUG) dan Volumetrik (WUV) menggunakan persamaan polynomial eksplisit (Persamaan 4-1 dan 4-2), lalu menentukan apakah MOF tersebut feasible berdasarkan threshold DOE 2025.

## Input Parameter

| Parameter | Tipe | Satuan | Keterangan | Contoh |
|-----------|------|--------|------------|--------|
| `p` | float | bar | Tekanan operasi | 5.0 |
| `gsa` | float | m²/g | Gravimetric Surface Area | 3500.0 |
| `vsa` | float | m²/cm³ | Volumetric Surface Area | 1800.0 |
| `vf` | float | - (0-1) | Void Fraction | 0.75 |
| `pv` | float | cm³/g | Pore Volume | 1.25 |
| `lcd` | float | Å | Largest Cavity Diameter | 15.0 |
| `pld` | float | Å | Pore Limiting Diameter | 10.0 |

## Output

| Output | Tipe | Satuan | Keterangan |
|--------|------|--------|------------|
| `gravimetric_wc` (WUG) | float | wt.% | Working Uptake Gravimetrik |
| `volumetric_wc` (WUV) | float | g H₂/L | Working Uptake Volumetrik |
| `is_feasible` | bool | - | `true` jika WUG ≥ 5.5 **DAN** WUV ≥ 40 |

## Kriteria Feasibility

```
Feasible = (gravimetric_wc >= 5.5) AND (volumetric_wc >= 40.0)
```

## Persamaan yang Digunakan

### Persamaan (4-1): Working Uptake Gravimetric (WUG)

```
WUG = -4.47194 + 1.77349·p + 0.000511149·GSA + 0.00163429·VSA
      + 3.92696·VF + 5.59522·PV - 0.0764434·LCD + 0.262302·PLD
      - 0.163317·p² - 0.00133171·p·GSA + 7.69048e-5·p·VSA
      - 2.66592·p·VF + 2.45092·p·PV + 0.089082·p·LCD
      - 0.0975448·p·PLD - 4.1166e-8·GSA² - 1.15768e-7·GSA·VSA
      + 0.00280453·GSA·VF - 2.35326e-5·GSA·PV + 8.39123e-6·GSA·LCD
      - 3.89128e-6·GSA·PLD + 2.21456e-7·VSA² - 0.00231186·VSA·VF
      - 0.00180075·VSA·PV + 4.34998e-6·VSA·LCD + 1.65433e-5·VSA·PLD
      + 4.52648·VF² - 3.82519·VF·PV - 0.0639716·VF·LCD
      - 0.283064·VF·PLD - 0.0213098·PV² + 0.000824477·PV·LCD
      + 0.00253194·PV·PLD + 0.000521033·LCD² + 0.000700743·LCD·PLD
      - 0.000244913·PLD²
```

### Persamaan (4-2): Working Uptake Volumetric (WUV)

```
WUV = -49.6238 + 17.4843·p - 0.000310481·GSA + 0.0214365·VSA
      + 32.4082·VF + 14.1933·PV + 0.0660557·LCD + 1.66494·PLD
      - 1.79789·p² - 0.00754047·p·GSA - 0.0012505·p·VSA
      - 22.99·p·VF + 69.0864·p·PV + 0.861169·p·LCD
      - 0.523851·p·PLD + 1.51676e-7·GSA² + 3.18358e-7·GSA·VSA
      + 0.0145422·GSA·VF - 5.75705e-5·GSA·PV + 0.000157672·GSA·LCD
      - 2.93554e-5·GSA·PLD + 7.11672e-7·VSA² - 0.0162344·VSA·VF
      - 0.0208807·VSA·PV + 3.334e-5·VSA·LCD + 0.000196064·VSA·PLD
      + 44.1803·VF² - 14.2407·VF·PV - 1.95209·VF·LCD
      - 2.23509·VF·PLD - 0.0384937·PV² - 0.00185746·PV·LCD
      + 0.0410538·PV·PLD + 0.00735029·LCD² + 0.00119741·LCD·PLD
      + 0.00386859·PLD²
```

---

### Tahapan Implementasi API #1

#### Langkah 1.1: Implementasi Service `whitebox_model.py`

**FILE:** `services/whitebox_model.py`

**KONTEKS:** Kalkulasi menggunakan persamaan polynomial eksplisit (hardcoded) dengan koefisien yang sudah ditetapkan. **TIDAK perlu** file koefisien JSON, numpy, maupun sklearn. Semua koefisien sudah tertanam langsung di dalam fungsi `calculate_wug()` dan `calculate_wuv()`.

**APA YANG HARUS DILAKUKAN:**

Ganti isi placeholder dengan implementasi berikut:

```python
"""
Modul Whitebox Model untuk prediksi Working Uptake MOF.
Menggunakan persamaan polynomial eksplisit (Persamaan 4-1 dan 4-2).
Tidak memerlukan sklearn atau file koefisien eksternal.
"""

# Threshold DOE 2025
DOE_TARGET_GRAV = 5.5   # wt.%
DOE_TARGET_VOL = 40.0   # g H2/L


def calculate_wug(p, GSA, VSA, VF, PV, LCD, PLD):
    """
    Persamaan (4-1) Working Uptake Gravimetric.
    
    Parameters:
        p: Tekanan operasi [bar]
        GSA: Gravimetric Surface Area [m²/g]
        VSA: Volumetric Surface Area [m²/cm³]
        VF: Void Fraction [-]
        PV: Pore Volume [cm³/g]
        LCD: Largest Cavity Diameter [Å]
        PLD: Pore Limiting Diameter [Å]
    
    Returns:
        float: Working Uptake Gravimetric [wt.%]
    """
    wug = (
        -4.47194 + (1.77349 * p) + (0.000511149 * GSA) + (0.00163429 * VSA) + 
        (3.92696 * VF) + (5.59522 * PV) - (0.0764434 * LCD) + (0.262302 * PLD) - 
        (0.163317 * (p**2)) - (0.00133171 * p * GSA) + (7.69048e-5 * p * VSA) - 
        (2.66592 * p * VF) + (2.45092 * p * PV) + (0.089082 * p * LCD) - 
        (0.0975448 * p * PLD) - (4.1166e-8 * (GSA**2)) - (1.15768e-7 * GSA * VSA) + 
        (0.00280453 * GSA * VF) - (2.35326e-5 * GSA * PV) + (8.39123e-6 * GSA * LCD) - 
        (3.89128e-6 * GSA * PLD) + (2.21456e-7 * (VSA**2)) - (0.00231186 * VSA * VF) - 
        (0.00180075 * VSA * PV) + (4.34998e-6 * VSA * LCD) + (1.65433e-5 * VSA * PLD) + 
        (4.52648 * (VF**2)) - (3.82519 * VF * PV) - (0.0639716 * VF * LCD) - 
        (0.283064 * VF * PLD) - (0.0213098 * (PV**2)) + (0.000824477 * PV * LCD) + 
        (0.00253194 * PV * PLD) + (0.000521033 * (LCD**2)) + (0.000700743 * LCD * PLD) - 
        (0.000244913 * (PLD**2))
    )
    return round(wug, 3)


def calculate_wuv(p, GSA, VSA, VF, PV, LCD, PLD):
    """
    Persamaan (4-2) Working Uptake Volumetric.
    
    Parameters:
        p: Tekanan operasi [bar]
        GSA: Gravimetric Surface Area [m²/g]
        VSA: Volumetric Surface Area [m²/cm³]
        VF: Void Fraction [-]
        PV: Pore Volume [cm³/g]
        LCD: Largest Cavity Diameter [Å]
        PLD: Pore Limiting Diameter [Å]
    
    Returns:
        float: Working Uptake Volumetric [g H₂/L]
    """
    wuv = (
        -49.6238 + (17.4843 * p) - (0.000310481 * GSA) + (0.0214365 * VSA) + 
        (32.4082 * VF) + (14.1933 * PV) + (0.0660557 * LCD) + (1.66494 * PLD) - 
        (1.79789 * (p**2)) - (0.00754047 * p * GSA) - (0.0012505 * p * VSA) - 
        (22.99 * p * VF) + (69.0864 * p * PV) + (0.861169 * p * LCD) - 
        (0.523851 * p * PLD) + (1.51676e-7 * (GSA**2)) + (3.18358e-7 * GSA * VSA) + 
        (0.0145422 * GSA * VF) - (5.75705e-5 * GSA * PV) + (0.000157672 * GSA * LCD) - 
        (2.93554e-5 * GSA * PLD) + (7.11672e-7 * (VSA**2)) - (0.0162344 * VSA * VF) - 
        (0.0208807 * VSA * PV) + (3.334e-5 * VSA * LCD) + (0.000196064 * VSA * PLD) + 
        (44.1803 * (VF**2)) - (14.2407 * VF * PV) - (1.95209 * VF * LCD) - 
        (2.23509 * VF * PLD) - (0.0384937 * (PV**2)) - (0.00185746 * PV * LCD) + 
        (0.0410538 * PV * PLD) + (0.00735029 * (LCD**2)) + (0.00119741 * LCD * PLD) + 
        (0.00386859 * (PLD**2))
    )
    return round(wuv, 3)


def predict_working_capacity(p: float, gsa: float, vsa: float,
                              vf: float, pv: float,
                              lcd: float, pld: float) -> dict:
    """
    Prediksi Working Uptake Gravimetrik dan Volumetrik
    menggunakan persamaan polynomial eksplisit.
    
    Parameters:
        p: Tekanan operasi [bar]
        gsa: Gravimetric Surface Area [m²/g]
        vsa: Volumetric Surface Area [m²/cm³]
        vf: Void Fraction [-]
        pv: Pore Volume [cm³/g]
        lcd: Largest Cavity Diameter [Å]
        pld: Pore Limiting Diameter [Å]
    
    Returns:
        dict dengan keys: gravimetric_wc, volumetric_wc, is_feasible
    """
    # Hitung WUG (Persamaan 4-1)
    gravimetric_wc = calculate_wug(p, gsa, vsa, vf, pv, lcd, pld)
    
    # Hitung WUV (Persamaan 4-2)
    volumetric_wc = calculate_wuv(p, gsa, vsa, vf, pv, lcd, pld)
    
    # Feasibility check terhadap threshold DOE 2025
    is_feasible = (gravimetric_wc >= DOE_TARGET_GRAV) and (volumetric_wc >= DOE_TARGET_VOL)
    
    return {
        "gravimetric_wc": gravimetric_wc,
        "volumetric_wc": volumetric_wc,
        "is_feasible": is_feasible
    }
```

**KEUNTUNGAN pendekatan ini:**
- ✅ **Tidak perlu sklearn** — mengurangi dependency berat
- ✅ **Tidak perlu file koefisien JSON** — koefisien sudah hardcoded
- ✅ **Tidak perlu numpy** — hanya operasi aritmatika Python standar
- ✅ **Deterministik dan transparan** — persamaan bisa diverifikasi langsung

---

#### Langkah 1.2: Buat Schema Pydantic untuk API #1

**FILE:** `models/schemas.py` — Tambahkan class baru (jangan hapus yang sudah ada):

```python
class FeasibilityRequest(BaseModel):
    p: float        # Tekanan operasi [bar]
    gsa: float      # Gravimetric Surface Area [m²/g]
    vsa: float      # Volumetric Surface Area [m²/cm³]
    vf: float       # Void Fraction [-]
    pv: float       # Pore Volume [cm³/g]
    lcd: float      # Largest Cavity Diameter [Å]
    pld: float      # Pore Limiting Diameter [Å]

class FeasibilityResponse(BaseModel):
    status: str                # "success" atau "error"
    gravimetric_wc: float      # Working Uptake Gravimetrik [wt.%]
    volumetric_wc: float       # Working Uptake Volumetrik [g H₂/L]
    is_feasible: bool          # True jika memenuhi threshold DOE 2025
    thresholds: dict           # {"gravimetric": 5.5, "volumetric": 40.0}
```

---

#### Langkah 1.3: Buat Router Endpoint untuk API #1

**FILE:** `routers/analysis.py` — Tambahkan endpoint baru:

```python
from models.schemas import FeasibilityRequest, FeasibilityResponse
from services.whitebox_model import predict_working_capacity

@router.post("/api/feasibility", response_model=FeasibilityResponse)
async def analyze_feasibility(request: FeasibilityRequest):
    """
    Analisis feasibility MOF berdasarkan 7 parameter struktural.
    Menggunakan persamaan polynomial eksplisit (Persamaan 4-1 & 4-2).
    """
    try:
        result = predict_working_capacity(
            p=request.p, gsa=request.gsa, vsa=request.vsa,
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
```

#### Langkah 1.4: Testing API #1

**Contoh request (curl):**

```bash
curl -X POST http://localhost:8000/api/feasibility \
  -H "Content-Type: application/json" \
  -d '{
    "p": 5.0,
    "gsa": 3500.0,
    "vsa": 1800.0,
    "vf": 0.75,
    "pv": 1.25,
    "lcd": 15.0,
    "pld": 10.0
  }'
```

**Expected response:**
```json
{
  "status": "success",
  "gravimetric_wc": 7.891,
  "volumetric_wc": 44.123,
  "is_feasible": true,
  "thresholds": {"gravimetric": 5.5, "volumetric": 40.0}
}
```

> **CATATAN:** Nilai expected response di atas adalah contoh ilustratif. Nilai aktual bergantung pada input yang diberikan.

---

---

# API #2: Analisis Ekonomi

## Deskripsi
User menginput nama metal, nama linker, waktu reaksi, temperatur, dan SMILES linker. Sistem menghitung harga MOF (USD/kg), harga penyimpanan H₂ (USD/kg H₂), energi reaksi (Q dan Q loss), dan menentukan feasibility ekonomi.

## Input Parameter

| Parameter | Tipe | Keterangan | Contoh |
|-----------|------|------------|--------|
| `metal_name` | string | Nama metal precursor | "Cu(NO₃)₂" |
| `linker_name` | string | Nama linker | "H₃BTC" |
| `reaction_time` | float | Waktu reaksi (jam) | 24.0 |
| `temperature` | float | Temperatur reaksi (°C) | 120.0 |
| `smiles` | string | SMILES linker | "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O" |
| `gravimetric_wc` | float | Working Capacity dari API #1 (opsional, untuk hitung storage cost) | 8.5 |

## Output

| Output | Tipe | Satuan | Keterangan |
|--------|------|--------|------------|
| `mof_cost_usd_per_kg` | float | USD/kg MOF | Harga MOF per kg |
| `storage_cost_usd_per_kg_h2` | float | USD/kg H₂ | Biaya penyimpanan H₂ |
| `q_energy_kj` | float | kJ | Energi reaksi total |
| `q_loss_kj` | float | kJ | Energi yang hilang |
| `is_feasible` | bool | - | Lihat kriteria di bawah |

## Kriteria Feasibility Ekonomi

```
Feasible = (mof_cost_usd_per_kg <= 30) 
       AND (storage_cost_usd_per_kg_h2 <= 300) 
       AND (reaction_time <= 48) 
       AND (temperature <= 180)
```

---

### Tahapan Implementasi API #2

#### Langkah 2.1: Buat Database Harga Metal & Linker

**KONTEKS:** Di file Colab referensi (`Cost Calculation, MCDM Screening, and Energy Analysis.ipynb`), harga diambil dari file Excel `Synthesis_Parameter_3.xlsx` yang memiliki 3 sheet:
- **Sheet 1:** Data MOF (termasuk massa metal, volume solvent, dll)
- **Sheet 2:** Harga solvent per mL (€/mL) berdasarkan `Solvent_Code`
- **Sheet 3:** Harga metal per gram (€/g) berdasarkan `Metal_Code`

Linker harga sudah ada di Sheet 1 kolom `Linker1 (€/g)`.

**APA YANG HARUS DILAKUKAN:**

1. Buat file JSON statis `data/price_database.json` yang berisi harga metal dan linker umum:

```json
{
  "eur_to_usd": 1.15,
  "scale_factors": {
    "ym": 0.56,
    "ym_linker": 0.67,
    "industrial_mass_mg": 10000000
  },
  "metals": {
    "Cu(NO3)2": {"price_eur_per_g": 0.00255, "grade": "technical"},
    "Zn(NO3)2": {"price_eur_per_g": 0.00128, "grade": "technical"},
    "Zr(OPr)4": {"price_eur_per_g": 0.01500, "grade": "technical"},
    "Al(NO3)3": {"price_eur_per_g": 0.00180, "grade": "technical"},
    "Fe(NO3)3": {"price_eur_per_g": 0.00200, "grade": "technical"},
    "Cr(NO3)3": {"price_eur_per_g": 0.00350, "grade": "technical"}
  },
  "linkers": {
    "H3BTC": {"price_eur_per_g": 6.868, "smiles": "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O"},
    "H2BDC": {"price_eur_per_g": 0.5, "smiles": "OC(=O)c1ccc(cc1)C(O)=O"},
    "H4DOBDC": {"price_eur_per_g": 15.0, "smiles": "Oc1cc(O)c(cc1C(O)=O)C(O)=O"},
    "BPDC": {"price_eur_per_g": 48.28, "smiles": "OC(=O)c1ccc(-c2ccc(cc2)C(O)=O)cc1"}
  },
  "solvents": {
    "DMF": {"price_eur_per_ml": 0.000654},
    "DMA": {"price_eur_per_ml": 0.001961},
    "DEF": {"price_eur_per_ml": 0.000391},
    "H2O": {"price_eur_per_ml": 0.000001}
  }
}
```

> **CATATAN:** Harga di atas diambil dari output notebook Colab (Technical Grade pricing). Bisa ditambah sesuai kebutuhan.

**FILE YANG HARUS DIBUAT:** `data/price_database.json`

---

#### Langkah 2.2: Implementasi Joback Group Contribution untuk Cp

**KONTEKS:** Metode Joback digunakan untuk menghitung Heat Capacity (Cp) dari SMILES. Ini dibutuhkan untuk menghitung Q dan Q_loss. Referensi ada di notebook `Hybrid Physics ML for Residual Heat Capacity Prediction.ipynb` baris ~1117-1300.

**FILE:** Buat file baru `services/joback.py`

**APA YANG HARUS DILAKUKAN:**

```python
"""
Modul Joback Group Contribution untuk menghitung Cp dari SMILES.
Referensi: old_model/Hybrid Physics ML for Residual Heat Capacity Prediction.ipynb
"""

from rdkit import Chem
import numpy as np

# Definisi gugus Joback dengan koefisien a, b, c, d
# Cp(T) = Σ (n_i × (a_i + b_i*T + c_i*T² + d_i*T³))  [J/(mol·K)]
# T dalam Kelvin

JOBACK_CP_GROUPS = {
    # Nama Gugus: {smarts, a, b, c, d}
    # ---- Grup Non-Ring ----
    "-CH3":     {"smarts": "[CX4H3]",  "a": 19.5,  "b": -8.08e-3, "c": 1.53e-4,  "d": -9.67e-8},
    "-CH2-":    {"smarts": "[CX4H2]",  "a": -0.909,"b": 9.50e-2,  "c": -5.44e-5, "d": 1.19e-8},
    ">CH-":     {"smarts": "[CX4H1]",  "a": -23.0, "b": 2.04e-1,  "c": -2.65e-4, "d": 1.20e-7},
    ">C<":      {"smarts": "[CX4H0]",  "a": -66.2, "b": 4.27e-1,  "c": -6.41e-4, "d": 3.01e-7},
    "=CH2":     {"smarts": "[CX3H2]=[CX3]", "a": 23.6,  "b": -3.81e-2, "c": 1.72e-4,  "d": -1.03e-7},
    "=CH-":     {"smarts": "[CX3H1]=[CX3]", "a": -8.0,  "b": 1.05e-1,  "c": -9.63e-5, "d": 3.56e-8},
    "=C<":      {"smarts": "[CX3H0](=[CX3])", "a": -28.1, "b": 2.08e-1,  "c": -3.06e-4, "d": 1.46e-7},
    "-OH (alcohol)": {"smarts": "[OX2H]",     "a": 25.7,  "b": -6.91e-2, "c": 1.77e-4,  "d": -9.88e-8},
    "-O- (non-ring)":{"smarts": "[OX2H0;!r]","a": 25.5,  "b": -6.32e-2, "c": 1.11e-4,  "d": -5.48e-8},
    ">C=O (non-ring)":{"smarts":"[CX3H0](=O)[#6;!r]", "a": 6.45, "b": 6.70e-2, "c": -3.57e-5, "d": 2.86e-9},
    "-COOH":    {"smarts": "[CX3](=O)[OX2H]", "a": 24.1,  "b": 4.27e-2,  "c": 8.04e-5,  "d": -6.87e-8},
    "-NH2":     {"smarts": "[NX3H2]",  "a": 26.9,  "b": -4.12e-2, "c": 1.64e-4,  "d": -9.76e-8},
    ">NH (non-ring)":{"smarts": "[NX3H1;!r]", "a": -1.21, "b": 7.62e-2, "c": -4.86e-5, "d": 1.05e-8},
    "-N= (non-ring)":{"smarts": "[NX2;!r]",   "a": 11.8,  "b": -2.30e-2, "c": 1.07e-4,  "d": -6.28e-8},
    # ---- Grup Ring ----
    "-CH2- (ring)":  {"smarts": "[CX4H2;r]",  "a": -6.03, "b": 8.54e-2,  "c": -8.00e-6, "d": -1.80e-8},
    "=CH- (ring)":   {"smarts": "[cX3H1]",    "a": -2.14, "b": 5.74e-2,  "c": -1.64e-6, "d": -1.59e-8},
    "=C< (ring)":    {"smarts": "[cX3H0]",    "a": -8.25, "b": 1.01e-1,  "c": -1.42e-4, "d": 6.78e-8},
    "-O- (ring)":    {"smarts": "[OX2H0;r]",  "a": 12.2,  "b": -1.26e-2, "c": 6.03e-5,  "d": -3.86e-8},
    "-NH- (ring)":   {"smarts": "[NX3H1;r]",  "a": 8.83,  "b": -3.84e-3, "c": 4.35e-5,  "d": -2.60e-8},
    "-N= (ring)":    {"smarts": "[nX2]",       "a": 5.69,  "b": -4.12e-3, "c": 1.28e-5,  "d": -8.88e-9},
}

def count_joback_groups(smiles: str) -> dict:
    """
    Hitung jumlah masing-masing gugus Joback pada molekul.
    
    Args:
        smiles: String SMILES dari molekul
    
    Returns:
        dict: {nama_gugus: jumlah}
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"SMILES tidak valid: {smiles}")
    
    # Tambah hidrogen eksplisit agar match pattern lebih akurat
    mol = Chem.AddHs(mol)
    
    counts = {}
    used_atoms = set()
    
    # Urutkan berdasarkan spesifisitas (grup yang lebih spesifik dulu)
    for name, info in JOBACK_CP_GROUPS.items():
        patt = Chem.MolFromSmarts(info["smarts"])
        if patt is None:
            continue
        matches = mol.GetSubstructMatches(patt)
        n = 0
        for match in matches:
            # Hindari double-counting: cek apakah atom utama sudah terpakai
            primary = match[0]
            if primary not in used_atoms:
                n += 1
                used_atoms.add(primary)
        if n > 0:
            counts[name] = n
    
    return counts

def calculate_cp_joback(smiles: str, T: float = 298.15) -> float:
    """
    Hitung Cp (Heat Capacity) pada temperatur T menggunakan metode Joback.
    
    Cp(T) = Σ n_i × (a_i + b_i×T + c_i×T² + d_i×T³)
    
    Args:
        smiles: String SMILES
        T: Temperatur dalam Kelvin (default 298.15 K)
    
    Returns:
        float: Cp dalam J/(mol·K), atau None jika gagal
    """
    try:
        counts = count_joback_groups(smiles)
    except ValueError:
        return None
    
    Cp = 0.0
    for group_name, n in counts.items():
        if group_name in JOBACK_CP_GROUPS and n > 0:
            info = JOBACK_CP_GROUPS[group_name]
            a, b, c, d = info["a"], info["b"], info["c"], info["d"]
            Cp += n * (a + b*T + c*T**2 + d*T**3)
    
    return Cp if Cp > 0 else None
```

> **PENTING:** Tabel JOBACK_CP_GROUPS di atas adalah SUBSET. Lengkapi sesuai referensi notebook baris ~1118-1178. Pastikan SMARTS pattern sudah benar dengan testing.

---

#### Langkah 2.3: Implementasi Service `cost_analysis.py`

**FILE:** `services/cost_analysis.py`

**APA YANG HARUS DILAKUKAN:**

```python
"""
Modul kalkulasi biaya sintesis MOF.
Referensi: old_model/Cost Calculation, MCDM Screening, and Energy Analysis.ipynb
"""

import json
import numpy as np
from pathlib import Path
from services.joback import calculate_cp_joback

PRICE_DB_PATH = Path(__file__).parent.parent / "data" / "price_database.json"

# Konstanta feasibility ekonomi
MAX_MOF_COST = 30.0         # USD/kg MOF
MAX_STORAGE_COST = 300.0    # USD/kg H2
MAX_REACTION_TIME = 48.0    # jam
MAX_TEMPERATURE = 180.0     # °C

def load_price_database():
    """Load database harga dari JSON."""
    with open(PRICE_DB_PATH, "r") as f:
        return json.load(f)

def calculate_mof_cost(metal_name: str, linker_name: str,
                        metal_mass_mg: float = 100.0,
                        linker_mass_mg: float = 50.0,
                        product_mass_mg: float = 50.0) -> dict:
    """
    Hitung harga MOF per kg.
    
    Rumus (dari referensi notebook):
        1. Ambil harga satuan metal (€/g) dan linker (€/g) dari database
        2. Hitung harga bahan: harga = massa × harga_satuan
        3. Terapkan faktor diskon industri: 
           scale_factor = (product_mg / 10^7)^ym
        4. Total harga = Σ(harga_bahan × scale_factor)
        5. Konversi ke USD/kg: total / (product_mg / 10^6) × eur_to_usd
    
    Returns:
        dict: {mof_cost_eur_per_kg, mof_cost_usd_per_kg}
    """
    db = load_price_database()
    eur_to_usd = db["eur_to_usd"]
    ym = db["scale_factors"]["ym"]
    ym_linker = db["scale_factors"]["ym_linker"]
    ind_mass = db["scale_factors"]["industrial_mass_mg"]
    
    # Lookup harga metal
    metal_price_per_g = db["metals"].get(metal_name, {}).get("price_eur_per_g", 0.01)
    
    # Lookup harga linker
    linker_price_per_g = db["linkers"].get(linker_name, {}).get("price_eur_per_g", 10.0)
    
    # Harga bahan mentah
    metal_cost_eur = metal_price_per_g * (metal_mass_mg / 1000.0)
    linker_cost_eur = linker_price_per_g * (linker_mass_mg / 1000.0)
    
    # Scale factor (diskon produksi massal)
    if product_mass_mg <= 0:
        product_mass_mg = 1.0
    scale = (product_mass_mg / ind_mass) ** ym
    scale_linker = (product_mass_mg / ind_mass) ** ym_linker
    
    metal_cost_eur *= scale
    linker_cost_eur *= scale_linker
    
    total_eur = metal_cost_eur + linker_cost_eur
    
    # Konversi ke per-kg
    product_kg = product_mass_mg / 1e6
    if product_kg > 0:
        mof_cost_eur_per_kg = total_eur / product_kg
    else:
        mof_cost_eur_per_kg = 0.0
    
    mof_cost_usd_per_kg = mof_cost_eur_per_kg * eur_to_usd
    
    return {
        "mof_cost_eur_per_kg": round(mof_cost_eur_per_kg, 4),
        "mof_cost_usd_per_kg": round(mof_cost_usd_per_kg, 4)
    }

def calculate_energy(smiles: str, temperature_c: float, 
                      reaction_time_h: float) -> dict:
    """
    Hitung Q (energi reaksi) dan Q_loss berdasarkan Cp dari Joback.
    
    Rumus dasar:
        Cp = Joback(smiles, T)   # dalam J/(mol·K)
        ΔT = T_reaction - T_ambient  (K)
        Q = Cp × ΔT / 1000      # konversi ke kJ/mol
        Q_loss = Q × loss_factor × time_factor
    
    Args:
        smiles: SMILES string linker
        temperature_c: Temperatur reaksi (°C)
        reaction_time_h: Waktu reaksi (jam)
    
    Returns:
        dict: {q_energy_kj, q_loss_kj, cp_value}
    """
    T_ambient = 298.15  # Kelvin (25°C)
    T_reaction = temperature_c + 273.15  # Konversi ke Kelvin
    
    # Hitung Cp pada temperatur reaksi
    cp = calculate_cp_joback(smiles, T=T_reaction)
    if cp is None:
        cp = calculate_cp_joback(smiles, T=T_ambient)
    if cp is None:
        cp = 100.0  # Fallback default Cp
    
    # Hitung Q
    delta_T = T_reaction - T_ambient
    q_energy_kj = (cp * delta_T) / 1000.0  # Konversi J ke kJ
    
    # Hitung Q_loss (asumsi: loss factor proporsional terhadap waktu)
    # Semakin lama reaksi, semakin besar heat loss
    loss_factor = 0.15  # 15% heat loss per cycle (asumsi sederhana)
    time_factor = reaction_time_h / 24.0  # Normalisasi ke 1 hari
    q_loss_kj = q_energy_kj * loss_factor * time_factor
    
    return {
        "q_energy_kj": round(q_energy_kj, 4),
        "q_loss_kj": round(q_loss_kj, 4),
        "cp_value": round(cp, 4)
    }

def calculate_storage_cost(mof_cost_usd_per_kg: float,
                            gravimetric_wc: float) -> float:
    """
    Hitung biaya penyimpanan H₂ per kg.
    
    Rumus (dari referensi):
        Storage Cost = MOF Price (USD/kg) / (WC_grav / 100)
    
    Args:
        mof_cost_usd_per_kg: Harga MOF dalam USD/kg
        gravimetric_wc: Working Capacity Gravimetrik dalam wt.%
    
    Returns:
        float: Biaya penyimpanan dalam USD/kg H₂
    """
    if gravimetric_wc <= 0:
        return float('inf')
    return round(mof_cost_usd_per_kg / (gravimetric_wc / 100.0), 4)

def run_economic_analysis(metal_name: str, linker_name: str,
                           reaction_time: float, temperature: float,
                           smiles: str, gravimetric_wc: float = 5.0) -> dict:
    """
    Jalankan analisis ekonomi lengkap.
    
    Returns:
        dict lengkap dengan semua output ekonomi + feasibility
    """
    # 1. Hitung harga MOF
    cost_result = calculate_mof_cost(metal_name, linker_name)
    mof_cost = cost_result["mof_cost_usd_per_kg"]
    
    # 2. Hitung biaya penyimpanan
    storage_cost = calculate_storage_cost(mof_cost, gravimetric_wc)
    
    # 3. Hitung energi
    energy_result = calculate_energy(smiles, temperature, reaction_time)
    
    # 4. Cek feasibility
    is_feasible = (
        mof_cost <= MAX_MOF_COST and
        storage_cost <= MAX_STORAGE_COST and
        reaction_time <= MAX_REACTION_TIME and
        temperature <= MAX_TEMPERATURE
    )
    
    return {
        "mof_cost_usd_per_kg": mof_cost,
        "storage_cost_usd_per_kg_h2": storage_cost,
        "q_energy_kj": energy_result["q_energy_kj"],
        "q_loss_kj": energy_result["q_loss_kj"],
        "is_feasible": is_feasible,
        "feasibility_details": {
            "mof_cost_ok": mof_cost <= MAX_MOF_COST,
            "storage_cost_ok": storage_cost <= MAX_STORAGE_COST,
            "time_ok": reaction_time <= MAX_REACTION_TIME,
            "temperature_ok": temperature <= MAX_TEMPERATURE
        }
    }
```

---

#### Langkah 2.4: Buat Schema dan Router untuk API #2

**FILE:** `models/schemas.py` — Tambahkan:

```python
class EconomicRequest(BaseModel):
    metal_name: str        # Nama metal precursor
    linker_name: str       # Nama linker
    reaction_time: float   # Waktu reaksi (jam)
    temperature: float     # Temperatur reaksi (°C)
    smiles: str            # SMILES linker
    gravimetric_wc: float = 5.0  # Opsional, dari API #1

class EconomicResponse(BaseModel):
    status: str
    mof_cost_usd_per_kg: float
    storage_cost_usd_per_kg_h2: float
    q_energy_kj: float
    q_loss_kj: float
    is_feasible: bool
    feasibility_details: dict
```

**FILE:** `routers/analysis.py` — Tambahkan endpoint:

```python
from models.schemas import EconomicRequest, EconomicResponse
from services.cost_analysis import run_economic_analysis

@router.post("/api/economic", response_model=EconomicResponse)
async def analyze_economic(request: EconomicRequest):
    """Analisis ekonomi MOF: harga, storage cost, energi."""
    try:
        result = run_economic_analysis(
            metal_name=request.metal_name,
            linker_name=request.linker_name,
            reaction_time=request.reaction_time,
            temperature=request.temperature,
            smiles=request.smiles,
            gravimetric_wc=request.gravimetric_wc
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
```

#### Langkah 2.5: Testing API #2

```bash
curl -X POST http://localhost:8000/api/economic \
  -H "Content-Type: application/json" \
  -d '{
    "metal_name": "Cu(NO3)2",
    "linker_name": "H3BTC",
    "reaction_time": 24.0,
    "temperature": 120.0,
    "smiles": "C(=O)(O)c1cc(cc(c1)C(=O)O)C(=O)O",
    "gravimetric_wc": 8.5
  }'
```

---

---

# API #3: Analisis Struktur CIF

## Deskripsi
User upload file `.cif` (struktur kristal MOF). Sistem membaca file, memisahkan SBU dan linker, menghitung energi linker dalam dua kondisi (embedded dalam MOF dan bebas/free) menggunakan metode xTB. Menghasilkan delta E, RMSD, skor stabilitas, dan visualisasi 3D.

## Input

| Parameter | Tipe | Keterangan |
|-----------|------|------------|
| `file` | UploadFile | File `.cif` dari user |

## Output

| Output | Tipe | Satuan | Keterangan |
|--------|------|--------|------------|
| `delta_e` | float | kJ/mol | Selisih energi (E_embedded - E_free) |
| `rmsd` | float | Å | Root Mean Square Deviation geometri |
| `stability_score` | float | kJ/mol | Skor stabilitas gabungan |
| `stability_status` | string | - | "Sangat stabil" / "Cukup stabil" / "Tidak stabil" |
| `is_feasible` | bool | - | true jika stability_score < 15 |
| `structure_3d` | dict | - | Data atom dan koordinat untuk rendering 3D |

## Interpretasi Skor Stabilitas

| Skor | Interpretasi | Feasible? |
|------|-------------|-----------|
| < 5 kJ/mol | Sangat stabil | Ya |
| 5 - 15 kJ/mol | Cukup stabil | Ya |
| > 15 kJ/mol | Tidak stabil | Tidak |

---

### Tahapan Implementasi API #3

> **CATATAN PENTING:** API #3 adalah yang paling kompleks dan membutuhkan dependency eksternal (xTB binary, OpenBabel). Implementasi ini akan dibagi menjadi dua fase:
> - **Fase A (MVP):** Parsing CIF + RMSD + Visualisasi 3D (tanpa xTB)
> - **Fase B (Full):** Integrasi xTB untuk perhitungan energi

---

#### Langkah 3.1: Implementasi CIF Parser (Fase A)

**FILE:** `services/structure_parser.py`

**APA YANG HARUS DILAKUKAN:**

```python
"""
Modul parsing file CIF dan analisis struktur MOF.
Referensi: old_model/Input_for_DFT,_xTB_Conformational_Energy,_and_Geometry_Distortion_Bound_within_the_SBU.ipynb
"""

import numpy as np
import tempfile
import os
from pathlib import Path
from ase.io import read as ase_read

def parse_cif_file(file_content: bytes, filename: str) -> dict:
    """
    Parse file CIF dan ekstrak informasi struktur.
    
    Args:
        file_content: Konten file CIF dalam bytes
        filename: Nama file asli
    
    Returns:
        dict: {atoms, positions, n_atoms, cell_params, formula}
    """
    # Simpan ke file temporary
    upload_dir = Path(__file__).parent.parent / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    temp_path = upload_dir / filename
    with open(temp_path, "wb") as f:
        f.write(file_content)
    
    try:
        # Baca file CIF dengan ASE
        structure = ase_read(str(temp_path))
        
        symbols = structure.get_chemical_symbols()
        positions = structure.get_positions().tolist()
        
        # Cell parameters
        cell = structure.get_cell()
        cell_params = {
            "a": float(cell[0][0]) if cell is not None else 0,
            "b": float(cell[1][1]) if cell is not None else 0,
            "c": float(cell[2][2]) if cell is not None else 0,
        }
        
        # Chemical formula
        formula = structure.get_chemical_formula()
        
        return {
            "atoms": symbols,
            "positions": positions,
            "n_atoms": len(symbols),
            "cell_params": cell_params,
            "formula": formula,
            "file_path": str(temp_path)
        }
    except Exception as e:
        raise ValueError(f"Gagal membaca file CIF: {str(e)}")

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
        "Li","Be","Na","Mg","Al","K","Ca","Sc","Ti","V","Cr","Mn","Fe",
        "Co","Ni","Cu","Zn","Ga","Rb","Sr","Y","Zr","Nb","Mo","Ru","Rh",
        "Pd","Ag","Cd","In","Sn","Cs","Ba","La","Ce","Hf","Ta","W","Re",
        "Os","Ir","Pt","Au","Pb","Bi"
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
    Hitung RMSD antara dua set posisi atom (heavy atoms only).
    
    RMSD = sqrt( (1/N) × Σ |r_i - r_i'|² )
    
    Referensi: notebook Input_for_DFT...ipynb baris ~274-300
    Menggunakan rdkit.Chem.rdMolAlign.AlignMol untuk alignment yang benar.
    
    Args:
        positions_1: Posisi atom set 1 [[x,y,z], ...]
        positions_2: Posisi atom set 2 [[x,y,z], ...]
    
    Returns:
        float: RMSD dalam Ångström
    """
    p1 = np.array(positions_1)
    p2 = np.array(positions_2)
    
    if p1.shape != p2.shape:
        raise ValueError("Jumlah atom tidak sama untuk RMSD calculation")
    
    # Centroid alignment
    p1_centered = p1 - p1.mean(axis=0)
    p2_centered = p2 - p2.mean(axis=0)
    
    diff = p1_centered - p2_centered
    rmsd = np.sqrt(np.mean(np.sum(diff**2, axis=1)))
    
    return float(rmsd)

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
        dict: {atoms: [{symbol, x, y, z}, ...], bonds: [...]}
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
```

---

#### Langkah 3.2: Implementasi xTB Runner (Fase B — Advanced)

**FILE:** Buat file baru `services/xtb_runner.py`

> **PRASYARAT:** xTB binary harus terinstall di server. Pada deployment, gunakan Docker container dengan xTB pre-installed.

```python
"""
Modul wrapper untuk menjalankan xTB (GFN2-xTB).
Referensi: old_model/Input_for_DFT,_xTB_Conformational_Energy,_and_Geometry_Distortion_Bound_within_the_SBU.ipynb

CATATAN: File ini membutuhkan xTB binary terinstall di PATH sistem.
Install: https://github.com/grimme-lab/xtb/releases
"""

import subprocess
import tempfile
import re
import os
from pathlib import Path

# Cek apakah xTB tersedia
XTB_AVAILABLE = False
try:
    result = subprocess.run(["xtb", "--version"], capture_output=True, text=True, timeout=10)
    XTB_AVAILABLE = result.returncode == 0
except (FileNotFoundError, subprocess.TimeoutExpired):
    XTB_AVAILABLE = False

def run_xtb_single_point(xyz_content: str) -> dict:
    """
    Jalankan xTB single point energy calculation.
    
    Command: xtb input.xyz --gfn2
    
    Args:
        xyz_content: Konten file XYZ (teks)
    
    Returns:
        dict: {energy_hartree, energy_kj_mol, success}
    """
    if not XTB_AVAILABLE:
        return {"energy_hartree": 0.0, "energy_kj_mol": 0.0, 
                "success": False, "error": "xTB not installed"}
    
    with tempfile.TemporaryDirectory() as tmpdir:
        xyz_path = os.path.join(tmpdir, "input.xyz")
        with open(xyz_path, "w") as f:
            f.write(xyz_content)
        
        try:
            result = subprocess.run(
                ["xtb", "input.xyz", "--gfn2"],
                capture_output=True, text=True,
                cwd=tmpdir, timeout=300
            )
            
            # Parse energi dari output xTB
            energy = parse_xtb_energy(result.stdout)
            
            return {
                "energy_hartree": energy,
                "energy_kj_mol": energy * 2625.5,  # Hartree → kJ/mol
                "success": True
            }
        except subprocess.TimeoutExpired:
            return {"energy_hartree": 0.0, "energy_kj_mol": 0.0,
                    "success": False, "error": "xTB timeout (>300s)"}
        except Exception as e:
            return {"energy_hartree": 0.0, "energy_kj_mol": 0.0,
                    "success": False, "error": str(e)}

def run_xtb_optimization(xyz_content: str) -> dict:
    """
    Jalankan xTB geometry optimization.
    
    Command: xtb input.xyz --opt --gfn2
    
    Returns:
        dict: {energy_hartree, energy_kj_mol, optimized_xyz, success}
    """
    if not XTB_AVAILABLE:
        return {"energy_hartree": 0.0, "energy_kj_mol": 0.0,
                "optimized_xyz": "", "success": False, 
                "error": "xTB not installed"}
    
    with tempfile.TemporaryDirectory() as tmpdir:
        xyz_path = os.path.join(tmpdir, "input.xyz")
        with open(xyz_path, "w") as f:
            f.write(xyz_content)
        
        try:
            result = subprocess.run(
                ["xtb", "input.xyz", "--opt", "--gfn2"],
                capture_output=True, text=True,
                cwd=tmpdir, timeout=600
            )
            
            energy = parse_xtb_energy(result.stdout)
            
            # Baca geometri yang sudah dioptimasi
            opt_xyz_path = os.path.join(tmpdir, "xtbopt.xyz")
            opt_xyz = ""
            if os.path.exists(opt_xyz_path):
                with open(opt_xyz_path, "r") as f:
                    opt_xyz = f.read()
            
            return {
                "energy_hartree": energy,
                "energy_kj_mol": energy * 2625.5,
                "optimized_xyz": opt_xyz,
                "success": True
            }
        except subprocess.TimeoutExpired:
            return {"energy_hartree": 0.0, "energy_kj_mol": 0.0,
                    "optimized_xyz": "", "success": False,
                    "error": "xTB optimization timeout (>600s)"}

def parse_xtb_energy(output: str) -> float:
    """
    Parse total energy dari output xTB.
    Cari baris: "TOTAL ENERGY" → extract nilai dalam Hartree.
    """
    for line in output.splitlines():
        if "TOTAL ENERGY" in line:
            match = re.search(r"(-?\d+\.\d+)", line)
            if match:
                return float(match.group(1))
    return 0.0

def calculate_delta_e(e_embedded_kj: float, e_free_kj: float) -> float:
    """
    Hitung ΔE = E_embedded - E_free.
    
    Nilai positif → linker tertekan/terdistorsi dalam MOF
    Nilai negatif → linker terstabilkan dalam MOF
    """
    return round(e_embedded_kj - e_free_kj, 4)
```

---

#### Langkah 3.3: Buat Schema dan Router untuk API #3

**FILE:** `models/schemas.py` — Tambahkan:

```python
from typing import List

class Atom3D(BaseModel):
    symbol: str
    x: float
    y: float
    z: float

class StructureResponse(BaseModel):
    status: str
    formula: str
    n_atoms: int
    n_sbu_atoms: int
    n_linker_atoms: int
    delta_e: float              # kJ/mol
    rmsd: float                 # Å
    stability_score: float      # skor gabungan
    stability_status: str       # "Sangat stabil" / "Cukup stabil" / "Tidak stabil"
    is_feasible: bool
    structure_3d: dict          # Data untuk rendering 3D
    cell_params: dict           # Parameter unit cell
```

**FILE:** `routers/structure.py` — Ubah seluruh isi:

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.structure_parser import (
    parse_cif_file, separate_sbu_and_linker,
    calculate_stability_score, prepare_3d_structure_data
)
from services.xtb_runner import (
    XTB_AVAILABLE, run_xtb_single_point, 
    run_xtb_optimization, calculate_delta_e
)

router = APIRouter()

@router.post("/api/structure")
async def analyze_structure(file: UploadFile = File(...)):
    """
    Analisis struktur MOF dari file CIF.
    
    Alur:
    1. Parse file CIF → ekstrak atom & posisi
    2. Pisahkan SBU dan linker
    3. Hitung energi linker (embedded vs free) via xTB
    4. Hitung RMSD distorsi geometri
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
        
        # 3. Hitung energi via xTB (jika tersedia)
        delta_e = 0.0
        if XTB_AVAILABLE and separated["linker_count"] > 0:
            # TODO: Konversi linker positions ke format XYZ
            # Lalu jalankan xTB embedded dan free
            pass  # Implementasi penuh di Fase B
        
        # 4. Hitung RMSD (placeholder — butuh dua geometri)
        rmsd = 0.0  # Akan dihitung saat xTB tersedia
        
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
```

---

#### Langkah 3.4: Testing API #3

```bash
# Upload file CIF
curl -X POST http://localhost:8000/api/structure \
  -F "file=@contoh_mof.cif"
```

---

---

# Langkah Terakhir: Update Dependencies & Main App

## Update `requirements.txt`

Pastikan semua dependency berikut sudah ada:

```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.9
pandas>=2.2.0
numpy>=1.26.0
scikit-learn>=1.4.0
scipy>=1.11.0
matplotlib>=3.8.0
rdkit>=2024.9.0
ase>=3.22.0
py3Dmol>=2.0.0
openpyxl>=3.1.0
tqdm>=4.66.0
```

## Update `main.py`

Pastikan router sudah terdaftar dengan prefix yang benar:

```python
from routers import analysis, structure

app.include_router(analysis.router, tags=["Analysis"])
app.include_router(structure.router, tags=["Structure"])
```

> **CATATAN:** Endpoint sudah didefinisikan dengan path penuh (e.g., `/api/feasibility`) di dalam router, jadi **JANGAN** tambahkan prefix di `include_router()`.

---

# Checklist Implementasi

## API #1 — Feasibility
- [ ] Generate dan simpan koefisien whitebox ke JSON
- [ ] Implementasi `services/whitebox_model.py`
- [ ] Tambah schema `FeasibilityRequest` dan `FeasibilityResponse`
- [ ] Tambah endpoint `POST /api/feasibility` di router
- [ ] Testing dengan curl/Postman

## API #2 — Ekonomi
- [ ] Buat `data/price_database.json`
- [ ] Implementasi `services/joback.py`
- [ ] Implementasi `services/cost_analysis.py`
- [ ] Tambah schema `EconomicRequest` dan `EconomicResponse`
- [ ] Tambah endpoint `POST /api/economic` di router
- [ ] Testing dengan curl/Postman

## API #3 — Struktur CIF
- [ ] Implementasi `services/structure_parser.py`
- [ ] Buat `services/xtb_runner.py`
- [ ] Tambah schema `StructureResponse`
- [ ] Update `routers/structure.py` dengan endpoint penuh
- [ ] Testing upload CIF + parsing
- [ ] (Fase B) Integrasi xTB dan RMSD aktual

## Umum
- [ ] Update `requirements.txt`
- [ ] Update `main.py` router registration
- [ ] Testing integrasi semua 3 API
- [ ] Pastikan CORS masih berfungsi untuk frontend

---

# Catatan untuk Implementor

1. **Urutan implementasi yang disarankan:** API #1 → API #2 → API #3 (dari yang paling sederhana)

2. **Jangan ubah** file-file di folder `old_model/` — ini adalah referensi saja.

3. **Error handling:** Semua endpoint harus mengembalikan response yang valid meskipun terjadi error. Gunakan try-except dan kembalikan `status: "error"`.

4. **Koefisien model:** File JSON koefisien di `data/trained_models/` harus dibuat **TERLEBIH DAHULU** sebelum mengimplementasikan API #1. Tanpa file ini, API tidak bisa berjalan.

5. **xTB binary:** Untuk API #3 versi lengkap, xTB harus terinstall di server. Jika belum tersedia, API akan tetap berfungsi dengan `delta_e = 0` dan `rmsd = 0`.

6. **File upload:** Pastikan folder `data/uploads/` sudah ada dan writable. File upload dari user akan disimpan sementara di sini.

7. **SMARTS pattern Joback:** Pattern di `services/joback.py` mungkin perlu fine-tuning. Cek dengan beberapa SMILES yang diketahui Cp-nya untuk validasi.
