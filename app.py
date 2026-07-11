import streamlit as st
import pandas as pd
import numpy as np
import os

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

@st.cache_resource
def train_model(algo, analysis_type, X_train, y_train):
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.svm import SVC, SVR
    from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

    if analysis_type == "Regresi":
        if algo == "Linear Regression": model = LinearRegression()
        elif algo == "Random Forest": model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        elif algo == "SVR": model = SVR()
        elif algo == "KNN": model = KNeighborsRegressor()
        elif algo == "Decision Tree": model = DecisionTreeRegressor(random_state=42)
    else:
        if algo == "Logistic Regression": model = LogisticRegression(max_iter=1000)
        elif algo == "Random Forest": model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        elif algo == "SVM": model = SVC()
        elif algo == "KNN": model = KNeighborsClassifier()
        elif algo == "Decision Tree": model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    return model

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
    st.subheader("Kelompok 1")
    st.caption("Praktikum Data Mining 2026")
    st.markdown("""
    | Nama | GitHub |
    |------|--------|
    | Alvin Alfandy | [alvinalfandy](https://github.com/alvinalfandy) |
    | Abidzar Sabil Handoyo | [eufroshine](https://github.com/eufroshine) |
    | Ridho Fauzi | [ridhoofauzii](https://github.com/ridhoofauzii) |
    """)

df = load_data(uploaded_file)

if df is None:
    st.warning("Dataset tidak ditemukan.")
    st.stop()

st.write(f"Dataset: {df.shape[0]:,} baris, {df.shape[1]} kolom")

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
with col4:
    if 'cnt' in df.columns:
        st.metric("Total Penyewaan", f"{int(df['cnt'].sum()):,}")

tab1, tab2, tab3, tab4 = st.tabs(["Explorasi Data", "Pemodelan", "Prediksi", "Data Mentah"])

with tab1:
    import plotly.express as px
    import plotly.graph_objects as go
    import matplotlib.pyplot as plt
    import seaborn as sns

    if 'dteday' in df.columns and 'cnt' in df.columns:
        st.subheader("Tren Penyewaan Sepeda per Jam")
        df_temp = df.copy()
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
        del df_temp

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Matriks Korelasi")
        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            fig_corr, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', ax=ax, square=True)
            st.pyplot(fig_corr)
            plt.close(fig_corr)

    with col_right:
        st.subheader("Distribusi Fitur")
        if len(numeric_cols) > 0:
            default_idx = list(numeric_cols).index('cnt') if 'cnt' in numeric_cols else 0
            feature_to_plot = st.selectbox("Pilih Fitur", numeric_cols, index=default_idx)
            fig_dist = px.histogram(df, x=feature_to_plot, nbins=30, template='plotly_white')
            fig_dist.update_layout(showlegend=False)
            st.plotly_chart(fig_dist, use_container_width=True)

