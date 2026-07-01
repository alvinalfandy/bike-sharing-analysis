# Bike Sharing Dataset Analysis

Aplikasi Streamlit untuk analisis dataset Bike Sharing.

## Deskripsi
Project akhir praktikum Data Mining 2026. Aplikasi ini memungkinkan pengguna untuk:
- Mengupload dataset (.csv)
- Melakukan analisis eksplorasi data (EDA)
- Visualisasi korelasi fitur
- Membangun model Regresi Linier untuk prediksi jumlah penyewaan sepeda (`cnt`)

## Instalasi
1. Clone repositori ini
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```bash
   streamlit run app.py
   ```

## Dataset
Dataset yang digunakan adalah [Bike Sharing Dataset](https://archive.ics.uci.edu/ml/datasets/Bike+Sharing+Dataset) dari UCI Machine Learning Repository.

## Fitur
- Upload dataset custom (.csv)
- Preview dataset
- Visualisasi heatmap korelasi
- Training model Regresi Linier
- Evaluasi model (MAE, MSE, RMSE, R2 Score)
- Visualisasi Prediksi vs Aktual
