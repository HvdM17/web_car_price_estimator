# Estimator Harga Mobil Bekas

Prototipe edukatif prediksi harga mobil bekas berbasis FastAPI dan scikit-learn. Harga model berasal dari dataset CarDekho dalam INR, lalu ditampilkan dalam Rupiah (IDR) menggunakan kurs lokal yang tercatat.

## Menjalankan

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python training\train.py
uvicorn backend.app:app --reload
```

Buka `http://127.0.0.1:8000/`. Dokumentasi API tersedia di `/docs`, status model di `/health`, dan opsi dropdown di `/options`.

Server juga dapat dijalankan dari folder `backend` dengan `uvicorn app:app --reload`.

## API singkat

`POST /predict` menerima 11 fitur kendaraan dan mengembalikan harga model dalam INR, hasil konversi IDR, rentang ± MAE, nama model, serta versi artefak. `GET /options` menjadi sumber kategori frontend dan validasi pasangan merek-model.

## Disclaimer Akademik

Sistem ini adalah prototipe edukatif yang dibuat untuk keperluan Tugas Besar Praktikum Pembelajaran Mesin. Estimasi harga berasal dari model statistik yang dilatih pada data historis dan bukan penilaian profesional, penilaian resmi, atau dasar keputusan jual beli nyata.

## Keterbatasan

Model aktif adalah Random Forest dengan transformasi target `log1p`. Evaluasi holdout menghasilkan MAE `108362.81 INR`, RMSE `617818.45 INR`, dan R² `0.7045` pada 3.048 baris uji. Model hanya menggunakan fitur yang tersedia di dataset dan tidak mempertimbangkan kondisi fisik, lokasi, riwayat servis, atau perubahan harga pasar terkini. Rentang ± MAE adalah error tipikal, bukan interval kepercayaan statistik.
