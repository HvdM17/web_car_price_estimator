# DESIGN.md: Desain Antarmuka

**Produk:** Estimator Harga Mobil Bekas
**Status:** DRAFT v0.1
**Cakupan:** Landing page (`/`) dan bagian prediksi harga, dengan layout desktop dan mobile.

---

## 1. Referensi Visual dan Analisis

Kelompok memakai screenshot landing page komersial sebagai referensi **struktur layout**, bukan sebagai contoh estetika akhir.

### 1.1 Yang diambil dari referensi

| Elemen | Pengamatan | Adaptasi untuk proyek ini |
|---|---|---|
| Tema gelap | Latar hitam dengan aksen biru dan merah | Tema gelap dengan satu warna aksen, tidak dengan banyak warna |
| Navigasi atas | Logo kiri, menu ikon + label di tengah, tombol bahasa dan menu kanan | Logo kiri, tiga menu (Beranda, Prediksi, Tentang), tanpa pemilih bahasa |
| Hero dua kolom | Judul besar di kiri, kartu contoh hasil di kanan | Sama. Kartu kanan menampilkan contoh prediksi statis |
| Kartu hasil mengambang | Kartu putih dengan dua kotak statistik | Kartu contoh: merek, model, harga prediksi, dan rentang |
| CTA biru solid | Tombol biru di bawah deskripsi | Tombol "Coba Prediksi" dengan gaya yang sama |
| Baris kartu horizontal | Empat kartu kecil di bagian bawah | Tiga kartu fitur |
| Indikator carousel | Titik dan tombol jeda | Tidak dipakai, karena tidak ada carousel di prototipe |

### 1.2 Yang tidak diambil

- Logo, nama merek, dan aset gambar dari situs referensi.
- Teks promosi, klaim "#1 di Indonesia", dan statistik data pasar.
- Efek animasi kompleks dan video latar.
- Pemilih bahasa (proyek ini berbahasa Indonesia).

### 1.3 Catatan ulasan

Referensi ini memperlihatkan pola yang umum dan bisa dipakai ulang. Ada beberapa kekurangan yang sebaiknya tidak ditiru:

- Tombol ikon di navigasi tidak diberi label pada layar kecil, sehingga sulit dipahami.
- Kartu hasil di hero menampilkan angka tanpa penjelasan satuan atau sumber.
- Teks putih di atas gambar latar bisa kurang kontras.
- Kartu di bagian bawah terpotong ("ARENA GX AMBULA...") tanpa cara membaca teks lengkap.

Untuk proyek ini:
- Setiap ikon navigasi disertai label.
- Setiap angka harga diberi satuan `₹`.
- Latar hero dibuat polos atau gradasi gelap tanpa gambar, dengan kontras teks minimal 4,5:1.
- Teks panjang dipotong dengan `text-overflow: ellipsis` dan `title` untuk tooltip.

---

## 2. Sistem Warna dan Tipografi

### 2.1 Variabel CSS

```css
:root {
  --bg: #0b0f17;
  --bg-elevated: #131a26;
  --text: #f5f7fa;
  --text-muted: #9aa4b2;
  --accent: #1f5eff;
  --accent-hover: #3d75ff;
  --success: #22c55e;
  --danger: #ef4444;
  --radius: 12px;
  --space-unit: 8px;
}
```

Kontras minimal: teks utama di atas `--bg` harus memenuhi WCAG AA (4,5:1). Teks sekunder (`--text-muted`) juga harus memenuhi 4,5:1 pada ukuran normal.

### 2.2 Tipografi

- Font: `Inter` dari Google Fonts, dengan fallback `system-ui, -apple-system, Segoe UI, Roboto, sans-serif`.
- Skala: H1 `clamp(2.25rem, 5vw, 3.5rem)`, H2 `2rem`, body `1rem` (16px), label `0.875rem`.
- Baris: `line-height: 1.6` untuk body, `1.2` untuk heading.

---

## 3. Layout dan Breakpoint

| Breakpoint | Lebar | Layout |
|---|---|---|
| Mobile | < 640px | Satu kolom. Menu dalam hamburger. Form satu kolom |
| Tablet | 640–1023px | Hero satu kolom. Form dua kolom |
| Desktop | ≥ 1024px | Hero dua kolom. Form dua kolom. Kartu fitur tiga kolom |

Lebar konten maksimum 1200px, dengan padding horizontal 16px (mobile) dan 32px (desktop).

### 3.1 Struktur Landing Page

