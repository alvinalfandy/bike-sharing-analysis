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
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import plotly.express as px
import plotly.graph_objects as go

# Page Config
st.set_page_config(
    page_title="Pro Analisis Bike Sharing",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Look
st.markdown("""
<style>
    .main { background-color: #f5f5f5; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 5px; }
    .stTextInput>div>div>input { border-radius: 5px; }
    .metric-card { 
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    h1, h2, h3 { color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.title("🚲 Bike Sharing Analytics")
    st.markdown("---")
    
    # File Upload
    st.subheader("📁 Data Input")
    st.caption("Dataset default sudah dimuat. Upload file baru jika ingin mengganti.")
    uploaded_file = st.file_uploader("Upload Custom Dataset (.csv)", type=["csv"])
    
    st.markdown("---")
    st.info("Aplikasi ini dibuat untuk Analisis Data Mining.")
    st.markdown("Made with ❤️ by Kelompok 1")

# Main Content
st.title("🚲 Dashboard Analisis Bike Sharing")

# Load Data
@st.cache_data
def load_data(file):
    if file is not None:
        return pd.read_csv(file)
    else:
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bike-sharing-dataset", "day.csv")
        if os.path.exists(default_path):
            return pd.read_csv(default_path)
        return None

df = load_data(uploaded_file)

if df is None:
    st.error("⚠️ Dataset tidak ditemukan. Silakan upload file CSV.")
    st.stop()

# Metrics Row
st.subheader("📊 Statistik Dataset")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Baris", f"{df.shape[0]:,}")
with col2:
    st.metric("Total Kolom", f"{df.shape[1]}")
with col3:
    if 'cnt' in df.columns:
        st.metric("Rata-rata Penyewaan", f"{int(df['cnt'].mean()):,}")
with col4:
    if 'cnt' in df.columns:
        st.metric("Total Penyewaan", f"{int(df['cnt'].sum()):,}")

# Tabs for Analysis
tab1, tab2, tab3 = st.tabs(["📈 Explorasi Data", "🔬 Pemodelan", "📥 Data Mentah"])

with tab1:
    # Time Series Plot
    if 'dteday' in df.columns and 'cnt' in df.columns:
        st.subheader("Tren Penyewaan Sepeda")
        df['dteday'] = pd.to_datetime(df['dteday'])
        fig_ts = px.line(df, x='dteday', y='cnt', title='Jumlah Penyewaan Harian', template='plotly_white')
        st.plotly_chart(fig_ts, use_container_width=True)

    # Correlation & Distribution
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Korelasi Fitur")
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        corr = df[numeric_cols].corr()
        fig_corr, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
        st.pyplot(fig_corr)
    
    with col_right:
        st.subheader("Distribusi Fitur")
        feature_to_plot = st.selectbox("Pilih Fitur", numeric_cols, index=list(numeric_cols).index('cnt') if 'cnt' in numeric_cols else 0)
        fig_dist = px.histogram(df, x=feature_to_plot, nbins=30, title=f'Distribusi {feature_to_plot}', template='plotly_white')
        st.plotly_chart(fig_dist, use_container_width=True)

with tab2:
    st.subheader("⚙️ Konfigurasi Model")
    
    # Analysis Type
    analysis_type = st.radio("Tipe Analisis:", ["Klasifikasi", "Regresi"], horizontal=True)
    
    # Target & Features
    all_cols = df.columns.tolist()
    target_col = st.selectbox("Pilih Target", all_cols)
    feature_cols = st.multiselect("Pilih Fitur", [c for c in all_cols if c != target_col], default=[c for c in ['temp', 'hum', 'windspeed', 'season'] if c != target_col])
    
    if not feature_cols:
        st.warning("Pilih minimal 1 fitur.")
        st.stop()

    # Algorithm Selection
    if analysis_type == "Regresi":
        algo = st.selectbox("Algoritma", ["Linear Regression", "Random Forest", "SVR", "KNN", "Decision Tree"])
    else:
        algo = st.selectbox("Algoritma", ["Logistic Regression", "Random Forest", "SVM", "KNN", "Decision Tree"])

    # Training Settings
    test_size = st.slider("Ukuran Data Test (%)", 10, 40, 20) / 100.0
    
    if st.button("🚀 Latih Model", use_container_width=True):
        with st.spinner('Melatih model...'):
            X = df[feature_cols]
            y = df[target_col]
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            
            # Model Initialization
            model = None
            if analysis_type == "Regresi":
                if algo == "Linear Regression": model = LinearRegression()
                elif algo == "Random Forest": model = RandomForestRegressor()
                elif algo == "SVR": model = SVR()
                elif algo == "KNN": model = KNeighborsRegressor()
                elif algo == "Decision Tree": model = DecisionTreeRegressor()
            else:
                if algo == "Logistic Regression": model = LogisticRegression(max_iter=1000)
                elif algo == "Random Forest": model = RandomForestClassifier()
                elif algo == "SVM": model = SVC()
                elif algo == "KNN": model = KNeighborsClassifier()
                elif algo == "Decision Tree": model = DecisionTreeClassifier()
            
            # Train
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Results
            st.subheader("🏆 Hasil Evaluasi Model")
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.write("### Metrik")
                if analysis_type == "Regresi":
                    st.metric("R2 Score", f"{r2_score(y_test, y_pred):.4f}")
                    st.metric("RMSE", f"{np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")
                else:
                    st.metric("Accuracy", f"{accuracy_score(y_test, y_pred):.4f}")
                    st.metric("F1 Score", f"{f1_score(y_test, y_pred, average='weighted'):.4f}")
            
            with res_col2:
                st.write("### Visualisasi Prediksi")
                if analysis_type == "Regresi":
                    fig_pred = px.scatter(x=y_test, y=y_pred, labels={'x': 'Aktual', 'y': 'Prediksi'}, title='Prediksi vs Aktual')
                    fig_pred.add_trace(go.Scatter(x=[y.min(), y.max()], y=[y.min(), y.max()], mode='lines', name='Garis Ideal', line=dict(color='red', dash='dash')))
                    st.plotly_chart(fig_pred, use_container_width=True)
                else:
                    cm = confusion_matrix(y_test, y_pred)
                    fig_cm = px.imshow(cm, text_auto=True, title='Confusion Matrix', labels=dict(x="Prediksi", y="Aktual"))
                    st.plotly_chart(fig_cm, use_container_width=True)

with tab3:
    st.subheader("📋 Data Mentah")
    st.dataframe(df, use_container_width=True)
