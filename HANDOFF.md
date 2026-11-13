# HANDOFF.md

Dokumen serah terima dan panduan kerja tim untuk **Estimator Harga Mobil Bekas**.
Dokumen ini dibaca pertama kali oleh setiap anggota sebelum mulai mengerjakan bagian mereka.

**Status:** DRAFT v0.1

---

## 1. Ringkasan Status

| Bagian | Pemilik | Status |
|---|---|---|
| Dokumen (ARCHITECTURE, PRD, DESIGN, HANDOFF) | Semua, dikoordinasi Dokumentasi & QA | Draft v0.1 |
| EDA & cleaning | Data & EDA | Belum mulai |
| Pipeline & model | ML Modeling | Belum mulai |
| Backend API | Backend (lead) | Belum mulai |
| Landing page & layout | Frontend Layout | Belum mulai |
| Logika form & Fetch | Frontend Integrasi | Belum mulai |
| Test case & laporan | Dokumentasi & QA | Belum mulai |

Ganti "Belum mulai" menjadi "Berjalan", "Review", atau "Selesai" setiap minggu.

---

## 2. Pembagian Kerja (6 Anggota)

Setiap anggota memiliki satu area utama. Area lain boleh disentuh, tetapi harus lewat pull request dan diketahui pemilik area tersebut.

| No | Peran | Tanggung jawab utama | File yang dimiliki |
|---|---|---|---|
| 1 | **Backend (lead)** | API FastAPI, validasi Pydantic, pemuatan model, penanganan error, `requirements.txt`, test API | `backend/app.py`, `backend/schemas.py`, `backend/config.py`, `tests/test_api.py`, `requirements.txt` |
| 2 | **Data & EDA** | Eksplorasi data, cleaning, aturan outlier, daftar kategori bersih, data dictionary | `training/01_eda.ipynb`, `data/cardekho_clean.csv`, `DATASET_*.md` |
| 3 | **ML Modeling** | Pipeline, perbandingan algoritma, 5-fold CV, GridSearchCV, export `.joblib` | `training/train.py`, `models/model_kelompok_X.joblib`, `training/02_modeling.ipynb` |
| 4 | **Frontend Layout** | Landing page, navbar, hero, kartu, responsif, styling | `frontend/index.html`, `frontend/style.css` |
| 5 | **Frontend Integrasi** | Logika form, validasi browser, Fetch API, render hasil dan error, dropdown dinamis | `frontend/app.js` |
| 6 | **Dokumentasi & QA** | Test case manual, screenshot, bab laporan, README, koordinasi repo | `ARCHITECTURE.md`, `PRD.md`, `DESIGN.md`, `HANDOFF.md`, `README.md`, `laporan/`, `tests/` |

### 2.1 Tugas Backend (anggota 1, fokus ketua)

Ini bagian yang menjadi fokus utama. Urutan kerjanya:

1. **Siapkan kerangka proyek.** Buat `app.py`, `schemas.py`, `config.py`, dan `requirements.txt`. Pastikan `uvicorn app:app --reload` jalan walau model belum ada.
2. **Definisikan skema.** Tulis `CarInput`, `PredictionOutput`, dan `HealthOutput` dengan `Field(ge=, le=)`. Angka diambil dari ARCHITECTURE §5.3 dan harus disetujui Data & EDA sebelum dikunci.
3. **Implementasi `GET /health`.** Mengembalikan status server dan apakah model sudah termuat.
4. **Muat model saat startup.** Gunakan `lifespan` FastAPI. Jika gagal, catat error di log dan biarkan `/health` tetap merespons dengan `model_loaded: false`.
5. **Implementasi `POST /predict`.** Konversi input ke DataFrame dengan kolom sama seperti saat training, panggil `pipeline.predict`, hitung rentang dari MAE, susun respons.
6. **Penanganan error.** Terapkan tabel di ARCHITECTURE §6. Jangan pernah membocorkan traceback ke klien.
7. **Tulis test API.** Minimal 12 test case di `tests/test_api.py` (lihat §6), menggunakan `pytest` dan `TestClient`.
8. **Ekspor kontrak.** Tulis contoh request dan response di README agar frontend bisa bekerja tanpa menunggu.

Catatan koordinasi: `config.py` diisi dari hasil EDA (anggota 2). Jangan menuliskan daftar merek manual tanpa mencocokkannya dengan `cardekho_clean.csv`.

### 2.2 Urutan Ketergantungan