with tab2:
    import plotly.express as px
    import plotly.graph_objects as go
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

    st.subheader("Konfigurasi Model")

    analysis_type = st.radio("Tipe Analisis:", ["Klasifikasi", "Regresi"], horizontal=True)

    numeric_cols_model = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    exclude_cols = ['cnt', 'casual', 'registered', 'instant']
    all_cols = [c for c in numeric_cols_model if c not in exclude_cols]
    target_col = st.selectbox("Pilih Target", numeric_cols_model, index=numeric_cols_model.index('cnt') if 'cnt' in numeric_cols_model else 0)
    default_features = [c for c in all_cols if c != target_col]
    feature_cols = st.multiselect("Pilih Fitur", [c for c in numeric_cols_model if c != target_col and c not in exclude_cols], default=default_features)

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
            X = df[feature_cols].values
            y = df[target_col].values

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

            try:
                model = train_model(algo, analysis_type, X_train, y_train)
                y_pred_train = model.predict(X_train)
                y_pred = model.predict(X_test)

                st.subheader("Hasil Evaluasi Model")

                if analysis_type == "Regresi":
                    r2_train = r2_score(y_train, y_pred_train)
                    r2_test = r2_score(y_test, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    mae = mean_absolute_error(y_test, y_pred)

                    met1, met2, met3, met4 = st.columns(4)
                    with met1: st.metric("R2 Train", f"{r2_train:.4f}")
                    with met2: st.metric("R2 Test", f"{r2_test:.4f}")
                    with met3: st.metric("RMSE", f"{rmse:.2f}")
                    with met4: st.metric("MAE", f"{mae:.2f}")

                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(name='Train', x=['R2 Score'], y=[r2_train], marker_color='#3498db'))
                    fig_bar.add_trace(go.Bar(name='Test', x=['R2 Score'], y=[r2_test], marker_color='#e74c3c'))
                    fig_bar.update_layout(title='Perbandingan R2 Score (Train vs Test)', yaxis_title='R2 Score', template='plotly_white', barmode='group', yaxis_range=[0, 1])
                    st.plotly_chart(fig_bar, use_container_width=True)

                    viz1, viz2 = st.columns(2)
                    with viz1:
                        st.write("**Aktual vs Prediksi**")
                        fig_pred = px.scatter(x=y_test, y=y_pred, labels={'x': 'Aktual', 'y': 'Prediksi'}, template='plotly_white', opacity=0.6)
                        fig_pred.add_trace(go.Scatter(x=[y.min(), y.max()], y=[y.min(), y.max()], mode='lines', name='Garis Ideal', line=dict(color='red', dash='dash')))
                        st.plotly_chart(fig_pred, use_container_width=True)
                    with viz2:
                        st.write("**Residual Plot**")
                        residuals = y_test - y_pred
                        fig_res = px.scatter(x=y_pred, y=residuals, labels={'x': 'Prediksi', 'y': 'Residual'}, template='plotly_white', opacity=0.6)
                        fig_res.add_hline(y=0, line_dash="dash", line_color="red")
                        st.plotly_chart(fig_res, use_container_width=True)

                else:
                    acc_train = accuracy_score(y_train, y_pred_train)
                    acc_test = accuracy_score(y_test, y_pred)
                    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)

                    met1, met2, met3, met4, met5 = st.columns(5)
                    with met1: st.metric("Accuracy Train", f"{acc_train:.4f}")
                    with met2: st.metric("Accuracy Test", f"{acc_test:.4f}")
                    with met3: st.metric("F1 Score", f"{f1:.4f}")
                    with met4: st.metric("Precision", f"{prec:.4f}")
                    with met5: st.metric("Recall", f"{rec:.4f}")

                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(name='Train', x=['Accuracy'], y=[acc_train], marker_color='#3498db'))
                    fig_bar.add_trace(go.Bar(name='Test', x=['Accuracy'], y=[acc_test], marker_color='#e74c3c'))
                    fig_bar.update_layout(title='Perbandingan Akurasi (Train vs Test)', yaxis_title='Accuracy', template='plotly_white', barmode='group', yaxis_range=[0, 1])
                    st.plotly_chart(fig_bar, use_container_width=True)

                    viz1, viz2 = st.columns(2)
                    with viz1:
                        st.write("**Confusion Matrix**")
                        cm = confusion_matrix(y_test, y_pred)
                        fig_cm = px.imshow(cm, text_auto=True, labels=dict(x="Prediksi", y="Aktual"), template='plotly_white', color_continuous_scale='Blues')
                        st.plotly_chart(fig_cm, use_container_width=True)
                    with viz2:
                        st.write("**Distribusi Prediksi**")
                        pred_df = pd.DataFrame({'Kategori': ['Rendah', 'Tinggi'], 'Jumlah': [(y_pred == 0).sum(), (y_pred == 1).sum()]})
                        fig_dist = px.bar(pred_df, x='Kategori', y='Jumlah', template='plotly_white', color='Kategori', color_discrete_sequence=['#3498db', '#e74c3c'])
                        st.plotly_chart(fig_dist, use_container_width=True)

                if hasattr(model, 'feature_importances_'):
                    st.subheader("Feature Importance")
                    imp_df = pd.DataFrame({'Fitur': feature_cols, 'Importance': model.feature_importances_}).sort_values('Importance', ascending=True)
                    fig_imp = px.bar(imp_df, x='Importance', y='Fitur', orientation='h', template='plotly_white', color='Importance', color_continuous_scale='Viridis')
                    fig_imp.update_layout(showlegend=False)
                    st.plotly_chart(fig_imp, use_container_width=True)

            except Exception as e:
                st.error(f"Terjadi error saat melatih model: {e}")

