# PRD.md: Product Requirements Document

**Produk:** Estimator Harga Mobil Bekas
**Konteks:** Tugas Besar Praktikum Pembelajaran Mesin, Prodi S1 Sistem Informasi, Universitas Bengkulu
**Kelompok:** `[NOMOR KELOMPOK]`
**Status:** DRAFT v0.1

---

## 1. Latar Belakang

Harga mobil bekas dipengaruhi banyak faktor: merek, model, usia, jarak tempuh, jenis bahan bakar, transmisi, dan spesifikasi mesin. Penjual sering kesulitan menentukan harga yang wajar, dan pembeli sulit menilai apakah sebuah harga masuk akal.

Proyek ini membangun prototipe edukatif yang memperlihatkan bagaimana model machine learning regresi dapat diubah menjadi layanan web yang bisa digunakan. Sistem ini **bukan** penentu harga resmi dan tidak boleh dijadikan dasar keputusan jual beli nyata.

---

## 2. Tujuan

1. Membangun pipeline machine learning regresi yang lengkap, mulai dari EDA sampai model yang siap dipakai.
2. Menyajikan model sebagai REST API (FastAPI) yang tervalidasi dengan Pydantic.
3. Menyediakan antarmuka web yang memungkinkan pengguna memasukkan spesifikasi mobil dan melihat estimasi harga tanpa reload halaman.
4. Menampilkan disclaimer akademik agar sistem tidak disalahartikan sebagai penilai profesional.

---

## 3. Pengguna

| Pengguna | Kebutuhan | Yang dilihat |
|---|---|---|
| Penguji / asisten praktikum | Memverifikasi bahwa sistem berjalan dan metodologinya benar | Landing page, halaman prediksi, dokumentasi, source code |
| Pengunjung umum (simulasi) | Mencoba memperkirakan harga mobil bekas berdasarkan spesifikasi | Form prediksi dan hasil estimasi |
| Anggota kelompok | Mengembangkan dan menguji sistem | ARCHITECTURE.md, HANDOFF.md, DESIGN.md |

Catatan: pengguna utama adalah penguji akademik. Desain tidak perlu dioptimalkan untuk penjual atau pembeli sungguhan.

---

## 4. Ruang Lingkup

### 4.1 Halaman

**A. Landing page (`/`)**

Halaman pembuka yang menjelaskan tujuan proyek dan mengarahkan pengguna ke halaman prediksi. Isi minimal:

- Navigasi: logo proyek, tautan "Beranda", "Prediksi Harga", "Tentang".
- Hero: judul singkat, deskripsi satu-dua kalimat, tombol utama "Coba Prediksi".
- Kartu fitur (3 kartu): Analisis data, Model machine learning, Estimasi real-time.
- Bagian "Cara Kerja" (3 langkah): isi spesifikasi, sistem memproses, lihat estimasi.
- Contoh hasil statis (opsional, dari data uji): satu contoh mobil dengan harga prediksi.
- Footer berisi disclaimer akademik.

**B. Halaman prediksi (`/#predict` atau bagian di halaman yang sama)**

Form input, tombol "Estimasi Harga", area hasil, dan area error.

### 4.2 Fitur Wajib

