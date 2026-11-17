# ARCHITECTURE.md

Dokumen arsitektur sistem **Estimator Harga Mobil Bekas** (Tugas Besar Praktikum Pembelajaran Mesin, Prodi S1 Sistem Informasi, Universitas Bengkulu).

Status: **Implemented baseline**. Dokumen ini menggambarkan implementasi yang berjalan pada branch `main`.

---

## 1. Ringkasan

Sistem berupa aplikasi web prediksi harga jual mobil bekas. Pengguna mengisi form spesifikasi mobil, lalu browser mengirim data ke REST API berbasis FastAPI. API memvalidasi input, memanggil pipeline machine learning yang sudah dilatih (disimpan sebagai file `.joblib`), dan mengembalikan estimasi harga beserta rentang error model.

Tipe tugas ML: **Regresi kontinu** (prediksi harga).
Dataset: `cardekho_dataset.csv` (CarDekho, pasar India, harga dalam INR).

---

## 2. Diagram Arsitektur

```
┌──────────────┐   submit form    ┌──────────────────┐   fetch POST /predict   ┌────────────────────┐
│    User      │ ───────────────▶ │  Form HTML       │ ──────────────────────▶ │  FastAPI Backend   │
│  (Browser)   │                  │  (index.html)    │   JSON payload          │  (app.py)          │
└──────────────┘                  └──────────────────┘                         │                    │
       ▲                                   ▲                                   │  1. Pydantic       │
       │                                   │                                   │     validasi       │
       │ tampilkan hasil                   │ render hasil / error              │  2. Konversi ke    │
       │                                   │                                   │     DataFrame      │
┌──────────────────┐   JSON response       │                                   │  3. Joblib model   │
│  Display Result  │ ◀─────────────────────┴────────────────────────────────── │     .predict()     │
│  (app.js)        │                                                           │  4. Susun response │
└──────────────────┘                                                           └─────────┬──────────┘
                                                                                        │ load sekali saat startup
                                                                                        ▼
                                                                              ┌────────────────────┐
                                                                              │ models/            │
                                                                              │ model_kelompok_X   │
                                                                              │ .joblib            │
                                                                              │ (Pipeline lengkap) │
                                                                              └────────────────────┘
```

Alur sesuai panduan: **User → Form HTML → Fetch API → FastAPI Backend → Joblib Model → Display Result**.

---

## 3. Struktur Folder

Struktur mengikuti layout proyek yang sudah dibuat di komputer pengembang. Server (`backend/`) dan antarmuka (`frontend/`) dipisah menjadi dua folder, sedangkan model, script training, dan data berada di folder terpisah.

```
car_price_estimator/
├── .git/                           # Repository Git (dibuat oleh git init)
├── .gitignore                      # Mengabaikan venv/, __pycache__/, .pytest_cache/, dll.
├── README.md                       # Cara menjalankan proyek
├── requirements.txt                # Versi library (wajib sama dengan saat training)
├── ARCHITECTURE.md                 # Dokumen arsitektur (dokumen ini)
├── PRD.md                          # Product requirements
├── DESIGN.md                       # Desain antarmuka
├── HANDOFF.md                      # Pembagian kerja & panduan tim
├── DATASET_*.md                    # Catatan dataset (lihat catatan di bawah)
├── backend/                        # Server FastAPI
│   ├── app.py                      # Entry point FastAPI (endpoint, startup load model)
│   ├── schemas.py                  # Kelas Pydantic (BaseModel) untuk validasi input & output
│   └── config.py                   # Konstanta: path model, rentang validasi, daftar kategori
├── frontend/                       # Antarmuka web (HTML5, CSS3, JavaScript Fetch)
│   ├── index.html                  # Landing page + halaman prediksi
│   ├── style.css                   # Styling (CSS3, tanpa framework)
│   └── app.js                      # Logika form, fetch API, render hasil
├── training/                       # Pipeline machine learning
│   ├── train.py                    # Script training: cleaning, pipeline, CV, GridSearch, export
│   ├── 01_EDA.ipynb                # Notebook EDA
│   ├── 02_modelling.ipynb          # Notebook modelling lama/pendukung
│   └── train.py                    # Pipeline training yang dipakai sistem
├── models/                         # Hasil export model
│   └── model_kelompok_X.joblib     # Pipeline final (preprocessing + model)
├── data/                           # Dataset
│   ├── cardekho_dataset.csv        # Dataset mentah (tidak diubah)
│   └── cardekho_clean.csv          # Hasil cleaning
├── tests/                          # Test API
│   └── test_api.py                 # 13 test API
├── arsip_sintetis/                 # Arsip data sintetis lama (tidak dipakai di kode utama)
└── venv/                           # Virtual environment lokal (tidak di-commit)
```