```
Data & EDA (2) ──▶ ML Modeling (3) ──▶ Backend (1) ──▶ Frontend Integrasi (5)
       │                                     │
       └──▶ config.py (kategori, rentang) ───┘
                                             │
Frontend Layout (4) ─────────────────────────┴──▶ Integrasi & QA (6)
```

Backend bisa mulai sejak hari pertama dengan `schemas.py` dan `config.py` yang disepakati. Model bisa diganti tanpa mengubah API selama nama fitur dan kontraknya tetap.

---

## 3. Alur Kerja (6 Langkah Modul)

Mengikuti panduan Langkah 1–6:

| Langkah | Modul | Pemilik utama | Output |
|---|---|---|---|
| 1 | Cari & EDA dataset | Data & EDA | Dataset bersih, catatan EDA |
| 2 | Preprocessing & split | Data & EDA, ML | Split train/test 80:20 |
| 3 | Training & CV pipeline | ML Modeling | Tabel perbandingan metrik, konfigurasi terbaik |
| 4 | Export joblib | ML Modeling | `model_kelompok_X.joblib` |
| 5 | REST API FastAPI | Backend | `app.py` dan kelas Pydantic |
| 6 | Integrasi frontend web | Frontend Layout & Integrasi | Halaman web yang bisa memanggil API |

Langkah 5 dan 6 bisa dikerjakan paralel setelah langkah 4 selesai. Frontend bisa mulai dengan mock response sebelum model final tersedia.

---

## 4. Git dan Repository

### 4.1 Struktur branch

- `main`: versi yang bisa dijalankan. Tidak boleh di-push langsung.
- `feat/<area>-<deskripsi>`: branch kerja per anggota. Contoh:
  - `feat/backend-predict-endpoint`
  - `feat/eda-cleaning`
  - `feat/ml-pipeline-cv`
  - `feat/frontend-landing`
  - `feat/frontend-fetch-form`
  - `docs/laporan-bab1`

### 4.2 Aturan

1. Setiap anggota bekerja di branch sendiri dan membuat pull request ke `main`.
2. Minimal satu anggota lain melakukan review sebelum merge. Pemilik area tidak boleh mereview pekerjaannya sendiri.
3. Pesan commit dalam format singkat: `tipe: deskripsi`. Tipe: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
   - Contoh: `feat: tambah validasi rentang vehicle_age di schemas`
4. Jangan commit file besar yang tidak perlu. File `.joblib` dibawa ke repository, tetapi dataset mentah (`cardekho_dataset.csv`) cukup disertakan jika ukurannya wajar (sekitar 1,4 MB) dan tidak melanggar lisensi.
5. `.gitignore` wajib memuat: `__pycache__/`, `venv/`, `.ipynb_checkpoints/`, `*.log`.
6. Sebelum merge, jalankan `pytest` dan pastikan `uvicorn app:app` bisa dijalankan.

### 4.3 Sinkronisasi

- Setiap pagi (atau sebelum mulai kerja), jalankan `git pull origin main` dan rebase branch.
- Jika mengubah kontrak API (nama field, bentuk response), beri tahu anggota 4 dan 5 lewat grup sebelum merge.

---

## 5. Keputusan yang Masih Terbuka

Setiap keputusan berikut harus diselesaikan dan dicatat di laporan.

| No | Keputusan | Pemilik | Batas waktu |
|---|---|---|---|
| D1 | Baris `km_driven` ekstrem (> 500.000 km): dibuang atau dipertahankan? | Data & EDA | Sebelum EDA selesai |
| D2 | Baris `seats = 0` (2 baris): dibuang? | Data & EDA | Sebelum EDA selesai |
| D3 | Kategori `Electric` (4 baris): digabung, dibuang, atau tetap? | Data & EDA | Sebelum dropdown dibuat |
| D4 | `Mercedes-AMG` dan `Mercedes-Benz`: digabung atau tidak? | Data & EDA | Sebelum dropdown dibuat |
| D5 | Transformasi log pada target `selling_price`? | ML Modeling | Setelah baseline |
| D6 | Algoritma final yang dipilih | ML Modeling | Setelah GridSearchCV |
| D7 | Format tampilan rupiah atau INR (`₹`) | Frontend Layout | Sebelum desain final |
| D8 | "Probabilitas" di panduan untuk regresi: diganti rentang? | Ketua kelompok, konfirmasi asisten | Sebelum laporan |
| D9 | Jumlah anggota: panduan menyebut 5 per kelompok, tim ini 6 orang | Ketua kelompok, konfirmasi asisten | Segera |
| D10 | Lisensi dataset Kaggle | Dokumentasi & QA | Sebelum laporan |
| D11 | Persetujuan dataset dari Asisten Praktikum | Ketua kelompok | Segera |
| D12 | Rentang validasi final (`ge`/`le`) | Backend & Data & EDA | Sebelum kontrak API dikunci |