with tab3:
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

    st.subheader("Prediksi Peluang Penyewaan Sepeda")
    
    model_type = st.radio("Jenis Prediksi:", ["Regresi (Jumlah Sepeda)", "Klasifikasi (Tinggi/Rendah)"], horizontal=True)
    
    st.subheader("Input Data Prediksi")
    st.caption("Masukkan kondisi untuk memprediksi jumlah penyewaan sepeda")
    
    pred_exclude = ['cnt', 'casual', 'registered', 'instant']
    pred_features = [c for c in df.select_dtypes(include=['float64','int64']).columns if c not in pred_exclude]
    
    col1, col2, col3, col4 = st.columns(4)
    input_data = {}
    with col1:
        if 'season' in pred_features:
            input_data['season'] = st.slider("Musim", min_value=1, max_value=4, value=2, step=1)
            st.caption("1=Semi, 2=Panas, 3=Gugur, 4=Dingin")
        if 'yr' in pred_features:
            input_data['yr'] = st.slider("Tahun", min_value=0, max_value=1, value=1, step=1)
            st.caption("0=2011, 1=2012")
        if 'mnth' in pred_features:
            input_data['mnth'] = st.slider("Bulan", min_value=1, max_value=12, value=6, step=1)
        if 'hr' in pred_features:
            input_data['hr'] = st.slider("Jam", min_value=0, max_value=23, value=12, step=1)
    with col2:
        if 'holiday' in pred_features:
            input_data['holiday'] = st.slider("Hari Libur", min_value=0, max_value=1, value=0, step=1)
            st.caption("0=Bukan, 1=Ya")
        if 'weekday' in pred_features:
            input_data['weekday'] = st.slider("Hari", min_value=0, max_value=6, value=3, step=1)
            st.caption("0=Minggu ... 6=Sabtu")
        if 'workingday' in pred_features:
            input_data['workingday'] = st.slider("Hari Kerja", min_value=0, max_value=1, value=1, step=1)
            st.caption("0=Bukan, 1=Ya")
        if 'weathersit' in pred_features:
            input_data['weathersit'] = st.slider("Cuaca", min_value=1, max_value=4, value=1, step=1)
            st.caption("1=Cerah, 2=Berawan, 3=Hujan, 4=Ekstrem")
    with col3:
        if 'temp' in pred_features:
            input_data['temp'] = st.slider("Suhu", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
            st.caption("Ternormalisasi (0=-8C, 1=39C)")
        if 'atemp' in pred_features:
            input_data['atemp'] = st.slider("Suhu Terasa", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
            st.caption("Ternormalisasi")
    with col4:
        if 'hum' in pred_features:
            input_data['hum'] = st.slider("Kelembaban", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
            st.caption("Ternormalisasi (0=Kering, 1=Lembab)")
        if 'windspeed' in pred_features:
            input_data['windspeed'] = st.slider("Kecepatan Angin", min_value=0.0, max_value=1.0, value=0.3, step=0.01)
            st.caption("Ternormalisasi (0=Tenang, 1=Kencang)")

    st.subheader("Hasil Prediksi")
    
    if st.button("Hitung Prediksi", use_container_width=True):
        with st.spinner("Menghitung..."):
            feature_cols_pred = list(input_data.keys())
            target_col_pred = 'cnt'
            
            missing_features = [f for f in feature_cols_pred if f not in df.columns]
            if missing_features:
                st.error(f"Fitur {missing_features} tidak ditemukan di dataset.")
                st.stop()
            
            X_pred = df[feature_cols_pred].values
            y_pred_target = df[target_col_pred].values
            
            if model_type == "Klasifikasi (Tinggi/Rendah)":
                median_cnt = np.median(y_pred_target)
                y_pred_target = (y_pred_target >= median_cnt).astype(int)
            
            try:
                if model_type == "Regresi (Jumlah Sepeda)":
                    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
                else:
                    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
                model.fit(X_pred, y_pred_target)
                
                input_df = pd.DataFrame([input_data])
                
                pred_result = model.predict(input_df)[0]
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if model_type == "Regresi (Jumlah Sepeda)":
                        st.metric("Prediksi Jumlah Penyewaan", f"{int(round(pred_result))} sepeda")
                    else:
                        st.metric("Prediksi Kategori", "Tinggi" if pred_result >= 1 else "Rendah")
                with col_b:
                    if model_type == "Regresi (Jumlah Sepeda)":
                        q25, q50, q75 = np.percentile(df['cnt'], [25, 50, 75])
                        if pred_result < q25:
                            status, color = "Sangat Rendah", "red"
                        elif pred_result < q50:
                            status, color = "Rendah", "orange"
                        elif pred_result < q75:
                            status, color = "Sedang", "blue"
                        else:
                            status, color = "Tinggi", "green"
                        st.markdown(f"<h3 style='color:{color}'>Status: {status}</h3>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")

with tab4:
    st.subheader("Data Mentah")
    st.dataframe(df, use_container_width=True)