Catatan struktur:
- **Frontend dipisah dari backend.** `backend/app.py` melayani file dari `../frontend/` sebagai file statis. Path ini dihitung relatif terhadap lokasi `app.py`, sehingga server tidak bergantung pada direktori kerja saat dijalankan.
- Frontend tetap berada di `frontend/` dan dilayani `backend/app.py` melalui `StaticFiles`.
- **`models/` dibaca oleh `backend/config.py`** sebagai path relatif terhadap root proyek. Pastikan training menulis ke folder yang sama.
- **`venv/` dan cache lokal tidak di-commit.** Dataset dan artefak model aktif disimpan agar clone siap dijalankan.

**Catatan dataset.** Dataset yang dipakai adalah `data/cardekho_dataset.csv`, bukan dataset pembelajaran mahasiswa. Lisensi dan izin distribusi dataset tetap perlu dicatat untuk laporan.

## 4. Komponen Backend

### 4.1 `app.py`
- Membuat instance FastAPI dan memuat model `.joblib` **sekali saat startup**, bukan setiap request.
- Menyajikan file statis dari folder `frontend/` pada route `/`.
- Endpoint:
  - `GET /health`: cek status server dan apakah model sudah termuat.
  - `POST /predict`: menerima payload JSON, memvalidasi lewat Pydantic, memprediksi harga.
  - `GET /options`: menyediakan kategori frontend dan pasangan merek-model.
- Menangani error secara eksplisit (lihat bagian 6).

### 4.2 `schemas.py`
- `CarInput` (BaseModel): skema input dengan `Field(ge=..., le=...)` untuk setiap fitur numerik dan validator untuk kategorikal.
- `PredictionOutput` (BaseModel): skema response.
- `HealthOutput` (BaseModel): skema response `/health`.

### 4.3 `config.py`
- Path model dan dataset.
- Path konfigurasi kurs lokal `backend/exchange_rate.json` (INR→IDR).
- Daftar kategori yang valid (`BRANDS`, `FUEL_TYPES`, `SELLER_TYPES`, `TRANSMISSION_TYPES`) yang diambil dari data setelah cleaning, sehingga dropdown di frontend dan validasi backend selalu sama.
- Rentang validasi numerik (lihat bagian 5).

### 4.4 `training/train.py`
Menjalankan seluruh alur modeling dari panduan Langkah 1 sampai 4 secara terprogram, sehingga hasilnya bisa diulang.

---

## 5. Kontrak API

### 5.1 `GET /health`