```
┌─────────────────────────────────────────────────────────────┐
│ Navbar: Logo | Beranda | Prediksi | Tentang                 │
├─────────────────────────────────┬───────────────────────────┤
│ Hero                            │ Kartu contoh prediksi     │
│ H1: Estimasi harga mobil bekas  │ (statis, dari data uji)   │
│ Deskripsi singkat               │                           │
│ [ Coba Prediksi ]               │                           │
├─────────────────────────────────┴───────────────────────────┤
│ Kartu fitur: [Analisis Data] [Model ML] [Estimasi Cepat]    │
├─────────────────────────────────────────────────────────────┤
│ Cara Kerja: 1. Isi spesifikasi → 2. Sistem memproses →      │
│             3. Lihat estimasi                               │
├─────────────────────────────────────────────────────────────┤
│ Footer: Disclaimer Akademik + nama kelompok                 │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Struktur Halaman Prediksi

```
┌─────────────────────────────────────────────────────────────┐
│ Navbar                                                      │
├─────────────────────────────┬───────────────────────────────┤
│ Form input (11 field)       │ Panel hasil                   │
│  Kelompok: Mobil            │  - Estimasi harga (₹)         │
│  Kelompok: Mesin            │  - Rentang low–high           │
│  Kelompok: Kepemilikan      │  - Info model yang dipakai    │
│  [ Estimasi Harga ]         │  - Disclaimer                 │
│  [ Isi contoh ] (opsional)  │                               │
└─────────────────────────────┴───────────────────────────────┘
```

Pada mobile, panel hasil berada di bawah form. Saat hasil muncul, layar otomatis menggulir ke panel hasil.

---

## 4. Form Input

### 4.1 Pengelompokan field

Field dikelompokkan agar mudah diisi:

**Kelompok A: Identitas mobil**
- Merek (`brand`): dropdown
- Model (`model`): dropdown, bergantung pada merek yang dipilih (opsional, lihat catatan di 4.3)

**Kelompok B: Riwayat pemakaian**
- Usia kendaraan (`vehicle_age`): input angka, tahun
- Jarak tempuh (`km_driven`): input angka, km
- Tipe penjual (`seller_type`): dropdown
- Jenis bahan bakar (`fuel_type`): dropdown
- Transmisi (`transmission_type`): dropdown

**Kelompok C: Spesifikasi teknis**
- Konsumsi BBM (`mileage`): input angka, km/l
- Kapasitas mesin (`engine`): input angka, cc
- Tenaga maksimum (`max_power`): input angka, bhp
- Jumlah kursi (`seats`): dropdown atau input angka, 2–9

### 4.2 Spesifikasi field

Batas nilai sama dengan `schemas.py` dan ARCHITECTURE.md §5.3. Keduanya harus diperbarui bersamaan.

| Field | Komponen | `min` | `max` | `step` | Placeholder | Pesan error |
|---|---|---|---|---|---|---|
| `vehicle_age` | number | 0 | 30 | 1 | "contoh: 5" | "Usia 0–30 tahun" |
| `km_driven` | number | 0 | 1000000 | 1 | "contoh: 50000" | "Jarak tempuh 0–1.000.000 km" |
| `mileage` | number | 4 | 40 | 0.01 | "contoh: 19.5" | "Konsumsi 4–40 km/l" |
| `engine` | number | 500 | 7000 | 1 | "contoh: 1197" | "Kapasitas mesin 500–7000 cc" |
| `max_power` | number | 30 | 700 | 0.1 | "contoh: 82" | "Tenaga 30–700 bhp" |
| `seats` | select | 2 | 9 | - | - | "Pilih jumlah kursi" |
| `brand` | select | - | - | - | "Pilih merek" | "Pilih merek" |
| `model` | select | - | - | - | "Pilih model" | "Pilih model" |
| `seller_type` | select | - | - | - | "Pilih tipe penjual" | "Pilih tipe penjual" |
| `fuel_type` | select | - | - | - | "Pilih bahan bakar" | "Pilih bahan bakar" |
| `transmission_type` | select | - | - | - | "Pilih transmisi" | "Pilih transmisi" |

Validasi browser (`required`, `min`, `max`) hanya membantu pengguna. Validasi resmi tetap di backend.

### 4.3 Opsi dropdown

- **Merek:** 31 nilai setelah pembersihan. `ISUZU` digabung ke `Isuzu`, dan `Mercedes-AMG` diperlakukan sebagai merek tersendiri atau digabung ke `Mercedes-Benz` (keputusan dicatat di laporan).
- **Model:** 120 nilai. Nama model tidak unik antar merek (misalnya `3`, `5`, `7` untuk BMW). Oleh karena itu **model harus dipilih bersama merek**. Pilihan model difilter di frontend sesuai merek yang dipilih.
- **Bahan bakar:** `Petrol`, `Diesel`, `CNG`, `LPG`, `Electric`. Nilai `Electric` hanya 4 baris, jadi perlu diputuskan apakah tetap ditampilkan.
- **Tipe penjual:** `Dealer`, `Individual`, `Trustmark Dealer`.
- **Transmisi:** `Manual`, `Automatic`.

Label yang ditampilkan ke pengguna dalam Bahasa Indonesia, tetapi nilai yang dikirim ke API tetap sama dengan data (misalnya label "Manual", value "Manual"). Ini menghindari kesalahan pemetaan.

### 4.4 Perilaku form

- Tombol "Estimasi Harga" disabled saat request sedang berjalan, dan teksnya berubah menjadi "Menghitung...".
- Input yang salah diberi garis merah dan pesan di bawahnya. Pesan tampil saat field kehilangan fokus, bukan saat mengetik.
- Setelah error server, form tetap terisi.
- Tombol "Isi contoh" (opsional) mengisi form dengan satu contoh mobil dari data uji.

---

## 5. Komponen Hasil

### 5.1 Keadaan (state)

| State | Tampilan |
|---|---|
| Awal | Panel hasil berisi teks "Isi form lalu klik Estimasi Harga" |
| Loading | Spinner kecil dan tombol disabled |
| Sukses | Harga utama besar (contoh: `₹ 2,15,000`), rentang di bawahnya, info model, dan disclaimer |
| Error validasi (422) | Pesan di field terkait, panel hasil menampilkan ringkasan "Periksa kembali isian" |
| Error server (500 / 503) | Kartu merah dengan pesan "Layanan sedang tidak tersedia. Coba lagi beberapa saat." |
| Gagal jaringan | Kartu merah dengan pesan "Tidak dapat terhubung ke server" dan tombol "Coba lagi" |

### 5.2 Format angka

- Harga ditampilkan dengan simbol `₹` dan pemisah ribuan. Pola yang dipakai: `₹ 2,15,000` (format India) atau `₹ 215,000` (format internasional). Keputusan final dicatat di laporan.
- Rentang ditampilkan sebagai `₹ 180,000 – ₹ 250,000`.
- Konsumsi BBM dan tenaga ditampilkan dengan satu desimal.

### 5.3 Penjelasan rentang

Di bawah rentang harga ditulis:
> Rentang ini dihitung dari rata-rata selisih absolut prediksi terhadap harga sebenarnya pada data uji. Ini bukan interval kepercayaan statistik.

---

## 6. Disclaimer

Disclaimer akademik wajib tampil di dua tempat:
1. **Footer** landing page dan halaman prediksi.
2. **Di bawah panel hasil**, setiap kali ada estimasi harga.

Teks disclaimer sama dengan PRD §9. Disclaimer di bawah hasil tidak boleh disembunyikan dengan `display: none` atau dipotong pada layar kecil.

---

## 7. Interaksi dan Aksesibilitas

- Setiap field punya `<label>` yang terhubung dengan `for`/`id`.
- Pesan error menggunakan `aria-live="polite"` agar dibacakan oleh pembaca layar.
- Semua tombol dan tautan bisa dijangkau dengan Tab dan memiliki focus style yang terlihat.
- Target sentuh minimal 44×44 px pada mobile.
- Animasi dibatasi dengan `prefers-reduced-motion`.

---

## 8. Tidak Termasuk

- Tema terang (light mode).
- Pemilih bahasa.
- Animasi carousel dan video latar.
- Grafik tren harga.
- Penyimpanan riwayat prediksi.

---

## 9. Checklist Desain

- [ ] Layout desktop sesuai §3.1 dan §3.2
- [ ] Layout mobile satu kolom, panel hasil di bawah form
- [ ] Semua field memiliki label, batas, dan pesan error
- [ ] Dropdown model difilter berdasarkan merek
- [ ] Format `₹` konsisten di seluruh halaman
- [ ] Disclaimer tampil di footer dan di bawah hasil
- [ ] Kontras teks memenuhi 4,5:1
- [ ] Diuji di layar 375px, 768px, dan 1280px
