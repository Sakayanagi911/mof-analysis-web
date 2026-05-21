# MOF Analysis API Backend

Backend ini dibangun menggunakan **FastAPI** (Python) untuk melakukan analisis kelayakan (*feasibility*), analisis ekonomi (*cost & energy*), serta analisis struktural (*structural parser* & xTB) pada *Metal-Organic Frameworks* (MOFs).

---

## Daftar Isi
1. [Prasyarat & Instalasi](#prasyarat--instalasi)
2. [Menjalankan Server](#menjalankan-server)
3. [Database & Model Data](#database--model-data)
4. [Dokumentasi REST API](#dokumentasi-rest-api)
   - [API Publik & Data](#1-api-publik--data)
   - [API Analisis & Prediksi](#2-api-analisis--prediksi)
   - [API Analisis Struktur (CIF)](#3-api-analisis-struktur-cif)
   - [API Visualisasi](#4-api-visualisasi)
5. [Contoh Pengujian API Menggunakan cURL](#contoh-pengujian-api-menggunakan-curl)
   - [Termasuk Pengujian File `zif-8-f.cif`](#pengujian-analisis-struktur-dengan-zif-8-fcif)

---

## Prasyarat & Instalasi

### 1. Kebutuhan Sistem
* Python 3.9 atau lebih tinggi.
* RdKit (untuk pemrosesan struktur kimia SMILES).
* (Opsional) `xtb` pada sistem PATH jika ingin menjalankan kalkulasi energi konformasi linker secara lokal.

### 2. Cara Instalasi
Clone repositori dan install dependensi dari folder `backend`:
```bash
pip install -r requirements.txt
```

---

## Menjalankan Server

Untuk menjalankan server pengembangan lokal (development server):
```bash
python main.py
```
atau menggunakan Uvicorn secara langsung:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Server akan berjalan di `http://127.0.0.1:8000`. Dokumentasi interaktif Swagger UI dapat diakses langsung melalui browser di `http://127.0.0.1:8000/docs`.

---

## Database & Model Data

Backend menggunakan database lokal berbasis JSON yang berlokasi di `data/price_database.json`. Database ini menyimpan informasi:
* **Logam (Metals)**: CAS number, kode, dan harga per gram dalam EUR (misal: `Cu(NO₃)₂·3H₂O`, `Zn(NO₃)₂·6H₂O`).
* **Pelarut (Solvents)**: CAS number, kode, dan harga per mL dalam EUR (misal: `DMF`, `EtOH`, `H2O`).
* **Aditif & Modulator**: Harga per mL dalam EUR (misal: `HCl`, `HNO3`, `Triethylamine`).
* **SMILES Mapping**: Hubungan antara representasi SMILES linker dengan nama linker serta harga per gram.
* **Uptake Data**: Data praprediksi kapasitas penyimpanan gas hidrogen untuk SMILES tertentu.

---

## Dokumentasi REST API

### 1. API Publik & Data

#### **GET /**
Mengecek status server dan versi API.
* **Response**: `200 OK`
  ```json
  {
    "message": "MOF Analysis API is running",
    "version": "1.0.0"
  }
  ```

#### **GET /get-prices**
Mendapatkan database lengkap harga logam, pelarut, aditif, modulator, dan SMILES mapping.
* **Response**: `200 OK`
  ```json
  {
    "eur_to_usd": 1.15,
    "scale_factors": { ... },
    "metals": { ... },
    "solvents": { ... },
    "additives": { ... },
    "modulators": { ... },
    "smiles_mapping": { ... }
  }
  ```

#### **GET /get-smiles-mapping**
Mendapatkan *mapping* dari SMILES ke nama linker komersial beserta informasi harga.
* **Response**: `200 OK`
  ```json
  {
    "description": "SMILES to Linker Name mapping...",
    "total_entries": 46,
    "mapping": {
      "C1(=CC=C(C=C1)C(=O)O)C(=O)O": {
        "linker_name": "H₂BDC",
        "price_eur_per_g": 0.0215,
        "source": "Linker1"
      },
      ...
    }
  }
  ```

---

### 2. API Analisis & Prediksi

#### **POST /analyze**
Endpoint utama yang memproses form data secara komprehensif untuk memprediksi kapasitas kerja hidrogen (gravimetrik & volumetrik), kelayakan target DOE, estimasi biaya sintesis MOF, biaya penyimpanan hidrogen, serta energi reaksi (sensible heat, stirrer, dll.).
* **Content-Type**: `multipart/form-data`
* **Request Parameters (Form)**:
  * `density` (string, default: "0.8"): Densitas kristal MOF ($g/cm^3$)
  * `pv` (string, default: "1.2"): Pore Volume ($cm^3/g$)
  * `gsa` (string, default: "3000"): Gravimetric Surface Area ($m^2/g$)
  * `vsa` (string, default: "1500"): Volumetric Surface Area ($m^2/cm^3$)
  * `lcd` (string, default: "12.1"): Largest Cavity Diameter ($Å$)
  * `pld` (string, default: "8"): Pore Limiting Diameter ($Å$)
  * `vf` (string, default: "0.5"): Void Fraction
  * `metal_name` (string): Nama logam dari database (misal: `Zn(NO₃)₂·6H₂O`)
  * `metal_mass` (string): Massa logam precursor ($mg$)
  * `linker_name` (string): Nama linker (misal: `2-Methylimidazole`)
  * `smiles` (string): SMILES linker (misal: `CC1=NC=CN1`)
  * `linker_mass` (string): Massa linker ($mg$)
  * `solvent_name` (string): Nama solvent (misal: `DMF`)
  * `solvent_volume` (string): Volume solvent ($mL$)
  * `modulator_name` (string): Nama modulator ($mL$)
  * `modulator_volume` (string): Volume modulator ($mL$)
  * `product_mass` (string): Massa produk MOF yang diperoleh ($mg$)
  * `reaction_time` (string): Durasi reaksi ($jam$)
  * `temperature` (string): Suhu reaksi ($^\circ C$)
* **Response**: `200 OK`
  ```json
  {
    "status": "success",
    "results": {
      "gravimetric_h2": 5.827,
      "volumetric_h2": 44.677,
      "doe_feasible": true,
      "mof_cost": 150.25,
      "mof_cost_ok": true,
      "storage_cost": 12.35,
      ...
    }
  }
  ```

#### **POST /api/feasibility**
Endpoint cepat untuk menghitung working capacity penyimpanan hidrogen (gravimetrik & volumetrik) berdasarkan struktur geometri MOF.
* **Content-Type**: `application/json`
* **JSON Body**:
  * `p` (float): Tekanan operasi (*bar*)
  * `gsa` (float): Gravimetric Surface Area ($m^2/g$)
  * `vsa` (float): Volumetric Surface Area ($m^2/cm^3$)
  * `vf` (float): Void Fraction
  * `pv` (float): Pore Volume ($cm^3/g$)
  * `lcd` (float): Largest Cavity Diameter ($Å$)
  * `pld` (float): Pore Limiting Diameter ($Å$)
* **Response**: `200 OK`
  ```json
  {
    "status": "success",
    "gravimetric_wc": 5.82,
    "volumetric_wc": 44.67,
    "is_feasible": true,
    "thresholds": {
      "gravimetric": 5.5,
      "volumetric": 40.0
    }
  }
  ```

#### **POST /api/economic**
Endpoint cepat untuk melakukan perhitungan biaya sintesis MOF ($USD/kg$), biaya penyimpanan hidrogen ($USD/kg\ H_2$), serta energi panas sensible ($q\_energy$) dan kehilangan panas ($q\_loss$).
* **Content-Type**: `application/json`
* **JSON Body**:
  * `metal_name` (string): Nama logam precursor
  * `linker_name` (string): Nama linker
  * `reaction_time` (float): Waktu reaksi dalam jam
  * `temperature` (float): Temperatur reaksi dalam $^\circ C$
  * `smiles` (string): SMILES linker
  * `gravimetric_wc` (float): Kapasitas gravimetrik (default: 5.0)
  * `product_mass_mg` (float): Massa produk yang terbentuk ($mg$)
  * `metal_mass_mg` (float): Massa logam ($mg$)
  * `linker_mass_mg` (float): Massa linker ($mg$)
  * `solvent_name` (string): Nama pelarut
  * `solvent_volume_ml` (float): Volume pelarut ($mL$)
  * `additive_name` (string): Nama aditif
  * `additive_volume_ml` (float): Volume aditif ($mL$)
  * `modulator_name` (string): Nama modulator
  * `modulator_volume_ml` (float): Volume modulator ($mL$)
* **Response**: `200 OK`
  ```json
  {
    "status": "success",
    "mof_cost_usd_per_kg": 254.30,
    "storage_cost_usd_per_kg_h2": 15.42,
    "q_energy_mj": 1.25,
    "q_loss_mj": 0.85,
    "is_feasible": true,
    ...
  }
  ```

---

### 3. API Analisis Struktur (CIF)

#### **POST /api/structure**
Melakukan analisis mendalam file geometri `.cif`.
* Mem-parsing file CIF untuk mendapatkan formula kimia dan cell parameters.
* Memisahkan atom SBU (Metal Cluster) dari Organic Linker.
* Melakukan optimasi geometri linker via xTB (jika tersedia) dan menghitung energi deformasi $\Delta E$ (deformasi konformasi linker) dan RMSD distorsi geometri (menggunakan algoritma alignment Kabsch).
* Menghasilkan skor stabilitas termodinamika.
* Mengekspor data atom 3D untuk rendering visualizer.
* **Content-Type**: `multipart/form-data`
* **Request Parameters**:
  * `file`: File `.cif` (UploadFile)
* **Response**: `200 OK`
  ```json
  {
    "status": "success",
    "formula": "C48H24N12O24Zn6",
    "n_atoms": 114,
    "n_sbu_atoms": 54,
    "n_linker_atoms": 60,
    "delta_e": 0.0,
    "rmsd": 0.0,
    "stability_score": 85.0,
    "stability_status": "Sangat stabil",
    "is_feasible": true,
    "structure_3d": {
      "atoms": [
        {"symbol": "Zn", "x": 8.446, "y": 8.439, "z": 12.656},
        ...
      ],
      "n_atoms": 114
    },
    "cell_params": {
      "a": 16.892,
      "b": 16.879,
      "c": 16.915,
      "alpha": 89.95,
      "beta": 89.98,
      "gamma": 90.08
    },
    "xtb_available": false
  }
  ```

#### **POST /api/structure/3d-view**
Mendapatkan koordinat mentah 3D atom dari file `.cif` untuk kebutuhan rendering visual di frontend (misal 3Dmol.js atau NGL).
* **Content-Type**: `multipart/form-data`
* **Request Parameters**:
  * `file`: File `.cif` (UploadFile)
* **Response**: `200 OK`
  ```json
  {
    "status": "success",
    "cif_content": "data_global\n...",
    "structure_3d": {
      "atoms": [ ... ],
      "n_atoms": 114
    },
    "formula": "C48H24N12O24Zn6",
    "cell_params": { ... }
  }
  ```

---

### 4. API Visualisasi

#### **GET /visualize/doe-scatter**
* **Response**: `200 OK`
  ```json
  {"message": "DOE scatter plot data will be available here."}
  ```

#### **GET /visualize/correlation**
* **Response**: `200 OK`
  ```json
  {"message": "Correlation heatmap data will be available here."}
  ```

---

## Contoh Pengujian API Menggunakan cURL

Gunakan perintah cURL berikut di terminal Anda untuk menguji endpoint ketika server lokal aktif (`http://127.0.0.1:8000`).

### 1. Cek Server Status (Root)
```bash
curl -X GET "http://127.0.0.1:8000/"
```

### 2. Mendapatkan Database Harga Bahan
```bash
curl -X GET "http://127.0.0.1:8000/get-prices"
```

### 3. Mendapatkan Mapping SMILES Linker
```bash
curl -X GET "http://127.0.0.1:8000/get-smiles-mapping"
```

### 4. Pengujian Prediksi Geometri (Feasibility Analysis)
```bash
curl -X POST "http://127.0.0.1:8000/api/feasibility" \
     -H "Content-Type: application/json" \
     -d '{
       "p": 5.8,
       "gsa": 3200.0,
       "vsa": 1600.0,
       "vf": 0.65,
       "pv": 1.25,
       "lcd": 12.1,
       "pld": 8.0
     }'
```

### 5. Pengujian Biaya dan Energi (Economic Analysis)
```bash
curl -X POST "http://127.0.0.1:8000/api/economic" \
     -H "Content-Type: application/json" \
     -d '{
       "metal_name": "Zn(NO3)2·6H2O",
       "linker_name": "2-Methylimidazole",
       "reaction_time": 24.0,
       "temperature": 120.0,
       "smiles": "CC1=NC=CN1",
       "gravimetric_wc": 5.82,
       "product_mass_mg": 50.0,
       "metal_mass_mg": 100.0,
       "linker_mass_mg": 50.0,
       "solvent_name": "DMF",
       "solvent_volume_ml": 10.0,
       "additive_name": "-",
       "additive_volume_ml": 0.0,
       "modulator_name": "-",
       "modulator_volume_ml": 0.0
     }'
```

### 6. Pengujian Analisis Komprehensif (POST /analyze)
```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
     -F "pv=1.2" \
     -F "gsa=3000" \
     -F "vsa=1500" \
     -F "lcd=12.1" \
     -F "pld=8" \
     -F "vf=0.5" \
     -F "density=0.8" \
     -F "metal_name=Zn(NO3)2·6H2O" \
     -F "metal_mass=100" \
     -F "linker_name=2-Methylimidazole" \
     -F "linker_mass=50" \
     -F "smiles=CC1=NC=CN1" \
     -F "solvent_name=DMF" \
     -F "solvent_volume=10" \
     -F "product_mass=50" \
     -F "reaction_time=24" \
     -F "temperature=120"
```

### Pengujian Analisis Struktur dengan `zif-8-f.cif`

File CIF contoh **`zif-8-f.cif`** berada di folder `backend/uploads/zif-8-f.cif`. Pastikan Anda menjalankan perintah ini dari folder `backend/` agar file path `./uploads/zif-8-f.cif` terdeteksi secara tepat.

#### 7. Analisis Struktur CIF (`/api/structure`)
Perintah ini mengunggah file `zif-8-f.cif` untuk dianalisis (ekstraksi atom logam/linker, formula, parameter cell, dan skor stabilitas):
```bash
curl -X POST "http://127.0.0.1:8000/api/structure" \
     -H "Accept: application/json" \
     -F "file=@uploads/zif-8-f.cif"
```

#### 8. Visualisasi 3D CIF (`/api/structure/3d-view`)
Perintah ini mengunggah file `zif-8-f.cif` dan meminta data JSON representasi koordinat 3D untuk visualizer:
```bash
curl -X POST "http://127.0.0.1:8000/api/structure/3d-view" \
     -H "Accept: application/json" \
     -F "file=@uploads/zif-8-f.cif"
```

---
*Catatan: Pada OS Windows PowerShell, jika perintah `-F "file=@..."` mengalami kendala, Anda dapat mengganti path file menjadi path absolut atau menggunakan CMD standard.*