| ID | Fitur | Prioritas | Catatan |
|---|---|---|---|
| F1 | Form input 11 fitur (dropdown dan input angka) | Wajib | Sesuai fitur input di ARCHITECTURE.md |
| F2 | Validasi input di sisi browser (atribut `required`, `min`, `max`) | Wajib | Validasi utama tetap di backend |
| F3 | Pengiriman data ke `POST /predict` via Fetch API tanpa reload | Wajib | Panduan: wajib AJAX/Fetch |
| F4 | Tampilan estimasi harga dalam format rupiah atau INR | Wajib | Lihat catatan mata uang di bagian 8 |
| F5 | Tampilan rentang estimasi (range low–high) | Wajib | Pengganti "probabilitas" untuk regresi, perlu konfirmasi asisten |
| F6 | Penanganan error: 422, 500, 503, dan gagal jaringan | Wajib | Pesan ramah, bukan respons mentah |
| F7 | Disclaimer akademik di halaman | Wajib | Sesuai panduan Etika & Responsible Use |
| F8 | Landing page dengan tautan ke halaman prediksi | Wajib | Sesuai kebutuhan kelompok |
| F9 | Tampilan responsif (desktop dan mobile) | Wajib | Kriteria: antarmuka responsif |
| F10 | Endpoint `GET /health` | Wajib | Panduan Langkah 5 |
| F11 | Dropdown dibangun dari daftar kategori yang sama dengan backend | Disarankan | Mencegah ketidaksesuaian |
| F12 | Contoh input cepat (tombol "isi contoh") | Opsional | Memudahkan penguji |

### 4.3 Di Luar Ruang Lingkup

- Scraping data iklan secara real-time.
- Penyimpanan riwayat prediksi atau akun pengguna.
- Prediksi untuk pasar selain India, atau untuk properti.
- Autentikasi dan otorisasi.
- Pembaruan model otomatis dari data baru.
- Aplikasi mobile native.

---

## 5. Alur Pengguna

```
Buka landing page
   │
   ├─▶ Baca penjelasan & disclaimer
   │
   └─▶ Klik "Coba Prediksi"
          │
          ▼
     Isi form (11 fitur)
          │
          ▼
     Klik "Estimasi Harga"
          │
          ├─ Input tidak valid  ──▶ Pesan error di field terkait
          ├─ Server error       ──▶ Pesan error umum, form tetap terisi
          └─ Sukses             ──▶ Tampilkan harga, rentang, dan disclaimer
```

Form tidak dikosongkan setelah error agar pengguna bisa memperbaiki input.

---

## 6. Kebutuhan Non-Fungsional

| Aspek | Target |
|---|---|
| Waktu respons `/predict` | Di bawah 500 ms untuk satu permintaan pada laptop standar |
| Reproducibility | Seluruh proses dapat dijalankan ulang dengan `requirements.txt` dan `train.py` |
| Aksesibilitas | Label untuk setiap field, kontras teks memadai, navigasi keyboard |
| Kompatibilitas browser | Chrome dan Firefox versi terbaru, Safari untuk iOS |
| Keamanan | Tidak ada data pribadi yang disimpan. Input divalidasi di backend |

Angka target pada tabel ini adalah **asumsi awal**. Kelompok perlu mengukurnya dan memperbarui dokumen.

---

## 7. Metrik Keberhasilan

Target metrik dibiarkan terbuka sampai baseline model selesai. Kriteria kualitatif:

- Pipeline berjalan dari awal sampai akhir tanpa error.
- Tidak ada data leakage (preprocessing di dalam pipeline, split dilakukan sebelum fit).
- Perbandingan minimal 2–3 algoritma dengan 5-fold CV, dilaporkan dalam tabel.
- Seluruh 12 test case lulus.
- Repository bisa dijalankan ulang oleh orang lain mengikuti README.

Target angka `[ISI SETELAH BASELINE]`:
- MAE: `___`
- RMSE: `___`
- R²: `___`

---

## 8. Asumsi dan Batasan

