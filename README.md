# Analisis Bike Sharing Dataset

Aplikasi web interaktif untuk analisis dan prediksi penyewaan sepeda berbasis dataset Bike Sharing dari UCI Machine Learning Repository.

## Tentang Project

Project akhir Praktikum Data Mining 2026. Aplikasi ini dibangun menggunakan Python dan Streamlit untuk menganalisis pola penyewaan sepeda dan memprediksi jumlah penyewaan berdasarkan faktor cuaca, musim, dan hari.

## Dataset

Dataset: [Bike Sharing Dataset](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) - UCI Machine Learning Repository

- File: `hour.csv`
- Jumlah baris: 17.379
- Jumlah kolom: 17

## Fitur Aplikasi

- Upload dataset custom (.csv)
- Explorasi Data: tren penyewaan, korelasi, distribusi
- Pemodelan: Linear Regression, Random Forest, SVM, KNN, Decision Tree
- Prediksi interaktif berdasarkan input cuaca, suhu, musim, dll
- Evaluasi model: R2, RMSE, MAE, Accuracy, F1 Score

## Cara Menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tim - Kelompok 1

| Nama | GitHub |
|------|--------|
| Alvin Alfandy | [alvinalfandy](https://github.com/alvinalfandy) |
| Abidzar Sabil Handoyo | [eufroshine](https://github.com/eufroshine) |
| Ridho Fauzi | [ridhoofauzii](https://github.com/ridhoofauzii) |

## Link Deploy

[https://bike-sharing-analysis-aby.streamlit.app](https://bike-sharing-analysis-aby.streamlit.app)
