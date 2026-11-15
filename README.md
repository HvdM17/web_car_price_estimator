# Estimator Harga Mobil Bekas

Prototipe edukatif prediksi harga mobil bekas berbasis FastAPI dan scikit-learn. Harga berasal dari dataset CarDekho dan ditampilkan dalam INR.

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

`POST /predict` menerima 11 fitur kendaraan dan mengembalikan estimasi harga, rentang ± MAE, mata uang, nama model yang ramah pengguna, serta versi artefak model. `GET /options` menjadi sumber kategori frontend dan validasi pasangan merek-model.

## Disclaimer Akademik

Sistem ini adalah prototipe edukatif yang dibuat untuk keperluan Tugas Besar Praktikum Pembelajaran Mesin. Estimasi harga berasal dari model statistik yang dilatih pada data historis dan bukan penilaian profesional, penilaian resmi, atau dasar keputusan jual beli nyata.

## Keterbatasan

Model hanya menggunakan fitur yang tersedia di dataset dan tidak mempertimbangkan kondisi fisik, lokasi, riwayat servis, atau perubahan harga pasar terkini. Rentang ± MAE bukan interval kepercayaan statistik.
