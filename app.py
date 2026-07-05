import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Analisis Bike Sharing",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #fafafa; }
    .stButton>button { background-color: #2c3e50; color: white; border-radius: 5px; border: none; }
    .stButton>button:hover { background-color: #34495e; }
    h1, h2, h3 { color: #2c3e50; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("Dashboard Analisis Bike Sharing")

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            return pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
            return None
    else:
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bike-sharing-dataset", "hour.csv")
        if os.path.exists(default_path):
            return pd.read_csv(default_path)
        return None

with st.sidebar:
    st.title("Analisis Bike Sharing")
    st.markdown("---")
    st.subheader("Upload Dataset")
    uploaded_file = st.file_uploader("Upload file CSV (.csv)", type=["csv"])
    if uploaded_file is not None:
        st.success(f"File dimuat: {uploaded_file.name}")
    else:
        st.caption("Menggunakan dataset default: hour.csv")
    st.markdown("---")
    st.markdown("**Kelompok 1**")
    st.caption("Praktikum Data Mining 2026")

df = load_data(uploaded_file)

if df is None:
    st.warning("Dataset tidak ditemukan.")
    st.stop()

st.write(f"Dataset: {df.shape[0]:,} baris, {df.shape[1]} kolom")

# Ensure df is a clean copy to avoid cache mutation issues
df = df.copy()

st.subheader("Statistik Dataset")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Baris", f"{df.shape[0]:,}")
with col2:
    st.metric("Total Kolom", f"{df.shape[1]}")
with col3:
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if 'cnt' in df.columns:
        st.metric("Rata-rata Penyewaan", f"{int(df['cnt'].mean()):,}")
    elif len(numeric_cols) > 0:
        st.metric(f"Rata-rata {numeric_cols[0]}", f"{df[numeric_cols[0]].mean():.2f}")
with col4:
    if 'cnt' in df.columns:
        st.metric("Total Penyewaan", f"{int(df['cnt'].sum()):,}")
    elif len(numeric_cols) > 0:
        st.metric(f"Total {numeric_cols[0]}", f"{df[numeric_cols[0]].sum():.2f}")

tab1, tab2, tab3, tab4 = st.tabs(["Explorasi Data", "Pemodelan", "Prediksi", "Data Mentah"])

with tab1:
    df_temp = df.copy()
    if 'dteday' in df_temp.columns and 'cnt' in df_temp.columns:
        st.subheader("Tren Penyewaan Sepeda per Jam")
        df_temp['dteday'] = pd.to_datetime(df_temp['dteday'])
        if 'hr' in df_temp.columns:
            df_temp['datetime'] = df_temp['dteday'] + pd.to_timedelta(df_temp['hr'], unit='h')
            fig_ts = px.line(df_temp, x='datetime', y='cnt', labels={'datetime': 'Waktu', 'cnt': 'Jumlah Penyewaan'}, template='plotly_white')
        else:
            fig_ts = px.line(df_temp, x='dteday', y='cnt', labels={'dteday': 'Tanggal', 'cnt': 'Jumlah Penyewaan'}, template='plotly_white')
        fig_ts.update_layout(showlegend=False)
        st.plotly_chart(fig_ts, use_container_width=True)

        if 'hr' in df_temp.columns:
            st.subheader("Rata-rata Penyewaan per Jam")
            hourly_avg = df_temp.groupby('hr')['cnt'].mean().reset_index()
            fig_hourly = px.bar(hourly_avg, x='hr', y='cnt', labels={'hr': 'Jam', 'cnt': 'Rata-rata Penyewaan'}, template='plotly_white')
            fig_hourly.update_layout(showlegend=False)
            st.plotly_chart(fig_hourly, use_container_width=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Matriks Korelasi")
        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            fig_corr, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', ax=ax, square=True)
            st.pyplot(fig_corr)
        else:
            st.info("Tidak cukup kolom numerik untuk menampilkan korelasi.")

    with col_right:
        st.subheader("Distribusi Fitur")
        if len(numeric_cols) > 0:
            default_idx = list(numeric_cols).index('cnt') if 'cnt' in numeric_cols else 0
            feature_to_plot = st.selectbox("Pilih Fitur", numeric_cols, index=default_idx)
            fig_dist = px.histogram(df, x=feature_to_plot, nbins=30, template='plotly_white')
            fig_dist.update_layout(showlegend=False)
            st.plotly_chart(fig_dist, use_container_width=True)

with tab2:
    st.subheader("Konfigurasi Model")

    analysis_type = st.radio("Tipe Analisis:", ["Klasifikasi", "Regresi"], horizontal=True)

    numeric_cols_model = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    all_cols = numeric_cols_model
    target_col = st.selectbox("Pilih Target", all_cols, index=all_cols.index('cnt') if 'cnt' in all_cols else 0)
    default_features = [c for c in ['temp', 'hum', 'windspeed', 'season'] if c in all_cols and c != target_col]
    feature_cols = st.multiselect("Pilih Fitur", [c for c in all_cols if c != target_col], default=default_features)

    if not feature_cols:
        st.warning("Pilih minimal 1 fitur.")
        st.stop()

    if analysis_type == "Regresi":
        algo = st.selectbox("Algoritma", ["Linear Regression", "Random Forest", "SVR", "KNN", "Decision Tree"])
    else:
        algo = st.selectbox("Algoritma", ["Logistic Regression", "Random Forest", "SVM", "KNN", "Decision Tree"])

    test_size = st.slider("Ukuran Data Test (%)", 10, 40, 20) / 100.0

    if st.button("Latih Model", use_container_width=True):
        with st.spinner("Sedang melatih model..."):
            X = df[feature_cols]
            y = df[target_col]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

            model = None
            if analysis_type == "Regresi":
                if algo == "Linear Regression": model = LinearRegression()
                elif algo == "Random Forest": model = RandomForestRegressor(n_estimators=100, random_state=42)
                elif algo == "SVR": model = SVR()
                elif algo == "KNN": model = KNeighborsRegressor()
                elif algo == "Decision Tree": model = DecisionTreeRegressor(random_state=42)
            else:
                if algo == "Logistic Regression": model = LogisticRegression(max_iter=1000)
                elif algo == "Random Forest": model = RandomForestClassifier(n_estimators=100, random_state=42)
                elif algo == "SVM": model = SVC()
                elif algo == "KNN": model = KNeighborsClassifier()
                elif algo == "Decision Tree": model = DecisionTreeClassifier(random_state=42)

            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                st.subheader("Hasil Evaluasi Model")
                res_col1, res_col2 = st.columns(2)

                with res_col1:
                    st.write("**Metrik Evaluasi**")
                    if analysis_type == "Regresi":
                        st.metric("R2 Score", f"{r2_score(y_test, y_pred):.4f}")
                        st.metric("RMSE", f"{np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")
                        st.metric("MAE", f"{mean_absolute_error(y_test, y_pred):.4f}")
                    else:
                        st.metric("Accuracy", f"{accuracy_score(y_test, y_pred):.4f}")
                        st.metric("F1 Score", f"{f1_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
                        st.metric("Precision", f"{precision_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")

                with res_col2:
                    st.write("**Visualisasi Prediksi**")
                    if analysis_type == "Regresi":
                        fig_pred = px.scatter(x=y_test, y=y_pred, labels={'x': 'Aktual', 'y': 'Prediksi'}, template='plotly_white')
                        fig_pred.add_trace(go.Scatter(x=[y.min(), y.max()], y=[y.min(), y.max()], mode='lines', name='Garis Ideal', line=dict(color='red', dash='dash')))
                        fig_pred.update_layout(showlegend=False)
                        st.plotly_chart(fig_pred, use_container_width=True)
                    else:
                        cm = confusion_matrix(y_test, y_pred)
                        fig_cm = px.imshow(cm, text_auto=True, labels=dict(x="Prediksi", y="Aktual"), template='plotly_white')
                        st.plotly_chart(fig_cm, use_container_width=True)

            except Exception as e:
                st.error(f"Terjadi error saat melatih model: {e}")

with tab3:
    st.subheader("Prediksi Peluang Penyewaan Sepeda")
    
    model_type = st.radio("Jenis Prediksi:", ["Regresi (Jumlah Sepeda)", "Klasifikasi (Tinggi/Rendah)"], horizontal=True)
    
    st.subheader("Input Data Prediksi")
    st.caption("Masukkan kondisi untuk memprediksi jumlah penyewaan sepeda")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        temp = st.slider("Suhu", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
        st.caption("Ternormalisasi: 0 = -8 derajat C, 1 = 39 derajat C")
        hum = st.slider("Kelembaban", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
        st.caption("Ternormalisasi: 0 = Kering, 1 = Lembab")
    with col2:
        windspeed = st.slider("Kecepatan Angin", min_value=0.0, max_value=1.0, value=0.3, step=0.01)
        st.caption("Ternormalisasi: 0 = Tenang, 1 = Kencang")
        season = st.slider("Musim", min_value=1, max_value=4, value=2, step=1)
        st.caption("1 = Semi, 2 = Panas, 3 = Gugur, 4 = Dingin")
    with col3:
        weathersit = st.slider("Situasi Cuaca", min_value=1, max_value=4, value=1, step=1)
        st.caption("1 = Cerah, 2 = Berawan, 3 = Hujan Ringan, 4 = Hujan Deras")
        holiday = st.slider("Hari Libur", min_value=0, max_value=1, value=0, step=1)
        st.caption("0 = Bukan, 1 = Ya")
    with col4:
        workingday = st.slider("Hari Kerja", min_value=0, max_value=1, value=1, step=1)
        st.caption("0 = Bukan, 1 = Ya")
        yr = st.slider("Tahun", min_value=0, max_value=1, value=1, step=1)
        st.caption("0 = 2011, 1 = 2012")

    st.subheader("Hasil Prediksi")
    
    if st.button("Hitung Prediksi", use_container_width=True):
        with st.spinner("Menghitung..."):
            # Default features for prediction
            feature_cols_pred = ['temp', 'hum', 'windspeed', 'season']
            target_col_pred = 'cnt'
            
            # Check if features exist in dataset
            missing_features = [f for f in feature_cols_pred if f not in df.columns]
            if missing_features:
                st.error(f"Fitur {missing_features} tidak ditemukan di dataset.")
                st.stop()
            
            X_pred = df[feature_cols_pred]
            y_pred_target = df[target_col_pred]
            
            if model_type == "Klasifikasi (Tinggi/Rendah)":
                median_cnt = y_pred_target.median()
                y_pred_target = (y_pred_target >= median_cnt).astype(int)
            
            X_train_pred, X_test_pred, y_train_pred, y_test_pred = train_test_split(X_pred, y_pred_target, test_size=0.2, random_state=42)
            
            model = None
            
            try:
                if model_type == "Regresi (Jumlah Sepeda)":
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                    model.fit(X_train_pred, y_train_pred)
                else:
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                    model.fit(X_train_pred, y_train_pred)
                
                input_data = pd.DataFrame({
                    'temp': [temp],
                    'hum': [hum],
                    'windspeed': [windspeed],
                    'season': [season]
                })
                
                pred_result = model.predict(input_data)[0]
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if model_type == "Regresi (Jumlah Sepeda)":
                        st.metric("Prediksi Jumlah Penyewaan", f"{int(round(pred_result))} sepeda")
                    else:
                        st.metric("Prediksi Kategori", "Tinggi" if pred_result >= 1 else "Rendah")
                with col_b:
                    if model_type == "Regresi (Jumlah Sepeda)":
                        if pred_result < df['cnt'].quantile(0.25):
                            status = "Sangat Rendah"
                            color = "red"
                        elif pred_result < df['cnt'].quantile(0.50):
                            status = "Rendah"
                            color = "orange"
                        elif pred_result < df['cnt'].quantile(0.75):
                            status = "Sedang"
                            color = "blue"
                        else:
                            status = "Tinggi"
                            color = "green"
                        st.markdown(f"<h3 style='color:{color}'>Status: {status}</h3>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

with tab4:
    st.subheader("Data Mentah")
    st.dataframe(df, use_container_width=True)
