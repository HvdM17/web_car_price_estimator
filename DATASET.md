# Dataset

## Identitas

- Nama lokal: `data/cardekho_dataset.csv`
- Domain: harga mobil bekas
- Sumber: [CarDekho Used Car Dataset di Kaggle](https://www.kaggle.com/datasets/manishkr1754/cardekho-used-car-data)
- Mata uang target: INR
- Baris mentah yang tercatat di PRD: 15.411
- Baris setelah cleaning: 15.240

## Status sumber dan lisensi

- URL halaman distribusi: https://www.kaggle.com/datasets/manishkr1754/cardekho-used-car-data
- Status distribusi: hanya untuk penggunaan akademik internal sampai sumber dan lisensi dikonfirmasi.

## Cleaning aktif

- Kolom index dibuang.
- Duplikat dibuang.
- Kategori `ISUZU` dinormalisasi menjadi `Isuzu`.
- Nilai numerik dan target dikonversi ke numerik.
- Baris dengan nilai wajib kosong dibuang.
- Baris `seats < 2` dibuang.
- Baris `km_driven > 1.000.000` dibuang.