- **Dataset.** Menggunakan `cardekho_dataset.csv` (15.411 baris, 14 kolom termasuk index). Dataset praktikum `student-por.csv` tidak digunakan, sesuai ketentuan.
- **Mata uang.** Dataset berasal dari pasar India dan harganya dalam **INR (₹)**. Tampilan di web harus menulis `₹`, bukan `Rp`. Mengonversi ke rupiah membutuhkan kurs dan tidak dilakukan pada prototipe ini.
- **Periode data.** Data merepresentasikan kondisi pasar pada saat dikumpulkan. Harga pasar berubah, sehingga prediksi tidak berlaku untuk saat ini.
- **Cakupan data.** Model hanya tahu merek, model, dan atribut yang ada di dataset. Kondisi fisik mobil (kerusakan, cat, riwayat servis), lokasi, dan ketersediaan tidak termasuk.
- **Outlier.** Data memiliki nilai ekstrem (misalnya jarak tempuh jutaan km dan harga puluhan juta). Keputusan membuang atau mempertahankan dicatat di laporan.
- **Ketidakseimbangan merek.** Beberapa merek memiliki sampel sangat sedikit (misalnya Ferrari dengan 1 baris), sehingga prediksinya kurang dapat diandalkan.
- **Rentang estimasi.** Rentang ± MAE dihitung dari data uji. Ini bukan interval kepercayaan statistik dan harus dijelaskan dengan benar di UI.

---

## 9. Disclaimer Akademik (teks wajib)

> **Disclaimer Akademik:** Sistem ini adalah prototipe edukatif yang dibuat untuk keperluan Tugas Besar Praktikum Pembelajaran Mesin. Estimasi harga yang ditampilkan berasal dari model statistik yang dilatih pada data historis dan **bukan merupakan penilaian profesional, penilaian resmi, atau dasar keputusan jual beli nyata**. Gunakan hasil ini hanya sebagai bahan belajar.

Teks ini ditampilkan di footer landing page dan di bawah hasil prediksi.

---

## 10. Pembagian Tanggung Jawab Produk

Pembagian detail per anggota ada di HANDOFF.md. Ringkasannya:

- **Backend:** API, validasi, pemuatan model, penanganan error.
- **Data & ML:** EDA, cleaning, pipeline, evaluasi, export model.
- **Frontend:** layout, styling, dan logika Fetch.
- **Dokumentasi & QA:** laporan, test case, screenshot, dan integrasi akhir.

---

## Lampiran A: Penelusuran Kebutuhan terhadap Panduan

Tabel ini memastikan setiap butir wajib di panduan memiliki tempat di dokumen.

| Butir panduan | Dokumen / bagian |
|---|---|
| Dataset tabular `.csv`, 8–15 fitur input | ARCHITECTURE §4.4, §7 (11 fitur) |
| Dataset tidak boleh `student-por.csv` | PRD §8 (dataset `cardekho_dataset.csv`) |
| Pipeline + ColumnTransformer, anti data leakage | ARCHITECTURE §7 |
| Export `.joblib` | ARCHITECTURE §3, §7 |
| FastAPI | ARCHITECTURE §4 |
| Pydantic `BaseModel` dengan `Field(ge=, le=)` | ARCHITECTURE §5.3, DESIGN §3 |
| `GET /health`, `POST /predict` | ARCHITECTURE §5 |
| HTML5, CSS3, JavaScript Fetch | ARCHITECTURE §8, DESIGN |
| Form tanpa page reload | PRD F3 |
| Menampilkan prediksi dan probabilitas secara informatif | PRD F4–F5 (rentang untuk regresi, perlu konfirmasi) |
| Disclaimer Akademik | PRD §9, DESIGN §6 |
| Alur 6 langkah | HANDOFF §3 |
| Struktur proyek lokal | ARCHITECTURE §3 |
| Uvicorn `app:app --reload` | ARCHITECTURE §10 |
| Metrik regresi MAE, RMSE, R² | ARCHITECTURE §7 |
| 5-fold CV, GridSearchCV | ARCHITECTURE §7 |
| 12 test case | HANDOFF §6 |
| Laporan: cover, BAB I–V, lampiran | HANDOFF §7 |

Catatan: panduan menulis "probabilitas" untuk hasil, tetapi konsep ini hanya berlaku untuk klasifikasi. Untuk regresi, dokumen ini menggunakan rentang estimasi. **Konfirmasi ke asisten sebelum laporan final.**