Response 200:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_version": "model_kelompok_X.joblib"
}
```

### 5.2 `POST /predict`

Request body:
```json
{
  "brand": "Maruti",
  "model": "Alto",
  "vehicle_age": 9,
  "km_driven": 120000,
  "seller_type": "Individual",
  "fuel_type": "Petrol",
  "transmission_type": "Manual",
  "mileage": 19.7,
  "engine": 796,
  "max_power": 46.3,
  "seats": 5
}
```

Response 200:
```json
{
  "predicted_price": 215000,
  "currency": "INR",
  "range_low": 180000,
  "range_high": 250000,
  "predicted_price_idr": 40903750,
  "range_low_idr": 34245000,
  "range_high_idr": 47562500,
  "exchange_rate": 190.25,
  "exchange_rate_date": "2026-11-15",
  "range_note": "Rentang ± MAE dari data uji, bukan interval kepercayaan statistik",
  "model_name": "Random Forest",
  "model_version": "model_kelompok_X.joblib"
}
```

### 5.3 Rentang validasi input

| Field | Tipe | Batas | Sumber batas |
|---|---|---|---|
| `vehicle_age` | int | `ge=0, le=30` | Maks di data: 29 |
| `km_driven` | int | `ge=0, le=1_000_000` | Batas training dan API saat ini |
| `mileage` | float | `ge=4, le=40` | Data: 4–33,5. Perlu dicek satuan CNG/LPG |
| `engine` | int | `ge=500, le=7000` | Data: 793–6.592 cc |
| `max_power` | float | `ge=30, le=700` | Data: 38–626 bhp |
| `seats` | int | `ge=2, le=9` | Data: 0–9, nilai 0 dianggap tidak valid |

Kategorikal (`brand`, `model`, `seller_type`, `fuel_type`, `transmission_type`) divalidasi terhadap daftar di `config.py`. Nilai di luar daftar mengembalikan 422.

---

## 6. Penanganan Error

| Kondisi | HTTP | Pesan |
|---|---|---|
| JSON valid, tetapi field hilang | 422 | Pydantic default |
| Nilai di luar rentang `ge`/`le` | 422 | Pydantic default, detail menunjuk field |
| Kategori tidak dikenal | 422 | Validator custom |
| Body bukan JSON atau payload tidak valid | 422 | Detail validasi FastAPI/Pydantic |
| Model gagal dimuat saat startup | 503 pada `/predict` | "Model belum siap" |
| Konfigurasi kurs lokal tidak tersedia atau tidak valid | 503 pada `/predict` | "Kurs konversi belum siap" |
| Error tak terduga saat prediksi | 500 | "Terjadi kesalahan internal" (detail tidak dibocorkan ke klien) |

Frontend wajib menampilkan pesan error ini secara ramah, bukan respons mentah.

---

## 7. Pipeline Machine Learning

Pipeline disusun dengan `ColumnTransformer` dan `Pipeline` agar preprocessing dipelajari hanya dari data training (menghindari data leakage).

```python
preprocessor = ColumnTransformer(
    transformers=[
        ("num", Pipeline([
            ("scale", StandardScaler()),
        ]), NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ]
)

best_pipeline = Pipeline([
    ("preprocess", preprocessor),
    ("model", <estimator terbaik dari GridSearchCV>),
])
```

Fitur input (11):
- Numerik (6): `vehicle_age`, `km_driven`, `mileage`, `engine`, `max_power`, `seats`
- Kategorikal (5): `brand`, `model`, `seller_type`, `fuel_type`, `transmission_type`
- Dibuang: `car_name` (redundan dengan `brand` + `model`), `Unnamed: 0` (index)

Target: `selling_price`. Pipeline aktif memakai transformasi target `log1p` dan mengembalikan prediksi ke skala harga asli.

Evaluasi:
- Validasi silang: **KFold 5-fold dengan shuffle** (stratified hanya untuk klasifikasi, sesuai panduan).
- Algoritma pembanding: Linear Regression, Random Forest Regressor, dan Gradient Boosting Regressor, masing-masing diuji pada target raw dan `log1p`.
- Tuning: `GridSearchCV` pada kandidat terbaik; konfigurasi model aktif adalah Random Forest `n_estimators=100`, `max_depth=20` dengan target `log1p`.
- Metrik: MAE, RMSE, R².
- Ekspor: `joblib.dump(best_pipeline, "models/model_kelompok_X.joblib")` setelah fit pada split training 80%; metrik dihitung pada holdout 20%.

Baseline aktif: MAE `108362.81 INR`, RMSE `617818.45 INR`, dan R² `0.7045`.

---

## 8. Frontend

- HTML5, CSS3, dan JavaScript dengan Fetch API. Tanpa framework tambahan.
- Form dikirim lewat `fetch('/predict', { method: 'POST', ... })` dengan `event.preventDefault()`, sehingga halaman tidak reload.
- Dropdown dibangun dari `GET /options`, yang berasal dari artefak opsi hasil cleaning dan dipakai untuk validasi pasangan merek-model.
- Hasil dan rentang ditampilkan dalam IDR dengan kurs/tanggal dari konfigurasi lokal; API tetap mengembalikan prediksi asli dalam INR.

---

## 9. Keamanan dan Batasan

- Tidak ada autentikasi, karena prototipe akademik dan tidak menyimpan data pengguna.
- Tidak ada penyimpanan input pengguna ke database.
- CORS tidak diaktifkan karena frontend dilayani dari origin yang sama.
- Model tidak diunduh dari internet saat runtime. File `.joblib` dibawa bersama repository.

---

## 10. Versi dan Reproducibility

- `requirements.txt` memuat versi eksak library: `fastapi`, `uvicorn`, `pydantic`, `scikit-learn`, `pandas`, `numpy`, `joblib`.
- Versi scikit-learn **harus sama** antara training dan serving, karena joblib bergantung pada versi tersebut.
- Seed tetap (`random_state=42`) di semua proses acak.
- Perintah menjalankan (dari root proyek):
  ```bash
  pip install -r requirements.txt
  cd backend
  uvicorn app:app --reload
  ```