---

## 6. Test Case Minimal (12)

Panduan mewajibkan minimal 12 test case yang mencakup input valid, input di luar batas atau tidak valid, field hilang, dan respons API. Berikut rancangannya:

| ID | Skenario | Input | Hasil yang diharapkan |
|---|---|---|---|
| TC01 | Health check | `GET /health` | 200, `status: ok`, `model_loaded: true` |
| TC02 | Prediksi valid | Payload contoh lengkap | 200, `predicted_price` > 0, ada `range_low` dan `range_high` |
| TC03 | Usia di luar batas | `vehicle_age: 40` | 422, detail menunjuk `vehicle_age` |
| TC04 | Jarak tempuh negatif | `km_driven: -1` | 422 |
| TC05 | Konsumsi BBM di bawah minimum | `mileage: 2` | 422 |
| TC06 | Kapasitas mesin di atas maksimum | `engine: 9000` | 422 |
| TC07 | Jumlah kursi 0 | `seats: 0` | 422 |
| TC08 | Field hilang | Tanpa `brand` | 422 |
| TC09 | Merek tidak dikenal | `brand: "Tesla"` | 422 |
| TC10 | Body bukan JSON | Teks biasa | 400 atau 422 |
| TC11 | Model belum termuat | Simulasi startup gagal | 503 pada `/predict` |
| TC12 | Respons memiliki struktur lengkap | Payload valid | Semua field di `PredictionOutput` terisi dengan tipe yang benar |

Pelaksana: Backend menulis TC01–TC12 sebagai pytest. Dokumentasi & QA menyalin hasilnya ke tabel laporan dan menambahkan uji manual di browser (desktop dan mobile).

---

## 7. Rencana Laporan (ringkas)

Laporan dikerjakan setelah sistem berjalan. Struktur mengikuti panduan Bagian E:

1. Cover dan identitas kelompok.
2. Daftar anggota dan pembagian peran (dari §2).
3. BAB I Pendahuluan: latar belakang, rincian dataset, tujuan.
4. BAB II Metodologi dan pemodelan: preprocessing, split, tabel metrik, hyperparameter terbaik, bukti export dan impor joblib.
5. BAB III Arsitektur dan implementasi: diagram dari ARCHITECTURE §2, potongan kode `app.py`, `schemas.py`, dan `app.js`.
6. BAB IV Pengujian: tabel TC01–TC12, screenshot desktop dan mobile, screenshot prediksi sukses dan error.
7. BAB V Kesimpulan dan ethical use: ringkasan, keterbatasan dataset dan model, disclaimer.
8. Lampiran: tautan repository GitHub yang memuat source code, `.joblib`, dan `requirements.txt`.

---

## 8. Definisi Selesai (Definition of Done)

Sebuah bagian dianggap selesai jika:

- [ ] Kode sudah di-merge ke `main` lewat pull request yang direview.
- [ ] Bagian yang bergantung padanya bisa berjalan tanpa perubahan lokal.
- [ ] Jika menyentuh API, `pytest` lulus dan `uvicorn app:app` berjalan.
- [ ] Jika menyentuh tampilan, sudah dicek di layar 375px dan 1280px.
- [ ] Dokumentasi terkait sudah diperbarui (ARCHITECTURE, DESIGN, atau README).
- [ ] Keputusan terbuka yang terkait sudah dicatat di §5.

---

## 9. Cara Menjalankan (untuk anggota baru)

```bash
git clone <url-repo>
cd web_price_estimator
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn app:app --reload
```

Buka `http://127.0.0.1:8000` untuk halaman web dan `http://127.0.0.1:8000/docs` untuk dokumentasi interaktif FastAPI.

Jalankan test (dari root proyek):

```bash
pytest tests/
```

Menjalankan ulang training (dari root proyek):

```bash
python training/train.py
```

## 10. Catatan Serah Terima

Bagian ini diisi setiap kali ada perpindahan pemilik area:

| Tanggal | Dari | Ke | Catatan |
|---|---|---|---|
| - | - | - | - |
