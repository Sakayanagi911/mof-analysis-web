# Repositori Binari xTB (Windows & Linux)

Folder ini digunakan untuk menyimpan file binari Grimme **xTB (v6.7.1)** agar aplikasi backend dapat berjalan secara portabel di lingkungan Windows maupun Linux tanpa mengharuskan instalasi xTB di tingkat sistem global (`PATH`).

## Struktur Direktori

Pastikan file binari diletakkan sesuai dengan struktur berikut:

```text
backend/bin/xtb/
├── windows/
│   ├── bin/
│   │   ├── xtb.exe          <-- Letakkan file xtb.exe Windows di sini
│   │   └── (file pendukung dll jika ada)
│   └── share/
│       └── xtb/
│           ├── gfn2-xtb.param  <-- Letakkan parameter GFN2-xTB di sini
│           └── (parameter lainnya)
│
├── linux/
│   ├── bin/
│   │   ├── xtb              <-- Letakkan executable file xtb Linux di sini
│   │   └── (file pendukung .so jika ada)
│   └── share/
│       └── xtb/
│           ├── gfn2-xtb.param  <-- Letakkan parameter GFN2-xTB di sini
│           └── (parameter lainnya)
└── README.md
```

## Langkah Mendapatkan Binari Resmi

### 1. Untuk Windows (x86_64)
*   Unduh arsip kompilasi Windows dari rilis resmi Grimme xTB:
    *   Tautan: `https://github.com/grimme-lab/xtb/releases/download/v6.7.1/xtb-6.7.1-windows-x86_64.zip` (atau versi windows resmi lainnya).
*   Ekstrak file zip tersebut.
*   Salin isi folder `bin/` hasil ekstrak ke `backend/bin/xtb/windows/bin/`.
*   Salin isi folder `share/xtb/` hasil ekstrak ke `backend/bin/xtb/windows/share/xtb/`.

### 2. Untuk Linux (x86_64)
*   Unduh arsip Linux dari rilis resmi Grimme xTB:
    *   Tautan: `https://github.com/grimme-lab/xtb/releases/download/v6.7.1/xtb-6.7.1-linux-x86_64.tar.xz`
*   Ekstrak arsip tersebut.
*   Salin isi folder `bin/` hasil ekstrak ke `backend/bin/xtb/linux/bin/`.
*   Salin isi folder `share/xtb/` hasil ekstrak ke `backend/bin/xtb/linux/share/xtb/`.
*   Pastikan binari linux diberi hak akses eksekusi (`chmod +x backend/bin/xtb/linux/bin/xtb`).

## Cara Kerja Pendeteksian Otomatis di Backend

Di dalam modul `backend/services/xtb_runner.py`, backend akan mendeteksi sistem operasi menggunakan pustaka Python `platform` dan mencari executable lokal ini terlebih dahulu:

1.  **Jika Windows**: Backend mencari `backend/bin/xtb/windows/bin/xtb.exe`.
    *   Jika ada, ia akan mengatur environment variable `XTBPATH` secara dinamis ke folder `backend/bin/xtb/windows/share/xtb`.
2.  **Jika Linux**: Backend mencari `backend/bin/xtb/linux/bin/xtb`.
    *   Jika ada, ia akan mengatur environment variable `XTBPATH` secara dinamis ke folder `backend/bin/xtb/linux/share/xtb`.
3.  **Fallback**: Jika tidak ditemukan binari lokal di repositori, backend akan mencoba memanggil `xtb` secara global dari `PATH` sistem operasi.
